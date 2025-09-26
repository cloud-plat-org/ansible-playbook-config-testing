# Testing & Validation - Job Testing & Expected Outputs

## Overview
This document covers AWX job testing, expected output verification, and troubleshooting test failures.

## Pre-Test Verification

### 1. Ensure All Components Are Running
```bash
# Check WSL instances are running
wsl --list --verbose

# Check AWX pods
kubectl get pods -n awx

# Test SSH connectivity
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "echo 'Ubuntu OK'"
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2224 daniv@172.22.192.129 "echo 'Kali OK'"
```

## AWX Job Testing

### 1. Launch Test Job
```bash
# Activate AWX environment
source ~/awx-venv/bin/activate
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# Launch AWX job
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Test Service Lifecycle WSL" --extra_vars '{"target_service": "cron"}' | jq -r .id)

echo "Job ID: $JOB_ID"
```

### 2. Test Different Services
```bash
# Test cron service (safe - won't break SSH)
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Test Service Lifecycle WSL" --extra_vars '{"target_service": "cron"}' | jq -r .id)

# Test systemd-resolved service
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Test Service Lifecycle WSL" --extra_vars '{"target_service": "systemd-resolved"}' | jq -r .id)

# Test with default service (cron) - no extra_vars needed
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Test Service Lifecycle WSL" | jq -r .id)
```

### 3. Monitor Job Progress
```bash
# Check job status
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '{id, status, started, finished}'

# Get job output
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"
```

## Service Testing Examples

### Safe Services to Test:
- **`cron`** - Safe, won't break connectivity
- **`systemd-resolved`** - DNS resolution service
- **`systemd-networkd`** - Network management
- **`rsyslog`** - Logging service

### Services to Avoid:
- **`ssh`** - Will break AWX connectivity
- **`systemd-logind`** - Core login service
- **`dbus`** - System message bus

## Expected Successful Output

### Service Lifecycle Test Output
```text
PLAY [Test service lifecycle on WSL instances] ******************************

TASK [Gathering Facts] ****************************************************
ok: [wslkali1]
ok: [wslubuntu1]

TASK [Stop service: cron] **************************************************
changed: [wslkali1]
changed: [wslubuntu1]

TASK [Wait for service to stop] ********************************************
ok: [wslkali1]
ok: [wslubuntu1]

TASK [Start service: cron] *************************************************
changed: [wslkali1]
changed: [wslubuntu1]

TASK [Verify service is running] *******************************************
ok: [wslkali1]
changed: [wslubuntu1]

PLAY RECAP ****************************************************************
wslkali1                   : ok=5    changed=2    unreachable=0    failed=0
wslubuntu1                 : ok=5    changed=2    unreachable=0    failed=0
```

## Performance Validation

### 1. Job Execution Time
```bash
# Check job execution time
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '{started, finished, elapsed}'

# Expected: Job should complete in under 60 seconds
```

### 2. Resource Usage
```bash
# Check AWX pod resource usage
kubectl top pods -n awx

# Check system resources
kubectl top nodes
```

## Troubleshooting Test Failures

### Common Issues
```bash
# Check job status and output
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '{id, status, finished}'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"

# Check host connectivity
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "echo 'test'"

# Check credential configuration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential get "$CRED_ID" | jq '.inputs'

# Test SSH key manually
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "sudo whoami"
```

## Validation Checklist

### 1. Basic Functionality
- [ ] Test connection playbook runs successfully
- [ ] Service lifecycle playbook runs successfully
- [ ] All hosts are reachable and responding
- [ ] Sudo access is working properly
- [ ] Service management commands execute correctly

### 2. AWX Integration
- [ ] Jobs launch successfully from AWX
- [ ] Job output is displayed correctly
- [ ] Job status updates properly
- [ ] Extra variables are passed correctly
- [ ] Credentials are used properly

### 3. Performance
- [ ] Jobs complete in reasonable time (< 60 seconds)
- [ ] No resource exhaustion issues
- [ ] AWX pods remain stable

### 4. Error Handling
- [ ] Failed tasks are handled gracefully
- [ ] Error messages are informative
- [ ] Jobs don't hang indefinitely

## Next Steps

Once testing is complete and all validations pass, proceed to:
- [08-Daily-Operations.md](08-Daily-Operations.md) - Startup scripts, maintenance

## Final Verification Checklist

Before proceeding to daily operations, verify:
- [ ] All test jobs run successfully
- [ ] Expected outputs match actual outputs
- [ ] Performance is within acceptable limits
- [ ] Error handling works properly
- [ ] No critical issues or warnings
- [ ] System is stable and reliable
- [ ] Ready for production use