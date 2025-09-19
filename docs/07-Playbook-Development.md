# Playbook Development - Ansible Playbook Creation

## Overview
This document covers Ansible playbook development, working directory setup, Git repository integration, and best practices for WSL automation.

## Working Directory Setup

### 1. Create Project Directory
```bash
# Create project directory
mkdir -p ~/ansible/test2
cd ~/ansible/test2

# Initialize git repository (if not already done)
git init
git remote add origin https://github.com/cloud-plat-org/ansible-playbook-config-testing.git
```

### 2. Verify Git Configuration
```bash
# Check git status
git status

# Check remote configuration
git remote -v

# Expected output:
# origin  https://github.com/cloud-plat-org/ansible-playbook-config-testing.git (fetch)
# origin  https://github.com/cloud-plat-org/ansible-playbook-config-testing.git (push)
```

## Playbook Development

### 1. Create Final Working Playbook
```bash
cat > stop_services.yml << 'EOF'
---
- name: Stop services on WSL instances
  hosts: all
  become: true
  become_method: sudo
  become_user: daniv
  tasks:
    - name: Debug - Show basic info
      debug:
        msg: "Host: {{ inventory_hostname }}\nUser: {{ ansible_user }}\nService: {{ service_name }}"

    - name: Test sudo access
      command: whoami
      register: whoami_result

    - name: Show whoami result
      debug:
        msg: "Running as: {{ whoami_result.stdout }}"

    - name: Check service status before stop
      command: systemctl status {{ service_name }}
      register: status_before
      ignore_errors: true

    - name: Show service status before stop
      debug:
        msg: "Service status before: {{ status_before.stdout_lines[0] if status_before.stdout_lines else 'Service not found' }}"

    - name: Stop service using systemctl command
      command: systemctl stop {{ service_name }}
      register: stop_result
      ignore_errors: true

    - name: Show stop result
      debug:
        msg: "Stop result: {{ stop_result.stdout if stop_result.stdout else 'No output' }}, RC: {{ stop_result.rc }}"

    - name: Check service status after stop
      command: systemctl status {{ service_name }}
      register: status_after
      ignore_errors: true

    - name: Show final status
      debug:
        msg: "Final status: {{ status_after.stdout_lines[0] if status_after.stdout_lines else 'Service not found' }}"

    - name: Test additional services (if service_name is ssh)
      block:
        - name: Stop cron service
          command: systemctl stop cron
          register: cron_result
          ignore_errors: true

        - name: Stop systemd-resolved service
          command: systemctl stop systemd-resolved
          register: resolved_result
          ignore_errors: true

        - name: Show additional service results
          debug:
            msg: "Cron stop: {{ cron_result.rc }}, Resolved stop: {{ resolved_result.rc }}"
      when: service_name == "ssh"
EOF
```

### 2. Create Additional Playbooks
```bash
# Create a simple test playbook
cat > test_connection.yml << 'EOF'
---
- name: Test connection to WSL instances
  hosts: all
  become: true
  become_method: sudo
  become_user: daniv
  tasks:
    - name: Test basic connectivity
      ping:

    - name: Show system information
      debug:
        msg: "Host: {{ inventory_hostname }}, OS: {{ ansible_distribution }} {{ ansible_distribution_version }}"

    - name: Show current user
      command: whoami
      register: current_user

    - name: Display current user
      debug:
        msg: "Current user: {{ current_user.stdout }}"

    - name: Show system uptime
      command: uptime
      register: uptime_result

    - name: Display uptime
      debug:
        msg: "System uptime: {{ uptime_result.stdout }}"
EOF

# Create a service management playbook
cat > manage_services.yml << 'EOF'
---
- name: Manage services on WSL instances
  hosts: all
  become: true
  become_method: sudo
  become_user: daniv
  vars:
    service_state: "{{ service_action | default('status') }}"
  tasks:
    - name: Show service information
      debug:
        msg: "Managing service: {{ service_name }}, Action: {{ service_state }}"

    - name: Check service status
      command: systemctl status {{ service_name }}
      register: service_status
      ignore_errors: true

    - name: Show service status
      debug:
        msg: "Service status: {{ service_status.stdout_lines[0] if service_status.stdout_lines else 'Service not found' }}"

    - name: Start service
      command: systemctl start {{ service_name }}
      when: service_state == "start"
      ignore_errors: true

    - name: Stop service
      command: systemctl stop {{ service_name }}
      when: service_state == "stop"
      ignore_errors: true

    - name: Restart service
      command: systemctl restart {{ service_name }}
      when: service_state == "restart"
      ignore_errors: true

    - name: Enable service
      command: systemctl enable {{ service_name }}
      when: service_state == "enable"
      ignore_errors: true

    - name: Disable service
      command: systemctl disable {{ service_name }}
      when: service_state == "disable"
      ignore_errors: true
EOF
```

