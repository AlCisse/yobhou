# 🔒 Security Core - Yobhou Project

## Docker Secrets mandatory for ALL secrets

**NO EXCEPTIONS.** All API keys, merchant IDs, encryption keys, and credentials **MUST** use Docker Secrets.

## Security Architecture

### 1. Docker Secrets Flow
```
Secrets (created on host) → Docker Swarm → Mount as read-only file in container → Read by app at runtime
```

### 2. Container Hardening
```yaml
security_opt:
  - no-new-privileges:true
read_only: true
tmpfs:
  - /tmp:size=64M,mode=1777
```

### 3. Network Segmentation
- **Frontend services**: Public access (Traefik)
- **Backend services**: Internal only (overlay network)
- **Database**: Isolated from all services (separate network)
- **Redis**: Isolated (separate network)

### 4. Encryption at Rest
- **QR Code keys**: AES-256 encrypted
- **Secrets**: Encrypted in Docker Swarm
- **Database**: TLS 1.3 encrypted connections

## QR Code Payment Integration (Future)

### Architecture
```
Merchant → Scan QR Code → Decrypt Key → Verify Signature → Pay via API
```

### Secrets Required
```yaml
secrets:
  qr_code_encryption_key:
    external: true
  qr_code_signing_private_key:
    external: true
  merchant_api_key:
    external: true
```

### Security Flow
1. Backend generates QR code with encrypted merchant ID + timestamp
2. QR code contains: `merchant_id_encrypted:timestamp:sig`
3. Client scans → decrypts → verifies signature → pays
4. All transactions logged in audit database

## Audit Logging

**ALL** payment operations must be logged:
- Timestamp
- User ID
- Transaction ID
- Amount
- Payment Method
- Status
- IP Address
- User Agent

## Emergency Procedures

### If secret is compromised:
1. Rotate secret immediately
2. Re-deploy stack
3. Audit all transactions since last rotation
4. Notify relevant parties

### If breach detected:
1. Isolate affected services
2. Disable compromised secrets
3. Initiate incident response
4. Notify legal/security team

---

*This file is part of the Security Core. Unauthorized modification triggers alert.*