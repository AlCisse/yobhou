import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../constants/app_constants.dart';

class ApiClient {
  late final Dio _dio;
  final FlutterSecureStorage _secureStorage;

  ApiClient({required FlutterSecureStorage secureStorage})
      : _secureStorage = secureStorage {
    _dio = Dio(BaseOptions(
      baseUrl: AppConstants.apiBaseUrl,
      connectTimeout: AppConstants.connectionTimeout,
      receiveTimeout: AppConstants.receiveTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Add auth token to requests
        final token = await _secureStorage.read(key: AppConstants.tokenStorageKey);
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onResponse: (response, handler) {
        return handler.next(response);
      },
      onError: (error, handler) {
        // Handle 401 (unauthorized) - token expired
        if (error.response?.statusCode == 401) {
          // Trigger token refresh or logout
          _handleTokenRefresh();
        }
        return handler.next(error);
      },
    ));
  }

  Future<void> _handleTokenRefresh() async {
    // Implement token refresh logic here
    await _secureStorage.delete(key: AppConstants.tokenStorageKey);
    // Navigate to login or refresh token
  }

  Dio get dio => _dio;

  // Auth endpoints
  Future<Map<String, dynamic>> login({
    required String username,
    required String password,
  }) async {
    final response = await _dio.post('/login/', data: {
      'username': username,
      'password': password,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> register({
    required String username,
    required String phoneNumber,
    required String password,
    required DateTime dateOfBirth,
  }) async {
    final response = await _dio.post('/register/', data: {
      'username': username,
      'phone_number': phoneNumber,
      'password': password,
      'date_of_birth': dateOfBirth.toIso8601String().split('T')[0],
    });
    return response.data;
  }

  Future<Map<String, dynamic>> uploadInvoice(String filePath) async {
    final formData = FormData.fromMap({
      'invoice': await MultipartFile.fromFile(filePath),
    });
    final response = await _dio.post('/upload-invoice/', data: formData);
    return response.data;
  }

  Future<Map<String, dynamic>> captureMeter(String filePath) async {
    final formData = FormData.fromMap({
      'meter_photo': await MultipartFile.fromFile(filePath),
    });
    final response = await _dio.post('/capture-meter/', data: formData);
    return response.data;
  }

  Future<Map<String, dynamic>> validateReading({
    required String meterNumber,
    required double currentIndex,
    required double meterNumberConfidence,
    required double indexConfidence,
  }) async {
    final response = await _dio.post('/validate-reading/', data: {
      'meter_number': meterNumber,
      'current_index': currentIndex,
      'meter_number_confidence': meterNumberConfidence,
      'index_confidence': indexConfidence,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> initiatePayment({
    required double amount,
    required String paymentMethod,
    required String meterReadingId,
  }) async {
    final response = await _dio.post('/initiate-payment/', data: {
      'amount': amount,
      'payment_method': paymentMethod,
      'meter_reading_id': meterReadingId,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> verifyOTP({
    required String otp,
    required String transactionId,
  }) async {
    final response = await _dio.post('/verify-otp/', data: {
      'otp': otp,
      'transaction_id': transactionId,
    });
    return response.data;
  }

  Future<List<Map<String, dynamic>>> getTransactions() async {
    final response = await _dio.get('/transactions/');
    return List<Map<String, dynamic>>.from(response.data);
  }

  Future<Map<String, dynamic>> getUserProfile() async {
    final response = await _dio.get('/profile/');
    return response.data;
  }
}
