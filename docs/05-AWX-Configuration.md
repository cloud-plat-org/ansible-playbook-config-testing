# AWX Configuration - Projects, Inventory & Templates

## Overview
This document covers AWX project creation, inventory setup, host configuration, credential creation, and job template setup for WSL automation.

## AWX Project Creation

### 1. Activate AWX Environment
```bash
# Activate AWX virtual environment
source ~/awx-venv/bin/activate

# Extract stored OAuth2 token (no regeneration needed - valid for ~1 year)
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# Verify AWX CLI access
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me
```

### 2. Create AWX Project
```bash
# Create project pointing to Git repository
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project create \
  --name "WSL Project" \
  --description "Playbooks for WSL Lab" \
  --organization Default \
  --scm_type git \
  --scm_url "https://github.com/cloud-plat-org/ansible-playbook-config-testing.git" \
  --scm_branch "CLPLAT-2223"

## Changing branch back to main.
```bash
# Get project ID first
PROJECT_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq -r '.results[] | select(.name=="WSL Project") | .id')

# Change branch to "main"
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project modify "$PROJECT_ID" --scm_branch "CLPLAT-2223"

# Verify the change
echo "Updated branch:"
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '{scm_branch, scm_url}'
```

### 3. Enable Auto-Sync on Launch
```bash
# Get project ID
PROJECT_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list |
 jq -r '.results[] | select(.name == "WSL Project") | .id')

# Enable auto-sync
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project modify "$PROJECT_ID" --scm_update_on_launch true

# Verify project configuration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" |
 jq '{name, scm_type, scm_url, scm_branch, scm_update_on_launch}'
```

## AWX Inventory Setup

### 1. Create AWX Inventory
```bash
# Create inventory
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory create \
  --name "WSL Lab" \
  --description "WSL instances for automation" \
  --organization Default

# Get inventory ID
INVENTORY_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory list | jq -r '.results[] | select(.name == "WSL Lab") | .id')
echo "Inventory ID: $INVENTORY_ID"
```

### 2. Create Host Group
```bash
# Create host group
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" group create \
  --name all_servers \
  --inventory "WSL Lab"

# Get group ID
GROUP_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" group list --inventory "WSL Lab" | jq -r '.results[] | select(.name == "all_servers") | .id')
echo "Group ID: $GROUP_ID"
```

## Host Configuration

### 1. Add Ubuntu-24.04 Host
```bash
# Add Ubuntu-24.04 host
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host create \
  --name wslubuntu1 \
  --inventory "WSL Lab" \
  --variables '{"ansible_host": "172.22.192.129", "ansible_port": 2223}'

# Get host ID
UBUNTU_HOST_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab" | jq -r '.results[] | select(.name == "wslubuntu1") | .id')
echo "Ubuntu Host ID: $UBUNTU_HOST_ID"
```

### 2. Add Kali-Linux Host
```bash
# Add Kali-Linux host
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host create \
  --name wslkali1 \
  --inventory "WSL Lab" \
  --variables '{"ansible_host": "172.22.192.129", "ansible_port": 2224}'

# Get host ID
KALI_HOST_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab" | jq -r '.results[] | select(.name == "wslkali1") | .id')
echo "Kali Host ID: $KALI_HOST_ID"
```

### 3. Associate Hosts with Group
```bash
# Associate Ubuntu host with group
curl -k -H "Authorization: Bearer $AWX_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  https://localhost/api/v2/groups/$GROUP_ID/hosts/ \
  -d "{\"id\": $UBUNTU_HOST_ID}"

# Associate Kali host with group
curl -k -H "Authorization: Bearer $AWX_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  https://localhost/api/v2/groups/$GROUP_ID/hosts/ \
  -d "{\"id\": $KALI_HOST_ID}"
```

## Credential Creation

### 1. Create SSH Key Credential
```bash
# Create machine credential with SSH key
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential create \
  --name "WSL SSH Key" \
  --description "SSH key for WSL hosts" \
  --credential_type "Machine" \
  --organization Default \
  --inputs "{\"username\": \"daniv\", \"ssh_key_data\": \"$(awk 'NF{printf \"%s\\n\",$0;}' ~/.ssh/awx_wsl_key_traditional)\"}"

# Get credential ID
CRED_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential list --name "WSL SSH Key" | jq -r '.results[0].id')
echo "Credential ID: $CRED_ID"
```

### 2. Verify Credential Configuration
```bash
# Check credential inputs
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential get "$CRED_ID" | jq '.inputs'

# Expected output:
# {
#   "username": "daniv",
#   "ssh_key_data": "-----BEGIN RSA PRIVATE KEY-----\n..."
# }
```

## Job Template Creation

### 1. Create Job Template

**Prerequisite:** The playbook must exist in the GitHub repository. If you get "Playbook not found for project" error, you need to push the playbook to GitHub first.

```bash
# Option A: Use existing playbook (if new playbook not pushed yet)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template create \
  --name "Test Service Lifecycle WSL" \
  --project "WSL Project" \
  --inventory "WSL Lab" \
  --playbook "stop_services.yml" \
  --become_enabled true \
  --ask_credential_on_launch false

# Option B: Use new playbook (after pushing to GitHub)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template create \
  --name "Test Service Lifecycle WSL" \
  --project "WSL Project" \
  --inventory "WSL Lab" \
  --playbook "test_service_lifecycle.yml" \
  --become_enabled true \
  --ask_credential_on_launch false

# Get job template ID
JOB_TEMPLATE_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template list --name "Test Service Lifecycle WSL" | jq -r '.results[0].id')
echo "Job Template ID: $JOB_TEMPLATE_ID"
```

**If you get "Playbook not found" error:**
1. **Push the playbook to GitHub**: `git push origin CLPLAT-2223`
2. **Sync AWX project**: `awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project update "WSL Project"`
3. **Wait for sync to complete**: Check status with `awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project_update get UPDATE_ID | jq '{status, finished}'`
4. **Then create the job template**

**Important Notes:**
- AWX only sees playbooks that are committed and pushed to GitHub
- Project sync is required after every git push
- Job template creation will fail if playbook doesn't exist in the repository

### 2. Associate SSH Key Credential
```bash
# Method 1: Associate credential using credential ID
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template associate --credential "$CRED_ID" "$JOB_TEMPLATE_ID"

