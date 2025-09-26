# AWX Installation - Operator & Instance Deployment

## Overview
This document covers the installation of the AWX Operator, deployment of AWX instance, and HTTPS ingress configuration.

## AWX Operator Installation

### 1. Clone and Deploy AWX Operator
```bash
cd ~
git clone https://github.com/ansible/awx-operator.git
cd awx-operator
git checkout 2.19.1

# Deploy operator
export NAMESPACE=awx
kubectl create namespace $NAMESPACE
make deploy
```

### 2. Verify Operator Installation
```bash
kubectl get pods -n awx-operator-system
# Expected: awx-operator-controller-manager should be Running
```

## AWX Instance Deployment

### 1. Create and Deploy AWX Instance
```bash
# Create AWX deployment
cat > awx-deploy.yml << 'EOF'
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx
spec:
  service_type: nodeport
  ingress_type: none
EOF

# Deploy AWX
kubectl apply -f awx-deploy.yml -n awx
kubectl get pods -n awx -w
```

### 2. Wait for AWX Pods to be Ready
```bash
kubectl get pods -n awx
# Expected: awx-migration-* (Completed), awx-postgres-* (Running), awx-task-* (Running), awx-web-* (Running)
```

## HTTPS Ingress Configuration

### 1. Create TLS Certificate and Secret
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -out awx-ingress.crt -keyout awx-ingress.key \
  -subj "/CN=localhost/O=awx-ingress"

# Create TLS secret
kubectl create secret tls awx-ingress-tls \
  --namespace awx --key awx-ingress.key --cert awx-ingress.crt
```

### 2. Create Ingress Resource
```bash
# Apply the existing ingress configuration (awx-ingress.yml)
kubect
```

## AWX CLI Setup

### 1. Install AWX CLI
```bash
source ~/awx-venv/bin/activate
pip install awxkit
awx --version
```

### 2. Get Admin Password and Set Token
```bash
# Get admin password
export AWX_PASSWORD=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# Generate OAuth2 token (valid for ~1 year)
export AWX_TOKEN=$(awx --conf.host https://localhost -k --conf.username admin --conf.password "$AWX_PASSWORD" login -f json | jq -r .token)

# Test CLI connection
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me
```

## Verification

### Complete Status Check
```bash
echo "=== AWX Status ==="
kubectl get pods,svc,ingress -n awx
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me
curl -k -I https://localhost
```

## Next Steps

Once AWX is properly installed and accessible, proceed to:
- [04-SSH-Authentication.md](04-SSH-Authentication.md) - SSH keys, credential setup

## Verification Checklist

Before proceeding to SSH authentication, verify:
- [ ] AWX Operator is deployed and running
- [ ] AWX instance pods are all Running
- [ ] HTTPS ingress is configured and working
- [ ] AWX CLI is installed and can connect
- [ ] Web UI is accessible at https://localhost
- [ ] Admin password is retrieved and working