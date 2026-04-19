/// Register Screen - Premium Fintech Design
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/widgets/ui_components.dart';
import '../../../core/utils/validation_utils.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});
  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  DateTime? _dateOfBirth;
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _isLoading = false;

  @override
  void dispose() {
    _phoneController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime(2000),
      firstDate: DateTime(1950),
      lastDate: DateTime.now().subtract(const Duration(days: 18 * 365)),
      helpText: 'Sélectionnez votre date de naissance',
    );
    if (picked != null) setState(() => _dateOfBirth = picked);
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;
    if (_dateOfBirth == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Veuillez sélectionner votre date de naissance')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final response = await http.post(
        Uri.parse('${const String.fromEnvironment('API_URL', defaultValue: 'http://10.0.2.2:8000/api')}/register/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'phone_number': '+224${_phoneController.text}',
          'date_of_birth': DateFormat('yyyy-MM-dd').format(_dateOfBirth!),
          'password': _passwordController.text,
          'username': 'user_${_phoneController.text}',
        }),
      );

      if (response.statusCode == 201) {
        final data = jsonDecode(response.body);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Inscription réussie!'), backgroundColor: Color(0xFF10B981)),
          );
          context.push('/upload-invoice');
        }
      } else {
        final error = jsonDecode(response.body);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(error['message'] ?? error.toString())),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erreur de connexion: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Inscription')),
    body: SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 20),
              Align(alignment: Alignment.centerLeft, child: IconButton(onPressed: () => context.pop(), icon: const Icon(Icons.arrow_back_ios_rounded, size: 20, color: Color(0xFF0F172A)))),
              const SizedBox(height: 20),
              const Text('Créer un compte', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
              const SizedBox(height: 12),
              const Text('Complétez vos informations', textAlign: TextAlign.center, style: TextStyle(fontSize: 14, color: Color(0xFF64748B))),
              const SizedBox(height: 40),
              FloatingInputField(controller: _phoneController, label: 'Numéro de téléphone', hintText: '+224 6XX XX XX XX', prefixIcon: const Icon(Icons.phone_rounded, color: Color(0xFF2563EB)), validator: (v) => v == null || v.isEmpty ? 'Requis' : !ValidationUtils.isValidGuineaPhone(v) ? 'Format invalide (+224 6XX XX XX XX)' : null),
              const SizedBox(height: 20),
              InkWell(
                onTap: _selectDate,
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: 'Date de naissance',
                    prefixIcon: Icon(Icons.calendar_today, color: Color(0xFF2563EB)),
                    border: OutlineInputBorder(),
                  ),
                  child: Text(
                    _dateOfBirth == null ? 'Sélectionner' : DateFormat('dd/MM/yyyy').format(_dateOfBirth!),
                    style: TextStyle(color: _dateOfBirth == null ? Color(0xFF64748B) : Color(0xFF0F172A)),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              FloatingInputField(controller: _passwordController, label: 'Mot de passe', hintText: 'Minimum 8 caractères', obscureText: _obscurePassword, prefixIcon: const Icon(Icons.lock_outline_rounded, color: Color(0xFF2563EB)), suffixIcon: IconButton(icon: Icon(_obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined, color: Color(0xFF64748B)), onPressed: () => setState(() => _obscurePassword = !_obscurePassword)), validator: (v) => v == null || v.isEmpty ? 'Requis' : v.length < 8 ? 'Min 8 caractères' : null),
              const SizedBox(height: 20),
              FloatingInputField(controller: _confirmPasswordController, label: 'Confirmer mot de passe', hintText: 'Répétez le mot de passe', obscureText: _obscureConfirmPassword, prefixIcon: const Icon(Icons.lock_rounded, color: Color(0xFF2563EB)), suffixIcon: IconButton(icon: Icon(_obscureConfirmPassword ? Icons.visibility_outlined : Icons.visibility_off_outlined, color: Color(0xFF64748B)), onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword)), validator: (v) => v == null || v.isEmpty ? 'Requis' : v != _passwordController.text ? 'Ne correspondent pas' : null),
              const SizedBox(height: 32),
              PremiumButton(label: 'S\'inscrire', onPressed: _handleRegister),
              const SizedBox(height: 20),
              Row(mainAxisAlignment: MainAxisAlignment.center, children: [const Text('Déjà un compte ? ', style: TextStyle(fontSize: 14, color: Color(0xFF64748B))), TextButton(onPressed: () => context.push('/login'), child: const Text('Se connecter', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Color(0xFF2563EB))))]),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    ),
  );
}
