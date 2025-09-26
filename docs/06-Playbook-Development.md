# Playbook Development - Ansible Playbook Creation

## Overview
This document covers Ansible playbook development and AWX integration for WSL automation.

## AWX Integration Setup

### Verify AWX Project Configuration
```bash
# Get AWX token
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# Check project configuration
PROJECT_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq -r '.results[] | select(.name=="WSL Project") | .id')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '{name, scm_url, scm_branch, scm_update_on_launch}'
```

## Playbook Development

### Current Working Playbook Structure
Our current setup uses a role-based approach with the `service_management` role. The `test_service_lifecycle.yml` playbook is already created and working.

**Key Features:**
- **Flexible Service Testing**: Uses `target_service` variable to test any service
- **Role-Based Architecture**: Leverages the `service_management` role for reusability
- **Safe Defaults**: Defaults to `cron` service (won't break SSH connectivity)
- **Complete Lifecycle**: Stop -> Wait -> Start -> Verify

### Development Workflow
```bash
# Edit, test, and sync
vim test_service_lifecycle.yml
ansible-playbook --syntax-check test_service_lifecycle.yml
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project update "WSL Project"
```

### Testing New Playbooks
```bash
# Test with different services
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Test Service Lifecycle WSL" --extra_vars '{"target_service": "systemd-resolved"}' | jq -r .id)

# Monitor execution
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '{id, status, started, finished}'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"
```

## Development Tools

### Ansible Lint
```bash
# Install and use ansible-lint
pip install ansible-lint
ansible-lint test_service_lifecycle.yml
ansible-lint configure_new_wsl_instances.yml
```

### Syntax Validation
```bash
# Check playbook syntax
ansible-playbook --syntax-check test_service_lifecycle.yml
```
### YAML Linting
```bash
# Install and use yamllint
pip install yamllint

# Check workflow files
yamllint .github/workflows/ansible-ci.yml

# Check all YAML files
yamllint .
```

## Best Practices

### Variable Usage
```yaml
# Use flexible variables with defaults
vars:
  service_name: "{{ target_service | default('cron') }}"
  service_action: "{{ action | default('status') }}"
```

### Error Handling
```yaml
# Always handle potential failures
- name: Stop service
  command: systemctl stop {{ service_name }}
  register: stop_result
  ignore_errors: true
```

## Verification Checklist

Before proceeding to testing, verify:
- [ ] AWX project is configured with correct repository and branch
- [ ] Test inventory contains both WSL instances
- [ ] SSH credentials are properly configured in AWX
- [ ] Current playbook is syntactically correct
- [ ] Playbook uses flexible variables
- [ ] AWX project sync is working