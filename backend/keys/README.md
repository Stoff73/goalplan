# JWT RSA Key Pair

This directory contains RSA-2048 key pairs used for JWT token signing and verification.

## Security Notice

**CRITICAL:** The private key (`jwt_private_key.pem`) must NEVER be committed to version control or shared publicly. These keys are used to sign authentication tokens, and compromise of the private key would allow attackers to forge authentication tokens.

## Key Files

- `jwt_private_key.pem` - RSA-2048 private key for signing JWT tokens (RS256)
- `jwt_public_key.pem` - RSA-2048 public key for verifying JWT signatures

## Key Generation

If you need to generate new keys, run:

```bash
python3 -c "
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Generate RSA-2048 key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Serialize private key
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Serialize public key
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Write keys
with open('keys/jwt_private_key.pem', 'wb') as f:
    f.write(private_pem)

with open('keys/jwt_public_key.pem', 'wb') as f:
    f.write(public_pem)

print('Keys generated successfully')
"
```

## Production Deployment

For production environments:

1. **Generate new keys** for each environment (dev, staging, production)
2. **Store private key securely** using:
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault
   - Environment variables (with proper encryption at rest)
3. **Set proper file permissions:**
   ```bash
   chmod 600 jwt_private_key.pem  # Read/write for owner only
   chmod 644 jwt_public_key.pem   # Read for all
   ```
4. **Update .env file** to point to key locations:
   ```
   JWT_PRIVATE_KEY_PATH=/secure/path/to/jwt_private_key.pem
   JWT_PUBLIC_KEY_PATH=/secure/path/to/jwt_public_key.pem
   ```
5. **Rotate keys regularly** (recommended: every 90 days)

## Key Rotation

When rotating keys:

1. Generate new key pair
2. Keep old public key for verification during transition period
3. Start signing new tokens with new private key
4. After all old tokens expire (7 days for refresh tokens), remove old keys
5. Update all services that verify tokens with new public key

## Security Best Practices

- Never commit private keys to version control (.gitignore enforced)
- Use different keys for each environment
- Monitor key access and usage
- Implement key rotation schedule
- Store keys encrypted at rest
- Use hardware security modules (HSM) for production if possible
- Audit key access regularly

## Algorithm Details

- **Algorithm:** RS256 (RSA Signature with SHA-256)
- **Key Size:** 2048 bits (256 bytes)
- **Public Exponent:** 65537
- **Format:** PEM-encoded PKCS#8

## Token Expiration

- **Access tokens:** 15 minutes
- **Refresh tokens:** 7 days

These short expiration times provide defense in depth if tokens are compromised.
