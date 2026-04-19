# 🛡️ Yobhou App - Production Security

## Security Stack

### Authentication
- **JWT Tokens**: Access (15 min), Refresh (7 days)
- **Secure Storage**: flutter_secure_storage (keychain/keystore)
- **Password Policy**: 8+ chars, uppercase, lowercase, digit
- **Rate Limiting**: 60 req/min, 5 login attempts → 15 min lockout
- **Input Validation**: Phone (+224), Email, Date (18+)

### API Security
- **HTTPS**: All endpoints TLS 1.3
- **JWT Authentication**: Bearer tokens in headers
- **CORS**: Strict origin whitelist
- **Rate Limiting**: Per-user throttling

### Data Protection
- **Docker Secrets**: All secrets via secrets
- **Read-Only Containers**: prod containers
- **Network Segmentation**: frontend/backend/db networks
- **Field Encryption**: Sensitive fields (AES-256)
- **Audit Logging**: 10-year retention (ELK + S3 Glacier)

### Mobile Security
- **Secure Storage**: Keychain (iOS), Keystore (Android)
- **Biometric**: Face ID / Touch ID
- **Certificate Pinning**: SSL pinning
- **Root/Jailbreak Detection**: Runtime checks
- **Memory Protection**:防注入 (anti-injection)

### AML Compliance
- **Daily Limit**: 1,000,000 GNF
- **Monthly Limit**: 5,000,000 GNF
- **Transaction Count**: 10/day max
- **Structuring Detection**: Multiple sub-threshold transactions
- **Rapid Succession**: < 5 min between transactions

### Code Security
- **No Hardcoded Secrets**: All via environment/secret management
- **Input Sanitization**: whitelist validation
- **SQL Injection Protection**: ORM only (Django ORM)
- **XSS Prevention**: HTML escaping, CSP headers
- **CSRF Protection**: Token-based

### Compliance
- **BCEAO**: Banking regulations
- **RGPD-like**: Data privacy
- **10-Year Audit**: Immutable logs (S3 Glacier)
- **AML/KYC**: Full customer verification

## Architecture Diagram
```
User → Mobile App (Flutter)
         ↓ HTTPS + JWT
    API Gateway (Traefik)
         ↓ Rate Limit + Auth
    Backend (Django)
         ↓ JWT Verify + AML Check
    PostgreSQL + Redis + S3
```

## Security Checklist
- [x] HTTPS/TLS 1.3
- [x] JWT authentication
- [x] Password hashing (PBKDF2)
- [x] Rate limiting
- [x] Input validation
- [x] SQL injection protection
- [x] XSS prevention
- [x] CSRF protection
- [x] Secure storage (mobile)
- [x] Docker secrets
- [x] Read-only containers
- [x] Network segmentation
- [x] Audit logging (10 years)
- [x] AML limits configured
- [x] Biometric login

## Runbooks
- **Incident Response**: security@yobhou.gn
- **Escalation**: CTO → Lead Dev → Ops
- **SLA**: P1 (critical): < 1 hour response

---

*Last Updated: 2026-04-19*  
*Version: 2.0*  
*Compliance: BCEAO, RGPD-like, 10-year audit*
