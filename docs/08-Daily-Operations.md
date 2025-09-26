# Daily Operations - Startup Scripts & Maintenance

## Overview
This document covers daily startup workflows, automation scripts, and maintenance procedures for the AWX setup.

## Daily Startup Workflow

### 1. Manual Startup Steps
```bash
# 1. Start Docker Desktop
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &

# 2. Wait for Docker to be ready
sleep 30
docker ps

# 3. Start Minikube
minikube start
minikube tunnel &  # In separate terminal

# 4. Check AWX status
kubectl get pods -n awx

# 5. Activate AWX environment
source ~/awx-venv/bin/activate
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# 6. Test AWX access
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me
```

### 2. Automated Startup Script
```bash
# Create comprehensive startup script
cat > ~/start_awx.sh << 'EOF'
#!/bin/bash

echo "=== AWX Startup Script ==="

# Start Docker Desktop
echo "1. Starting Docker Desktop..."
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &
sleep 30

# Start Minikube
echo "2. Starting Minikube..."
minikube start --driver=docker --cpus=4 --memory=8g --addons=ingress
minikube tunnel &

# Check AWX pods
echo "3. Checking AWX pods..."
kubectl get pods -n awx

# Setup AWX environment
echo "4. Setting up AWX environment..."
source ~/awx-venv/bin/activate
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# Test AWX access
echo "5. Testing AWX access..."
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me

echo "=== AWX Startup Complete ==="
echo "Web UI: https://localhost"
echo "CLI: awx --conf.host https://localhost -k --conf.token \"\$AWX_TOKEN\""
EOF

chmod +x ~/start_awx.sh
```

### 3. Status Check Script
```bash
# Create status check script
cat > ~/check_awx_status.sh << 'EOF'
#!/bin/bash

echo "=== AWX Status Check ==="

# Check Docker
echo "1. Docker Status:"
if docker ps >/dev/null 2>&1; then
    echo "   [OK] Docker is running"
else
    echo "   [ERROR] Docker is not running"
fi

# Check Minikube
echo "2. Minikube Status:"
if minikube status >/dev/null 2>&1; then
    echo "   [OK] Minikube is running"
else
    echo "   [ERROR] Minikube is not running"
fi

# Check AWX pods
echo "3. AWX Pods Status:"
kubectl get pods -n awx

# Check AWX access
echo "4. AWX Access Status:"
if [ -f ~/awx-venv/bin/activate ]; then
    source ~/awx-venv/bin/activate
    export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d 2>/dev/null)
    if awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me >/dev/null 2>&1; then
        echo "   [OK] AWX CLI access working"
    else
        echo "   [ERROR] AWX CLI access failed"
    fi
else
    echo "   [ERROR] AWX virtual environment not found"
fi

echo "=== Status Check Complete ==="
EOF

chmod +x ~/check_awx_status.sh
```

## Maintenance Procedures

### 1. Regular Maintenance
```bash
# Create maintenance script
cat > ~/awx_maintenance.sh << 'EOF'
#!/bin/bash

echo "=== AWX Maintenance Script ==="

# Update system packages
echo "1. Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Clean up Docker
echo "2. Cleaning up Docker..."
docker system prune -f

# Clean up Minikube
echo "3. Cleaning up Minikube..."
minikube ssh -- docker system prune -f

# Check disk space
echo "4. Checking disk space..."
df -h

# Check memory usage
echo "5. Checking memory usage..."
free -h

echo "=== Maintenance Complete ==="
EOF

chmod +x ~/awx_maintenance.sh
```

