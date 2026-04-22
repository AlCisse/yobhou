import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'package:shared_preferences/shared_preferences.dart';

class InvoiceUploadScreen extends StatefulWidget {
  final Map<String, dynamic> registrationData;

  const InvoiceUploadScreen({super.key, required this.registrationData});

  @override
  State<InvoiceUploadScreen> createState() => _InvoiceUploadScreenState();
}

class _InvoiceUploadScreenState extends State<InvoiceUploadScreen> {
  XFile? _invoiceFile;
  final ImagePicker _picker = ImagePicker();
  bool _isProcessing = false;
  String? _accessToken;

  // Données extraites de la facture EDG
  Map<String, dynamic>? _extractedData;

  // Champs à extraire
  final Map<String, String> _fieldLabels = {
    'nom_titulaire': 'Nom du titulaire',
    'quartier': 'Quartier',
    'numero_compteur': 'N° Compteur',
    'conso_actuelle': 'Consommation actuelle (kWh)',
    'tranche_conso': 'Tranche de conso',
    'tarification': 'Tarification',
    'date_facture': 'Date facture',
    'montant': 'Montant (GNF)',
  };

  @override
  void initState() {
    super.initState();
    _loadAccessToken();
  }

  Future<void> _loadAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _accessToken = prefs.getString('access_token');
    });
  }

  Future<void> _pickInvoice(ImageSource source) async {
    final pickedFile = await _picker.pickImage(
      source: source,
      maxWidth: 640,  // Réduit pour vitesse OCR (matche backend 320-640px)
      maxHeight: 640,
      imageQuality: 75,  // Compression accrue pour vitesse
    );

    if (pickedFile != null) {
      setState(() {
        _invoiceFile = pickedFile;
        _isProcessing = true;
        _extractedData = null;
      });

      await _processInvoice();
    }
  }

  Future<void> _processInvoice() async {
    if (_invoiceFile == null) return;

    try {
      // Préparation de la requête multipart
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('${const String.fromEnvironment('API_URL', defaultValue: 'http://10.0.2.2:8000/api')}/upload-invoice/'),
      );

      // Ajouter le token d'authentification si disponible
      if (_accessToken != null) {
        request.headers['Authorization'] = 'Bearer $_accessToken';
      }

      // Ajouter le fichier
      request.files.add(
        await http.MultipartFile.fromPath(
          'invoice',
          _invoiceFile!.path,
          filename: 'invoice_${DateTime.now().millisecondsSinceEpoch}.jpg',
        ),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);

        // Parser les données OCR pour extraire les infos EDG
        final ocrData = data['ocr_data'] as Map<String, dynamic>?;
        if (ocrData != null) {
          final extractedInfo = _parseEDGInvoice(ocrData['extracted_text'] as List<dynamic>);

          setState(() {
            _extractedData = extractedInfo;
            _isProcessing = false;
          });
        } else {
          setState(() => _isProcessing = false);
          _showError('Aucune donnée extraite');
        }
      } else {
        setState(() => _isProcessing = false);
        final error = jsonDecode(response.body);
        _showError(error['error'] ?? error['message'] ?? 'Erreur lors du traitement');
      }
    } catch (e) {
      setState(() => _isProcessing = false);
      _showError('Erreur de connexion: $e');
    }
  }

  Map<String, dynamic> _parseEDGInvoice(List<dynamic> rawText) {
    // Parser le texte brut pour extraire les informations structurées
    final text = rawText.join('\n').toUpperCase();

    // Extraction avec regex simplifié
    final data = <String, dynamic>{};

    // Numéro de compteur (6-10 chiffres)
    final compteurRegex = RegExp(r'(\d{6,10})');
    final compteurMatch = compteurRegex.firstMatch(text);
    data['numero_compteur'] = compteurMatch?.group(0) ?? 'Non détecté';

    // Quartier (mots après "QUARTIER" ou "SECTEUR")
    final quartierRegex = RegExp(r'(?:QUARTIER|SECTEUR)[:\s]+([A-Z\s]+)', multiLine: true);
    final quartierMatch = quartierRegex.firstMatch(text);
    data['quartier'] = (quartierMatch?.group(1) ?? 'Non détecté').trim();

    // Nom du titulaire (après "TITULAIRE" ou "CLIENT")
    final nomRegex = RegExp(r'(?:TITULAIRE|CLIENT|ABONNE)[:\s]+([A-Z\s]+)', multiLine: true);
    final nomMatch = nomRegex.firstMatch(text);
    data['nom_titulaire'] = (nomMatch?.group(1) ?? 'Non détecté').trim();

    // Consommation actuelle (chiffres avant "KWH")
    final consoRegex = RegExp(r'(\d+(?:\.\d+)?)\s*(?:KWH|CONSOMMATION)', multiLine: true);
    final consoMatch = consoRegex.firstMatch(text);
    data['conso_actuelle'] = consoMatch?.group(1) ?? 'Non détecté';

    // Tranche de consommation
    final trancheRegex = RegExp(r'TRANCHE\s*[:\s]*([A-Z0-9\-]+)', multiLine: true);
    final trancheMatch = trancheRegex.firstMatch(text);
    data['tranche_conso'] = trancheMatch?.group(1) ?? 'Non détecté';

    // Tarification
    final tarifRegex = RegExp(r'(?:PRIX UNITAIRE|TARIF)[:\s]+([\d\s,]+)', multiLine: true);
    final tarifMatch = tarifRegex.firstMatch(text);
    data['tarification'] = tarifMatch?.group(1) ?? 'Non détecté';

    // Montant
    final montantRegex = RegExp(r'(?:TOTAL\s*À\s*PAYER|MONTANT\s*TOTAL)[:\s]+([\d\s,]+)', multiLine: true);
    final montantMatch = montantRegex.firstMatch(text);
    data['montant'] = montantMatch?.group(1) ?? 'Non détecté';

    // Date facture
    final dateRegex = RegExp(r'(\d{2}[/\-]\d{2}[/\-]\d{4})');
    final dateMatch = dateRegex.firstMatch(text);
    data['date_facture'] = dateMatch?.group(0) ?? 'Non détecté';

    // Texte brut pour référence
    data['raw_text'] = rawText;

    return data;
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }

  Future<void> _handleSubmit() async {
    if (_extractedData == null) return;

    // Naviguer vers l'écran de confirmation
    if (mounted) {
      context.push('/register-confirm', extra: {
        ...widget.registrationData,
        ..._extractedData!,
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Facture EDG'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/register'),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Header
              Card(
                color: Colors.blue.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.upload_file, color: Colors.blue.shade700, size: 28),
                          const SizedBox(width: 12),
                          const Text(
                            'Étape 2/2 : Vérification EDG',
                            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Prenez en photo ou importez votre dernière facture EDG pour vérifier votre adresse.',
                        style: TextStyle(fontSize: 14),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Zone de prévisualisation
              if (_invoiceFile == null)
                Container(
                  height: 250,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade200,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.grey.shade400, width: 2),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.document_scanner, size: 80, color: Colors.grey.shade400),
                      const SizedBox(height: 16),
                      Text(
                        'Aucune facture sélectionnée',
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 16),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Prenez une photo ou importez depuis la galerie',
                        style: TextStyle(color: Colors.grey.shade500, fontSize: 14),
                      ),
                    ],
                  ),
                )
              else
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Stack(
                    children: [
                      Image.file(
                        File(_invoiceFile!.path),
                        height: 250,
                        width: double.infinity,
                        fit: BoxFit.cover,
                      ),
                      if (_isProcessing)
                        Container(
                          color: Colors.black54,
                          child: const Center(
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                CircularProgressIndicator(color: Colors.white),
                                SizedBox(height: 16),
                                Text(
                                  'Analyse en cours...',
                                  style: TextStyle(color: Colors.white, fontSize: 16),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              const SizedBox(height: 24),

              // Boutons d'action
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  ElevatedButton.icon(
                    onPressed: _isProcessing ? null : () => _pickInvoice(ImageSource.camera),
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('Prendre photo'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    ),
                  ),
                  ElevatedButton.icon(
                    onPressed: _isProcessing ? null : () => _pickInvoice(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Galerie'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 32),

              // Résultats extraits
              if (_extractedData != null) ...[
                const Divider(),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.green.shade700, size: 28),
                    const SizedBox(width: 12),
                    const Text(
                      'Informations extraites',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Grille des informations
                ..._fieldLabels.entries.map((entry) => _buildInfoRow(entry.value, _extractedData![entry.key] ?? 'N/A')),

                const SizedBox(height: 24),

                // Bouton de confirmation
                SizedBox(
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _handleSubmit,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: const Text(
                      'Confirmer et créer mon compte',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
                const SizedBox(height: 12),

                OutlinedButton.icon(
                  onPressed: () {
                    setState(() {
                      _invoiceFile = null;
                      _extractedData = null;
                    });
                  },
                  icon: const Icon(Icons.refresh),
                  label: const Text('Recommencer'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    final isValid = value != 'Non détecté' && value != 'N/A';

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 140,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 13),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: isValid ? Colors.green.shade50 : Colors.orange.shade50,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: isValid ? Colors.green.shade200 : Colors.orange.shade200,
                ),
              ),
              child: Row(
                children: [
                  if (isValid)
                    Icon(Icons.check, size: 16, color: Colors.green.shade700)
                  else
                    Icon(Icons.warning, size: 16, color: Colors.orange.shade700),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      value,
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        color: isValid ? Colors.green.shade900 : Colors.orange.shade900,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
