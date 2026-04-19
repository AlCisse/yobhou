import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:path_provider/path_provider.dart';
import 'core/constants/app_constants.dart';
import 'core/network/api_client.dart';
import 'features/auth/data/models/user_model.dart';
import 'features/auth/presentation/screens/login_screen.dart';
import 'features/auth/presentation/screens/register_screen.dart';
import 'features/auth/presentation/screens/invoice_upload_screen.dart';
import 'features/auth/presentation/screens/register_confirm_screen.dart';
import 'features/onboarding/presentation/screens/onboarding_screen.dart';
import 'features/meter/presentation/screens/capture_meter_screen.dart';
import 'features/payment/presentation/screens/payment_screen.dart';
import 'features/dashboard/presentation/screens/dashboard_screen.dart';
import 'di.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Hive for offline storage
  final dir = await getApplicationDocumentsDirectory();
  Hive.init(dir.path);

  // Register adapters
  await _registerHiveAdapters();

  // Initialize dependency injection
  await initDependencies();

  runApp(const ProviderScope(child: YobhouApp()));
}

Future<void> _registerHiveAdapters() async {
  Hive.registerAdapter(UserModelAdapter());
  // Add more adapters as needed
}

class YobhouApp extends ConsumerWidget {
  const YobhouApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'Yobhou',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        fontFamily: 'Poppins',
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppConstants.primaryColor,
          brightness: Brightness.light,
        ),
      ),
      routerConfig: router,
    );
  }
}

// Router configuration
final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authStateNotifierProvider);

  return GoRouter(
    initialLocation: '/onboarding',
    redirect: (context, state) {
      final isLoggedIn = authState.isLoggedIn;
      final isLoggingIn = state.matchedLocation == '/login' ||
          state.matchedLocation == '/register';
      final isOnboarding = state.matchedLocation == '/onboarding';

      if (!isLoggedIn && !isLoggingIn && !isOnboarding) {
        return '/login';
      }

      if (isLoggedIn && (isLoggingIn || isOnboarding)) {
        return '/dashboard';
      }

      return null;
    },
    routes: [
      GoRoute(
        path: '/onboarding',
        name: 'onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
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
          final data = state.extra as Map<String, dynamic>?;
          return InvoiceUploadScreen(registrationData: data ?? {});
        },
      ),
      GoRoute(
        path: '/register-confirm',
        name: 'register-confirm',
        builder: (context, state) {
          final data = state.extra as Map<String, dynamic>?;
          return RegisterConfirmScreen(userData: data ?? {});
        },
      ),
      GoRoute(
        path: '/dashboard',
        name: 'dashboard',
        builder: (context, state) => const DashboardScreen(),
      ),
      GoRoute(
        path: '/capture-meter',
        name: 'capture-meter',
        builder: (context, state) => const CaptureMeterScreen(),
      ),
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
});
