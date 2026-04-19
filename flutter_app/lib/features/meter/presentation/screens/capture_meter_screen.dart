import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:go_router/go_router.dart';
import 'dart:io';

class CaptureMeterScreen extends StatefulWidget {
  const CaptureMeterScreen({super.key});

  @override
  State<CaptureMeterScreen> createState() => _CaptureMeterScreenState();
}

class _CaptureMeterScreenState extends State<CaptureMeterScreen> {
  XFile? _photo;
  final ImagePicker _picker = ImagePicker();
  bool _isProcessing = false;
  String? _extractedNumber;
  String? _extractedIndex;
  double? _confidence;

  Future<void> _takePhoto() async {
    final photo = await _picker.pickImage(source: ImageSource.camera);
    if (photo != null) {
      setState(() {
        _photo = photo;
        _isProcessing = true;
      });

      // Simulate OCR processing (replace with actual API call)
      await Future.delayed(const Duration(seconds: 2));
      
      setState(() {
        _isProcessing = false;
        _extractedNumber = '12345678';
        _extractedIndex = '450';
        _confidence = 0.92;
      });
    }
  }

  Future<void> _pickFromGallery() async {
    final photo = await _picker.pickImage(source: ImageSource.gallery);
    if (photo != null) {
      setState(() {
        _photo = photo;
        _isProcessing = true;
      });

      // Simulate OCR processing
      await Future.delayed(const Duration(seconds: 2));
      
      setState(() {
        _isProcessing = false;
        _extractedNumber = '12345678';
        _extractedIndex = '450';
        _confidence = 0.88;
      });
    }
  }

  void _handleSubmit() {
    if (_extractedNumber == null || _extractedIndex == null) return;
    
    // Navigate to validation screen or submit to API
    context.push('/payment?amount=125000');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Relever le compteur')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Instructions
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Instructions',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    const Text('1. Prenez votre compteur en photo'),
                    const Text('2. Assurez-vous que les chiffres sont lisibles'),
                    const Text('3. Vérifiez les données extraites'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Camera preview or photo
            if (_photo == null)
              Container(
                height: 300,
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.camera_alt, size: 64, color: Colors.grey),
                    const SizedBox(height: 16),
                    const Text('Aucune photo'),
                  ],
                ),
              )
            else
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.file(File(_photo!.path), height: 300, fit: BoxFit.cover),
              ),
            const SizedBox(height: 24),

            // Camera buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  onPressed: _takePhoto,
                  icon: const Icon(Icons.camera),
                  label: const Text('Prendre photo'),
                ),
                ElevatedButton.icon(
                  onPressed: _pickFromGallery,
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Galerie'),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // OCR Results
            if (_isProcessing)
              const Center(child: CircularProgressIndicator())
            else if (_extractedNumber != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Données extraites',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 16),
                      _buildResultRow('Numéro compteur:', _extractedNumber!),
                      _buildResultRow('Index (kWh):', _extractedIndex!),
                      _buildResultRow('Confiance:', '${(_confidence! * 100).toInt()}%'),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          const Icon(Icons.info_outline, size: 16, color: Colors.blue),
                          const SizedBox(width: 8),
                          const Expanded(
                            child: Text(
                              'Vérifiez les données avant de continuer',
                              style: TextStyle(fontSize: 12, color: Colors.grey),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 24),

            // Action buttons
            if (_extractedNumber != null) ...[
              SizedBox(
                height: 50,
                child: ElevatedButton(
                  onPressed: _handleSubmit,
                  child: const Text('Valider et continuer', style: TextStyle(fontSize: 16)),
                ),
              ),
              const SizedBox(height: 16),
              OutlinedButton(
                onPressed: () {
                  setState(() {
                    _photo = null;
                    _extractedNumber = null;
                    _extractedIndex = null;
                    _confidence = null;
                  });
                },
                child: const Text('Recommencer'),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildResultRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        ],
      ),
    );
  }
}
