# Infrastructure Setup - Docker, Minikube & Tools Installation

## Overview
This document covers the installation and configuration of Docker Desktop, Minikube, and all required tools for the AWX setup.

## Docker Desktop Setup

### 1. Start Docker Desktop
```bash
# From WSL Ubuntu (ubuntuAWX)
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &

# Or start from Windows Start menu
# Wait for Docker to be fully running (system tray icon stops spinning)
```

### 2. Verify Docker Installation
```bash
# Check Docker version
docker --version

# Test Docker functionality
docker ps

# Expected output: Empty container list (no errors)
```

### 3. Docker Desktop Configuration
Ensure Docker Desktop is configured for WSL2:
- Open Docker Desktop settings
- Go to "Resources" -> "WSL Integration"
- Enable integration with Ubuntu-22.04
- Apply & Restart

## Minikube Installation and Configuration

### 1. Start Minikube with Proper Resources
```bash
# Start Minikube with adequate resources
minikube start --driver=docker --cpus=4 --memory=8g --addons=ingress

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

### 2. Verify Kubernetes Cluster
```bash
# Check cluster nodes
kubectl get nodes

# Check all pods
kubectl get pods -A

# Expected: All system pods should be Running
```

### 3. Enable Minikube Addons
```bash
# List available addons
minikube addons list

# Enable ingress addon (if not already enabled)
minikube addons enable ingress

# Verify ingress is running
kubectl get pods -n ingress-nginx
```

## Network and Tunnel Setup

### 1. Start Minikube Tunnel
```bash
# In a separate terminal, keep this running
minikube tunnel

# Keep this terminal open and running
# This enables LoadBalancer services to work at localhost
```

### 2. Verify Network Configuration
```bash
# Check Minikube IP
minikube ip

# Check services
kubectl get svc -A

# Test connectivity
curl -k https://$(minikube ip)
```

## Required Tools Installation

### 1. Install Additional Tools
```bash
# Install additional required packages
sudo apt install -y curl wget git vim jq openssl ca-certificates

# Verify installations
curl --version
wget --version
git --version
vim --version
jq --version
openssl version
```

### 2. Python Environment Setup
```bash
# Install Python development tools
sudo apt install -y python3-dev python3-pip python3-venv

# Create virtual environment for AWX CLI
python3 -m venv ~/awx-venv

### 3. Install AWX CLI
```bash
# Ensure virtual environment is activated
source ~/awx-venv/bin/activate

# Install AWX CLI
pip install awxkit

# Verify installation
awx --version
```

## Verification Steps

### 1. Complete System Check
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
```

### 2. Network Connectivity Test
```bash
# Test local connectivity
curl -k https://localhost

# Test Minikube connectivity
curl -k https://$(minikube ip)

# Check if tunnel is working
kubectl get svc -A | grep LoadBalancer
```

## Configuration Files

### 1. kubectl Configuration
```bash
# Check kubectl configuration
kubectl config view

# Verify current context
kubectl config current-context

# Should show: minikube
```

### 2. Minikube Configuration
```bash
# Check Minikube configuration
minikube config view

# Set additional configurations if needed
minikube config set memory 8192
minikube config set cpus 4
```

## Troubleshooting Infrastructure Issues

### Common Problems

#### Docker Desktop Not Starting
```bash
# Check if Docker Desktop process is running
ps aux | grep -i docker

# Restart Docker Desktop
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &

# Wait and verify
sleep 30
docker ps
```

#### Minikube Start Failures
```bash
# Check Minikube logs
minikube logs

# Delete and recreate Minikube
minikube delete
minikube start --driver=docker --cpus=4 --memory=8g --addons=ingress
```

#### Kubernetes Pod Issues
```bash
# Check pod status
kubectl get pods -A

# Check pod logs for failed pods
kubectl logs -n kube-system <pod-name>

# Restart Minikube if needed
minikube stop
minikube start
```

#### Network Connectivity Issues
```bash
# Check if tunnel is running
ps aux | grep "minikube tunnel"

# Restart tunnel
minikube tunnel &

# Check firewall settings
sudo ufw status
```

## Performance Optimization

### 1. Resource Allocation
```bash
# Increase Minikube resources if available
minikube config set memory 16384
minikube config set cpus 6

# Restart Minikube with new resources
minikube stop
minikube start
```

### 2. Docker Resource Settings
- Open Docker Desktop settings
- Go to "Resources" -> "Advanced"
- Increase Memory to 8GB+ (if available)
- Increase CPUs to 4+ (if available)

## Next Steps

Once infrastructure is properly set up, proceed to:
- [03-AWX-Installation.md](03-AWX-Installation.md) - AWX operator, deployment, HTTPS

## Verification Checklist

Before proceeding to AWX installation, verify:

- [ ] Docker Desktop is running and accessible
- [ ] Minikube is running with proper resources
- [ ] Kubernetes cluster is healthy (all pods Running)
- [ ] Ingress addon is enabled and running
- [ ] Minikube tunnel is running in separate terminal
- [ ] All required tools are installed (kubectl, jq, git, etc.)
- [ ] Python virtual environment is created
- [ ] AWX CLI is installed in virtual environment
- [ ] Network connectivity is working
- [ ] kubectl can communicate with cluster
