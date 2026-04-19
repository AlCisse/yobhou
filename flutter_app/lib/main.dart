/// Main App
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'core/core.dart';
import 'features/home/presentation/home_exports.dart';
import 'features/auth/presentation/auth_exports.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const ProviderScope(child: YobhouApp()));
}

class YobhouApp extends StatelessWidget {
  const YobhouApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp.router(
    title: AppConstants.appName,
    debugShowCheckedModeBanner: false,
    theme: AppTheme.lightTheme,
    routerConfig: _router,
  );
}

final GoRouter _router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(path: '/', name: 'home', builder: (context, state) => const HomeScreen()),
    GoRoute(path: '/register', name: 'register', builder: (context, state) => const RegisterScreen()),
    GoRoute(path: '/upload-invoice', name: 'upload-invoice', builder: (context, state) => const UploadInvoiceScreen()),
  ],
);
