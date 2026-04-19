import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../constants/app_constants.dart';

/// Network Error Types - Fintech Standard
abstract class AppError implements Exception {
  final String message;
  final int? statusCode;
  
  const AppError(this.message, [this.statusCode]);
  
  @override
  String toString() => 'AppError: $message (Status: $statusCode)';
}

class NetworkError extends AppError {
  const NetworkError(String message, [int? statusCode]) : super(message, statusCode);
}

class TimeoutError extends AppError {
  const TimeoutError(String message) : super(message, 408);
}

class AuthError extends AppError {
  const AuthError(String message, [int? statusCode]) : super(message, statusCode);
}

class ValidationError extends AppError {
  final Map<String, String>? fieldErrors;
  
  const ValidationError(String message, [int? statusCode, this.fieldErrors]) : super(message, statusCode);
}

class ServerError extends AppError {
  const ServerError(String message, [int? statusCode]) : super(message, statusCode);
}

/// API Service - Production Ready
class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  
  factory ApiClient() => _instance;
  
  late final Dio _dio;
  String? _accessToken;
  String? _refreshToken;
  
  ApiClient._internal() {
    _initDio();
  }
  
  void _initDio() {
    _dio = Dio(BaseOptions(
      baseUrl: AppConstants.apiBaseUrl,
      connectTimeout: Duration(seconds: AppConstants.apiTimeoutSeconds),
      receiveTimeout: Duration(seconds: AppConstants.apiTimeoutSeconds),
      sendTimeout: Duration(seconds: AppConstants.apiTimeoutSeconds),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-App-Version': AppConstants.appVersion,
      },
    ));
    
    // Request interceptor - Add auth token
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        if (_accessToken != null) {
          options.headers['Authorization'] = 'Bearer $_accessToken';
        }
        return handler.next(options);
      },
      onResponse: (response, handler) {
        // Log successful response (no sensitive data)
        debugPrint('[API] ${response.statusCode} ${response.requestOptions.path}');
        return handler.next(response);
      },
      onError: (error, handler) {
        debugPrint('[API ERROR] ${error.response?.statusCode ?? 'UNKNOWN'} ${error.requestOptions.path}: ${error.message}');
        return handler.next(error);
      },
    ));
    
    // Response interceptor - Handle errors
    _dio.interceptors.add(InterceptorsWrapper(
      onError: (error, handler) {
        if (error.response != null) {
          switch (error.response!.statusCode) {
            case 400:
              throw ValidationError(
                error.response!.data['message'] ?? 'Validation error',
                400,
                error.response!.data['errors'],
              );
            case 401:
              throw AuthError('Session expired', 401);
            case 403:
              throw AuthError('Access denied', 403);
            case 404:
              throw NetworkError('Resource not found', 404);
            case 429:
              throw NetworkError('Rate limit exceeded', 429);
            case 500:
              throw ServerError('Internal server error', 500);
            case 502:
              throw ServerError('Bad gateway', 502);
            case 503:
              throw ServerError('Service unavailable', 503);
          }
        } else if (error.type == DioErrorType.connectionTimeout) {
          throw TimeoutError('Connection timeout');
        } else if (error.type == DioErrorType.receiveTimeout) {
          throw TimeoutError('Receive timeout');
        } else if (error.type == DioErrorType.sendTimeout) {
          throw TimeoutError('Send timeout');
        } else if (error.type == DioErrorType.connectionError) {
          throw NetworkError('No internet connection');
        }
        
        return handler.next(error);
      },
    ));
  }
  
  /// Set Auth Token
  void setAuthTokens(String accessToken, String refreshToken) {
    _accessToken = accessToken;
    _refreshToken = refreshToken;
  }
  
  /// Clear Auth Tokens
  void clearAuthTokens() {
    _accessToken = null;
    _refreshToken = null;
  }
  
  /// Check if user is authenticated
  bool get isAuthenticated => _accessToken != null;
  
  /// Make GET request
  Future<dynamic> get(String path, {Map<String, dynamic>? queryParameters}) async {
    final response = await _dio.get(path, queryParameters: queryParameters);
    return response.data;
  }
  
  /// Make POST request
  Future<dynamic> post(String path, {Map<String, dynamic>? data, Options? options}) async {
    final response = await _dio.post(path, data: data, options: options);
    return response.data;
  }
  
  /// Make PUT request
  Future<dynamic> put(String path, {Map<String, dynamic>? data}) async {
    final response = await _dio.put(path, data: data);
    return response.data;
  }
  
  /// Make DELETE request
  Future<dynamic> delete(String path, {Map<String, dynamic>? data}) async {
    final response = await _dio.delete(path, data: data);
    return response.data;
  }
  
  /// Upload file
  Future<dynamic> upload(String path, FormData formData) async {
    final response = await _dio.post(
      path,
      data: formData,
      onSendProgress: (int sent, int total) {
        debugPrint('Upload progress: ${(sent / total * 100).toInt()}%');
      },
    );
    return response.data;
  }
  
  /// Download file
  Future<void> download(String path, String savePath) async {
    await _dio.download(path, savePath, onReceiveProgress: (received, total) {
      if (total != -1) {
        debugPrint('Download progress: ${(received / total * 100).toInt()}%');
      }
    });
  }
}
