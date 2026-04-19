import '../repositories/auth_repository.dart';

class RegisterUseCase {
  final AuthRepository _repository;

  RegisterUseCase({required AuthRepository repository}) : _repository = repository;

  Future<Map<String, dynamic>> execute({
    required String username,
    required String phoneNumber,
    required String password,
    required DateTime dateOfBirth,
  }) async {
    // Validate input
    if (username.isEmpty || username.length < 3) {
      throw Exception('Username must be at least 3 characters');
    }

    if (phoneNumber.isEmpty || !phoneNumber.startsWith('+224')) {
      throw Exception('Phone number must start with +224 (Guinea)');
    }

    if (phoneNumber.length != 13) {
      throw Exception('Phone number must be 13 digits (+224XXXXXXXX)');
    }

    if (password.length < 8) {
      throw Exception('Password must be at least 8 characters');
    }

    // Check password strength
    if (!_isPasswordStrong(password)) {
      throw Exception('Password must contain at least one uppercase, one lowercase, and one number');
    }

    // Validate date of birth (must be at least 18 years old)
    final age = DateTime.now().difference(dateOfBirth).inDays ~/ 365;
    if (age < 18) {
      throw Exception('You must be at least 18 years old to register');
    }

    // Execute registration
    await _repository.register(
      username: username,
      phoneNumber: phoneNumber,
      password: password,
      dateOfBirth: dateOfBirth,
    );

    return {
      'success': true,
      'message': 'Registration successful. Please login.',
    };
  }

  bool _isPasswordStrong(String password) {
    final hasUppercase = password.contains(RegExp(r'[A-Z]'));
    final hasLowercase = password.contains(RegExp(r'[a-z]'));
    final hasNumber = password.contains(RegExp(r'[0-9]'));
    return hasUppercase && hasLowercase && hasNumber;
  }
}
