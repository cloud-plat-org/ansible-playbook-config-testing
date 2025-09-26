# Infrastructure Setup - Docker, Minikube & Tools Installation

## Overview
This document covers the installation and configuration of Docker Desktop, Minikube, and required tools for AWX setup.

## Docker Desktop Setup

### Start Docker Desktop
```bash
# From WSL Ubuntu (ubuntuAWX)
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &

# Wait for Docker to be fully running (system tray icon stops spinning)
```

### Verify Docker Installation
```bash
# Check Docker version and functionality
docker --version
docker ps
```

### Docker Desktop Configuration
Ensure Docker Desktop is configured for WSL2:
- Open Docker Desktop settings
- Go to "Resources" -> "WSL Integration"
- Enable integration with Ubuntu-22.04
- Apply & Restart

## Minikube Installation and Configuration

### Start Minikube
```bash
# Start Minikube with adequate resources
minikube start

# Verify cluster status
minikube status
```

Expected output:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

### Verify Kubernetes Cluster
```bash
# Check cluster nodes and pods
kubectl get nodes
kubectl get pods -A
```

### Enable Minikube Addons
```bash
# Enable ingress addon
minikube addons enable ingress

# Verify ingress is running
kubectl get pods -n ingress-nginx
```

## Network and Tunnel Setup

### Start Minikube Tunnel
```bash
# In a separate terminal, keep this running
minikube tunnel

# Keep this terminal open and running
# This enables LoadBalancer services to work at localhost
```

### Verify Network Configuration
```bash
# Check Minikube IP and services
minikube ip
kubectl get svc -A

# Test connectivity
curl -k https://localhost
```

## Required Tools Installation

### Install Additional Tools
```bash
# Install additional required packages
sudo apt install -y curl wget git vim jq openssl ca-certificates
```

### Python Environment Setup
```bash
# Create virtual environment for AWX CLI
python3 -m venv ~/awx-venv
source ~/awx-venv/bin/activate

# Install AWX CLI
pip install awxkit

# Verify installation
awx --version
```

## Verification Steps

### Complete System Check
```bash
# Check all components
echo "=== Docker Status ==="
docker --version
docker ps

echo "=== Minikube Status ==="
minikube status

echo "=== Kubernetes Status ==="
kubectl get nodes
kubectl get pods -A | grep -E "(Running|Completed)"

echo "=== Tools Status ==="
kubectl version --client
jq --version
git --version
python3 --version

echo "=== AWX Service Status ==="
kubectl get svc -n awx

echo "=== Connectivity Test ==="
curl -k https://localhost
```

## Configuration Files

### kubectl Configuration
```bash
# Check kubectl configuration
kubectl config view
kubectl config current-context
# Should show: minikube
```

### Minikube Configuration
```bash
# Check Minikube configuration
minikube config view

# Set additional configurations if needed
minikube config set memory 8192
minikube config set cpus 4
```

## Troubleshooting

### Common Problems
- **Docker Desktop Not Starting**: Restart from Windows or use the command above
- **Minikube Start Failures**: Check logs with `minikube logs`, delete and recreate if needed
- **Kubernetes Pod Issues**: Check pod status with `kubectl get pods -A`
- **Network Connectivity Issues**: Ensure `minikube tunnel` is running

### Performance Optimization
```bash
# Increase Minikube resources if available
minikube config set memory 16384
minikube config set cpus 6
minikube stop
minikube start
```

## Verification Checklist

Before proceeding to AWX installation, verify:
- [ ] Docker Desktop is running and accessible
- [ ] Minikube is running with proper resources
- [ ] Kubernetes cluster is healthy (all pods Running)
- [ ] Ingress addon is enabled and running
- [ ] Minikube tunnel is running in separate terminal
- [ ] All required tools are installed
- [ ] Python virtual environment is created
- [ ] AWX CLI is installed in virtual environment
- [ ] Network connectivity is working

## Next Steps

Once infrastructure is properly set up, proceed to:
- [03-AWX-Installation.md](03-AWX-Installation.md) - AWX operator, deployment, HTTPS