# Method 2: Associate credential using credential name (alternative approach)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template create \
  --name "Stop Services WSL" \
  --project "WSL Project" \
  --inventory "WSL Lab" \
  --playbook "stop_services.yml" \
  --credential "WSL SSH Key" \
  --become_enabled true

# Verify credential association
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '.summary_fields.credentials'
```

### 3. Verify Job Template Configuration
```bash
# Check job template settings
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '{name, project, inventory, playbook, become_enabled, ask_credential_on_launch}'

# Expected output:
# {
#   "name": "Stop Services WSL",
#   "project": 1,
#   "inventory": 1,
#   "playbook": "stop_services.yml",
#   "become_enabled": true,
#   "ask_credential_on_launch": false
# }
```

## Project Management

### 1. Check Project Status
```bash
# List all projects
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list

# Check project status with detailed information
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | \
jq -r '.results[] | {name, status, last_job_run, last_job_failed}'

# Check project status in tabular format
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | \
jq -r '.results[] | [.name, .status, .last_job_run, .last_job_failed] | @tsv'
```

### 2. Job Template Management
```bash
# List job templates
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template list

# Get job template details
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID"

# Check job template credentials
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '.summary_fields.credentials'
```

## Job Execution

### 1. Launch Job with Extra Variables
```bash
# Launch job with service name variable
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" \
  --extra_vars '{"service_name": "ssh"}' | jq -r .id)

echo "Job ID: $JOB_ID"
```

### 2. Monitor Job Execution
```bash
# Check job status
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '{id, status, started, finished}'

# Get job output
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"

# List all jobs
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job list
```

### 3. AWX Version Considerations
```bash
# Check AWX version
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me | jq '.version'

# Note: AWX CLI limitations in version 24.6.1
# - No direct group associate command
# - Use API calls for host-group management
# - Web UI recommended for complex group operations
```

## Configuration Verification

### 1. Complete Configuration Check
```bash
echo "=== AWX Project Status ==="
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq '.results[] | {name, scm_type, scm_url, scm_branch}'

echo "=== AWX Inventory Status ==="
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory list | jq '.results[] | {name, organization}'

echo "=== AWX Hosts Status ==="
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab" | jq '.results[] | {name, inventory, variables}'

echo "=== AWX Groups Status ==="
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" group list --inventory "WSL Lab" | jq '.results[] | {name, inventory}'

echo "=== AWX Credentials Status ==="
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential list | jq '.results[] | {name, credential_type, organization}'

echo "=== AWX Job Templates Status ==="
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template list | jq '.results[] | {name, project, inventory, playbook, become_enabled}'
```

### 2. Test Project Sync
```bash
# Test project sync
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project update "$PROJECT_ID"

# Check sync status
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '{name, status, last_job_run}'
```

## Troubleshooting AWX Configuration

### Common Issues

#### Project Sync Failures
```bash
# Check project sync logs
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '.last_job_run'

# Get job details
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq -r '.last_job_run')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"
```

#### Host Connection Issues
```bash
# Test host connectivity
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get "$UBUNTU_HOST_ID" | jq '.variables'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get "$KALI_HOST_ID" | jq '.variables'

# Verify host variables are correct
```

#### Credential Issues
```bash
# Check credential format
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential get "$CRED_ID" | jq '.inputs.ssh_key_data' | head -1

# Should show: "-----BEGIN RSA PRIVATE KEY-----"
```

#### Job Template Issues
```bash
# Check job template configuration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '{become_enabled, ask_credential_on_launch, summary_fields}'

# Verify all required fields are set
```

## Advanced Configuration

### 1. Add Extra Variables
```bash
# Add extra variables to job template
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template modify "$JOB_TEMPLATE_ID" \
  --extra_vars '{"service_name": "ssh", "debug_mode": true}'