### 2. Backup Procedures
```bash
# Create backup script
cat > ~/awx_backup.sh << 'EOF'
#!/bin/bash

echo "=== AWX Backup Script ==="

BACKUP_DIR="$HOME/awx_backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup AWX configuration
echo "1. Backing up AWX configuration..."
kubectl get awx -n awx -o yaml > "$BACKUP_DIR/awx-config.yaml"
kubectl get secret awx-admin-password -n awx -o yaml > "$BACKUP_DIR/awx-admin-password.yaml"

# Backup SSH keys
echo "2. Backing up SSH keys..."
cp ~/.ssh/awx_wsl_key_traditional* "$BACKUP_DIR/"

# Backup playbooks
echo "3. Backing up playbooks..."
cp ~/ansible/test2/*.yml "$BACKUP_DIR/" 2>/dev/null || true

# Create backup archive
echo "4. Creating backup archive..."
cd "$HOME/awx_backups"
tar -czf "$(basename "$BACKUP_DIR").tar.gz" "$(basename "$BACKUP_DIR")"
rm -rf "$BACKUP_DIR"

echo "Backup created: $HOME/awx_backups/$(basename "$BACKUP_DIR").tar.gz"
echo "=== Backup Complete ==="
EOF

chmod +x ~/awx_backup.sh
```

## Monitoring and Health Checks

### 1. Health Check Script
```bash
# Create health check script
cat > ~/awx_health_check.sh << 'EOF'
#!/bin/bash

echo "=== AWX Health Check ==="

HEALTH_STATUS="HEALTHY"
ISSUES=()

# Check Docker
if ! docker ps >/dev/null 2>&1; then
    HEALTH_STATUS="UNHEALTHY"
    ISSUES+=("Docker is not running")
fi

# Check Minikube
if ! minikube status | grep -q "Running"; then
    HEALTH_STATUS="UNHEALTHY"
    ISSUES+=("Minikube is not running")
fi

# Check AWX pods
if ! kubectl get pods -n awx | grep -q "Running"; then
    HEALTH_STATUS="UNHEALTHY"
    ISSUES+=("AWX pods are not running")
fi

# Check AWX access
if [ -f ~/awx-venv/bin/activate ]; then
    source ~/awx-venv/bin/activate
    export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d 2>/dev/null)
    if ! awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me >/dev/null 2>&1; then
        HEALTH_STATUS="UNHEALTHY"
        ISSUES+=("AWX CLI access failed")
    fi
else
    HEALTH_STATUS="UNHEALTHY"
    ISSUES+=("AWX virtual environment not found")
fi

# Report status
echo "Overall Status: $HEALTH_STATUS"

if [ ${#ISSUES[@]} -gt 0 ]; then
    echo "Issues found:"
    for issue in "${ISSUES[@]}"; do
        echo "  - $issue"
    done
else
    echo "All systems are healthy!"
fi

echo "=== Health Check Complete ==="
EOF

chmod +x ~/awx_health_check.sh
```

## Automation Scripts

### 1. Automated Job Execution
```bash
# Create automated job script
cat > ~/run_awx_job.sh << 'EOF'
#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <job_template_name> [extra_vars]"
    echo "Available job templates:"
    source ~/awx-venv/bin/activate
    export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)
    awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template list | jq '.results[] | .name'
    exit 1
fi

JOB_TEMPLATE="$1"
EXTRA_VARS="${2:-{}}"

echo "=== Running AWX Job ==="
echo "Job Template: $JOB_TEMPLATE"
echo "Extra Vars: $EXTRA_VARS"

# Activate environment
source ~/awx-venv/bin/activate
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# Launch job
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "$JOB_TEMPLATE" --extra_vars "$EXTRA_VARS" | jq -r .id)

echo "Job ID: $JOB_ID"

# Monitor job
echo "Monitoring job execution..."
while true; do
    STATUS=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq -r .status)
    echo "Job Status: $STATUS"
    
    if [ "$STATUS" = "successful" ] || [ "$STATUS" = "failed" ] || [ "$STATUS" = "error" ]; then
        break
    fi
    
    sleep 5
done

# Show job output
echo "Job Output:"
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"

echo "=== Job Complete ==="
EOF

chmod +x ~/run_awx_job.sh
```

## Next Steps

Once daily operations are set up, proceed to:
- [09-Troubleshooting.md](09-Troubleshooting.md) - Common issues and solutions

## Verification Checklist

Before proceeding to troubleshooting, verify:
- [ ] Startup scripts are created and working
- [ ] Status check scripts are functional
- [ ] Maintenance procedures are documented
- [ ] Backup procedures are tested
- [ ] Health check scripts are working
- [ ] Automation scripts are functional
- [ ] All scripts have proper permissions
- [ ] Documentation is complete and up-to-date