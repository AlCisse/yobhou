import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../core/constants/colors.dart';
import '../../core/constants/typography.dart';
import '../../core/widgets/app_button.dart';
import '../../core/services/api_service.dart';
import 'receipt_screen.dart';

class PaymentHistoryScreen extends StatefulWidget {
  const PaymentHistoryScreen({Key? key}) : super(key: key);

  @override
  State<PaymentHistoryScreen> createState() => _PaymentHistoryScreenState();
}

class _PaymentHistoryScreenState extends State<PaymentHistoryScreen> {
  List<dynamic> _payments = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadPayments();
  }

  Future<void> _loadPayments() async {
    try {
      final apiService = ApiService();
      final response = await apiService.getPayments();
      
      setState(() {
        _payments = response['payments'] ?? [];
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Erreur de chargement: $e';
        _loading = false;
      });
    }
  }

  Future<void> _refresh() async {
    setState(() => _loading = true);
    await _loadPayments();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text(
          'Historique des Paiements',
          style: AppTypography.h3.copyWith(color: Colors.white),
        ),
        centerTitle: true,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refresh,
          ),
        ],
      ),
      body: _loading 
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _buildError()
              : _payments.isEmpty
                  ? _buildEmpty()
                  : _buildList(),
    );
  }

  Widget _buildError() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: AppColors.error),
          const SizedBox(height: 16),
          Text(
            _error!,
            style: AppTypography.body,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          AppButton(
            text: 'Réessayer',
            onPressed: _refresh,
            type: ButtonType.primary,
          ),
        ],
      ),
    );
  }

  Widget _buildEmpty() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.receipt_long_outlined,
            size: 80,
            color: AppColors.textSecondary,
          ),
          const SizedBox(height: 16),
          Text(
            'Aucun paiement',
            style: AppTypography.h3,
          ),
          const SizedBox(height: 8),
          Text(
            'Vos paiements apparaîtront ici',
            style: AppTypography.body.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 24),
          AppButton(
            text: 'Payer une facture',
            onPressed: () => Navigator.pushNamed(context, '/upload-invoice'),
            type: ButtonType.primary,
          ),
        ],
      ),
    );
  }

  Widget _buildList() {
    return RefreshIndicator(
      onRefresh: _refresh,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _payments.length,
        itemBuilder: (context, index) {
          final payment = _payments[index];
          return _PaymentCard(
            payment: payment,
            onTap: () => _navigateToDetail(payment),
          );
        },
      ),
    );
  }

  void _navigateToDetail(dynamic payment) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ReceiptScreen(
          transactionReference: payment['transaction_reference'] ?? '',
          amount: (payment['amount'] ?? 0).toDouble(),
          paymentMethod: payment['payment_method'] ?? '',
          meterNumber: payment['meter_number'] ?? 'N/A',
          date: DateTime.parse(payment['created_at'] ?? DateTime.now().toIso8601String()),
          status: payment['status'] ?? 'PENDING',
        ),
      ),
    );
  }
}

class _PaymentCard extends StatelessWidget {
  final dynamic payment;
  final VoidCallback onTap;

  const _PaymentCard({
    required this.payment,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('dd/MM/yyyy HH:mm');
    final date = DateTime.tryParse(payment['created_at'] ?? '') ?? DateTime.now();
    final amount = (payment['amount'] ?? 0).toDouble();
    final status = payment['status'] ?? 'PENDING';
    
    Color statusColor;
    IconData statusIcon;
    
    switch (status) {
      case 'COMPLETED':
        statusColor = AppColors.success;
        statusIcon = Icons.check_circle;
        break;
      case 'FAILED':
        statusColor = AppColors.error;
        statusIcon = Icons.error;
        break;
      case 'PENDING':
      case 'INITIATED':
        statusColor = AppColors.warning;
        statusIcon = Icons.pending;
        break;
      default:
        statusColor = AppColors.textSecondary;
        statusIcon = Icons.help;
    }

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
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      payment['transaction_reference'] ?? 'N/A',
                      style: AppTypography.body.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Icon(statusIcon, color: statusColor, size: 24),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    dateFormat.format(date),
                    style: AppTypography.small.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                  Text(
                    '${amount.toStringAsFixed(0)} GNF',
                    style: AppTypography.h3.copyWith(
                      color: AppColors.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              if (payment['meter_number'] != null)
                Text(
                  'Compteur: ${payment['meter_number']}',
                  style: AppTypography.small.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