```

### 2. Configure Job Tags
```bash
# Add job tags
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template modify "$JOB_TEMPLATE_ID" \
  --job_tags "wsl,services,automation"
```

### 3. Set Job Timeout
```bash
# Set job timeout (in seconds)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template modify "$JOB_TEMPLATE_ID" \
  --timeout 1800
```

## Advanced AWX CLI Commands

### 1. Project Management
```bash
# Check project sync status and revision
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq '.results[] | {name, id, last_job_run, last_job_failed, status}'

# Get specific project details
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq '.results[] | select(.name == "WSL Project")'

# Capture project ID
PROJECT_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq -r '.results[] | select(.name == "WSL Project") | .id')
echo "WSL Project ID: $PROJECT_ID"

# Compare project revision with Git
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '.scm_revision'
git log -1 --format="%H"

# Check project branch and URL
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '{scm_branch, scm_url}'

# Change project branch
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project modify "$PROJECT_ID" --scm_branch "main"

# Enable automatic sync on launch
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project modify "$PROJECT_ID" --scm_update_on_launch true

# Check project local path
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '.local_path'
```

### 2. Project Update Monitoring
```bash
# Check project update progress
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project_update get 21 | jq '{status, started, finished, elapsed}'

# Monitor project update output
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project_update stdout 21

# Get latest project revision after update
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '.scm_revision'
```

### 3. Advanced Credential Management
```bash
# Check credential inputs (for troubleshooting)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential get "$CRED_ID" | jq '.inputs'

# Update credential with SSH key (proper formatting)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential modify "$CRED_ID" \
  --inputs "{\"username\": \"daniv\", \"ssh_key_data\": \"$(awk 'NF{printf \"%s\\n\",$0;}' ~/.ssh/awx_wsl_key_traditional)\"}"

# Disassociate old credential and associate new one
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template disassociate --credential "3" "$JOB_TEMPLATE_ID"
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template associate --credential "4" "$JOB_TEMPLATE_ID"

# Verify credential association
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '.summary_fields.credentials'
```

### 4. Advanced Host Management
```bash
# List all hosts with variables
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list | jq '.results[] | {name: .name, variables: .variables}'

# Get specific host variables
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslubuntu1 | jq '.variables'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslkali1 | jq '.variables'

# Update host variables (clean format)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host modify "$HOST_ID" --variables '{"ansible_host": "172.22.192.129", "ansible_port": 2223}'

# Delete host (if needed)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host delete "$HOST_ID"
```

### 5. Job Template Advanced Settings
```bash
# Check job template settings
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '{ask_credential_on_launch, ask_variables_on_launch, become_enabled}'

# Set job template to use stored credentials
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template modify "$JOB_TEMPLATE_ID" --ask_credential_on_launch false

# Enable privilege escalation
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template modify "$JOB_TEMPLATE_ID" --become_enabled true

# Verify job template settings
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '{become_enabled, ask_credential_on_launch}'
```

### 6. Job Environment and Arguments
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

### 7. SSH Key Troubleshooting
```bash
# Test SSH connectivity from AWX pod
# Get current AWX task pod name (pod names change on restarts)
kubectl get pods -n awx | grep awx-task

# Test SSH from AWX task pod (use current pod name from above)
kubectl exec -n awx -it awx-task-65c6fb66f6-f9gr7 -- ssh -p 2223 daniv@172.22.192.129
kubectl exec -n awx -it awx-task-65c6fb66f6-f9gr7 -- ssh -p 2224 daniv@172.22.192.129

# Test SSH from local machine (these work!)
ssh -p 2223 daniv@172.22.192.129  # Connects to Ubuntu-24.04 (wslubuntu1)
ssh -p 2224 daniv@172.22.192.129  # Connects to kali-linux (wslkali1)

# Add host keys to known_hosts
ssh-keyscan -p 2223 localhost >> ~/.ssh/known_hosts
ssh-keyscan -p 2224 localhost >> ~/.ssh/known_hosts
```

### 8. WSL Service Management
```bash
# Start WSL distributions
wsl --distribution Ubuntu-24.04 --user daniv
wsl --distribution Kali-Linux --user daniv

# Check SSH service status
sudo systemctl status ssh
sudo systemctl start ssh
sudo systemctl restart ssh

# Configure passwordless sudo
echo "daniv ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/daniv
```

## Next Steps

Once AWX configuration is complete, proceed to:
- [06-Playbook-Development.md](06-Playbook-Development.md) - Ansible playbooks

## Verification Checklist

Before proceeding to playbook development, verify:

- [ ] AWX project is created and syncing from Git
- [ ] Inventory is created with proper name
- [ ] Host group is created and configured
- [ ] Both WSL hosts are added with correct variables
- [ ] Hosts are associated with the group
- [ ] SSH key credential is created and formatted correctly
- [ ] Job template is created with all required settings
- [ ] Credential is associated with job template
- [ ] All configurations are verified and working
- [ ] Project sync is successful
- [ ] No configuration errors or warnings
