import '../../entities/user.dart';

abstract class AuthRepository {
  Future<void> login({
    required String username,
    required String password,
  });

  Future<void> register({
    required String username,
    required String phoneNumber,
    required String password,
    required DateTime dateOfBirth,
  });

  Future<bool> isLoggedIn();

  Future<void> logout();

  Future<String?> getToken();

  Future<UserModel?> getUser();

  Future<void> refreshToken();
}
