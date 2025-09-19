git # Testing & Validation - Job Testing & Expected Outputs

## Overview
This document covers AWX job testing, expected output verification, troubleshooting test failures, and performance validation.

## Pre-Test Verification

### 1. Ensure All Components Are Running
```bash
# Check WSL instances are running
wsl --list --verbose

# Expected output:
#   NAME            STATE           VERSION
#   Ubuntu-22.04    Running         2
#   Ubuntu-24.04    Running         2
#   kali-linux      Running         2
```

### 2. Verify AWX Status
```bash
# Check AWX pods
kubectl get pods -n awx

# Expected: All pods should be Running
# - awx-migration-* (Completed)
# - awx-operator-controller-manager-* (Running)
# - awx-postgres-* (Running)
# - awx-task-* (Running)
# - awx-web-* (Running)
```

### 3. Verify Network Connectivity
```bash
# Test SSH connectivity
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "echo 'Ubuntu OK'"
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2224 daniv@172.22.192.129 "echo 'Kali OK'"
```

## AWX Job Testing

### 1. Launch Test Job
```bash
# Activate AWX environment
source ~/awx-venv/bin/activate

# Extract stored OAuth2 token (no regeneration needed - valid for ~1 year)
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# Launch AWX job
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "ssh"}' | jq -r .id)

echo "Job ID: $JOB_ID"
```

### 2. Launch Job Without Extra Variables
```bash
# Launch job without extra variables (uses default service_name)
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" | jq -r .id)

echo "Job ID: $JOB_ID"
```

### 3. Launch Job with Different Service
```bash
# Launch job with different service
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "cron"}' | jq -r .id)

echo "Job ID: $JOB_ID"

# Job output 
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"
```

### 4. Monitor Job Execution
```bash
# Monitor job status
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '{id, status, started, finished}'

# Get job output
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"

# List all jobs
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job list
```

### 5. Test Different Services
```bash
# Test with different service
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "systemd-resolved"}' | jq -r .id)

# Monitor second job
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"
```

## Expected Successful Output

### 1. Test Connection Playbook
```text
PLAY [Test connection to WSL instances] ************************************

TASK [Gathering Facts] ****************************************************
ok: [wslkali1]
ok: [wslubuntu1]

TASK [Test basic connectivity] ********************************************
ok: [wslkali1] => {"changed": false, "ping": "pong"}
ok: [wslubuntu1] => {"changed": false, "ping": "pong"}

TASK [Show system information] ********************************************
ok: [wslkali1] => {
    "msg": "Host: wslkali1, OS: Kali GNU/Linux Rolling"
}
ok: [wslubuntu1] => {
    "msg": "Host: wslubuntu1, OS: Ubuntu 24.04"
}

TASK [Show current user] **************************************************
changed: [wslkali1]
changed: [wslubuntu1]

TASK [Display current user] ***********************************************
ok: [wslkali1] => {
    "msg": "Current user: daniv"
}
ok: [wslubuntu1] => {
    "msg": "Current user: daniv"
}

TASK [Show system uptime] *************************************************
changed: [wslkali1]
changed: [wslubuntu1]

TASK [Display uptime] *****************************************************
ok: [wslkali1] => {
    "msg": "System uptime: 12:34:56 up 1 day, 2:30, 0 users, load average: 0.00, 0.00, 0.00"
}
ok: [wslubuntu1] => {
    "msg": "System uptime: 12:34:56 up 1 day, 2:30, 0 users, load average: 0.00, 0.00, 0.00"
}

PLAY RECAP ****************************************************************
wslkali1                   : ok=7    changed=3    unreachable=0    failed=0
wslubuntu1                 : ok=7    changed=3    unreachable=0    failed=0
```

### 2. Stop Services Playbook
```text
PLAY [Stop services on WSL instances] ***********************************

TASK [Gathering Facts] ****************************************************
ok: [wslkali1]
ok: [wslubuntu1]

TASK [Debug - Show basic info] ********************************************
ok: [wslkali1] => {
    "msg": "Host: wslkali1\nUser: daniv\nService: ssh"
}
ok: [wslubuntu1] => {
    "msg": "Host: wslubuntu1\nUser: daniv\nService: ssh"
}

TASK [Test sudo access] ***************************************************
changed: [wslkali1]
changed: [wslubuntu1]

TASK [Show whoami result] *************************************************
ok: [wslkali1] => {
    "msg": "Running as: root"
}
ok: [wslubuntu1] => {
    "msg": "Running as: root"
}

TASK [Check service status before stop] ***********************************
changed: [wslkali1]
changed: [wslubuntu1]

TASK [Show service status before stop] ***********************************
ok: [wslkali1] => {
    "msg": "Service status before: ● ssh.service - OpenBSD Secure Shell server"
}
ok: [wslubuntu1] => {
    "msg": "Service status before: ● ssh.service - OpenBSD Secure Shell server"
}

TASK [Stop service using systemctl command] *******************************
changed: [wslkali1]
changed: [wslubuntu1]

TASK [Show stop result] ***************************************************
ok: [wslkali1] => {
    "msg": "Stop result: No output, RC: 0"
}
ok: [wslubuntu1] => {
    "msg": "Stop result: No output, RC: 0"
}

TASK [Check service status after stop] ************************************
changed: [wslkali1]
changed: [wslubuntu1]

TASK [Show final status] **************************************************
ok: [wslkali1] => {
    "msg": "Final status: ○ ssh.service - OpenBSD Secure Shell server"
}
ok: [wslubuntu1] => {
    "msg": "Final status: ○ ssh.service - OpenBSD Secure Shell server"
}

TASK [Test additional services (if service_name is ssh)] ******************
included: /runner/project/stop_services.yml for wslkali1, wslubuntu1

TASK [Stop cron service] **************************************************
changed: [wslkali1]
changed: [wslubuntu1]

TASK [Stop systemd-resolved service] *************************************
changed: [wslkali1]
changed: [wslubuntu1]

TASK [Show additional service results] ************************************
ok: [wslkali1] => {
    "msg": "Cron stop: 0, Resolved stop: 0"
}
ok: [wslubuntu1] => {
    "msg": "Cron stop: 0, Resolved stop: 0"
}

PLAY RECAP ****************************************************************
wslkali1                   : ok=13   changed=6    unreachable=0    failed=0
wslubuntu1                 : ok=13   changed=6    unreachable=0    failed=0
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

### 3. Concurrent Job Testing
```bash
# Launch multiple jobs simultaneously
JOB_ID3=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "cron"}' | jq -r .id)

