# SSH Authentication - SSH Key Authentication Setup

## Overview
This document covers SSH key pair generation, public key deployment to WSL instances, and authentication testing for AWX automation.

## SSH Key Pair Generation

### 1. Generate SSH Key Pair (on AWX host)
```bash
# Generate RSA key in traditional PEM format
ssh-keygen -t rsa -b 2048 -f ~/.ssh/awx_wsl_key_traditional -N "" -m PEM

# Verify key format
head -1 ~/.ssh/awx_wsl_key_traditional
# Should show: -----BEGIN RSA PRIVATE KEY-----
```

### 2. Verify Key Files Created
```bash
# Check that both key files exist
ls -la ~/.ssh/awx_wsl_key_traditional*

# Expected output:
# -rw------- 1 daniv daniv 1675 ... awx_wsl_key_traditional
# -rw-r--r-- 1 daniv daniv  393 ... awx_wsl_key_traditional.pub
```

### 3. Display Public Key
```bash
# Display public key for copying
cat ~/.ssh/awx_wsl_key_traditional.pub

# Expected format:
# ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ... daniv@ubuntuAWX
```

## Public Key Deployment

### 1. Deploy to Ubuntu-24.04 (wslubuntu1)
```bash
# Copy public key to Ubuntu-24.04
ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p 2223 daniv@172.22.192.129

# Expected output:
# Number of key(s) added: 1
# Now try logging into the machine...
```

### 2. Deploy to Kali-Linux (wslkali1)
```bash
# Copy public key to Kali-Linux
ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p 2224 daniv@172.22.192.129

# Expected output:
# Number of key(s) added: 1
# Now try logging into the machine...
```

### 3. Verify Key Deployment
```bash
# Check authorized_keys file on Ubuntu-24.04
ssh -p 2223 daniv@172.22.192.129 "cat ~/.ssh/authorized_keys"

# Check authorized_keys file on Kali-Linux
ssh -p 2224 daniv@172.22.192.129 "cat ~/.ssh/authorized_keys"

# Both should show the public key content
```

## Authentication Testing

### 1. Test SSH Key Authentication
```bash
# Test SSH key authentication to Ubuntu-24.04
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "whoami"

# Expected output: daniv

# Test SSH key authentication to Kali-Linux
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2224 daniv@172.22.192.129 "whoami"

# Expected output: daniv
```

### 2. Test Sudo Access
```bash
# Test sudo access on Ubuntu-24.04
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "sudo whoami"

# Expected output: root

# Test sudo access on Kali-Linux
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2224 daniv@172.22.192.129 "sudo whoami"

# Expected output: root
```

### 3. Test System Commands
```bash
# Test systemctl command on Ubuntu-24.04
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "sudo systemctl status ssh"

# Test systemctl command on Kali-Linux
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2224 daniv@172.22.192.129 "sudo systemctl status ssh"

# Both should show SSH service status
```

## Key Format Verification

### 1. Verify Private Key Format
```bash
# Check private key format
openssl rsa -in ~/.ssh/awx_wsl_key_traditional -check -noout

# Expected output: RSA key ok

# Display key information
openssl rsa -in ~/.ssh/awx_wsl_key_traditional -text -noout | head -10
```

### 2. Verify Public Key Format
```bash
# Check public key format
ssh-keygen -l -f ~/.ssh/awx_wsl_key_traditional.pub

# Expected output: 2048 SHA256:... daniv@ubuntuAWX (RSA)
```

### 3. Test Key Fingerprint
```bash
# Get key fingerprint
ssh-keygen -lf ~/.ssh/awx_wsl_key_traditional.pub

# Expected format: 2048 SHA256:... daniv@ubuntuAWX (RSA)
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

# Set proper permissions
chmod 600 ~/.ssh/config
```

### 2. Test SSH Config
```bash
# Test SSH using config
ssh wslubuntu1 "whoami"
ssh wslkali1 "whoami"

# Both should return: daniv
```

## Security Considerations

### 1. Key Security
```bash
# Set proper permissions on private key
chmod 600 ~/.ssh/awx_wsl_key_traditional

# Set proper permissions on public key
chmod 644 ~/.ssh/awx_wsl_key_traditional.pub

# Verify permissions
ls -la ~/.ssh/awx_wsl_key_traditional*
```

### 2. Disable Password Authentication (Optional)
```bash
# On both WSL instances, edit SSH config
# File: /etc/ssh/sshd_config
# Change: PasswordAuthentication no

# Restart SSH service
sudo systemctl restart ssh
```

### 3. Key Backup
```bash
# Backup SSH keys
cp ~/.ssh/awx_wsl_key_traditional ~/.ssh/awx_wsl_key_traditional.backup
cp ~/.ssh/awx_wsl_key_traditional.pub ~/.ssh/awx_wsl_key_traditional.pub.backup

# Store backup securely
```

## Verification Steps

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
```

### 2. Key Format Verification
```bash
echo "=== Key Format Verification ==="
openssl rsa -in ~/.ssh/awx_wsl_key_traditional -check -noout
ssh-keygen -l -f ~/.ssh/awx_wsl_key_traditional.pub
```

## Troubleshooting SSH Authentication

### Common Issues

#### SSH Key Authentication Failing
```bash
# Check SSH key permissions
ls -la ~/.ssh/awx_wsl_key_traditional

# Check authorized_keys file
ssh -p 2223 daniv@172.22.192.129 "ls -la ~/.ssh/authorized_keys"

# Test with verbose output
ssh -v -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129
```

#### Permission Denied Errors
```bash
# Check SSH directory permissions
ssh -p 2223 daniv@172.22.192.129 "ls -la ~/.ssh/"

# Fix permissions if needed
ssh -p 2223 daniv@172.22.192.129 "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

#### Key Format Issues
```bash
# Regenerate key if format is wrong
rm ~/.ssh/awx_wsl_key_traditional*
ssh-keygen -t rsa -b 2048 -f ~/.ssh/awx_wsl_key_traditional -N "" -m PEM

# Redeploy keys
ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p 2223 daniv@172.22.192.129
ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p 2224 daniv@172.22.192.129
```

#### Sudo Access Issues
```bash
# Check sudoers configuration
ssh -p 2223 daniv@172.22.192.129 "sudo cat /etc/sudoers.d/daniv-nopasswd"

# Test sudo access
ssh -p 2223 daniv@172.22.192.129 "sudo -l"
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
- [ ] No permission denied errors
- [ ] Keys are backed up securely
