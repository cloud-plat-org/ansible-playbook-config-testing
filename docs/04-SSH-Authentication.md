# SSH Authentication - SSH Key Authentication Setup

## Overview
This document covers SSH key pair generation, public key deployment to WSL instances, and authentication testing for AWX automation.

## SSH Key Pair Generation

### 1. Generate SSH Key Pair
```bash
# Generate RSA key in traditional PEM format
ssh-keygen -t rsa -b 2048 -f ~/.ssh/awx_wsl_key_traditional -N "" -m PEM

# Verify key files created
ls -la ~/.ssh/awx_wsl_key_traditional*

# Display public key for copying
cat ~/.ssh/awx_wsl_key_traditional.pub
```

### 2. Verify Key Format
```bash
# Check private key format
openssl rsa -in ~/.ssh/awx_wsl_key_traditional -check -noout
# Expected: RSA key ok

# Check public key format
ssh-keygen -l -f ~/.ssh/awx_wsl_key_traditional.pub
# Expected: 2048 SHA256:... daniv@ubuntuAWX (RSA)
```

## Public Key Deployment

### 1. Deploy to WSL Instances
```bash
# Deploy to Ubuntu-24.04 (wslubuntu1)
ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p 2223 daniv@172.22.192.129

# Deploy to Kali-Linux (wslkali1)
ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p 2224 daniv@172.22.192.129

# Verify deployment
ssh -p 2223 daniv@172.22.192.129 "cat ~/.ssh/authorized_keys"
ssh -p 2224 daniv@172.22.192.129 "cat ~/.ssh/authorized_keys"
```

## SSH Configuration Optimization

### 1. Create SSH Config File
```bash
# Create SSH config for easier access
cat > ~/.ssh/config << 'EOF'
Host wslubuntu1
    HostName 172.22.192.129
    Port 2223
    User daniv
    IdentityFile ~/.ssh/awx_wsl_key_traditional
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

Host wslkali1
    HostName 172.22.192.129
    Port 2224
    User daniv
    IdentityFile ~/.ssh/awx_wsl_key_traditional
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOF

chmod 600 ~/.ssh/config
```

## Authentication Testing

### 1. Complete Authentication Test
```bash
echo "=== SSH Key Authentication Test ==="
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "echo 'Ubuntu SSH Key OK'"
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2224 daniv@172.22.192.129 "echo 'Kali SSH Key OK'"

echo "=== Sudo Access Test ==="
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "sudo whoami"
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2224 daniv@172.22.192.129 "sudo whoami"

echo "=== System Command Test ==="
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "sudo systemctl is-active ssh"
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2224 daniv@172.22.192.129 "sudo systemctl is-active ssh"

echo "=== SSH Config Test ==="
ssh wslubuntu1 "whoami"
ssh wslkali1 "whoami"
```

## Security Considerations

### 1. Set Proper Permissions
```bash
# Set proper permissions on keys
chmod 600 ~/.ssh/awx_wsl_key_traditional
chmod 644 ~/.ssh/awx_wsl_key_traditional.pub

# Verify permissions
ls -la ~/.ssh/awx_wsl_key_traditional*
```

### 2. Key Backup
```bash
# Backup SSH keys
cp ~/.ssh/awx_wsl_key_traditional ~/.ssh/awx_wsl_key_traditional.backup
cp ~/.ssh/awx_wsl_key_traditional.pub ~/.ssh/awx_wsl_key_traditional.pub.backup
```

## Troubleshooting

### Common Issues
```bash
# Check SSH key permissions
ls -la ~/.ssh/awx_wsl_key_traditional

# Test with verbose output
ssh -v -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129

# Fix permissions if needed
ssh -p 2223 daniv@172.22.192.129 "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

## Next Steps

Once SSH key authentication is working properly, proceed to:
- [05-AWX-Configuration.md](05-AWX-Configuration.md) - Projects, inventory, job templates

## Verification Checklist

Before proceeding to AWX configuration, verify:
- [ ] SSH key pair is generated in correct format
- [ ] Public key is deployed to both WSL instances
- [ ] SSH key authentication works without password prompts
- [ ] Sudo access works with SSH key authentication
- [ ] System commands can be executed via SSH
- [ ] Key permissions are set correctly
- [ ] SSH config file is created (optional)
- [ ] All authentication tests pass