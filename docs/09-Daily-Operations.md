# Daily Operations - Startup Scripts & Maintenance

## Overview
This document covers daily startup workflows, automation scripts, maintenance procedures, and monitoring for the AWX setup.

## Daily Startup Workflow

### 1. Manual Startup Steps
```bash
# 1. Start Docker Desktop
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &

# 2. Wait for Docker to be ready
sleep 30
docker ps

# 3. Start Minikube\
minikube status
minikube start
minikube tunnel &  # In separate terminal

# 4. Check AWX status
minikube start
minikube tunnel 

# 5. Set up port forwarding (if needed)
kubectl port-forward svc/awx-service -n awx 443:80

# 6. Activate AWX environment
source ~/awx-venv/bin/activate

# Extract stored OAuth2 token (no regeneration needed - valid for ~1 year)
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# 7. Test AWX access
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me
```

### 2. Automated Startup Script
```bash
# Create comprehensive startup script
cat > ~/start_awx.sh << 'EOF'
#!/bin/bash

echo "=== AWX Startup Script ==="
echo "Starting AWX environment..."

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local service_name="$1"
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for $service_name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if eval "$2"; then
            echo "$service_name is ready!"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts - waiting..."
        sleep 10
        ((attempt++))
    done
    
    echo "ERROR: $service_name failed to start after $max_attempts attempts"
    return 1
}

# Start Docker Desktop
echo "1. Starting Docker Desktop..."
if [ -f "/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" ]; then
    "/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &
    wait_for_service "Docker Desktop" "docker ps >/dev/null 2>&1"
else
    echo "ERROR: Docker Desktop not found. Please start manually."
    exit 1
fi

# Start Minikube
echo "2. Starting Minikube..."
if command_exists minikube; then
    minikube start --driver=docker --cpus=4 --memory=8g --addons=ingress
    wait_for_service "Minikube" "minikube status | grep -q 'Running'"
else
    echo "ERROR: Minikube not found. Please install Minikube."
    exit 1
fi

# Start Minikube tunnel
echo "3. Starting Minikube tunnel..."
minikube tunnel &
TUNNEL_PID=$!
echo "Minikube tunnel started with PID: $TUNNEL_PID"

# Check AWX pods
echo "4. Checking AWX pods..."
wait_for_service "AWX Pods" "kubectl get pods -n awx | grep -q 'Running'"

# Get AWX admin password
echo "5. Setting up AWX environment..."
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# Activate virtual environment
if [ -f ~/awx-venv/bin/activate ]; then
    source ~/awx-venv/bin/activate
    echo "AWX virtual environment activated"
else
    echo "ERROR: AWX virtual environment not found. Please run setup first."
    exit 1
fi

# Test AWX access
echo "6. Testing AWX access..."
if awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me >/dev/null 2>&1; then
    echo "AWX access successful!"
else
    echo "WARNING: AWX access test failed. Check configuration."
fi

echo "=== AWX Startup Complete ==="
echo "Web UI: https://localhost"
echo "CLI: awx --conf.host https://localhost -k --conf.token \"\$AWX_TOKEN\""
echo "Minikube tunnel PID: $TUNNEL_PID"
echo "To stop: kill $TUNNEL_PID && minikube stop"
EOF

# Make script executable
chmod +x ~/start_awx.sh
```

