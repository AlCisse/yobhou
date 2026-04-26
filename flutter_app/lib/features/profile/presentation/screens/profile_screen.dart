import 'package:flutter/material.dart';
import '../../core/constants/colors.dart';
import '../../core/constants/typography.dart';
import '../../core/widgets/app_button.dart';
import '../../core/services/api_service.dart';
import '../../core/services/auth_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({Key? key}) : super(key: key);

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map<String, dynamic>? _user;
  bool _loading = true;
  bool _loggingOut = false;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final apiService = ApiService();
      final response = await apiService.getProfile();
      
      setState(() {
        _user = response;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur chargement profil: $e')),
      );
    }
  }

  Future<void> _logout() async {
    setState(() => _loggingOut = true);
    
    try {
      final authService = AuthService();
      await authService.logout();
      
      if (mounted) {
        Navigator.of(context).pushNamedAndRemoveUntil(
          '/login',
          (route) => false,
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur déconnexion: $e')),
      );
    } finally {
      setState(() => _loggingOut = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text(
          'Mon Profil',
          style: AppTypography.h3.copyWith(color: Colors.white),
        ),
        centerTitle: true,
        elevation: 0,
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _buildProfile(),
    );
  }

  Widget _buildProfile() {
    final phone = _user?['phone_number'] ?? 'Non disponible';
    final username = _user?['username'] ?? 'Utilisateur';
    final dateJoined = _user?['date_joined'] != null
        ? DateTime.tryParse(_user!['date_joined'])
        : null;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Avatar
          CircleAvatar(
            radius: 50,
            backgroundColor: AppColors.primary.withOpacity(0.1),
            child: Text(
              username.isNotEmpty ? username[0].toUpperCase() : 'U',
              style: AppTypography.h1.copyWith(
                color: AppColors.primary,
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Nom
          Text(
            username,
            style: AppTypography.h2,
          ),
          
          const SizedBox(height: 4),
          
          // Téléphone
          Text(
            phone,
            style: AppTypography.body.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          
          if (dateJoined != null) ...[
            const SizedBox(height: 4),
            Text(
              'Membre depuis ${dateJoined.day}/${dateJoined.month}/${dateJoined.year}',
              style: AppTypography.small.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ],
          
          const SizedBox(height: 32),
          
          // Menu options
          _buildMenuCard(
            icon: Icons.receipt_long,
            title: 'Mes Paiements',
            subtitle: 'Historique de vos factures payées',
            onTap: () => Navigator.pushNamed(context, '/payment-history'),
          ),
          
          _buildMenuCard(
            icon: Icons.account_balance,
            title: 'Mes Compteurs',
            subtitle: 'Gérer vos numéros de compteur',
            onTap: () {}, // TODO: Navigate to meters screen
          ),
          
          _buildMenuCard(
            icon: Icons.security,
            title: 'Sécurité',
            subtitle: 'Changer mot de passe, 2FA',
            onTap: () {}, // TODO: Navigate to security screen
          ),
          
          _buildMenuCard(
            icon: Icons.help_outline,
            title: 'Aide & Support',
            subtitle: 'FAQ, contact support',
            onTap: () {}, // TODO: Navigate to help screen
          ),
          
          const SizedBox(height: 32),
          
          // Version
          Text(
            'Yobhou v1.0.0',
            style: AppTypography.small.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          
          const SizedBox(height: 4),
          
          Text(
            '© 2026 Yobhou Fintech',
            style: AppTypography.small.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          
          const SizedBox(height: 32),
          
          // Bouton déconnexion
          AppButton(
            text: 'Déconnexion',
            onPressed: _loggingOut ? null : _logout,
            icon: _loggingOut
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : const Icon(Icons.logout),
            type: ButtonType.danger,
          ),
        ],
      ),
    );
  }

  Widget _buildMenuCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  icon,
                  color: AppColors.primary,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: AppTypography.body.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: AppTypography.small.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(
                Icons.chevron_right,
                color: AppColors.textSecondary,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