## Git Repository Integration

### 1. Commit and Push Playbooks
```bash
# Add all playbooks to git
git add *.yml

# Commit changes
git commit -m "Add working playbooks for WSL automation"

# Push to repository
git push origin CLPLAT-2221
```

### 2. Verify Git Integration
```bash
# Check git status
git status

# Check commit history
git log --oneline -5

# Verify remote tracking
git branch -vv
```

## Playbook Best Practices

### 1. Error Handling
```yaml
# Always use ignore_errors for potentially failing tasks
- name: Stop service
  command: systemctl stop {{ service_name }}
  ignore_errors: true
  register: stop_result

# Check results and handle errors
- name: Check stop result
  debug:
    msg: "Stop result: {{ stop_result.rc }}"
  when: stop_result.rc != 0
```

### 2. Variable Usage
```yaml
# Use variables for flexibility
vars:
  service_name: "{{ service_name | default('ssh') }}"
  service_action: "{{ service_action | default('status') }}"

# Use facts for system information
- name: Show system info
  debug:
    msg: "OS: {{ ansible_distribution }} {{ ansible_distribution_version }}"
```

### 3. Conditional Execution
```yaml
# Use when conditions for conditional tasks
- name: Stop additional services
  block:
    - name: Stop cron
      command: systemctl stop cron
  when: service_name == "ssh"
```

### 4. Block Organization
```yaml
# Use blocks for logical grouping
- name: Service management tasks
  block:
    - name: Check status
      command: systemctl status {{ service_name }}
    - name: Stop service
      command: systemctl stop {{ service_name }}
  rescue:
    - name: Handle errors
      debug:
        msg: "Service management failed"
```

## Development Tools Setup

### 1. Ansible Lint Installation
```bash
# Install python3-venv (if not already installed)
sudo apt install python3-venv

# Create dedicated virtual environment for ansible-lint
python3 -m venv ~/.venvs/ansible

# Activate virtual environment
source ~/.venvs/ansible/bin/activate

# Install ansible-lint
pip install ansible-lint

# Verify installation
ansible-lint --version
```

### 2. Configure Ansible Lint
```bash
# Create ansible-lint configuration file
# Create project-specific ansible-lint configuration for CI/CD
cat > .ansible-lint << 'EOF'
# Ansible Lint Configuration for CI/CD
skip_list:
  - yaml[line-length]  # Allow longer lines for readability
  - name[casing]      # Allow different naming conventions
  - risky-file-permissions  # Allow specific file permissions

exclude_paths:
  - .cache/
  - .github/
  - .git/
  - .tox/
  - .venv/
  - venv/

verbosity: 1
EOF

# Set up environment variable for cache
echo 'export ANSIBLE_CACHE_PLUGIN_CONNECTION=$(pwd)/.ansible' >> ~/.bashrc
source ~/.bashrc
```

### 3. Using Ansible Lint
```bash
# Activate ansible-lint environment
source ~/.venvs/ansible/bin/activate

# Lint a single playbook
ansible-lint stop_services.yml

# Lint all playbooks in directory
ansible-lint .

# Lint with verbose output
ansible-lint -v stop_services.yml

# Lint and fix common issues automatically
ansible-lint --fix stop_services.yml
```

### 4. IDE Integration
```bash
# For VS Code, create .vscode/settings.json
mkdir -p .vscode
cat > .vscode/settings.json << 'EOF'
{
    "ansible.ansibleLint.enabled": true,
    "ansible.ansibleLint.path": "~/.venvs/ansible/bin/ansible-lint",
    "ansible.validation.enabled": true,
    "ansible.python.interpreterPath": "~/.venvs/ansible/bin/python"
}
EOF

# For Vim/Neovim, add to ~/.vimrc or ~/.config/nvim/init.vim
echo '" Ansible Lint integration' >> ~/.vimrc
echo 'let g:ale_linters = {"yaml": ["ansible-lint"]}' >> ~/.vimrc
echo 'let g:ale_yaml_ansible_lint_options = "--offline"' >> ~/.vimrc
```

### 5. Pre-commit Hooks (Optional)
```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/ansible/ansible-lint
    rev: v6.17.2
    hooks:
      - id: ansible-lint
        args: [--fix]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
EOF

# Install pre-commit hooks
pre-commit install
```