JOB_ID4=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "systemd-resolved"}' | jq -r .id)

# Monitor both jobs
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID3" | jq '{id, status}'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID4" | jq '{id, status}'
```

## Troubleshooting Test Failures

### Common Issues

#### Job Stuck in "Running" State
```bash
# Check job details
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '{status, started, finished}'

# Check AWX task pod logs
kubectl logs -n awx awx-task-<pod-id> --tail=50

# Check job events
kubectl get events -n awx --sort-by='.lastTimestamp'
```

#### Host Unreachable
```bash
# Check host connectivity
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "echo 'test'"

# Check host variables
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab" | jq '.results[] | {name, variables}'

# Test with verbose output
ansible all -i "172.22.192.129:2223,172.22.192.129:2224" -m ping -vvv
```

#### Authentication Failures
```bash
# Check credential configuration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential get "$CRED_ID" | jq '.inputs'

# Test SSH key manually
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "sudo whoami"

# Check job environment
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_env' | grep -i ssh
```

#### Playbook Errors
```bash
# Check playbook syntax
ansible-playbook --syntax-check stop_services.yml

# Test playbook locally
ansible-playbook stop_services.yml -i local_inventory -e "service_name=ssh" --check

# Check AWX project sync
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '{status, last_job_run}'
```

## Validation Checklist

### 1. Basic Functionality
- [ ] Test connection playbook runs successfully
- [ ] Stop services playbook runs successfully
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
- [ ] Concurrent jobs work properly
- [ ] AWX pods remain stable

### 4. Error Handling
- [ ] Failed tasks are handled gracefully
- [ ] Error messages are informative
- [ ] Jobs don't hang indefinitely
- [ ] Recovery procedures work

## Advanced Testing

### 1. Load Testing
```bash
# Launch multiple jobs to test system load
for i in {1..5}; do
  awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
    --job_template "Stop Services WSL" --extra_vars "{\"service_name\": \"test$i\"}" &
done

# Monitor system performance
kubectl top pods -n awx
```

### 2. Failure Testing
```bash
# Test with invalid service name
JOB_ID_FAIL=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "nonexistent"}' | jq -r .id)

# Check how failure is handled
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID_FAIL"
```

### 3. Network Failure Testing
```bash
# Stop SSH service on one host to test network failure
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "sudo systemctl stop ssh"

# Launch job and see how it handles the failure
JOB_ID_NETWORK=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "ssh"}' | jq -r .id)

# Check job results
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID_NETWORK"

# Restart SSH service
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "sudo systemctl start ssh"
```

## Advanced Job Monitoring

### 1. Job Environment Debugging
```bash
# Check job environment variables
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_env'

# Check for password in job environment
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_env' | grep -i password

# Check job arguments
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_args'

# Verify credential in job
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.summary_fields.credentials'

# Check job working directory
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_cwd'
```

### 2. Project Sync Verification
```bash
# Check project sync status and revision
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq '.results[] | {name, id, last_job_run, last_job_failed, status}'

# Compare project revision with Git
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '.scm_revision'
git log -1 --format="%H"

# Check project update progress
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project_update get 21 | jq '{status, started, finished, elapsed}'

# Monitor project update output
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project_update stdout 21
```

### 3. Job Template Verification
```bash
# Check job template settings
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '{ask_credential_on_launch, ask_variables_on_launch, become_enabled}'

# Verify credential association
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '.summary_fields.credentials'
```

## Next Steps

Once testing is complete and all validations pass, proceed to:
- [09-Daily-Operations.md](09-Daily-Operations.md) - Startup scripts, maintenance

## Final Verification Checklist

Before proceeding to daily operations, verify:

- [ ] All test jobs run successfully
- [ ] Expected outputs match actual outputs
- [ ] Performance is within acceptable limits
- [ ] Error handling works properly
- [ ] Load testing passes
- [ ] Failure scenarios are handled gracefully
- [ ] No critical issues or warnings
- [ ] System is stable and reliable
- [ ] All validation checklists are complete
- [ ] Ready for production use
