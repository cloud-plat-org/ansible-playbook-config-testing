# WSL Configuration - Target WSL Instances Setup

## Overview
This document covers the configuration of target WSL instances (Ubuntu-24.04 and Kali-Linux) for AWX automation, including SSH service setup and passwordless sudo configuration.

## Ubuntu-24.04 Configuration (wslubuntu1)

### 1. Connect to Ubuntu WSL Instance
```bash
# Connect to Ubuntu-24.04 WSL instance
wsl -d Ubuntu-24.04
```

### 2. Configure SSH Service
```bash
# Edit SSH configuration
sudo vim /etc/ssh/sshd_config

# Add or modify these lines:
# ListenAddress 0.0.0.0
# Port 2223
# PermitRootLogin no
# PasswordAuthentication yes
# PubkeyAuthentication yes
```

### 3. Add Hostname Resolution
```bash
# Add hostname to /etc/hosts
echo "127.0.1.1 wslubuntu1" | sudo tee -a /etc/hosts

# Verify hostname
hostname
# Should show: wslubuntu1
```

### 4. Configure Passwordless Sudo

#### Option 1: Full Passwordless Sudo (Recommended for Development)
```bash
# Create sudoers file for daniv user
echo "daniv ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/daniv-nopasswd

# Verify sudoers file
sudo cat /etc/sudoers.d/daniv-nopasswd

# Test passwordless sudo
sudo whoami
# Should return: root
```

#### Option 2: Granular systemctl Permissions (More Secure)
```bash
# Create sudoers file with specific systemctl permissions
echo "daniv ALL=(ALL) NOPASSWD: /bin/systemctl stop *, /bin/systemctl start *, /bin/systemctl restart *, /bin/systemctl status *" | sudo tee /etc/sudoers.d/daniv-systemctl

# Verify sudoers file
sudo cat /etc/sudoers.d/daniv-systemctl

# Test systemctl operations
sudo systemctl stop ssh
sudo systemctl start ssh
sudo systemctl status ssh
```

**Note:** Option 1 is recommended for development environments. Option 2 provides more security by limiting sudo access to specific systemctl operations only.

### 5. Start and Enable SSH Service
```bash
# Restart SSH service
sudo systemctl restart ssh

# Enable SSH service
sudo systemctl enable ssh

# Check SSH status
sudo systemctl status ssh

# Verify SSH is listening on correct port
sudo netstat -tlnp | grep :2223
```

### 6. Exit Ubuntu Instance
```bash
exit
```

## Kali-Linux Configuration (wslkali1)

### 1. Connect to Kali WSL Instance
```bash
# Connect to Kali-Linux WSL instance
wsl -d kali-linux
```

### 2. Configure SSH Service
```bash
# Edit SSH configuration
sudo vim /etc/ssh/sshd_config

# Add or modify these lines:
# ListenAddress 0.0.0.0
# Port 2224
# PermitRootLogin no
# PasswordAuthentication yes
# PubkeyAuthentication yes
```

### 3. Add Hostname Resolution
```bash
# Add hostname to /etc/hosts
echo "127.0.1.1 wslkali1" | sudo tee -a /etc/hosts

# Verify hostname
hostname
# Should show: wslkali1
```

### 4. Configure Passwordless Sudo

#### Option 1: Full Passwordless Sudo (Recommended for Development)
```bash
# Create sudoers file for daniv user
echo "daniv ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/daniv-nopasswd

# Verify sudoers file
sudo cat /etc/sudoers.d/daniv-nopasswd

# Test passwordless sudo
sudo whoami
# Should return: root
```

#### Option 2: Granular systemctl Permissions (More Secure)
```bash
# Create sudoers file with specific systemctl permissions
echo "daniv ALL=(ALL) NOPASSWD: /bin/systemctl stop *, /bin/systemctl start *, /bin/systemctl restart *, /bin/systemctl status *" | sudo tee /etc/sudoers.d/daniv-systemctl

# Verify sudoers file
sudo cat /etc/sudoers.d/daniv-systemctl

# Test systemctl operations
sudo systemctl stop ssh
sudo systemctl start ssh
sudo systemctl status ssh
```

**Note:** Option 1 is recommended for development environments. Option 2 provides more security by limiting sudo access to specific systemctl operations only.

### 5. Start and Enable SSH Service
```bash
# Start SSH service (Kali may not have it enabled by default)
sudo systemctl start ssh

# Enable SSH service
sudo systemctl enable ssh

# Check SSH status
sudo systemctl status ssh

# Verify SSH is listening on correct port
sudo netstat -tlnp | grep :2224
```

### 6. Exit Kali Instance
```bash
exit
```

## Network Configuration Verification

