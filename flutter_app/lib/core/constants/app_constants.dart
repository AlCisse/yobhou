import 'package:flutter/material.dart';

class AppConstants {
  // App Info
  static const String appName = 'Yobhou';
  static const String appVersion = '1.0.0';

  // Colors
  static const Color primaryColor = Color(0xFF1E88E5);
  static const Color secondaryColor = Color(0xFF43A047);
  static const Color accentColor = Color(0xFFFFB300);
  static const Color errorColor = Color(0xFFE53935);
  static const Color successColor = Color(0xFF43A047);
  static const Color warningColor = Color(0xFFFFB300);

  // API Configuration
  static const String apiBaseUrl = 'https://api.yobhou.gn/api';
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);

  // Payment Limits (BCEAO compliance)
  static const double dailyLimit = 1000000; // 1M GNF
  static const double monthlyLimit = 5000000; // 5M GNF
  static const double transactionMin = 100; // 100 GNF
  static const double transactionMax = 1000000; // 1M GNF

  // OCR Confidence Threshold
  static const double ocrConfidenceThreshold = 0.85;

  // Storage Keys
  static const String tokenStorageKey = 'auth_token';
  static const String userStorageKey = 'user_data';
  static const String refreshTokenKey = 'refresh_token';

  // Hive Box Names
  static const String userBox = 'user_box';
  static const String transactionsBox = 'transactions_box';
  static const String metersBox = 'meters_box';

  // Routes
  static const String routeOnboarding = '/onboarding';
  static const String routeLogin = '/login';
  static const String routeRegister = '/register';
  static const String routeDashboard = '/dashboard';
  static const String routeCaptureMeter = '/capture-meter';
  static const String routePayment = '/payment';

  // OTP Configuration
  static const int otpLength = 6;
  static const Duration otpExpiry = Duration(minutes: 5);
  static const int otpResendCooldown = 60; // seconds

  // KYC Levels
  static const int kycLevel1 = 1; // Phone + CNI + Selfie
  static const int kycLevel2 = 2; // Video + Proof of Address

  // Offline Sync
  static const int maxOfflineTransactions = 10;
  static const Duration syncInterval = Duration(minutes: 15);

  // Analytics & Monitoring
  static const bool enableAnalytics = true;
  static const bool enableCrashlytics = true;

  // Feature Flags
  static const bool enableOfflineMode = true;
  static const bool enableBiometricAuth = true;
  static const bool enableQRPayment = true;
}
