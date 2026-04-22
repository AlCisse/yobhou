import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'core/core.dart';
import 'features/home/presentation/home_exports.dart';
import 'features/auth/presentation/auth_exports.dart';
import 'features/onboarding/presentation/screens/onboarding_screen.dart';
import 'features/meter/presentation/screens/capture_meter_screen.dart';
import 'features/payment/presentation/screens/payment_screen.dart';
import 'features/dashboard/presentation/screens/dashboard_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: YobhouApp()));
}

class YobhouApp extends StatelessWidget {
  const YobhouApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: AppConstants.appName,
      debugShowCheckedModeBanner: false,
      theme: PremiumTheme.lightTheme,
      routerConfig: _router,
    );
  }
}

final GoRouter _router = GoRouter(
  initialLocation: '/',
  routes: [
    // Home
    GoRoute(
      path: '/',
      name: 'home',
      builder: (context, state) => const HomeScreen(),
    ),
    // Onboarding
    GoRoute(
      path: '/onboarding',
      name: 'onboarding',
      builder: (context, state) => const OnboardingScreen(),
    ),
    // Auth
    GoRoute(
      path: '/login',
      name: 'login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/register',
      name: 'register',
      builder: (context, state) => const RegisterScreen(),
    ),
    GoRoute(
      path: '/upload-invoice',
      name: 'upload-invoice',
      builder: (context, state) {
        final data = state.extra as Map<String, dynamic>? ?? {};
        return InvoiceUploadScreen(registrationData: data);
      },
    ),
    GoRoute(
      path: '/register-confirm',
      name: 'register-confirm',
      builder: (context, state) {
        final data = state.extra as Map<String, dynamic>? ?? {};
        return RegisterConfirmScreen(userData: data);
      },
    ),
    // Dashboard
    GoRoute(
      path: '/dashboard',
      name: 'dashboard',
      builder: (context, state) => const DashboardScreen(),
    ),
    // Meter
    GoRoute(
      path: '/capture-meter',
      name: 'capture-meter',
      builder: (context, state) => const CaptureMeterScreen(),
    ),
    // Payment
    GoRoute(
      path: '/payment',
      name: 'payment',
      builder: (context, state) {
        final amount = state.uri.queryParameters['amount'];
        return PaymentScreen(amount: amount != null ? double.tryParse(amount) ?? 0 : 0);
      },
    ),
  ],
);
