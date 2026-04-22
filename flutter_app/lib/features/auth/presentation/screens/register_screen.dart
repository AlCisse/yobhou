import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/widgets/premium_widgets.dart';

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
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: AppTheme.primaryBlue,
              onPrimary: Colors.white,
              surface: Colors.white,
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) setState(() => _dateOfBirth = picked);
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;
    if (_dateOfBirth == null) {
      _showSnackBar('Veuillez sélectionner votre date de naissance', isError: true);
      return;
    }

    setState(() => _isLoading = true);

    try {
      final response = await http.post(
        Uri.parse('http://10.0.2.2:8000/api/register/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'phone_number': '+224${_phoneController.text}',
          'date_of_birth': DateFormat('yyyy-MM-dd').format(_dateOfBirth!),
          'password': _passwordController.text,
          'username': 'user_${_phoneController.text}',
        }),
      );

      if (response.statusCode == 201) {
        _showSnackBar('Inscription réussie !', isError: false);
        await Future.delayed(const Duration(milliseconds: 500));
        if (mounted) context.push('/upload-invoice');
      } else {
        final error = jsonDecode(response.body);
        _showSnackBar(error['message'] ?? 'Erreur lors de l\'inscription', isError: true);
      }
    } catch (e) {
      _showSnackBar('Erreur de connexion: $e', isError: true);
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showSnackBar(String message, {required bool isError}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              isError ? Icons.error_outline : Icons.check_circle_outline,
              color: Colors.white,
            ),
            const SizedBox(width: 12),
            Expanded(child: Text(message, style: const TextStyle(color: Colors.white))),
          ],
        ),
        backgroundColor: isError ? AppTheme.error : AppTheme.success,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppTheme.radiusMedium)),
        margin: const EdgeInsets.all(16),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;

    return Scaffold(
      body: Container(
        height: size.height,
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: AppTheme.spacingL),
            child: Column(
              children: [
                const SizedBox(height: AppTheme.spacingL),

                // Back button
                Align(
                  alignment: Alignment.centerLeft,
                  child: IconButton(
                    icon: const Icon(Icons.arrow_back_ios_rounded, size: 20, color: Colors.white),
                    onPressed: () => context.pop(),
                  ),
                ),
                const SizedBox(height: AppTheme.spacingM),

                // Icon
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(AppTheme.radiusXLarge),
                    border: Border.all(color: Colors.white.withOpacity(0.3), width: 2),
                  ),
                  child: const Icon(
                    Icons.person_add_outlined,
                    size: 40,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: AppTheme.spacingL),

                // Title
                const Text(
                  'Créer un compte',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: AppTheme.spacingS),
                Text(
                  'Rejoignez Yobhou dès aujourd\'hui',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.white.withOpacity(0.85),
                  ),
                ),
                const SizedBox(height: AppTheme.spacingXXL),

                // Form Card
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(AppTheme.spacingL),
                  decoration: BoxDecoration(
                    color: AppTheme.surface,
                    borderRadius: BorderRadius.circular(AppTheme.radiusXLarge),
                    boxShadow: AppTheme.mediumShadow,
                  ),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Phone
                        _buildInputField(
                          controller: _phoneController,
                          label: 'Numéro de téléphone',
                          hint: '6XX XX XX XX',
                          prefixIcon: Icons.phone_rounded,
                          keyboardType: TextInputType.phone,
                          validator: (v) {
                            if (v == null || v.isEmpty) return 'Requis';
                            if (v.length != 9) return '9 chiffres requis';
                            return null;
                          },
                        ),
                        const SizedBox(height: AppTheme.spacingM),

                        // Date of Birth
                        InkWell(
                          onTap: _selectDate,
                          borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: AppTheme.spacingM, vertical: 4),
                            decoration: BoxDecoration(
                              color: AppTheme.surfaceVariant,
                              borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
                            ),
                            child: Row(
                              children: [
                                const Icon(Icons.calendar_today_rounded, color: AppTheme.primaryBlue, size: 22),
                                const SizedBox(width: AppTheme.spacingM),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Date de naissance',
                                        style: TextStyle(
                                          fontSize: 12,
                                          fontWeight: FontWeight.w500,
                                          color: Colors.grey.shade600,
                                        ),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        _dateOfBirth == null
                                            ? 'Sélectionner une date'
                                            : DateFormat('dd MMMM yyyy', 'fr_FR').format(_dateOfBirth!),
                                        style: TextStyle(
                                          fontSize: 15,
                                          fontWeight: FontWeight.w500,
                                          color: _dateOfBirth == null ? Colors.grey.shade400 : AppTheme.textPrimary,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                Icon(Icons.arrow_forward_ios_rounded, size: 16, color: Colors.grey.shade400),
                              ],
                            ),
                          ),
                        ),
                        const SizedBox(height: AppTheme.spacingM),

                        // Password
                        _buildInputField(
                          controller: _passwordController,
                          label: 'Mot de passe',
                          hint: 'Minimum 8 caractères',
                          prefixIcon: Icons.lock_outline_rounded,
                          obscureText: _obscurePassword,
                          suffixIcon: IconButton(
                            icon: Icon(
                              _obscurePassword ? Icons.visibility_off_rounded : Icons.visibility_rounded,
                              color: Colors.grey,
                            ),
                            onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                          ),
                          validator: (v) => v == null || v.isEmpty ? 'Requis' : v.length < 8 ? 'Min 8 caractères' : null,
                        ),
                        const SizedBox(height: AppTheme.spacingM),

                        // Confirm Password
                        _buildInputField(
                          controller: _confirmPasswordController,
                          label: 'Confirmer le mot de passe',
                          hint: 'Répétez le mot de passe',
                          prefixIcon: Icons.lock_rounded,
                          obscureText: _obscureConfirmPassword,
                          suffixIcon: IconButton(
                            icon: Icon(
                              _obscureConfirmPassword ? Icons.visibility_off_rounded : Icons.visibility_rounded,
                              color: Colors.grey,
                            ),
                            onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
                          ),
                          validator: (v) => v == null || v.isEmpty ? 'Requis' : v != _passwordController.text ? 'Ne correspondent pas' : null,
                        ),
                        const SizedBox(height: AppTheme.spacingL + AppTheme.spacingM),

                        // Submit Button
                        PremiumButton(
                          label: 'S\'inscrire',
                          icon: Icons.arrow_forward_rounded,
                          onPressed: _handleRegister,
                          isLoading: _isLoading,
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: AppTheme.spacingL),

                // Login Link
                PremiumTextButton(
                  label: 'Se connecter',
                  prefixText: 'Déjà un compte ? ',
                  onPressed: () => context.push('/login'),
                ),
                const SizedBox(height: AppTheme.spacingL),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildInputField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData prefixIcon,
    Widget? suffixIcon,
    TextInputType? keyboardType,
    bool? obscureText,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscureText ?? false,
      validator: validator,
      style: AppTheme.bodyLarge,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: Icon(prefixIcon, color: AppTheme.primaryBlue, size: 22),
        suffixIcon: suffixIcon,
        filled: true,
        fillColor: AppTheme.surfaceVariant,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
          borderSide: const BorderSide(color: AppTheme.primaryBlue, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
          borderSide: const BorderSide(color: AppTheme.error),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(AppTheme.radiusMedium),
          borderSide: const BorderSide(color: AppTheme.error, width: 2),
        ),
      ),
    );
  }
}
