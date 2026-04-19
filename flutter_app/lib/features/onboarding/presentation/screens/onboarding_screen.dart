import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.account_balance, size: 100, color: Colors.blue),
              const SizedBox(height: 32),
              const Text(
                'Yobhou',
                style: TextStyle(fontSize: 40, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              const Text(
                'Payez vos factures d\'électricité en toute simplicité',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 18, color: Colors.grey),
              ),
              const SizedBox(height: 48),
              
              // Features
              _buildFeature(Icons.qr_code, 'Scannez votre facture EDG'),
              _buildFeature(Icons.camera_alt, 'Prenez votre compteur en photo'),
              _buildFeature(Icons.payment, 'Payez via Mobile Money ou agence'),
              _buildFeature(Icons.shield, 'Sécurisé et conforme BCEAO'),
              
              const Spacer(),
              
              // Get Started button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: () => context.go('/register'),
                  child: const Text('Commencer', style: TextStyle(fontSize: 18)),
                ),
              ),
              const SizedBox(height: 16),
              
              // Login link
              TextButton(
                onPressed: () => context.go('/login'),
                child: const Text('Déjà un compte ? Se connecter'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFeature(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          Icon(icon, color: Colors.blue, size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(fontSize: 16),
            ),
          ),
        ],
      ),
    );
  }
}
