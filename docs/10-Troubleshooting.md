# Troubleshooting - Common Issues & Solutions

## Overview
This document provides comprehensive troubleshooting guidance for common issues encountered in the AWX setup, including Minikube connection issues, SSH authentication problems, AWX job failures, and network issues.

## Minikube Connection Issues

### Problem: Connection Refused Errors
```bash
# Error: dial tcp 127.0.0.1:56627: connect: connection refused
```

#### Solution Steps:
```bash
# 1. Check Minikube status
minikube status

# 2. If kubelet/apiserver stopped, restart
minikube update-context
minikube start

# 3. Verify cluster
kubectl get nodes
kubectl get pods -A
```

#### Root Causes:
- Minikube VM running but Kubernetes components stopped
- kubeconfig pointing to wrong endpoint
- Resource exhaustion causing component failures

### Problem: Minikube Start Failures
```bash
# Error: minikube start fails with resource errors
```

#### Solution Steps:
```bash
# 1. Check system resources
free -h
df -h
nproc

# 2. Increase Minikube resources
minikube config set memory 8192
minikube config set cpus 4

# 3. Delete and recreate Minikube
minikube delete
minikube start --driver=docker --cpus=4 --memory=8g --addons=ingress

# 4. Check Docker resources
# Open Docker Desktop settings → Resources → Advanced
# Increase Memory to 8GB+, CPUs to 4+
```

### Problem: Ingress Not Working
```bash
# Error: Ingress controller not responding
```

#### Solution Steps:
```bash
# 1. Check ingress addon
minikube addons list | grep ingress

# 2. Enable ingress if not enabled
minikube addons enable ingress

# 3. Check ingress controller pods
kubectl get pods -n ingress-nginx

# 4. Restart ingress controller
kubectl delete pod -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# 5. Check ingress status
kubectl get ingress -n awx
```

## SSH Authentication Problems

### Problem: Permission Denied (publickey)
```bash
# Error: Permission denied (publickey)
```

#### Solution Steps:
```bash
# 1. Check SSH key permissions
ls -la ~/.ssh/awx_wsl_key_traditional
chmod 600 ~/.ssh/awx_wsl_key_traditional

# 2. Check authorized_keys file
ssh -p 2223 daniv@172.22.192.129 "ls -la ~/.ssh/authorized_keys"

# 3. Fix permissions on target host
ssh -p 2223 daniv@172.22.192.129 "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"

# 4. Test SSH key manually
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "whoami"
```

### Problem: SSH Key Format Issues
```bash
# Error: Invalid key format
```

#### Solution Steps:
```bash
# 1. Check key format
head -1 ~/.ssh/awx_wsl_key_traditional
# Should show: -----BEGIN RSA PRIVATE KEY-----

# 2. Regenerate key if format is wrong
rm ~/.ssh/awx_wsl_key_traditional*
ssh-keygen -t rsa -b 2048 -f ~/.ssh/awx_wsl_key_traditional -N "" -m PEM

# 3. Redeploy keys
ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p 2223 daniv@172.22.192.129
ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p 2224 daniv@172.22.192.129
```

### Problem: Sudo Access Issues
```bash
# Error: sudo: a password is required
```

#### Solution Steps:
```bash
# 1. Check sudoers configuration
ssh -p 2223 daniv@172.22.192.129 "sudo cat /etc/sudoers.d/daniv-nopasswd"

# 2. Recreate sudoers file
ssh -p 2223 daniv@172.22.192.129 "echo 'daniv ALL=(ALL) NOPASSWD: ALL' | sudo tee /etc/sudoers.d/daniv-nopasswd"

# 3. Test sudo access
ssh -p 2223 daniv@172.22.192.129 "sudo whoami"
```

## AWX Job Failures

### Problem: Job Stuck in "Running" State
```bash
# Job never completes or times out
```

#### Solution Steps:
```bash
# 1. Check job details
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '{status, started, finished}'

# 2. Check AWX task pod logs
kubectl logs -n awx awx-task-$(kubectl get pods -n awx | grep awx-task | awk '{print $1}') --tail=50

# 3. Check job events
kubectl get events -n awx --sort-by='.lastTimestamp'

# 4. Restart AWX task pod
kubectl delete pod -n awx awx-task-$(kubectl get pods -n awx | grep awx-task | awk '{print $1}')

# 5. Check host connectivity
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "echo test"
```

