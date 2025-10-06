# AWX Configuration - Inventory, Groups, Projects & Templates


# 1. Create Inventory (no dependencies)
INVENTORY_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" -f json --conf.color false inventories create \
  --name "WSL Lab2" \
  --organization "Default" | jq -r '.id')

# how do I add these hosts to this inventory?
- **argo_cd_mgt**: `172.22.192.129:2226`
- **ubuntuAWX**: `172.22.192.129:2225`
- **wslkali1**: `172.22.192.129:2224`
- **wslubuntu1**: `172.22.192.129:2223`



# 2. Create Project (no dependencies)  
PROJECT_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" -f json --conf.color false projects create \
  --name "WSL Project" \
  --organization "Default" \
  --scm_type "git" \
  --scm_url "https://github.com/your-repo.git" \
  --scm_branch "main" | jq -r '.id')

# 3. Create Job Template (requires both inventory and project)
TEMPLATE_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" -f json --conf.color false job_templates create \
  --name "Service Management" \
  --inventory "$INVENTORY_ID" \
  --project "$PROJECT_ID" \
  --playbook "playbooks/service_management.yml" | jq -r '.id')










































## Overview
This document covers AWX project creation, inventory setup, host configuration, credential creation, and job template setup for WSL automation.

## AWX Project Creation

### 1. Activate AWX Environment
```bash
# Activate AWX virtual environment
source ~/awx-venv/bin/activate

# Extract stored OAuth2 token
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
  --scm_branch "CLPLAT-2225"

# Enable auto-sync on launch
PROJECT_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq -r '.results[] | select(.name=="WSL Project") | .id')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project modify "$PROJECT_ID" --scm_update_on_launch true

# Sync project to get latest changes
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project update "WSL Project"
```

## AWX Inventory Setup

### 1. Create Inventory and Host Group
```bash
# Create inventory
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory create \
  --name "WSL Lab" \
  --description "WSL instances for automation" \
  --organization Default

# Create host group
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" group create \
  --name all_servers \
  --inventory "WSL Lab"

# Get IDs for later use
INVENTORY_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory list | jq -r '.results[] | select(.name == "WSL Lab") | .id')
GROUP_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" group list --inventory "WSL Lab" | jq -r '.results[] | select(.name == "all_servers") | .id')
```

### 2. Add WSL Hosts
```bash
# Add Ubuntu-24.04 host
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host create \
  --name wslubuntu1 \
  --inventory "WSL Lab" \
  --variables '{"ansible_host": "172.22.192.129", "ansible_port": 2223}'

# Add Kali-Linux host
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host create \
  --name wslkali1 \
  --inventory "WSL Lab" \
  --variables '{"ansible_host": "172.22.192.129", "ansible_port": 2224}'

# Get host IDs
UBUNTU_HOST_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab" | jq -r '.results[] | select(.name == "wslubuntu1") | .id')
KALI_HOST_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab" | jq -r '.results[] | select(.name == "wslkali1") | .id')

# Associate hosts with group
curl -k -H "Authorization: Bearer $AWX_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  https://localhost/api/v2/groups/$GROUP_ID/hosts/ \
  -d "{\"id\": $UBUNTU_HOST_ID}"

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
```

## Job Template Creation

### 1. Create Job Template
```bash
# Create job template for service lifecycle testing
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template create \
  --name "Test Service Lifecycle WSL" \
  --project "WSL Project" \
  --inventory "WSL Lab" \
  --playbook "test_service_lifecycle.yml" \
  --credential "WSL SSH Key" \
  --become_enabled true \
  --ask_credential_on_launch false

# Create job template for WSL configuration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template create \
  --name "Configure WSL Instances" \
  --project "WSL Project" \
  --inventory "WSL Lab" \
  --playbook "configure_new_wsl_instances.yml" \
  --credential "WSL SSH Key" \
  --become_enabled true \
  --ask_credential_on_launch false

# Get job template IDs
JOB_TEMPLATE_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template list --name "Test Service Lifecycle WSL" | jq -r '.results[0].id')
CONFIG_TEMPLATE_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template list --name "Configure WSL Instances" | jq -r '.results[0].id')
```

### 2. Verify Job Template Configuration
```bash
# Check job template settings
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '{name, project, inventory, playbook, become_enabled, ask_credential_on_launch}'

# Check credentials
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '.summary_fields.credentials'
```

## Job Execution

### 1. Launch Job with Extra Variables
```bash
# Launch service lifecycle test
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Test Service Lifecycle WSL" \
  --extra_vars '{"target_service": "cron"}' | jq -r .id)

echo "Job ID: $JOB_ID"
```

### 2. Monitor Job Execution
```bash
# Check job status
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '{id, status, started, finished}'

# Get job output
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"
```

## Configuration Verification

### 1. Complete Configuration Check
```bash
echo "=== AWX Configuration Status ==="
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq '.results[] | {name, scm_type, scm_url, scm_branch}'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory list | jq '.results[] | {name, organization}'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab" | jq '.results[] | {name, inventory, variables}'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential list | jq '.results[] | {name, credential_type, organization}'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template list | jq '.results[] | {name, project, inventory, playbook, become_enabled}'
```

## Troubleshooting

### Common Issues
```bash
# Check project sync status
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '{name, status, last_job_run}'

# Test host connectivity
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get "$UBUNTU_HOST_ID" | jq '.variables'

# Check credential format
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential get "$CRED_ID" | jq '.inputs'
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