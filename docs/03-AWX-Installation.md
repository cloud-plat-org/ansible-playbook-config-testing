# AWX Installation - Operator & Instance Deployment

## Overview
This document covers the installation of the AWX Operator, deployment of AWX instance, HTTPS ingress configuration, and AWX CLI setup.

## AWX Operator Installation

### 1. Clone AWX Operator Repository
```bash
cd ~
git clone https://github.com/ansible/awx-operator.git
cd awx-operator

# Checkout stable version
git checkout 2.19.1
```

### 2. Deploy AWX Operator
```bash
# Set namespace
export NAMESPACE=awx

# Create namespace
kubectl create namespace $NAMESPACE

# Deploy operator
make deploy
```

### 3. Verify Operator Installation
```bash
# Check operator pods
kubectl get pods -n awx

# Expected: awx-operator-controller-manager should be Running
kubectl get pods -n awx-operator-system
```

## AWX Instance Deployment

### 1. Create AWX Deployment Configuration
```bash
# Create AWX deployment file
cat > awx-deploy.yml << 'EOF'
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx
spec:
  service_type: nodeport
  ingress_type: none
EOF
```

### 2. Deploy AWX Instance
```bash
# Apply AWX deployment
kubectl apply -f awx-deploy.yml -n awx

# Monitor deployment progress
kubectl get pods -n awx -w
```

### 3. Wait for AWX Pods to be Ready
```bash
# Check pod status
kubectl get pods -n awx

# Expected pods:
# - awx-migration-* (Completed)
# - awx-operator-controller-manager-* (Running)
# - awx-postgres-* (Running)
# - awx-task-* (Running)
# - awx-web-* (Running)
```

## HTTPS Ingress Configuration

### 1. Create TLS Certificate
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -out awx-ingress.crt \
  -keyout awx-ingress.key \
  -subj "/CN=localhost/O=awx-ingress"

# Verify certificate
openssl x509 -in awx-ingress.crt -text -noout
```

### 2. Create Kubernetes TLS Secret
```bash
# Create TLS secret
kubectl create secret tls awx-ingress-tls \
  --namespace awx \
  --key awx-ingress.key \
  --cert awx-ingress.crt

# Verify secret
kubectl get secret awx-ingress-tls -n awx
```

### 3. Create Ingress Resource
```bash
# Create ingress configuration
cat > awx-ingress.yml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: awx-ingress
  namespace: awx
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - localhost
    secretName: awx-ingress-tls
  rules:
  - host: localhost
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: awx-service
            port:
              number: 80
EOF

# Apply ingress
kubectl apply -f awx-ingress.yml
```

### 4. Verify Ingress Configuration
```bash
# Check ingress status
kubectl get ingress -n awx

# Check ingress controller
kubectl get pods -n ingress-nginx
```

## AWX CLI Setup and Testing

### 1. Install AWX CLI
```bash
# Activate virtual environment
source ~/awx-venv/bin/activate

# Install AWX CLI
pip install awxkit

# Verify installation
awx --version
```

### 2. Get AWX Admin Password
```bash
# Retrieve admin password
kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d

# Save password for later use
export AWX_PASSWORD=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)
echo "AWX Admin Password: $AWX_PASSWORD"
```

### 3. Test AWX CLI Access
```bash
# Set AWX token
export AWX_TOKEN=$AWX_PASSWORD

# Test CLI connection
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me

# Expected: User information should be displayed
```

### 4. Test Web UI Access
```bash
# Test web access
curl -k https://localhost

# Expected: AWX login page HTML
```

## Service Configuration

### 1. Check AWX Services
```bash
# List all AWX services
kubectl get svc -n awx

# Expected services:
# - awx-service (NodePort)
# - awx-postgres-15 (ClusterIP)
# - awx-operator-controller-manager-metrics-service (ClusterIP)
```

### 2. Port Forwarding (Alternative Access)
```bash
# If ingress is not working, use port forwarding
kubectl port-forward svc/awx-service -n awx 443:80

# Access via: https://localhost:443
```

## Verification and Testing

### 1. Complete AWX Status Check
```bash
echo "=== AWX Pods Status ==="
kubectl get pods -n awx

echo "=== AWX Services ==="
kubectl get svc -n awx

echo "=== AWX Ingress ==="
kubectl get ingress -n awx

echo "=== AWX CLI Test ==="
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me
```

### 2. Web UI Access Test
```bash
# Test HTTPS access
curl -k -I https://localhost

# Expected: HTTP/2 200 or similar success response
```

## Troubleshooting AWX Installation

### Common Issues

#### AWX Pods Not Starting
```bash
# Check pod logs
kubectl logs -n awx awx-task-<pod-id>
kubectl logs -n awx awx-web-<pod-id>

# Check pod events
kubectl describe pod -n awx <pod-name>

# Restart problematic pods
kubectl delete pod -n awx <pod-name>
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
kubectl get pods -n awx | grep postgres
kubectl logs -n awx awx-postgres-15-0

# Check database connectivity
kubectl exec -n awx awx-task-<pod-id> -- psql -h awx-postgres-15 -U awx
```

#### Ingress Not Working
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress status
kubectl describe ingress -n awx awx-ingress

# Verify TLS secret
kubectl get secret awx-ingress-tls -n awx
```

#### CLI Authentication Issues
```bash
# Verify token
echo $AWX_TOKEN

# Test with verbose output
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" --conf.debug me

# Check AWX service status
kubectl get svc -n awx awx-service
```

## Performance Optimization

### 1. Resource Allocation
```bash
# Check resource usage
kubectl top pods -n awx

# Adjust resources if needed in awx-deploy.yml
```

### 2. Database Optimization
```bash
# Check PostgreSQL performance
kubectl exec -n awx awx-postgres-15-0 -- psql -U awx -c "SELECT * FROM pg_stat_activity;"
```

## Next Steps

Once AWX is properly installed and accessible, proceed to:
- [04-WSL-Configuration.md](04-WSL-Configuration.md) - Target WSL instances setup

## Verification Checklist

Before proceeding to WSL configuration, verify:

- [ ] AWX Operator is deployed and running
- [ ] AWX instance pods are all Running
- [ ] HTTPS ingress is configured and working
- [ ] AWX CLI is installed and can connect
- [ ] Web UI is accessible at https://localhost
- [ ] Admin password is retrieved and working
- [ ] All services are properly exposed
- [ ] Database is running and accessible
- [ ] No critical errors in pod logs
