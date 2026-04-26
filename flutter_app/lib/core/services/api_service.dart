import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'auth_service.dart';

class ApiService {
  static const String baseUrl = 'https://api.yobhou.gn';
  
  final AuthService _authService = AuthService();
  
  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    if (_authService.token != null) 
      'Authorization': 'Bearer ${_authService.token}',
  };
  
  // ==================== AUTH ====================
  
  Future<Map<String, dynamic>> register(Map<String, dynamic> data) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/register/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(data),
    );
    return _handleResponse(response);
  }
  
  Future<Map<String, dynamic>> login(String phone, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'phone_number': phone,
        'password': password,
      }),
    );
    return _handleResponse(response);
  }
  
  Future<Map<String, dynamic>> getProfile() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/profile/'),
      headers: _headers,
    );
    return _handleResponse(response);
  }
  
  // ==================== OCR ====================
  
  Future<Map<String, dynamic>> uploadInvoice(String imagePath) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/upload-invoice/'),
    );
    
    request.headers.addAll(_headers);
    request.files.add(await http.MultipartFile.fromPath('invoice_image', imagePath));
    
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    
    return _handleResponse(response);
  }
  
  Future<Map<String, dynamic>> captureMeter(String imagePath) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/capture-meter/'),
    );
    
    request.headers.addAll(_headers);
    request.files.add(await http.MultipartFile.fromPath('meter_photo', imagePath));
    
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    
    return _handleResponse(response);
  }
  
  // ==================== PAYMENT ====================
  
  Future<Map<String, dynamic>> initiatePayment({
    required int meterReadingId,
    required double amount,
    required String paymentMethod,
    required String paymentPhone,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/payment/initiate/'),
      headers: _headers,
      body: jsonEncode({
        'meter_reading_id': meterReadingId,
        'amount': amount,
        'payment_method': paymentMethod,
        'payment_phone': paymentPhone,
      }),
    );
    return _handleResponse(response);
  }
  
  Future<Map<String, dynamic>> confirmPayment(int paymentId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/payment/confirm/'),
      headers: _headers,
      body: jsonEncode({
        'payment_id': paymentId,
      }),
    );
    return _handleResponse(response);
  }
  
  Future<Map<String, dynamic>> getPaymentStatus(String reference) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/payment/status/$reference/'),
      headers: _headers,
    );
    return _handleResponse(response);
  }
  
  Future<Map<String, dynamic>> getPayments() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/payment/receipts/'),
      headers: _headers,
    );
    return _handleResponse(response);
  }
  
  Future<Uint8List> downloadReceipt(String reference) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/payment/receipts/$reference/pdf/'),
      headers: _headers,
    );
    
    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else {
      throw Exception('Erreur téléchargement: ${response.statusCode}');
    }
  }
  
  // ==================== HELPER ====================
  
  Map<String, dynamic> _handleResponse(http.Response response) {
    final body = jsonDecode(response.body);
    
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return body;
    } else if (response.statusCode == 401) {
      throw Exception('Session expirée. Veuillez vous reconnecter.');
    } else if (response.statusCode == 429) {
      throw Exception('Trop de requêtes. Veuillez patienter.');
    } else {
      throw Exception(body['message'] ?? 'Erreur serveur: ${response.statusCode}');
    }
  }
}