### 3. Quick Status Check Script
```bash
# Create status check script
cat > ~/check_awx_status.sh << 'EOF'
#!/bin/bash

echo "=== AWX Status Check ==="

# Check Docker
echo "1. Docker Status:"
if docker ps >/dev/null 2>&1; then
    echo "   ✓ Docker is running"
else
    echo "   ✗ Docker is not running"
fi

# Check Minikube
echo "2. Minikube Status:"
if minikube status >/dev/null 2>&1; then
    echo "   ✓ Minikube is running"
    minikube status | grep -E "(host|kubelet|apiserver)"
else
    echo "   ✗ Minikube is not running"
fi

# Check AWX pods
echo "3. AWX Pods Status:"
if kubectl get pods -n awx >/dev/null 2>&1; then
    kubectl get pods -n awx | grep -E "(Running|Completed|Error)"
else
    echo "   ✗ Cannot access AWX pods"
fi

# Check AWX services
echo "4. AWX Services Status:"
if kubectl get svc -n awx >/dev/null 2>&1; then
    kubectl get svc -n awx
else
    echo "   ✗ Cannot access AWX services"
fi

# Check AWX access
echo "5. AWX Access Status:"
if [ -f ~/awx-venv/bin/activate ]; then
    source ~/awx-venv/bin/activate
    export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d 2>/dev/null)
    if awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me >/dev/null 2>&1; then
        echo "   ✓ AWX CLI access working"
    else
        echo "   ✗ AWX CLI access failed"
    fi
else
    echo "   ✗ AWX virtual environment not found"
fi

echo "=== Status Check Complete ==="
EOF

# Make script executable
chmod +x ~/check_awx_status.sh
```

## Maintenance Procedures

### 1. Regular Maintenance Tasks
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
docker volume prune -f

# Clean up Minikube
echo "3. Cleaning up Minikube..."
minikube ssh -- docker system prune -f

# Check AWX logs for errors
echo "4. Checking AWX logs for errors..."
kubectl logs -n awx awx-task-$(kubectl get pods -n awx | grep awx-task | awk '{print $1}') --tail=100 | grep -i error

# Check disk space
echo "5. Checking disk space..."
df -h

# Check memory usage
echo "6. Checking memory usage..."
free -h

# Check AWX database size
echo "7. Checking AWX database size..."
kubectl exec -n awx awx-postgres-15-0 -- psql -U awx -c "SELECT pg_size_pretty(pg_database_size('awx'));"

echo "=== Maintenance Complete ==="
EOF

# Make script executable
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

# Backup AWX database
echo "2. Backing up AWX database..."
kubectl exec -n awx awx-postgres-15-0 -- pg_dump -U awx awx > "$BACKUP_DIR/awx-database.sql"

# Backup SSH keys
echo "3. Backing up SSH keys..."
cp ~/.ssh/awx_wsl_key_traditional* "$BACKUP_DIR/"

# Backup playbooks
echo "4. Backing up playbooks..."
cp ~/ansible/test2/*.yml "$BACKUP_DIR/" 2>/dev/null || true

# Create backup archive
echo "5. Creating backup archive..."
cd "$HOME/awx_backups"
tar -czf "$(basename "$BACKUP_DIR").tar.gz" "$(basename "$BACKUP_DIR")"
rm -rf "$BACKUP_DIR"

echo "Backup created: $HOME/awx_backups/$(basename "$BACKUP_DIR").tar.gz"
echo "=== Backup Complete ==="
EOF

# Make script executable
chmod +x ~/awx_backup.sh
```

### 3. Restore Procedures
```bash
# Create restore script
cat > ~/awx_restore.sh << 'EOF'
#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    echo "Available backups:"
    ls -la ~/awx_backups/*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="$HOME/awx_restore_$(date +%Y%m%d_%H%M%S)"

echo "=== AWX Restore Script ==="
echo "Restoring from: $BACKUP_FILE"

# Extract backup
echo "1. Extracting backup..."
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

# Restore AWX configuration
echo "2. Restoring AWX configuration..."
kubectl apply -f "$RESTORE_DIR"/*/awx-config.yaml
kubectl apply -f "$RESTORE_DIR"/*/awx-admin-password.yaml

# Restore AWX database
echo "3. Restoring AWX database..."
kubectl exec -n awx awx-postgres-15-0 -- psql -U awx -c "DROP DATABASE IF EXISTS awx;"
kubectl exec -n awx awx-postgres-15-0 -- psql -U awx -c "CREATE DATABASE awx;"
kubectl exec -i -n awx awx-postgres-15-0 -- psql -U awx awx < "$RESTORE_DIR"/*/awx-database.sql

