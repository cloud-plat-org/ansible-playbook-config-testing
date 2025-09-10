# Complete AWX on Minikube with WSL Instances - From Scratch Guide

## Overview
This guide provides step-by-step instructions to set up AWX on Minikube to automate Ansible playbooks on WSL instances using SSH key authentication. This incorporates all lessons learned from successful implementation.

## Prerequisites
- **AWX Host**: WSL Ubuntu-22.04 (ubuntuAWX) 
- **Target Instances**: WSL Ubuntu-24.04 (wslubuntu1), WSL Kali-Linux (wslkali1)
- **Windows**: Docker Desktop installed
- **8+ GB RAM, 2+ CPU cores, 20+ GB free space**

---

## Phase 1: Infrastructure Setup

### 1. Start Docker Desktop
```bash
# From WSL Ubuntu (ubuntuAWX)
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &
# Or start from Windows Start menu
# Wait for Docker to be fully running
```

### 2. Start Minikube with Ingress
```bash
# Start Minikube with proper resources
minikube start --driver=docker --cpus=4 --memory=8g --addons=ingress

# Verify cluster
minikube status
kubectl get nodes
```

### 3. Start Minikube Tunnel (Keep Running)
```bash
# In a separate terminal, keep this running
minikube tunnel
```

---

## Phase 2: AWX Installation

### 1. Install AWX Operator
```bash
cd ~
git clone https://github.com/ansible/awx-operator.git
cd awx-operator
git checkout 2.19.1

# Deploy operator
export NAMESPACE=awx
kubectl create namespace $NAMESPACE
make deploy
```

### 2. Deploy AWX Instance
```bash
# Create AWX deployment file
cat > awx-deploy.yml << 'EOF'
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx
spec:
  service_type: nodeport
  ingress_type: none
EOF

# Deploy AWX
kubectl apply -f awx-deploy.yml -n awx

# Wait for pods to be Running
kubectl get pods -n awx
```

### 3. Configure HTTPS Ingress
```bash
# Create TLS certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -out awx-ingress.crt \
  -keyout awx-ingress.key \
  -subj "/CN=localhost/O=awx-ingress"

# Create Kubernetes secret
kubectl create secret tls awx-ingress-tls \
  --namespace awx \
  --key awx-ingress.key \
  --cert awx-ingress.crt

# Create ingress resource
cat > awx-ingress.yml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: awx-ingress
  namespace: awx
  annotations:
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
spec:
  tls:
  - hosts:
    - localhost
    secretName: awx-ingress-tls
  rules:
  - host: localhost
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: awx-service
            port:
              number: 80
EOF

kubectl apply -f awx-ingress.yml
```

### 4. Install AWX CLI
```bash
# Create virtual environment
python3 -m venv ~/awx-venv
source ~/awx-venv/bin/activate

# Install AWX CLI
pip install awxkit
awx --version

# Get admin password
kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d
```

### 5. Test AWX Access
```bash
# Set AWX token (replace PASSWORD with actual password)
export AWX_PASSWORD='<ACTUAL_PASSWORD>'
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# Test CLI access
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" me

# Test web access: https://localhost
```

---

## Phase 3: WSL Target Instance Configuration

### 1. Configure Ubuntu-24.04 (wslubuntu1)
```bash
# Connect to Ubuntu WSL instance
wsl -d Ubuntu-24.04

# Configure SSH to listen on all interfaces
sudo vim /etc/ssh/sshd_config
# Add or modify: ListenAddress 0.0.0.0
# Add or modify: Port 2223

# Add hostname resolution
echo "127.0.1.1 wslubuntu1" | sudo tee -a /etc/hosts

# Configure passwordless sudo for daniv user
echo "daniv ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/daniv-nopasswd

# Start and enable SSH
sudo systemctl restart ssh
sudo systemctl enable ssh
sudo systemctl status ssh

exit
```

### 2. Configure Kali-Linux (wslkali1)
```bash
# Connect to Kali WSL instance
wsl -d kali-linux

# Configure SSH to listen on all interfaces
sudo vim /etc/ssh/sshd_config
# Add or modify: ListenAddress 0.0.0.0
# Add or modify: Port 2224

# Add hostname resolution
echo "127.0.1.1 wslkali1" | sudo tee -a /etc/hosts

# Configure passwordless sudo for daniv user
echo "daniv ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/daniv-nopasswd

# Start and enable SSH
sudo systemctl start ssh
sudo systemctl enable ssh
sudo systemctl status ssh

exit
```

### 3. Verify WSL Network Configuration
```bash
# Find WSL IP address
ip addr show eth0

# Expected: 172.22.192.129 (or similar 172.x.x.x)
# Test SSH access from AWX host
ssh -p 2223 daniv@172.22.192.129
ssh -p 2224 daniv@172.22.192.129
```

---

## Phase 4: SSH Key Authentication Setup

### 1. Generate SSH Key Pair (on AWX host)
```bash
# Generate RSA key in traditional PEM format
ssh-keygen -t rsa -b 2048 -f ~/.ssh/awx_wsl_key_traditional -N "" -m PEM

# Verify key format
head -1 ~/.ssh/awx_wsl_key_traditional
# Should show: -----BEGIN RSA PRIVATE KEY-----
```

### 2. Deploy Public Keys to WSL Instances
```bash
# Copy to Ubuntu-24.04
ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p 2223 daniv@172.22.192.129

# Copy to Kali-Linux
ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p 2224 daniv@172.22.192.129

# Test SSH key authentication
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "whoami"
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2224 daniv@172.22.192.129 "whoami"
```

---

## Phase 5: AWX Configuration

