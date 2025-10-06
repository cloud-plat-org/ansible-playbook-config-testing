# AWX Setup Guide - Complete Documentation Index

## Overview
This comprehensive guide provides step-by-step instructions to set up AWX on Minikube for automating Ansible playbooks on WSL instances using SSH key authentication. This consolidates all lessons learned from successful implementation.

## Quick Start
For experienced users who want to get started quickly:
1. [AWX Interactive Mode](docs/01-AWX-Interactive-Mode.md) - AWX setup and interactive management
2. [Execution Job Test](docs/02-Execution-Job-Test.md) - Job execution and testing procedures

---

## Documentation Structure

### [01-AWX-Interactive-Mode.md](docs/01-AWX-Interactive-Mode.md)
**AWX Setup and Interactive Management**
- SSH credential setup (critical prerequisites)
- AWX inventory management using Python scripts
- Interactive mode for AWX resource management
- Complete setup automation with `awx_inventory_manager.py`
- Troubleshooting and diagnostic procedures

### [02-Execution-Job-Test.md](docs/02-Execution-Job-Test.md)
**Job Execution and Testing Procedures**
- AWX job execution scripts and functions
- Launch options: script variables vs playbook defaults
- Job monitoring and output retrieval
- Diagnostic commands and testing workflows
- SSH credential requirements and setup

---

## Quick Reference

### Essential Commands
```bash
# Start everything
minikube start && minikube tunnel  # Terminal 1
kubectl port-forward svc/awx-service -n awx 443:80  # Terminal 2

# Check status
kubectl get pods -n awx
kubectl get svc -n awx

# AWX CLI
source ~/awx-venv/bin/activate
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me

# Validate YAML files
yamllint .github/workflows/ansible-ci.yml
```

### Access Points
- **Web UI**: https://localhost
- **CLI**: `awx --conf.host https://localhost:443 -k --conf.token "$AWX_TOKEN"`

### Key Files
- **AWX Scripts**: `scripts/awx_inventory_manager.py`, `scripts/awx-job-execution.sh`
- **SSH Key**: `~/.ssh/awx_wsl_key_traditional` (must be uploaded manually to AWX)
- **Playbooks**: `playbooks/service_management.yml`
- **Collections**: `dji_ansible.dji_administration` (custom collection)
- **Automation**: `scripts/ssh_config.py`
- **Inventory**: `inventory/wsl_instances.yml` (commented out - for local testing only)
- **GitHub**: `.github/workflows/ansible-ci.yml`
---

## Success Criteria

This configuration provides:
- **Fully automated AWX deployment** on Minikube
- **SSH key-based authentication** with `awx_wsl_key_traditional`
- **Manual SSH credential setup** through AWX web interface (required)
- **Non-interactive privilege escalation** via sudoers
- **Secure HTTPS access** with self-signed certificates
- **Multi-target automation** across different WSL distributions
- **Custom Ansible collection** for service management
- **Production-ready configuration** with proper error handling

The setup is completely reproducible and eliminates all interactive authentication requirements.

---

## Getting Help

If you encounter issues:
1. Check the [AWX Interactive Mode](docs/01-AWX-Interactive-Mode.md) guide for setup issues
2. Review the [Execution Job Test](docs/02-Execution-Job-Test.md) guide for job execution problems
3. Ensure SSH credentials are created manually through AWX web interface
4. Verify all prerequisites are met and scripts are properly configured

For specific issues, refer to the relevant detailed documentation file or use the diagnostic scripts provided.
