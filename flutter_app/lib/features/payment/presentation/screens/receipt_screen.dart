import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../core/constants/colors.dart';
import '../../core/constants/typography.dart';
import '../../core/widgets/app_button.dart';
import '../../core/services/pdf_service.dart';
import '../../core/services/api_service.dart';

class ReceiptScreen extends StatefulWidget {
  final String transactionReference;
  final double amount;
  final String paymentMethod;
  final String meterNumber;
  final DateTime date;
  final String status;

  const ReceiptScreen({
    Key? key,
    required this.transactionReference,
    required this.amount,
    required this.paymentMethod,
    required this.meterNumber,
    required this.date,
    required this.status,
  }) : super(key: key);

  @override
  State<ReceiptScreen> createState() => _ReceiptScreenState();
}

class _ReceiptScreenState extends State<ReceiptScreen> {
  bool _downloading = false;
  bool _sharing = false;

  Future<void> _downloadPdf() async {
    setState(() => _downloading = true);
    
    try {
      // Vérifier permission stockage
      if (Platform.isAndroid) {
        var status = await Permission.storage.request();
        if (!status.isGranted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Permission stockage requise')),
          );
          return;
        }
      }

      // Télécharger PDF depuis API
      final apiService = ApiService();
      final pdfBytes = await apiService.downloadReceipt(widget.transactionReference);
      
      // Sauvegarder dans Downloads
      final directory = await getExternalStorageDirectory();
      final path = '${directory?.path}/reçu_${widget.transactionReference}.pdf';
      
      final file = File(path);
      await file.writeAsBytes(pdfBytes);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Reçu sauvegardé: $path')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur: $e')),
      );
    } finally {
      setState(() => _downloading = false);
    }
  }

  Future<void> _shareReceipt() async {
    setState(() => _sharing = true);
    
    try {
      final apiService = ApiService();
      final pdfBytes = await apiService.downloadReceipt(widget.transactionReference);
      
      final directory = await getTemporaryDirectory();
      final path = '${directory.path}/reçu_${widget.transactionReference}.pdf';
      
      final file = File(path);
      await file.writeAsBytes(pdfBytes);

      await Share.shareXFiles(
        [XFile(path)],
        text: 'Mon reçu de paiement Yobhou - ${widget.transactionReference}',
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur partage: $e')),
      );
    } finally {
      setState(() => _sharing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('dd/MM/yyyy HH:mm');
    
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text(
          'Reçu de Paiement',
          style: AppTypography.h3.copyWith(color: Colors.white),
        ),
        centerTitle: true,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // En-tête avec logo
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  const Icon(
                    Icons.check_circle,
                    color: Colors.white,
                    size: 64,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Paiement Confirmé',
                    style: AppTypography.h2.copyWith(color: Colors.white),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    widget.status == 'COMPLETED' 
                        ? 'Terminé' 
                        : 'En cours',
                    style: AppTypography.body.copyWith(
                      color: Colors.white70,
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Détails transaction
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildDetailRow('Référence:', widget.transactionReference),
                  _buildDetailRow('Date:', dateFormat.format(widget.date)),
                  _buildDetailRow('Montant:', '${widget.amount.toStringAsFixed(0)} GNF'),
                  _buildDetailRow('Méthode:', widget.paymentMethod),
                  _buildDetailRow('Compteur:', widget.meterNumber),
                ],
              ),
            ),
            
            const SizedBox(height: 32),
            
            // Boutons action
            AppButton(
              text: 'Télécharger PDF',
              onPressed: _downloading ? null : _downloadPdf,
              icon: _downloading 
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.download),
              type: ButtonType.primary,
            ),
            
            const SizedBox(height: 12),
            
            AppButton(
              text: 'Partager',
              onPressed: _sharing ? null : _shareReceipt,
              icon: _sharing 
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: AppColors.primary,
                      ),
                    )
                  : const Icon(Icons.share),
              type: ButtonType.outline,
            ),
            
            const SizedBox(height: 12),
            
            AppButton(
              text: 'Retour à l\'accueil',
              onPressed: () => Navigator.of(context).pushNamedAndRemoveUntil(
                '/home',
                (route) => false,
              ),
              type: ButtonType.text,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: AppTypography.body.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          Text(
            value,
            style: AppTypography.body.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
