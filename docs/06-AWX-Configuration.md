# AWX Configuration - Projects, Inventory & Templates

## Overview
This document covers AWX project creation, inventory setup, host configuration, credential creation, and job template setup for WSL automation.

## AWX Project Creation

### 1. Activate AWX Environment
```bash
# Activate AWX virtual environment
source ~/awx-venv/bin/activate

# Set AWX token
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
  --scm_branch "CLPLAT-2221"
```

### 3. Enable Auto-Sync on Launch
```bash
# Get project ID
PROJECT_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq -r '.results[] | select(.name == "WSL Project") | .id')

# Enable auto-sync
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project modify "$PROJECT_ID" --scm_update_on_launch true

# Verify project configuration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '{name, scm_type, scm_url, scm_branch, scm_update_on_launch}'
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
```bash
# Create job template
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template create \
  --name "Stop Services WSL" \
  --project "WSL Project" \
  --inventory "WSL Lab" \
  --playbook "stop_services.yml" \
  --become_enabled true \
  --ask_credential_on_launch false

# Get job template ID
JOB_TEMPLATE_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template list --name "Stop Services WSL" | jq -r '.results[0].id')
echo "Job Template ID: $JOB_TEMPLATE_ID"
```

### 2. Associate SSH Key Credential
```bash
# Associate SSH key credential with job template
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template associate --credential "$CRED_ID" "$JOB_TEMPLATE_ID"

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

## Next Steps

Once AWX configuration is complete, proceed to:
- [07-Playbook-Development.md](07-Playbook-Development.md) - Ansible playbooks

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
