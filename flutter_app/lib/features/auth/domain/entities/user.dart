import 'package:equatable/equatable.dart';

class User extends Equatable {
  final int id;
  final String username;
  final String phoneNumber;
  final String? email;
  final String? profilePicture;
  final String? locationPrefecture;
  final String? locationQuartier;
  final DateTime? dateOfBirth;
  final int kycLevel;
  final DateTime createdAt;
  final DateTime updatedAt;

  const User({
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
  });

  @override
  List<Object?> get props => [
        id,
        username,
        phoneNumber,
        email,
        profilePicture,
        locationPrefecture,
        locationQuartier,
        dateOfBirth,
        kycLevel,
        createdAt,
        updatedAt,
      ];

  User copyWith({
    int? id,
    String? username,
    String? phoneNumber,
    String? email,
    String? profilePicture,
    String? locationPrefecture,
    String? locationQuartier,
    DateTime? dateOfBirth,
    int? kycLevel,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id ?? this.id,
      username: username ?? this.username,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      email: email ?? this.email,
      profilePicture: profilePicture ?? this.profilePicture,
      locationPrefecture: locationPrefecture ?? this.locationPrefecture,
      locationQuartier: locationQuartier ?? this.locationQuartier,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
      kycLevel: kycLevel ?? this.kycLevel,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
