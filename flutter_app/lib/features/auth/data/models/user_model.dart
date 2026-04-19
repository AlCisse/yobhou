import 'package:hive/hive.dart';
import '../../../domain/entities/user.dart';

part 'user_model.g.dart';

@HiveType(typeId: 0)
class UserModel extends User {
  @HiveField(0)
  final int id;

  @HiveField(1)
  final String username;

  @HiveField(2)
  final String phoneNumber;

  @HiveField(3)
  final String? email;

  @HiveField(4)
  final String? profilePicture;

  @HiveField(5)
  final String? locationPrefecture;

  @HiveField(6)
  final String? locationQuartier;

  @HiveField(7)
  final DateTime? dateOfBirth;

  @HiveField(8)
  final int kycLevel;

  @HiveField(9)
  final DateTime createdAt;

  @HiveField(10)
  final DateTime updatedAt;

  UserModel({
    required this.id,
    required this.username,
    required this.phoneNumber,
    this.email,
    this.profilePicture,
    this.locationPrefecture,
    this.locationQuartier,
    this.dateOfBirth,
    this.kycLevel = 1,
    required this.createdAt,
    required this.updatedAt,
  }) : super(
          id: id,
          username: username,
          phoneNumber: phoneNumber,
          email: email,
          profilePicture: profilePicture,
          locationPrefecture: locationPrefecture,
          locationQuartier: locationQuartier,
          dateOfBirth: dateOfBirth,
          kycLevel: kycLevel,
          createdAt: createdAt,
          updatedAt: updatedAt,
        );

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      username: json['username'],
      phoneNumber: json['phone_number'],
      email: json['email'],
      profilePicture: json['profile_picture'],
      locationPrefecture: json['location_prefecture'],
      locationQuartier: json['location_quartier'],
      dateOfBirth: json['date_of_birth'] != null 
          ? DateTime.parse(json['date_of_birth']) 
          : null,
      kycLevel: json['kyc_level'] ?? 1,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'phone_number': phoneNumber,
      'email': email,
      'profile_picture': profilePicture,
      'location_prefecture': locationPrefecture,
      'location_quartier': locationQuartier,
      'date_of_birth': dateOfBirth?.toIso8601String(),
      'kyc_level': kycLevel,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}
