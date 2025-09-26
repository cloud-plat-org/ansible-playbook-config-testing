# AWX Setup Guide - Complete Documentation Index

## Overview
This comprehensive guide provides step-by-step instructions to set up AWX on Minikube for automating Ansible playbooks on WSL instances using SSH key authentication. This consolidates all lessons learned from successful implementation.

## Quick Start
For experienced users who want to get started quickly:
1. [Prerequisites](docs/01-Prerequisites.md) - System requirements, tools, and WSL configuration
2. [Infrastructure Setup](docs/02-Infrastructure-Setup.md) - Docker, Minikube, tools installation
3. [AWX Installation](docs/03-AWX-Installation.md) - AWX operator, deployment, HTTPS
4. [SSH Authentication](docs/04-SSH-Authentication.md) - SSH keys, credential setup
5. [AWX Configuration](docs/05-AWX-Configuration.md) - Projects, inventory, job templates
6. [Playbook Development](docs/06-Playbook-Development.md) - Ansible playbooks
7. [Testing & Validation](docs/07-Testing-Validation.md) - Job testing, expected outputs
8. [Daily Operations](docs/08-Daily-Operations.md) - Startup scripts, maintenance
9. [Troubleshooting](docs/09-Troubleshooting.md) - Common issues and solutions

---

## Documentation Structure

### [01-Prerequisites.md](docs/01-Prerequisites.md)
**System Requirements, Tools & WSL Configuration**
- Hardware requirements (RAM, CPU, storage)
- Software prerequisites (Docker Desktop, WSL)
- Required tools (kubectl, jq, git, openssl)
- WSL instance configuration (Ubuntu-24.04, Kali-Linux)
- SSH service setup and passwordless sudo

### [02-Infrastructure-Setup.md](docs/02-Infrastructure-Setup.md)
**Docker, Minikube & Tools Installation**
- Docker Desktop startup
- Minikube installation and configuration
- Required tools installation
- Network and tunnel setup

### [03-AWX-Installation.md](docs/03-AWX-Installation.md)
**AWX Operator & Instance Deployment**
- AWX Operator installation
- AWX instance deployment
- HTTPS ingress configuration
- AWX CLI setup and testing

### [04-SSH-Authentication.md](docs/04-SSH-Authentication.md)
**SSH Key Authentication Setup**
- SSH key pair generation
- Public key deployment
- Authentication testing
- Key format verification

### [05-AWX-Configuration.md](docs/05-AWX-Configuration.md)
**AWX Projects, Inventory & Templates**
- Project creation and Git integration
- Inventory and host group setup
- Host addition and configuration
- Credential and job template creation

### [06-Playbook-Development.md](docs/06-Playbook-Development.md)
**Ansible Playbook Creation**
- Working directory setup
- Playbook development
- Git repository integration
- Best practices and patterns

### [07-Testing-Validation.md](docs/07-Testing-Validation.md)
**Job Testing & Validation**
- Test job execution
- Expected output verification
- Troubleshooting test failures
- Performance validation

### [08-Daily-Operations.md](docs/08-Daily-Operations.md)
**Startup Scripts & Maintenance**
- Daily startup workflow
- Automation scripts
- Maintenance procedures
- Monitoring and health checks

### [09-Troubleshooting.md](docs/09-Troubleshooting.md)
**Common Issues & Solutions**
- Minikube connection issues
- SSH authentication problems
- AWX job failures
- Network and service issues

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
```

### Access Points
- **Web UI**: https://localhost
- **CLI**: `awx --conf.host https://localhost:443 -k --conf.token "$AWX_TOKEN"`

### Key Files
- **AWX Config**: `awx-deploy.yml`, `awx-ingress.yml`
- **SSH Key**: `~/.ssh/awx_wsl_key_traditional`
- **Playbooks**: `test_service_lifecycle.yml` (modern collections-based), `configure_new_wsl_instances.yml` (production-ready with collections)
- **Collections**: `requirements.yml` (Ansible collections: `community.general`, `ansible.posix`)
- **Automation**: `scripts/ssh_config.py` (simple SSH setup script)
- **Standards**: `CODING_STANDARDS.md` (project coding and documentation standards)
- **Startup Script**: `~/start_awx.sh`
---

## Success Criteria

This configuration provides:
- **Fully automated AWX deployment** on Minikube
- **SSH key-based authentication** (no password prompts)
- **Non-interactive privilege escalation** via sudoers
- **Secure HTTPS access** with self-signed certificates
- **Multi-target automation** across different WSL distributions
- **Production-ready configuration** with proper error handling

The setup is completely reproducible and eliminates all interactive authentication requirements.

---

## Getting Help

If you encounter issues:
1. Check the [Troubleshooting](docs/09-Troubleshooting.md) guide first
2. Verify each phase was completed successfully
3. Check the logs and status of all components
4. Ensure all prerequisites are met

For specific issues, refer to the relevant detailed documentation file.


######################################################################
## Quick Start

### 1. Clone and Setup
```bash
cd ~/ansible/test2

# Install Ansible collections
ansible-galaxy collection install -r requirements.yml

# Test syntax
ansible-playbook --syntax-check test_service_lifecycle.yml
ansible-playbook --syntax-check configure_new_wsl_instances.yml
```

### 2. Run Playbooks
```bash
# Test service lifecycle (safe - uses cron by default)
ansible-playbook test_service_lifecycle.yml -i inventory.yml

# Configure new WSL instances (comprehensive setup)
ansible-playbook configure_new_wsl_instances.yml -i inventory.yml
```

### 3. AWX Integration
```bash
# Launch via AWX job template
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Test Service Lifecycle WSL" --extra_vars '{"target_service": "cron"}'
```
```