# Restore SSH keys
echo "4. Restoring SSH keys..."
cp "$RESTORE_DIR"/*/awx_wsl_key_traditional* ~/.ssh/
chmod 600 ~/.ssh/awx_wsl_key_traditional
chmod 644 ~/.ssh/awx_wsl_key_traditional.pub

# Restore playbooks
echo "5. Restoring playbooks..."
cp "$RESTORE_DIR"/*/*.yml ~/ansible/test2/ 2>/dev/null || true

# Clean up
rm -rf "$RESTORE_DIR"

echo "=== Restore Complete ==="
EOF

# Make script executable
chmod +x ~/awx_restore.sh
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

# Check AWX services
if ! kubectl get svc -n awx awx-service >/dev/null 2>&1; then
    HEALTH_STATUS="UNHEALTHY"
    ISSUES+=("AWX service is not available")
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

# Check WSL instances
if ! ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "echo test" >/dev/null 2>&1; then
    HEALTH_STATUS="UNHEALTHY"
    ISSUES+=("Ubuntu WSL instance not accessible")
fi

if ! ssh -i ~/.ssh/awx_wsl_key_traditional -p 2224 daniv@172.22.192.129 "echo test" >/dev/null 2>&1; then
    HEALTH_STATUS="UNHEALTHY"
    ISSUES+=("Kali WSL instance not accessible")
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

# Make script executable
chmod +x ~/awx_health_check.sh
```

### 2. Log Monitoring
```bash
# Create log monitoring script
cat > ~/awx_log_monitor.sh << 'EOF'
#!/bin/bash

echo "=== AWX Log Monitor ==="

# Monitor AWX task logs
echo "1. AWX Task Logs (last 50 lines):"
kubectl logs -n awx awx-task-$(kubectl get pods -n awx | grep awx-task | awk '{print $1}') --tail=50

echo ""
echo "2. AWX Web Logs (last 50 lines):"
kubectl logs -n awx awx-web-$(kubectl get pods -n awx | grep awx-web | awk '{print $1}') --tail=50

echo ""
echo "3. AWX Operator Logs (last 50 lines):"
kubectl logs -n awx awx-operator-controller-manager-$(kubectl get pods -n awx | grep awx-operator | awk '{print $1}') --tail=50

echo ""
echo "4. Recent Events:"
kubectl get events -n awx --sort-by='.lastTimestamp' | tail -10

echo "=== Log Monitor Complete ==="
EOF

# Make script executable
chmod +x ~/awx_log_monitor.sh
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

# Make script executable
chmod +x ~/run_awx_job.sh
```

### 2. Scheduled Maintenance
```bash
# Create scheduled maintenance script
cat > ~/scheduled_maintenance.sh << 'EOF'
#!/bin/bash

echo "=== Scheduled AWX Maintenance ==="
echo "Date: $(date)"

# Run health check
echo "1. Running health check..."
~/awx_health_check.sh

# Run maintenance
echo "2. Running maintenance..."
~/awx_maintenance.sh

# Create backup
echo "3. Creating backup..."
~/awx_backup.sh

echo "=== Scheduled Maintenance Complete ==="
EOF

# Make script executable
chmod +x ~/scheduled_maintenance.sh

# Add to crontab (run daily at 2 AM)
# crontab -e
# Add: 0 2 * * * ~/scheduled_maintenance.sh >> ~/awx_maintenance.log 2>&1
```

## Next Steps

Once daily operations are set up, proceed to:
- [10-Troubleshooting.md](10-Troubleshooting.md) - Common issues and solutions

## Verification Checklist

Before proceeding to troubleshooting, verify:

- [ ] Startup scripts are created and working
- [ ] Status check scripts are functional
- [ ] Maintenance procedures are documented
- [ ] Backup and restore procedures are tested
- [ ] Health check scripts are working
- [ ] Log monitoring is set up
- [ ] Automation scripts are functional
- [ ] Scheduled maintenance is configured
- [ ] All scripts have proper permissions
- [ ] Documentation is complete and up-to-date
