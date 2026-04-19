import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class PaymentScreen extends StatelessWidget {
  final double amount;

  const PaymentScreen({super.key, this.amount = 0});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Paiement')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Amount display
            Card(
              color: Colors.blue[50],
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    const Text('Montant à payer', style: TextStyle(color: Colors.grey)),
                    const SizedBox(height: 8),
                    Text(
                      '${amount.toStringAsFixed(0)} GNF',
                      style: const TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: Colors.blue),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Payment methods
            const Text(
              'Choisir le mode de paiement',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            // Orange Money
            _buildPaymentMethod(
              context,
              'Orange Money',
              Icons.phone_android,
              Colors.orange,
              () => _showPaymentDialog(context, 'Orange Money'),
            ),
            const SizedBox(height: 12),

            // MTN Mobile Money
            _buildPaymentMethod(
              context,
              'MTN Mobile Money',
              Icons.phone_android,
              Colors.yellow[700]!,
              () => _showPaymentDialog(context, 'MTN MoMo'),
            ),
            const SizedBox(height: 12),

            // Agence physique
            _buildPaymentMethod(
              context,
              'Payer en agence',
              Icons.store,
              Colors.green,
              () => _generateQRCode(context),
            ),
            const SizedBox(height: 12),

            // Carte bancaire (futur)
            _buildPaymentMethod(
              context,
              'Carte bancaire',
              Icons.credit_card,
              Colors.purple,
              () => _showComingSoon(context),
              isComingSoon: true,
            ),
            const SizedBox(height: 32),

            // Security notice
            Card(
              color: Colors.grey[100],
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    const Icon(Icons.shield, color: Colors.green),
                    const SizedBox(width: 16),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Paiement sécurisé', style: TextStyle(fontWeight: FontWeight.bold)),
                          Text('Conforme BCEAO • Crypté AES-256', style: TextStyle(fontSize: 12, color: Colors.grey)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPaymentMethod(
    BuildContext context,
    String name,
    IconData icon,
    Color color,
    VoidCallback onTap, {
    bool isComingSoon = false,
  }) {
    return Card(
      child: ListTile(
        onTap: isComingSoon ? null : onTap,
        leading: Icon(icon, color: color, size: 32),
        title: Text(name, style: const TextStyle(fontWeight: FontWeight.w500)),
        trailing: isComingSoon
            ? const Chip(label: Text('Bientôt', style: TextStyle(fontSize: 12)))
            : const Icon(Icons.arrow_forward_ios, size: 16),
        enabled: !isComingSoon,
      ),
    );
  }

  void _showPaymentDialog(BuildContext context, String method) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Paiement via $method'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Vous serez redirigé vers l\'application $method pour compléter le paiement.'),
            const SizedBox(height: 16),
            const Text('Montant: 125 000 GNF', style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Annuler'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _simulatePayment(context, method);
            },
            child: const Text('Payer'),
          ),
        ],
      ),
    );
  }

  void _generateQRCode(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Code de paiement agence'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Présentez ce code en agence EDG partenaire :'),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.black),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                'YBH-1234-5678-ABCD',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Valable 24 heures • Un code OTP vous sera envoyé pour validation',
              style: TextStyle(fontSize: 12, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Fermer'),
          ),
        ],
      ),
    );
  }

  void _showComingSoon(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Paiement par carte bientôt disponible')),
    );
  }

  void _simulatePayment(BuildContext context, String method) {
    // Simulate payment processing
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Traitement en cours...'),
          ],
        ),
      ),
    );

    // Simulate API call
    Future.delayed(const Duration(seconds: 3), () {
      Navigator.pop(context); // Close loading dialog
      
      // Show success
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Row(
            children: [
              Icon(Icons.check_circle, color: Colors.green),
              SizedBox(width: 8),
              Text('Paiement réussi'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Votre paiement a été effectué avec succès.'),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  children: [
                    Text('Référence: YBH-${DateTime.now().millisecondsSinceEpoch}'),
                    const SizedBox(height: 8),
                    Text('Montant: ${amount.toStringAsFixed(0)} GNF'),
                    const SizedBox(height: 8),
                    Text('Méthode: $method'),
                  ],
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                context.go('/dashboard');
              },
              child: const Text('Retour au tableau de bord'),
            ),
          ],
        ),
      );
    });
  }
}
