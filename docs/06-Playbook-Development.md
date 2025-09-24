# Playbook Development - Ansible Playbook Creation

## Overview
This document covers Ansible playbook development, AWX integration, Git repository management, and testing workflows for WSL automation.

## AWX Integration Setup

### 1. Verify AWX Project Configuration
```bash
# Get AWX token
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# Check project configuration
PROJECT_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq -r '.results[] | select(.name=="WSL Project") | .id')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '{name, scm_url, scm_branch, scm_update_on_launch}'

# Expected output:
# {
#   "name": "WSL Project",
#   "scm_url": "https://github.com/cloud-plat-org/ansible-playbook-config-testing.git",
#   "scm_branch": "CLPLAT-2223",
#   "scm_update_on_launch": true
# }
```

### 2. Verify Test Environment
```bash
# Check inventory and hosts
UBUNTU_HOST_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --name "wslubuntu1" | jq -r '.results[0].id')
KALI_HOST_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --name "wslkali1" | jq -r '.results[0].id')

# Get full host details including variables
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get "$UBUNTU_HOST_ID" | jq '.variables'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get "$KALI_HOST_ID" | jq '.variables'

# Expected output (if variables are properly set):
# "{\"ansible_host\": \"172.22.192.129\", \"ansible_port\": 2223}"
# "{\"ansible_host\": \"172.22.192.129\", \"ansible_port\": 2224}"
```

## Playbook Development

### 1. Current Working Playbook Structure
Our current setup uses a role-based approach with the `service_management` role. The `test_service_lifecycle.yml` playbook is already created and working.

**Key Features:**
- **Flexible Service Testing**: Uses `target_service` variable to test any service
- **Role-Based Architecture**: Leverages the `service_management` role for reusability
- **Safe Defaults**: Defaults to `cron` service (won't break SSH connectivity)
- **Complete Lifecycle**: Stop → Wait → Start → Verify

### 2. Making Changes to Existing Playbooks
```bash
# Edit the existing playbook
vim test_service_lifecycle.yml

# Test syntax after changes
ansible-playbook --syntax-check test_service_lifecycle.yml

# Sync AWX project to get latest changes
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project update "WSL Project"
```

## Git Workflow for Playbook Development

### 1. Development Process
```bash
# 1. Create/update playbook locally
vim test_service_lifecycle.yml

# 2. Test syntax
ansible-playbook --syntax-check test_service_lifecycle.yml

# 3. Commit changes
git commit -am "Update playbook"

# 4. Push to GitHub (AWX pulls from CLPLAT-2223 branch)
git push

# 5. Sync AWX project to get latest changes
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project update "WSL Project"
```

### 2. Testing New Playbooks
```bash
# Test with different services
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Test Service Lifecycle WSL" --extra_vars '{"target_service": "systemd-resolved"}' | jq -r .id)

# Monitor execution
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '{id, status, started, finished}'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"
```

## Development Tools

### 1. Ansible Lint (Already Configured)
```bash
# Check if ansible-lint is available
ansible-lint --version

# Lint current playbook
ansible-lint test_service_lifecycle.yml

# Lint with specific rules
ansible-lint --skip-list yaml[line-length],name[casing] test_service_lifecycle.yml
```

### 2. Syntax Validation
```bash
# Check playbook syntax
ansible-playbook --syntax-check test_service_lifecycle.yml

# Validate role syntax
ansible-playbook --syntax-check roles/service_management/tasks/main.yml
```

## Best Practices

### 1. Variable Usage
```yaml
# Use flexible variables with defaults
vars:
  service_name: "{{ target_service | default('cron') }}"
  service_action: "{{ action | default('status') }}"
  debug_mode: "{{ debug | default(false) }}"
```

### 2. Error Handling
```yaml
# Always handle potential failures
- name: Stop service
  command: systemctl stop {{ service_name }}
  register: stop_result
  ignore_errors: true

- name: Show result
  debug:
    msg: "Stop result: RC {{ stop_result.rc }}"
```

### 3. Role Organization
```yaml
# Use roles for reusable functionality
roles:
  - service_management
vars:
  service_name: "{{ target_service }}"
  service_action: "stop"
```

## Troubleshooting Development Issues

### Common Problems

#### Playbook Not Found in AWX
```bash
# Error: "Playbook not found for project"
# Solution: Push to GitHub and sync AWX project

git add test_service_lifecycle.yml
git commit -m "Add new playbook"
git push origin CLPLAT-2223

# Then sync AWX project
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project update "WSL Project"
```

#### Syntax Errors
```bash
# Check playbook syntax
ansible-playbook --syntax-check test_service_lifecycle.yml

# Check role syntax
ansible-playbook --syntax-check roles/service_management/tasks/main.yml
```

#### Job Execution Failures
```bash
# Check job status and output
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '{id, status, finished}'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"
```

## Verification Checklist

Before proceeding to testing, verify:

- [ ] AWX project is configured with correct repository and branch (CLPLAT-2223)
- [ ] Test inventory contains both WSL instances (wslubuntu1, wslkali1)
- [ ] SSH credentials are properly configured in AWX
- [ ] Current playbook (`test_service_lifecycle.yml`) is syntactically correct
- [ ] Service management role is properly structured
- [ ] Playbook uses flexible variables (`target_service`)
- [ ] Git repository is properly configured
- [ ] Changes are committed and pushed to GitHub
- [ ] AWX project sync is working
- [ ] Job template can be created successfully
- [ ] Playbook follows role-based best practices
- [ ] Error handling is implemented
- [ ] Documentation is up to date