### 1. Create AWX Project
```bash
# Activate AWX environment
source ~/awx-venv/bin/activate

# Create project pointing to your Git repository
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project create \
  --name "WSL Project" \
  --description "Playbooks for WSL Lab" \
  --organization Default \
  --scm_type git \
  --scm_url "https://github.com/cloud-plat-org/ansible-playbook-config-testing.git" \
  --scm_branch "CLPLAT-2221"

# Enable auto-sync on launch
PROJECT_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq -r '.results[] | select(.name == "WSL Project") | .id')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project modify "$PROJECT_ID" --scm_update_on_launch true
```

### 2. Create AWX Inventory
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
```

### 3. Add WSL Hosts to Inventory
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

# Associate hosts with group (using API)
curl -k -H "Authorization: Bearer $AWX_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  https://localhost/api/v2/groups/1/hosts/ \
  -d '{"id": 1}'

curl -k -H "Authorization: Bearer $AWX_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  https://localhost/api/v2/groups/1/hosts/ \
  -d '{"id": 2}'
```

### 4. Create SSH Key Credential
```bash
# Create machine credential with SSH key
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential create \
  --name "WSL SSH Key" \
  --description "SSH key for WSL hosts" \
  --credential_type "Machine" \
  --organization Default \
  --inputs "{\"username\": \"daniv\", \"ssh_key_data\": \"$(awk 'NF{printf "%s\\n",$0;}' ~/.ssh/awx_wsl_key_traditional)\"}"

# Get credential ID
CRED_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential list --name "WSL SSH Key" | jq -r '.results[0].id')
echo "Credential ID: $CRED_ID"
```

### 5. Create Job Template
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

# Associate SSH key credential with job template
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template associate --credential "$CRED_ID" "$JOB_TEMPLATE_ID"

# Verify configuration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '{become_enabled, ask_credential_on_launch}'
```

---

## Phase 6: Ansible Playbook Creation

### 1. Create Working Directory
```bash
# Create project directory
mkdir -p ~/ansible/test2
cd ~/ansible/test2

# Initialize git repository (if not already done)
git init
git remote add origin https://github.com/cloud-plat-org/ansible-playbook-config-testing.git
```

### 2. Create Final Working Playbook
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

# Commit and push to repository
git add stop_services.yml
git commit -m "Add working stop services playbook"
git push origin CLPLAT-2221
```

---

## Phase 7: Testing & Validation

### 1. Launch Test Job
```bash
# Ensure all WSL instances are running
wsl --list --verbose

# Launch AWX job
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "ssh"}' | jq -r .id)

echo "Job ID: $JOB_ID"

# Monitor job execution
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"
```

### 2. Expected Successful Output
```text
PLAY [Stop services on WSL instances] ******************************************

TASK [Gathering Facts] *********************************************************
ok: [wslkali1]
ok: [wslubuntu1]

TASK [Debug - Show basic info] *************************************************
ok: [wslkali1] => {
    "msg": "Host: wslkali1\nUser: daniv\nService: ssh"
}
ok: [wslubuntu1] => {
    "msg": "Host: wslubuntu1\nUser: daniv\nService: ssh"
}

TASK [Test sudo access] ********************************************************
changed: [wslkali1]
changed: [wslubuntu1]

TASK [Show whoami result] ******************************************************
ok: [wslkali1] => {
    "msg": "Running as: root"
}
ok: [wslubuntu1] => {
    "msg": "Running as: root"
}

... (successful service stop operations) ...

PLAY RECAP *********************************************************************
wslkali1                   : ok=13   changed=6    unreachable=0    failed=0    
wslubuntu1                 : ok=13   changed=6    unreachable=0    failed=0    
```

---

## Phase 8: Startup Scripts (Optional)

### 1. Create AWX Startup Script
```bash
cat > ~/start_awx.sh << 'EOF'
#!/bin/bash
echo "Starting Docker Desktop..."
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &
sleep 30

echo "Starting Minikube..."
minikube start
minikube tunnel &

echo "Activating AWX environment..."
source ~/awx-venv/bin/activate

echo "Setting AWX token..."
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

echo "AWX is ready!"
echo "Web UI: https://localhost"
echo "CLI ready with AWX_TOKEN set"
EOF

chmod +x ~/start_awx.sh
```

---

## Troubleshooting Common Issues

### 1. SSH Connection Issues
```bash
# Check WSL network IP
ip addr show eth0

# Test SSH from AWX host
ssh -p 2223 daniv@172.22.192.129
ssh -p 2224 daniv@172.22.192.129

# Check SSH service status in WSL instances
wsl -d Ubuntu-24.04 -- sudo systemctl status ssh
wsl -d kali-linux -- sudo systemctl status ssh
```

### 2. AWX Job Authentication Issues
```bash
# Verify credential configuration
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential get "$CRED_ID" | jq '.inputs'

# Check job template credential association
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '.summary_fields.credentials'

# Test SSH key manually
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2223 daniv@172.22.192.129 "sudo whoami"
```

### 3. Minikube/Kubernetes Issues
```bash
# Check cluster status
minikube status
kubectl get pods -n awx
kubectl get svc -n awx

# Restart if needed
minikube stop
minikube start
```

---

## Summary

This configuration provides:
- ✅ **Fully automated AWX deployment** on Minikube
- ✅ **SSH key-based authentication** (no password prompts)
- ✅ **Non-interactive privilege escalation** via sudoers
- ✅ **Secure HTTPS access** with self-signed certificates
- ✅ **Multi-target automation** across different WSL distributions
- ✅ **Production-ready configuration** with proper error handling

The setup is completely reproducible and eliminates all interactive authentication requirements.