### Problem: Host Unreachable
```bash
# Error: Host unreachable or connection timeout
```

#### Solution Steps:
```bash
# 1. Check host variables
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab" | jq '.results[] | {name, variables}'

# 2. Test SSH connectivity
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "echo test"

# 3. Check WSL instance status
wsl --list --verbose

# 4. Restart WSL instances if needed
wsl --shutdown
wsl -d Ubuntu-24.04
wsl -d kali-linux

# 5. Verify network configuration
ip addr show eth0
```

### Problem: Authentication Failures
```bash
# Error: Authentication failed
```

#### Solution Steps:
```bash
# 1. Check credential configuration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential get "$CRED_ID" | jq '.inputs'

# 2. Verify SSH key format
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential get "$CRED_ID" | jq '.inputs.ssh_key_data' | head -1

# 3. Test SSH key manually
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "sudo whoami"

# 4. Check job environment
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_env' | grep -i ssh

# 5. Recreate credential if needed
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential delete "$CRED_ID"
# Then recreate following the credential creation steps
```

## Network and Service Issues

### Problem: Port Forwarding Not Working
```bash
# Error: Port forwarding fails
```

#### Solution Steps:
```bash
# 1. Check if port is in use
netstat -tlnp | grep :443

# 2. Kill process using port
sudo kill -9 $(lsof -t -i:443)

# 3. Restart port forwarding
kubectl port-forward svc/awx-service -n awx 443:80

# 4. Test port forwarding
curl -k https://localhost:443
```

### Problem: WSL Network Issues
```bash
# Error: Cannot connect to WSL instances
```

#### Solution Steps:
```bash
# 1. Check WSL network configuration
ip addr show eth0

# 2. Check WSL instances are running
wsl --list --verbose

# 3. Restart WSL instances
wsl --shutdown
wsl -d Ubuntu-24.04
wsl -d kali-linux

# 4. Check SSH service status
wsl -d Ubuntu-24.04 -- sudo systemctl status ssh
wsl -d kali-linux -- sudo systemctl status ssh

# 5. Restart SSH services
wsl -d Ubuntu-24.04 -- sudo systemctl restart ssh
wsl -d kali-linux -- sudo systemctl restart ssh
```

### Problem: Database Connection Issues
```bash
# Error: Database connection failed
```

#### Solution Steps:
```bash
# 1. Check PostgreSQL status
kubectl get pods -n awx | grep postgres

# 2. Check PostgreSQL logs
kubectl logs -n awx awx-postgres-15-0

# 3. Test database connectivity
kubectl exec -n awx awx-postgres-15-0 -- psql -U awx -c "SELECT version();"

# 4. Restart PostgreSQL if needed
kubectl delete pod -n awx awx-postgres-15-0

# 5. Check database size
kubectl exec -n awx awx-postgres-15-0 -- psql -U awx -c "SELECT pg_size_pretty(pg_database_size('awx'));"
```

## AWX Configuration Issues

### Problem: Project Sync Failures
```bash
# Error: Project sync fails
```

#### Solution Steps:
```bash
# 1. Check project sync status
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '{status, last_job_run}'

# 2. Check sync job logs
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq -r '.last_job_run')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"

# 3. Test Git connectivity
git ls-remote https://github.com/cloud-plat-org/ansible-playbook-config-testing.git

# 4. Manually trigger sync
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project update "$PROJECT_ID"

# 5. Check project configuration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '{scm_type, scm_url, scm_branch}'
```

### Problem: Job Template Issues
```bash
# Error: Job template configuration problems
```

#### Solution Steps:
```bash
# 1. Check job template configuration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '{become_enabled, ask_credential_on_launch, summary_fields}'

# 2. Verify credential association
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '.summary_fields.credentials'

# 3. Check playbook exists
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '.scm_revision'

# 4. Verify inventory configuration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory get "$INVENTORY_ID" | jq '{name, organization}'

# 5. Test job template launch
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch "$JOB_TEMPLATE_ID" --extra_vars '{"service_name": "test"}'
```

## Performance Issues

