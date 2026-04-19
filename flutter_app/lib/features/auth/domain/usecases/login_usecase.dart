import '../entities/user.dart';
import '../repositories/auth_repository.dart';

class LoginUseCase {
  final AuthRepository _repository;

  LoginUseCase({required AuthRepository repository}) : _repository = repository;

  Future<Map<String, dynamic>> execute({
    required String username,
    required String password,
  }) async {
    // Validate input
    if (username.isEmpty || password.isEmpty) {
      throw Exception('Username and password are required');
    }

    if (password.length < 8) {
      throw Exception('Password must be at least 8 characters');
    }

    // Execute login
    await _repository.login(username: username, password: password);

    // Get user data
    final user = await _repository.getUser();
    final token = await _repository.getToken();

    return {
      'success': true,
      'user': user,
      'token': token,
    };
  }
}
