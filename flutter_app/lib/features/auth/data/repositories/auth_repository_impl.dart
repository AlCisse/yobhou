import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../../../core/constants/app_constants.dart';
import '../../../../core/network/api_client.dart';
import '../../domain/repositories/auth_repository.dart';
import '../models/user_model.dart';

class AuthRepositoryImpl implements AuthRepository {
  final ApiClient _apiClient;
  final FlutterSecureStorage _secureStorage;

  AuthRepositoryImpl({
    required ApiClient apiClient,
    required FlutterSecureStorage secureStorage,
  })  : _apiClient = apiClient,
        _secureStorage = secureStorage;

  @override
  Future<void> login({
    required String username,
    required String password,
  }) async {
    try {
      final response = await _apiClient.login(
        username: username,
        password: password,
      );

      // Store tokens
      await _secureStorage.write(
        key: AppConstants.tokenStorageKey,
        value: response['access'],
      );
      if (response['refresh'] != null) {
        await _secureStorage.write(
          key: AppConstants.refreshTokenKey,
          value: response['refresh'],
        );
      }

      // Store user data
      if (response['user'] != null) {
        final user = UserModel.fromJson(response['user']);
        // Save to Hive or other local storage
      }
    } catch (e) {
      throw Exception('Login failed: ${e.toString()}');
    }
  }

  @override
  Future<void> register({
    required String username,
    required String phoneNumber,
    required String password,
    required DateTime dateOfBirth,
  }) async {
    try {
      await _apiClient.register(
        username: username,
        phoneNumber: phoneNumber,
        password: password,
        dateOfBirth: dateOfBirth,
      );
    } catch (e) {
      throw Exception('Registration failed: ${e.toString()}');
    }
  }

  @override
  Future<bool> isLoggedIn() async {
    final token = await _secureStorage.read(key: AppConstants.tokenStorageKey);
    return token != null && token.isNotEmpty;
  }

  @override
  Future<void> logout() async {
    await _secureStorage.delete(key: AppConstants.tokenStorageKey);
    await _secureStorage.delete(key: AppConstants.refreshTokenKey);
  }

  @override
  Future<String?> getToken() async {
    return await _secureStorage.read(key: AppConstants.tokenStorageKey);
  }

  @override
  Future<Map<String, dynamic>?> getUser() async {
    // Implement user retrieval from local storage
    return null;
  }

  @override
  Future<void> refreshToken() async {
    final refreshToken = await _secureStorage.read(key: AppConstants.refreshTokenKey);
    if (refreshToken == null) {
      throw Exception('No refresh token available');
    }

    // Implement token refresh endpoint call
    // For now, just logout
    await logout();
  }
}
