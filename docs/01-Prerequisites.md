# Prerequisites - System Requirements & Tools

## Overview
This document outlines all system requirements, software prerequisites, and tools needed for the AWX setup on Minikube with WSL instances.

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

## Target Environment Setup

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

## Verification Checklist

Before proceeding to infrastructure setup, verify:

- [ ] Docker Desktop is installed and running
- [ ] WSL2 instances are running (Ubuntu-22.04, Ubuntu-24.04, Kali-Linux)
- [ ] kubectl is installed and working
- [ ] Minikube is installed
- [ ] Python 3 and pip are available
- [ ] jq, git, openssl are installed
- [ ] Target WSL instances have SSH running
- [ ] Network connectivity between WSL instances
- [ ] Sufficient disk space and RAM available

## Next Steps

Once all prerequisites are met, proceed to:
- [02-Infrastructure-Setup.md](02-Infrastructure-Setup.md) - Docker, Minikube, tools installation

## Troubleshooting Prerequisites

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