### 1. Find WSL IP Addresses
```bash
# From AWX host (ubuntuAWX), check network configuration
ip addr show eth0

# Expected output format:
# inet 172.22.192.129/20 brd 172.22.207.255 scope global eth0
# Note the IP address: 172.22.192.129 (example)
```

### 2. Test SSH Access from AWX Host
```bash
# Test SSH to Ubuntu-24.04
ssh -p 2223 daniv@172.22.192.129

# Test SSH to Kali-Linux
ssh -p 2224 daniv@172.22.192.129

# Both should prompt for password initially
# Exit SSH sessions after testing
```

### 3. Verify Network Connectivity
```bash
# Test connectivity to both instances
ping -c 3 172.22.192.129

# Test port connectivity
nc -zv 172.22.192.129 2223
nc -zv 172.22.192.129 2224
```

## Service Configuration Details

### SSH Configuration Best Practices
```bash
# Recommended SSH configuration for both instances
# File: /etc/ssh/sshd_config

# Basic settings
Port 2223  # or 2224 for Kali
ListenAddress 0.0.0.0
Protocol 2

# Security settings
PermitRootLogin no
PasswordAuthentication yes
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# Logging
SyslogFacility AUTH
LogLevel INFO

# Connection settings
MaxAuthTries 3
MaxSessions 10
```

### Firewall Configuration (if needed)
```bash
# Check if ufw is active
sudo ufw status

# If firewall is active, allow SSH ports
sudo ufw allow 2223/tcp  # Ubuntu
sudo ufw allow 2224/tcp  # Kali

# Reload firewall
sudo ufw reload
```

## Verification Steps

### 1. Complete WSL Configuration Check
```bash
echo "=== Ubuntu-24.04 Configuration ==="
wsl -d Ubuntu-24.04 -- hostname
wsl -d Ubuntu-24.04 -- sudo systemctl status ssh
wsl -d Ubuntu-24.04 -- sudo netstat -tlnp | grep :2223

echo "=== Kali-Linux Configuration ==="
wsl -d kali-linux -- hostname
wsl -d kali-linux -- sudo systemctl status ssh
wsl -d kali-linux -- sudo netstat -tlnp | grep :2224

echo "=== Network Connectivity ==="
ip addr show eth0
ping -c 2 172.22.192.129
```

### 2. SSH Service Verification
```bash
# Test SSH connectivity
ssh -o ConnectTimeout=5 -p 2223 daniv@172.22.192.129 "echo 'Ubuntu SSH OK'"
ssh -o ConnectTimeout=5 -p 2224 daniv@172.22.192.129 "echo 'Kali SSH OK'"
```

## Troubleshooting WSL Configuration

### Common Issues

#### SSH Service Not Starting
```bash
# Check SSH service status
sudo systemctl status ssh

# Check SSH configuration syntax
sudo sshd -t

# Restart SSH service
sudo systemctl restart ssh

# Check SSH logs
sudo journalctl -u ssh -f
```

#### Port Already in Use
```bash
# Check what's using the port
sudo netstat -tlnp | grep :2223
sudo netstat -tlnp | grep :2224

# Kill process if needed
sudo kill -9 <PID>

# Or change port in SSH config
```

#### Sudo Configuration Issues
```bash
# Check sudoers file syntax
sudo visudo -c

# Test sudo access
sudo -l

# Verify user is in correct groups
groups daniv
```

#### Network Connectivity Issues
```bash
# Check WSL network configuration
ip route show

# Check if instances are running
wsl --list --verbose

# Restart WSL instances if needed
wsl --shutdown
wsl -d Ubuntu-24.04
wsl -d kali-linux
```

## Security Considerations

### 1. SSH Security
- Use strong passwords initially
- SSH keys will be configured in next phase
- Consider disabling password authentication after key setup
- Monitor SSH logs for unauthorized access attempts

### 2. Sudo Security
- Passwordless sudo is configured for automation
- Consider restricting sudo commands if needed
- Monitor sudo usage logs

### 3. Network Security
- WSL instances are on internal network
- No external exposure by default
- Consider firewall rules if needed

## Next Steps

Once WSL instances are properly configured, proceed to:
- [05-SSH-Authentication.md](05-SSH-Authentication.md) - SSH keys, credential setup

## Verification Checklist

Before proceeding to SSH authentication, verify:

- [ ] Ubuntu-24.04 SSH service is running on port 2223
- [ ] Kali-Linux SSH service is running on port 2224
- [ ] Both instances have hostname resolution configured
- [ ] Passwordless sudo is working for daniv user
- [ ] SSH services are enabled and will start on boot
- [ ] Network connectivity is working from AWX host
- [ ] SSH ports are accessible and responding
- [ ] No firewall blocking SSH connections
- [ ] Both WSL instances are running and accessible
