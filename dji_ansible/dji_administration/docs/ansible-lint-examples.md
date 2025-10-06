# Ansible Lint Examples and Usage

This document contains comprehensive examples and usage patterns for ansible-lint.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Advanced Options](#advanced-options)
4. [Common Lint Rules](#common-lint-rules)
5. [Configuration Files](#configuration-files)
6. [Integration Examples](#integration-examples)
7. [Best Practices](#best-practices)

## Installation

### Using pip in virtual environment
```bash
# Activate your AWX virtual environment
source ~/awx-venv/bin/activate

# Install ansible-lint
pip install ansible-lint

# Check version
ansible-lint --version
```

### Using system package manager
```bash
# Ubuntu/Debian
sudo apt install ansible-lint

# CentOS/RHEL
sudo yum install ansible-lint

# Fedora
sudo dnf install ansible-lint
```

## Basic Usage

### Lint a single file
```bash
# Lint a specific playbook
ansible-lint configure_new_wsl_instances.yml

# Lint a role
ansible-lint dji_ansible/dji_administration/roles/service_mgmt/

# Lint a specific task file
ansible-lint dji_ansible/dji_administration/roles/service_mgmt/tasks/main.yml
```

### Lint entire collections
```bash
# Lint entire collection
ansible-lint dji_ansible/dji_administration/

# Lint from project root (detects .git directory)
ansible-lint
```

### Verbose output
```bash
# Verbose output
ansible-lint -v configure_new_wsl_instances.yml

# Very verbose output
ansible-lint -vv configure_new_wsl_instances.yml

# Maximum verbosity
ansible-lint -vvv configure_new_wsl_instances.yml
```

## Advanced Options

### Skip specific rules
```bash
# Skip one rule
ansible-lint --skip-list=risky-file-permissions configure_new_wsl_instances.yml

# Skip multiple rules
ansible-lint --skip-list=risky-file-permissions,line-length configure_new_wsl_instances.yml

# Skip all rules of a specific category
ansible-lint --skip-list=risky configure_new_wsl_instances.yml
```

### Include/exclude files
```bash
# Exclude specific files
ansible-lint --exclude=*.retry configure_new_wsl_instances.yml

# Include only specific file types
ansible-lint --include=*.yml configure_new_wsl_instances.yml
```

### Custom configuration
```bash
# Use custom config file
ansible-lint -c .ansible-lint.yml configure_new_wsl_instances.yml

# Use config from different location
ansible-lint -c /path/to/config.yml configure_new_wsl_instances.yml
```

### Output formats
```bash
# JSON output
ansible-lint --format=json configure_new_wsl_instances.yml

# Codeclimate output
ansible-lint --format=codeclimate configure_new_wsl_instances.yml

# PEP8 output
ansible-lint --format=pep8 configure_new_wsl_instances.yml
```

## Common Lint Rules

### Naming and Formatting
```bash
# name[casing] - Task names should be lowercase
ansible-lint --skip-list=name[casing] playbook.yml

# line-length - Lines too long (default 160 characters)
ansible-lint --skip-list=line-length playbook.yml

# yaml[line-length] - YAML line length issues
ansible-lint --skip-list=yaml[line-length] playbook.yml
```

### Security Rules
```bash
# risky-file-permissions - File permissions that are too permissive
ansible-lint --skip-list=risky-file-permissions playbook.yml

# risky-shell-pipe - Dangerous shell pipe usage
ansible-lint --skip-list=risky-shell-pipe playbook.yml

# no-log-password - Password logging in debug messages
ansible-lint --skip-list=no-log-password playbook.yml
```

### Best Practice Rules
```bash
# no-changed-when - Tasks that don't report changed status
ansible-lint --skip-list=no-changed-when playbook.yml

# command-instead-of-shell - Using shell instead of command module
ansible-lint --skip-list=command-instead-of-shell playbook.yml

# package-latest - Using latest package versions
ansible-lint --skip-list=package-latest playbook.yml
```

### Module-specific Rules
```bash
# git - Git module best practices
ansible-lint --skip-list=git playbook.yml

# service - Service module best practices
ansible-lint --skip-list=service playbook.yml

# file - File module best practices
ansible-lint --skip-list=file playbook.yml
```

## Configuration Files

### .ansible-lint.yml
```yaml
# Project root configuration
---
# List of profiles to use
profile: production

# List of rules to skip
skip_list:
  - risky-file-permissions
  - line-length
  - name[casing]

# List of tags to skip
skip_tags:
  - experimental

# List of rules to warn about
warn_list:
  - package-latest

# Exclude files/directories
exclude_paths:
  - .cache/
  - .github/
  - test/fixtures/

# Include files/directories
include_paths:
  - playbooks/
  - roles/

# Verbosity level
verbosity: 1

# Use colored output
colored: true

# Parseable output
parseable: false

# Quiet mode
quiet: false

# Offline mode
offline: false

# Mock modules
mock_modules:
  - custom_module

# Mock roles
mock_roles:
  - custom_role
```

### ansible-lint configuration in galaxy.yml
```yaml
# Collection-level configuration
---
namespace: dji_ansible
name: dji_administration
version: 1.0.0
description: Ansible collection for testing and stopping services
license:
  - MIT-0

# Lint configuration
lint:
  skip_list:
    - risky-file-permissions
    - line-length
  exclude_paths:
    - tests/
    - docs/
```

## Integration Examples

### Pre-commit hooks
```yaml
# .pre-commit-config.yaml
---
repos:
  - repo: https://github.com/ansible/ansible-lint
    rev: v6.22.2
    hooks:
      - id: ansible-lint
        args: [--fix]
        files: \.(yml|yaml)$
        exclude: ^(tests/|docs/)
```

### GitHub Actions
```yaml
# .github/workflows/ansible-lint.yml
name: Ansible Lint

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install ansible-lint
      run: |
        python -m pip install --upgrade pip
        pip install ansible-lint
    
    - name: Run ansible-lint
      run: |
        ansible-lint --version
        ansible-lint dji_ansible/dji_administration/
```

### Makefile integration
```makefile
# Makefile
.PHONY: lint lint-fix test

lint:
	ansible-lint dji_ansible/dji_administration/

lint-fix:
	ansible-lint --fix dji_ansible/dji_administration/

test: lint
	ansible-playbook --check --diff configure_new_wsl_instances.yml
```

### Shell script integration
```bash
#!/bin/bash
# lint.sh

set -e

echo "Running ansible-lint..."

# Activate virtual environment
source ~/awx-venv/bin/activate

# Run linting
ansible-lint -v dji_ansible/dji_administration/

echo "Linting complete!"
```

## Best Practices

### Development Workflow
```bash
# 1. Lint before committing
ansible-lint dji_ansible/dji_administration/

# 2. Fix auto-fixable issues
ansible-lint --fix dji_ansible/dji_administration/

# 3. Address remaining issues manually
ansible-lint -v dji_ansible/dji_administration/

# 4. Test after fixes
ansible-playbook --check --diff configure_new_wsl_instances.yml
```

### Rule Management
```bash
# List all available rules
ansible-lint --list-rules

# List rules by tag
ansible-lint --list-tags

# Show rule descriptions
ansible-lint --help | grep -A 5 "Available rules"
```

### Performance Optimization
```bash
# Lint only changed files
ansible-lint $(git diff --name-only HEAD~1 | grep '\.yml$')

# Use offline mode for faster execution
ansible-lint --offline dji_ansible/dji_administration/

# Exclude test files
ansible-lint --exclude=tests/ dji_ansible/dji_administration/
```

### Continuous Integration
```bash
# Exit on first error
ansible-lint --strict dji_ansible/dji_administration/

# Generate SARIF output for security scanning
ansible-lint --format=sarif dji_ansible/dji_administration/ > results.sarif

# Use specific profile
ansible-lint --profile=production dji_ansible/dji_administration/
```

## Common Issues and Solutions

### Permission Issues
```bash
# Problem: risky-file-permissions
# Solution: Use proper file permissions
- name: Configure sudoers file
  ansible.builtin.template:
    src: sudoers.j2
    dest: "/etc/sudoers.d/{{ awx_user }}-{{ sudoers_type }}"
    mode: '0440'  # Proper permissions
    owner: root
    group: root
```

### Line Length Issues
```bash
# Problem: line-length
# Solution: Break long lines
- name: Configure passwordless sudo (systemctl only)
  ansible.builtin.template:
    src: sudoers.j2
    dest: "/etc/sudoers.d/{{ awx_user }}-systemctl"
    mode: '0440'
    owner: root
    group: root
    validate: 'visudo -cf %s'
```

### Naming Issues
```bash
# Problem: name[casing]
# Solution: Use lowercase task names
- name: configure sudoers file  # lowercase
  ansible.builtin.template:
    src: sudoers.j2
    dest: "/etc/sudoers.d/{{ awx_user }}-{{ sudoers_type }}"
```

## Troubleshooting

### Common Error Messages
```bash
# Rule not found
ansible-lint: error: rule 'nonexistent-rule' not found

# Configuration file not found
ansible-lint: error: config file '.ansible-lint.yml' not found

# Invalid YAML
ansible-lint: error: failed to parse YAML file
```

### Debug Mode
```bash
# Enable debug mode
ansible-lint --debug dji_ansible/dji_administration/

# Show rule details
ansible-lint --list-rules | grep risky-file-permissions
```

### Version Compatibility
```bash
# Check ansible-lint version
ansible-lint --version

# Check ansible version
ansible --version

# Check compatibility
ansible-lint --help | grep "ansible-core"
```