### Problem: Slow Job Execution
```bash
# Jobs take too long to complete
```

#### Solution Steps:
```bash
# 1. Check system resources
kubectl top pods -n awx
kubectl top nodes

# 2. Check AWX pod resource usage
kubectl describe pod -n awx awx-task-$(kubectl get pods -n awx | grep awx-task | awk '{print $1}')

# 3. Increase Minikube resources
minikube config set memory 16384
minikube config set cpus 6
minikube stop
minikube start

# 4. Check database performance
kubectl exec -n awx awx-postgres-15-0 -- psql -U awx -c "SELECT * FROM pg_stat_activity;"

# 5. Restart AWX pods
kubectl delete pod -n awx awx-task-$(kubectl get pods -n awx | grep awx-task | awk '{print $1}')
kubectl delete pod -n awx awx-web-$(kubectl get pods -n awx | grep awx-web | awk '{print $1}')
```

### Problem: Memory Issues
```bash
# Out of memory errors
```

#### Solution Steps:
```bash
# 1. Check memory usage
free -h
kubectl top pods -n awx

# 2. Clean up Docker
docker system prune -f
docker volume prune -f

# 3. Clean up Minikube
minikube ssh -- docker system prune -f

# 4. Restart Minikube with more memory
minikube stop
minikube start --driver=docker --cpus=4 --memory=8g

# 5. Check for memory leaks
kubectl logs -n awx awx-task-$(kubectl get pods -n awx | grep awx-task | awk '{print $1}') | grep -i memory
```

## Recovery Procedures

### Complete System Recovery
```bash
# 1. Stop all services
minikube stop
docker stop $(docker ps -q)

# 2. Clean up resources
docker system prune -f
minikube delete

# 3. Restart Docker Desktop
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &

# 4. Recreate Minikube
minikube start --driver=docker --cpus=4 --memory=8g --addons=ingress

# 5. Redeploy AWX
kubectl apply -f awx-deploy.yml -n awx

# 6. Wait for pods to be ready
kubectl get pods -n awx

# 7. Restore configuration
# Follow the configuration steps from the main guide
```

### Data Recovery
```bash
# 1. Restore from backup
~/awx_restore.sh ~/awx_backups/backup_file.tar.gz

# 2. Verify restoration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me

# 3. Test functionality
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template list
```

## Prevention and Best Practices

### Regular Maintenance
```bash
# 1. Run health checks daily
~/awx_health_check.sh

# 2. Perform maintenance weekly
~/awx_maintenance.sh

# 3. Create backups regularly
~/awx_backup.sh

# 4. Monitor logs for errors
~/awx_log_monitor.sh
```

### Monitoring Setup
```bash
# 1. Set up log monitoring
tail -f ~/awx_maintenance.log

# 2. Monitor resource usage
watch kubectl top pods -n awx

# 3. Check system health
watch ~/awx_health_check.sh
```

## Getting Additional Help

### Log Collection
```bash
# Collect all relevant logs
mkdir -p ~/awx_debug_$(date +%Y%m%d_%H%M%S)
cd ~/awx_debug_*

# System information
uname -a > system_info.txt
free -h >> system_info.txt
df -h >> system_info.txt

# Minikube information
minikube status > minikube_status.txt
kubectl get nodes -o wide > nodes.txt
kubectl get pods -n awx -o wide > awx_pods.txt

# AWX information
source ~/awx-venv/bin/activate
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me > awx_user.txt
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template list > job_templates.txt

# Logs
kubectl logs -n awx awx-task-$(kubectl get pods -n awx | grep awx-task | awk '{print $1}') > awx_task.log
kubectl logs -n awx awx-web-$(kubectl get pods -n awx | grep awx-web | awk '{print $1}') > awx_web.log

echo "Debug information collected in ~/awx_debug_$(date +%Y%m%d_%H%M%S)"
```

### Common Error Codes
- **Exit Code 1**: General error, check logs
- **Exit Code 2**: Configuration error, verify settings
- **Exit Code 3**: Network error, check connectivity
- **Exit Code 4**: Authentication error, verify credentials
- **Exit Code 5**: Resource error, check system resources

This troubleshooting guide should help resolve most common issues encountered with the AWX setup. For persistent problems, collect the debug information and review the logs for specific error messages.
