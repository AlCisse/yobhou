/// App Constants - Fintech Standards
class AppConstants {
  static const String appName = 'Yobhou';
  static const String appVersion = '2.0.0';
  static const String appTagline = 'Payez vos factures d\'électricité en toute simplicité';

  // API Configuration - Use environment-specific URLs
  static const String _devApiBaseUrl = 'http://10.0.2.2:8000/api';
  static const String _prodApiBaseUrl = 'https://api.yobhou.gn/api';
  static String get apiBaseUrl => const bool.fromEnvironment('dart.vm.product') ? _prodApiBaseUrl : _devApiBaseUrl;

  static const int apiTimeoutSeconds = 30;
  static const int jwtAccessTokenLifetimeMinutes = 15;
  static const int jwtRefreshTokenLifetimeDays = 7;
  static const int rateLimitRequestsPerMinute = 60;
  static const int maxFileSizeMB = 10;
  static const double minConfidenceThreshold = 0.8;
  static const double dailyTransactionLimit = 1000000.0;
  static const double monthlyTransactionLimit = 5000000.0;
  static const int auditRetentionYears = 10;
  static const String supportEmail = 'support@yobhou.gn';

  // Storage keys
  static const String tokenStorageKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';

  // Security flags
  static const bool enableSslPinning = true;
  static const bool enableCertificatePinning = false; // Set to true in production with pinned certs
}
