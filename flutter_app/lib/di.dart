import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'core/network/api_client.dart';
import 'features/auth/data/repositories/auth_repository_impl.dart';
import 'features/auth/domain/repositories/auth_repository.dart';
import 'features/auth/domain/usecases/login_usecase.dart';
import 'features/auth/domain/usecases/register_usecase.dart';
import 'features/meter/data/repositories/meter_repository_impl.dart';
import 'features/meter/domain/repositories/meter_repository.dart';
import 'features/meter/domain/usecases/capture_meter_usecase.dart';
import 'features/payment/data/repositories/payment_repository_impl.dart';
import 'features/payment/domain/repositories/payment_repository.dart';
import 'features/payment/domain/usecases/initiate_payment_usecase.dart';

// Secure Storage
final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});

// API Client
final apiClientProvider = Provider<ApiClient>((ref) {
  final secureStorage = ref.watch(secureStorageProvider);
  return ApiClient(secureStorage: secureStorage);
});

// Auth Repository
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  final secureStorage = ref.watch(secureStorageProvider);
  return AuthRepositoryImpl(apiClient: apiClient, secureStorage: secureStorage);
});

// Meter Repository
final meterRepositoryProvider = Provider((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return MeterRepositoryImpl(apiClient: apiClient);
});

// Payment Repository
final paymentRepositoryProvider = Provider((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return PaymentRepositoryImpl(apiClient: apiClient);
});

// Auth Use Cases
final loginUseCaseProvider = Provider<LoginUseCase>((ref) {
  final repository = ref.watch(authRepositoryProvider);
  return LoginUseCase(repository: repository);
});

final registerUseCaseProvider = Provider<RegisterUseCase>((ref) {
  final repository = ref.watch(authRepositoryProvider);
  return RegisterUseCase(repository: repository);
});

// Meter Use Cases
final captureMeterUseCaseProvider = Provider<CaptureMeterUseCase>((ref) {
  final repository = ref.watch(meterRepositoryProvider);
  return CaptureMeterUseCase(repository: repository);
});

// Payment Use Cases
final initiatePaymentUseCaseProvider = Provider<InitiatePaymentUseCase>((ref) {
  final repository = ref.watch(paymentRepositoryProvider);
  return InitiatePaymentUseCase(repository: repository);
});

// Auth State Notifier
final authStateNotifierProvider = StateNotifierProvider<AuthStateNotifier, AuthState>((ref) {
  final repository = ref.watch(authRepositoryProvider);
  return AuthStateNotifier(repository: repository);
});

class AuthStateNotifier extends StateNotifier<AuthState> {
  final AuthRepository _repository;

  AuthStateNotifier({required AuthRepository repository})
      : _repository = repository,
        super(AuthState.initial()) {
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    final isLoggedIn = await _repository.isLoggedIn();
    state = state.copyWith(isLoggedIn: isLoggedIn);
  }

  Future<void> login(String username, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      await _repository.login(username: username, password: password);
      state = state.copyWith(isLoggedIn: true, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> logout() async {
    await _repository.logout();
    state = AuthState.initial();
  }
}

class AuthState {
  final bool isLoggedIn;
  final bool isLoading;
  final String? error;

  AuthState({
    required this.isLoggedIn,
    required this.isLoading,
    this.error,
  });

  factory AuthState.initial() {
    return AuthState(isLoggedIn: false, isLoading: false, error: null);
  }

  AuthState copyWith({
    bool? isLoggedIn,
    bool? isLoading,
    String? error,
  }) {
    return AuthState(
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

// Initialize dependencies
Future<void> initDependencies() async {
  // Any additional initialization logic
}
