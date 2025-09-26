# Prerequisites - System Requirements & WSL Configuration

## Overview
This document outlines system requirements, software prerequisites, and WSL instance configuration needed for AWX setup on Minikube.

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

# Expected output:
#  NAME              STATE           VERSION
#  Ubuntu            Running         2
#  docker-desktop    Running         2
#  Ubuntu-24.04      Running         2
#  kali-linux        Running         2
```

## Required Tools Installation

### Core Tools
```bash
# Update system and install essential packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git vim jq openssl python3 python3-pip python3-venv
```

### kubectl Installation
```bash
# Download and install kubectl
curl -LO "https://dl.k8s.io/release/v1.30.1/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client
```

### Minikube Installation
```bash
# Download and install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube version
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

### Automated Setup (Recommended)
Use the automated setup script for each WSL instance:

```bash
# For each WSL instance, run:
python3 ssh_config.py <hostname> <port>

# Examples:
# For wslubuntu1: python3 ssh_config.py wslubuntu1 2223
# For wslkali1: python3 ssh_config.py wslkali1 2224
```

This script will:
- Install SSH server
- Configure hostname and SSH port
- Set up passwordless sudo
- Enable and start SSH service

### Manual Configuration (Alternative)
If you prefer manual configuration:

```bash
# Connect to WSL instance
wsl -d Ubuntu-24.04  # or kali-linux

# Configure SSH service
sudo vim /etc/ssh/sshd_config
# Add: Port 2223 (or 2224), ListenAddress 0.0.0.0

# Configure hostname
echo "127.0.1.1 wslubuntu1" | sudo tee -a /etc/hosts

# Configure passwordless sudo
echo "daniv ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/daniv-nopasswd

# Start SSH service
sudo systemctl enable ssh
sudo systemctl restart ssh

# Exit instance
exit
```

## Network Configuration

### WSL Network Requirements
- SSH service running on target WSL instances
- Custom ports configured:
  - Ubuntu-24.04: Port 2223
  - Kali-Linux: Port 2224
- Username: `daniv` (consistent across all instances)
- Passwordless sudo configured

### Network Connectivity Verification
```bash
# Test SSH access from AWX host
ssh -p 2223 daniv@172.22.192.129
ssh -p 2224 daniv@172.22.192.129

# Test port connectivity
nc -zv 172.22.192.129 2223
nc -zv 172.22.192.129 2224
```

## Verification Checklist

Before proceeding to infrastructure setup, verify:

### System Requirements
- [ ] Docker Desktop is installed and running
- [ ] WSL2 instances are running (Ubuntu-22.04, Ubuntu-24.04, Kali-Linux)
- [ ] kubectl is installed and working
- [ ] Minikube is installed
- [ ] Python 3 and pip are available
- [ ] Essential tools (jq, git, openssl) are installed

### WSL Configuration
- [ ] Ubuntu-24.04 SSH service is running on port 2223
- [ ] Kali-Linux SSH service is running on port 2224
- [ ] Both instances have hostname resolution configured
- [ ] Passwordless sudo is working for daniv user
- [ ] SSH services are enabled and will start on boot
- [ ] Network connectivity is working from AWX host

## Troubleshooting

### Common Issues
- **Docker Desktop Not Starting**: Start manually from Windows
- **WSL Instances Not Running**: Use `wsl -d <instance-name>` to start
- **SSH Service Not Starting**: Check configuration with `sudo sshd -t`
- **Port Already in Use**: Check with `sudo netstat -tlnp | grep :<port>`

## Next Steps

Once all prerequisites are met, proceed to:
- [02-Infrastructure-Setup.md](02-Infrastructure-Setup.md) - Docker, Minikube, tools installation