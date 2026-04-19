import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class RegisterConfirmScreen extends StatefulWidget {
  final Map<String, dynamic> userData;

  const RegisterConfirmScreen({super.key, required this.userData});

  @override
  State<RegisterConfirmScreen> createState() => _RegisterConfirmScreenState();
}

class _RegisterConfirmScreenState extends State<RegisterConfirmScreen> {
  bool _isLoading = false;

  Future<void> _finalizeRegistration() async {
    setState(() => _isLoading = true);

    try {
      // Compléter l'inscription avec les données EDG
      final response = await http.post(
        Uri.parse('${const String.fromEnvironment('API_URL', defaultValue: 'http://10.0.2.2:8000/api')}/complete-registration/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'phone_number': widget.userData['phone_number'],
          'date_of_birth': widget.userData['date_of_birth'],
          'nom_titulaire': widget.userData['nom_titulaire'],
          'quartier': widget.userData['quartier'],
          'numero_compteur': widget.userData['numero_compteur'],
          'conso_actuelle': widget.userData['conso_actuelle'],
          'tranche_conso': widget.userData['tranche_conso'],
          'tarification': widget.userData['tarification'],
          'date_facture': widget.userData['date_facture'],
          'montant': widget.userData['montant'],
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);

        // Sauvegarder les tokens
        final prefs = await SharedPreferences.getInstance();
        if (data['access'] != null) {
          await prefs.setString('access_token', data['access']);
          await prefs.setString('refresh_token', data['refresh']);
        }

        if (mounted) {
          // Navigation vers le dashboard
          context.go('/dashboard');
        }
      } else {
        final error = jsonDecode(response.body);
        _showError(error['message'] ?? 'Erreur lors de la finalisation');
      }
    } catch (e) {
      _showError('Erreur de connexion: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Confirmation'),
        automaticallyImplyLeading: false,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Icone de succès
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.check_circle_outline,
                  size: 80,
                  color: Colors.green.shade700,
                ),
              ),
              const SizedBox(height: 24),

              // Titre
              const Text(
                'Votre compte est prêt !',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              const Text(
                'Vos informations ont été vérifiées avec succès',
                style: TextStyle(fontSize: 14, color: Colors.grey),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),

              // Résumé des informations
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Résumé de votre profil',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const Divider(height: 32),
                      _buildInfoRow('Téléphone', widget.userData['phone_number'] ?? 'N/A'),
                      _buildInfoRow('Compteur', widget.userData['numero_compteur'] ?? 'N/A'),
                      _buildInfoRow('Quartier', widget.userData['quartier'] ?? 'N/A'),
                      _buildInfoRow('Conso. actuelle', '${widget.userData['conso_actuelle'] ?? 'N/A'} kWh'),
                      if (widget.userData['montant'] != null && widget.userData['montant'] != 'Non détecté')
                        _buildInfoRow('Montant facture', '${widget.userData['montant']} GNF'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // Bouton de finalisation
              SizedBox(
                height: 50,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _finalizeRegistration,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : const Text(
                          'Activer mon compte',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}
