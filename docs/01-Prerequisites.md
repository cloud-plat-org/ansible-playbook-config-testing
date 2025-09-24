# Prerequisites - System Requirements & WSL Configuration

## Overview
This document outlines all system requirements, software prerequisites, tools installation, and WSL instance configuration needed for the AWX setup on Minikube with WSL instances.

## Hardware Requirements

### Minimum Specifications
- **RAM**: 8+ GB (16 GB recommended)
- **CPU**: 2+ cores (4 cores recommended)
- **Storage**: 20+ GB free space
- **Network**: Stable internet connection

### Recommended Specifications
- **RAM**: 16+ GB
- **CPU**: 4+ cores
- **Storage**: 50+ GB free space (SSD recommended)
- **Network**: High-speed internet for downloading images

## Software Prerequisites

### Windows Requirements
- **Windows 10/11** with WSL2 enabled
- **Docker Desktop** installed and configured
- **WSL2** with Ubuntu-22.04 (ubuntuAWX) as primary instance

### WSL Instances Required
- **AWX Host**: WSL Ubuntu-22.04 (ubuntuAWX)
- **Target Instances**: 
  - WSL Ubuntu-24.04 (wslubuntu1)
  - WSL Kali-Linux (wslkali1)

### WSL Configuration
```bash
# Verify WSL version
wsl --list --verbose

#  NAME              STATE           VERSION
#  Ubuntu            Running         2
#  docker-desktop    Running         2
#  Ubuntu-24.04      Running         2
#  kali-linux        Running         2
```

## Required Tools Installation

### Core Tools
```bash
# Check what updates are available
sudo apt list --upgradable

# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git vim jq openssl
```

### kubectl Installation
```bash
# Download kubectl
curl -LO "https://dl.k8s.io/release/v1.30.1/bin/linux/amd64/kubectl"

# Make executable and move to PATH
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

### Minikube Installation
```bash
# Download Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Install Minikube
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify installation
minikube version
```

### Python and pip
```bash
# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

### Docker Desktop Verification
```bash
# Check if Docker Desktop is running
docker --version
docker ps

# If Docker is not running, start it
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &
```

## WSL Instance Configuration

### Ubuntu-24.04 Configuration (wslubuntu1)

#### 1. Connect to Ubuntu WSL Instance
```bash
# Connect to Ubuntu-24.04 WSL instance
wsl -d Ubuntu-24.04
```

#### 2. Configure SSH Service
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

#### 3. Add Hostname Resolution
```bash
# Add hostname to /etc/hosts
echo "127.0.1.1 wslubuntu1" | sudo tee -a /etc/hosts

# Verify hostname
hostname
# Should show: wslubuntu1
```

#### 4. Configure Passwordless Sudo

##### Option 1: Full Passwordless Sudo (Recommended for Development)
```bash
# Create sudoers file for daniv user
echo "daniv ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/daniv-nopasswd

# Verify sudoers file
sudo cat /etc/sudoers.d/daniv-nopasswd

# Test passwordless sudo
sudo whoami
# Should return: root
```

##### Option 2: Granular systemctl Permissions (More Secure)
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

#### 5. Start and Enable SSH Service
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

#### 6. Exit Ubuntu Instance
```bash
exit
```

### Kali-Linux Configuration (wslkali1)

#### 1. Connect to Kali WSL Instance
```bash
# Connect to Kali-Linux WSL instance
wsl -d kali-linux
```

#### 2. Configure SSH Service
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

#### 3. Add Hostname Resolution
```bash
# Add hostname to /etc/hosts
echo "127.0.1.1 wslkali1" | sudo tee -a /etc/hosts

# Verify hostname
hostname
# Should show: wslkali1
```

#### 4. Configure Passwordless Sudo

##### Option 1: Full Passwordless Sudo (Recommended for Development)
```bash
# Create sudoers file for daniv user
echo "daniv ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/daniv-nopasswd

# Verify sudoers file
sudo cat /etc/sudoers.d/daniv-nopasswd

# Test passwordless sudo
sudo whoami
# Should return: root
```

##### Option 2: Granular systemctl Permissions (More Secure)
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

#### 5. Start and Enable SSH Service
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

#### 6. Exit Kali Instance
```bash
exit
```

## Network Configuration

### WSL Network Configuration
```bash
# Check WSL IP addresses
ip addr show eth0

# Expected format: 172.x.x.x
# Example: 172.22.192.129
```

### SSH Service Requirements
- SSH service must be running on target WSL instances
- SSH must listen on all interfaces (0.0.0.0)
- Custom ports configured:
  - Ubuntu-24.04: Port 2223
  - Kali-Linux: Port 2224

### User Configuration
- Username: `daniv` (consistent across all instances)
- Passwordless sudo configured
- SSH key authentication enabled

### Network Connectivity Verification
```bash
# Test SSH access from AWX host
ssh -p 2223 daniv@172.22.192.129
ssh -p 2224 daniv@172.22.192.129

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

## Verification Checklist

Before proceeding to infrastructure setup, verify:

### System Requirements
- [ ] Docker Desktop is installed and running
- [ ] WSL2 instances are running (Ubuntu-22.04, Ubuntu-24.04, Kali-Linux)
- [ ] kubectl is installed and working
- [ ] Minikube is installed
- [ ] Python 3 and pip are available
- [ ] jq, git, openssl are installed
- [ ] Sufficient disk space and RAM available

### WSL Configuration
- [ ] Ubuntu-24.04 SSH service is running on port 2223
- [ ] Kali-Linux SSH service is running on port 2224
- [ ] Both instances have hostname resolution configured
- [ ] Passwordless sudo is working for daniv user
- [ ] SSH services are enabled and will start on boot
- [ ] Network connectivity is working from AWX host
- [ ] SSH ports are accessible and responding
- [ ] No firewall blocking SSH connections
- [ ] Both WSL instances are running and accessible

### Complete Configuration Check
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

## Troubleshooting

### Common Issues

#### Docker Desktop Not Starting
```bash
# Check if Docker Desktop is installed
ls "/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe"

# Start Docker Desktop manually
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &

# Wait for Docker to be fully running
docker ps
```

#### WSL Instances Not Running
```bash
# List all WSL instances
wsl --list --verbose

# Start specific instance
wsl -d Ubuntu-22.04
wsl -d Ubuntu-24.04
wsl -d kali-linux
```

#### kubectl Command Not Found
```bash
# Reinstall kubectl
curl -LO "https://dl.k8s.io/release/v1.30.1/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

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

#### Insufficient Resources
```bash
# Check available memory
free -h

# Check available disk space
df -h

# Check CPU cores
nproc
```

If resources are insufficient, consider:
- Closing unnecessary applications
- Increasing WSL memory allocation
- Using a machine with more resources

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

Once all prerequisites are met, proceed to:
- [02-Infrastructure-Setup.md](02-Infrastructure-Setup.md) - Docker, Minikube, tools installation