### 6. Common Ansible Lint Rules
```bash
# Check specific rules
ansible-lint --list-rules

# Skip specific rules
ansible-lint --skip-list yaml[line-length],name[casing] stop_services.yml

# Show only errors
ansible-lint --quiet stop_services.yml

# Generate detailed report
ansible-lint --progressive stop_services.yml
```

## Testing Playbooks

### 1. Syntax Validation
```bash
# Check playbook syntax
ansible-playbook --syntax-check stop_services.yml
ansible-playbook --syntax-check test_connection.yml
ansible-playbook --syntax-check manage_services.yml
```

### 2. Dry Run Testing
```bash
# Test playbook without executing
ansible-playbook --check --diff stop_services.yml -i "172.22.192.129:2223,172.22.192.129:2224" -e "service_name=ssh"
```

### 3. Local Testing
```bash
# Test with local inventory
cat > local_inventory << 'EOF'
[all_servers]
wslubuntu1 ansible_host=172.22.192.129 ansible_port=2223
wslkali1 ansible_host=172.22.192.129 ansible_port=2224

[all_servers:vars]
ansible_user=daniv
ansible_ssh_private_key_file=~/.ssh/awx_wsl_key_traditional
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
EOF

# Test playbook locally
ansible-playbook test_connection.yml -i local_inventory
```

## Playbook Documentation

### 1. Create README
```bash
cat > README.md << 'EOF'
# WSL Automation Playbooks

This repository contains Ansible playbooks for automating WSL instances.

## Playbooks

### stop_services.yml
Stops specified services on WSL instances.

**Variables:**
- `service_name`: Name of the service to stop (default: ssh)

**Usage:**
```bash
ansible-playbook stop_services.yml -e "service_name=ssh"
```

### test_connection.yml
Tests basic connectivity and shows system information.

**Usage:**
```bash
ansible-playbook test_connection.yml
```

### manage_services.yml
Manages services on WSL instances (start, stop, restart, enable, disable).

**Variables:**
- `service_name`: Name of the service to manage
- `service_action`: Action to perform (start, stop, restart, enable, disable, status)

**Usage:**
```bash
ansible-playbook manage_services.yml -e "service_name=ssh service_action=stop"
```

## Requirements

- Ansible 2.9+
- SSH key authentication configured
- Passwordless sudo configured on target hosts
EOF
```

### 2. Create Requirements File
```bash
cat > requirements.yml << 'EOF'
# Ansible requirements file
# Add any required Ansible collections or roles here

# Example:
# - name: community.general
#   version: ">=1.0.0"
EOF
```

## Version Control Best Practices

### 1. Git Workflow
```bash
# Create feature branch for new playbooks
git checkout -b feature/new-playbook

# Make changes and commit
git add new_playbook.yml
git commit -m "Add new playbook for service management"

# Push feature branch
git push origin feature/new-playbook

# Create pull request for review
```

### 2. Tagging Releases
```bash
# Tag stable versions
git tag -a v1.0.0 -m "Initial stable release"
git push origin v1.0.0
```

## Troubleshooting Playbook Issues

### Common Problems

#### Syntax Errors
```bash
# Check playbook syntax
ansible-playbook --syntax-check playbook.yml

# Use YAML linter
yamllint playbook.yml
```

#### Variable Issues
```bash
# Debug variables
ansible-playbook playbook.yml --extra-vars "debug_mode=true" -vvv

# Check variable precedence
ansible-playbook playbook.yml --list-hosts
```

#### Connection Issues
```bash
# Test connectivity
ansible all -i inventory -m ping

# Check SSH connection
ansible all -i inventory -m setup
```

## Next Steps

Once playbooks are developed and tested, proceed to:
- [08-Testing-Validation.md](08-Testing-Validation.md) - Job testing, expected outputs

## Verification Checklist

Before proceeding to testing, verify:

- [ ] All playbooks are created and syntactically correct
- [ ] Ansible-lint is installed and configured
- [ ] Playbooks pass ansible-lint validation
- [ ] IDE integration is set up (if using VS Code/Vim)
- [ ] Pre-commit hooks are installed (optional)
- [ ] Playbooks are committed to Git repository
- [ ] Git integration is working properly
- [ ] Playbooks follow best practices
- [ ] Error handling is implemented
- [ ] Variables are properly defined
- [ ] Documentation is created
- [ ] Local testing is successful
- [ ] No syntax errors or warnings
- [ ] Playbooks are ready for AWX execution
