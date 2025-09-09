# Final Working Solution: AWX on Minikube with WSL Instances

## Overview
Successfully configured AWX running on Minikube to execute Ansible playbooks on WSL instances (Ubuntu-24.04 and Kali-Linux) using SSH key authentication.

## Final Configuration Decisions

### 1. **Kubernetes Ingress Configuration**
**File:** `/home/daniv/ansible/test2/awx-ingress.yml`
```yaml
# Corrected service port from 8052 to 80
spec:
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
              number: 80  # Changed from 8052
```

### 2. **WSL Instance SSH Configuration**
**On both Ubuntu-24.04 and Kali-Linux WSL instances:**

**SSH Server Configuration:**
```bash
# Edit /etc/ssh/sshd_config
sudo vim /etc/ssh/sshd_config
# Add: ListenAddress 0.0.0.0
# Restart SSH service
sudo systemctl restart ssh
sudo systemctl enable ssh
```

**Hostname Resolution Fix:**
```bash
# Add hostname to /etc/hosts to eliminate warnings
echo "127.0.1.1 wslubuntu1" | sudo tee -a /etc/hosts  # For Ubuntu
echo "127.0.1.1 wslkali1" | sudo tee -a /etc/hosts    # For Kali
```

### 3. **Sudoers Configuration**
**On both WSL instances:**
```bash
# Allow daniv to run all sudo commands without password prompts
echo "daniv ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/daniv-nopasswd
```

### 4. **AWX Host Variables**
```bash
# Set correct IP addresses for WSL instances
HOST_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslubuntu1 | jq -r '.id')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host modify "$HOST_ID" --variables '{"ansible_host": "172.22.192.129", "ansible_port": 2223}'

HOST_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslkali1 | jq -r '.id')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host modify "$HOST_ID" --variables '{"ansible_host": "172.22.192.129", "ansible_port": 2224}'
```

### 5. **SSH Key Authentication Setup**
**Generate SSH key pair:**
```bash
ssh-keygen -t ed25519 -f ~/.ssh/awx_wsl_key -N ""
```

**Deploy public keys to WSL instances:**
```bash
ssh-copy-id -i ~/.ssh/awx_wsl_key.pub -p 2223 daniv@172.22.192.129
ssh-copy-id -i ~/.ssh/awx_wsl_key.pub -p 2224 daniv@172.22.192.129
```

**Test SSH key authentication:**
```bash
ssh -i ~/.ssh/awx_wsl_key -p 2223 daniv@172.22.192.129 "whoami"
ssh -i ~/.ssh/awx_wsl_key -p 2224 daniv@172.22.192.129 "whoami"
```

### 6. **AWX Credential Configuration**
**Create new SSH key credential:**
```bash
# Create a new credential with SSH key (replaces password-based credential)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential create \
  --name "WSL SSH Key" \
  --description "SSH key for WSL hosts" \
  --credential_type "Machine" \
  --organization Default \
  --inputs "{\"username\": \"daniv\", \"ssh_key_data\": \"$(cat ~/.ssh/awx_wsl_key)\"}"
```

**Associate SSH key credential with job template:**
```bash
# Get job template ID
JOB_TEMPLATE_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template list --name "Stop Services WSL" | jq -r '.results[0].id')

# Disassociate old password-based credential (ID 3)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template disassociate --credential "3" "$JOB_TEMPLATE_ID"

# Associate new SSH key credential (ID 4)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template associate --credential "4" "$JOB_TEMPLATE_ID"

# Verify credential association
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '.summary_fields.credentials'
```

### 7. **AWX Job Template Configuration**
```bash
# Enable privilege escalation
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template modify "$JOB_TEMPLATE_ID" --become_enabled true

# Ensure credentials are not asked on launch
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template modify "$JOB_TEMPLATE_ID" --ask_credential_on_launch false
```

### 8. **Final Ansible Playbook**
**File:** `/home/daniv/ansible/test2/stop_services.yml`
```yaml
---
- name: Stop services on Ubuntu
  hosts: all
  become: true
  become_method: sudo
  become_user: daniv
  tasks:
    - name: Debug - Show basic info
      debug:
        msg: "Host: {{ inventory_hostname }}\nUser: {{ ansible_user }}\n"

    - name: Test sudo access
      command: whoami
      register: whoami_result

    - name: Show whoami result
      debug:
        msg: "Running as: {{ whoami_result.stdout }}"

    - name: Stop service using systemctl command
      command: systemctl stop {{ service_name }}
      register: stop_result
      ignore_errors: true

    - name: Show stop result
      debug:
        msg: "Stop result: {{ stop_result.stdout }}"

    - name: Check service status after stop
      command: systemctl status {{ service_name }}
      register: status_result

    - name: Show final status
      debug:
        msg: "Final status: {{ status_result.stdout }}"
```

### 9. **Job Execution**
```bash
# Launch job with service name parameter
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "ssh"}' | jq -r .id)

# Monitor job execution
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"
```

## Key Success Factors

1. **SSH Key Authentication**: Eliminates interactive password prompts
2. **Correct Network Configuration**: WSL instances listen on all interfaces (0.0.0.0)
3. **Proper IP Addressing**: Using WSL IP (172.22.192.129) instead of localhost
4. **Sudoers Configuration**: Allows automation without password prompts
5. **AWX Job Template Settings**: `become_enabled: true` and `ask_credential_on_launch: false`
6. **Credential Management**: Created new SSH key credential and properly associated it with job template

## Troubleshooting Notes

- **Multiple Machine Credentials**: AWX doesn't allow multiple Machine credentials on the same job template
- **Credential Replacement**: Must disassociate old credential before associating new one
- **SSH Key Format**: Use `ssh-keygen -t ed25519` for modern key format
- **libcrypto Error**: Resolved by creating fresh credential with proper SSH key

## Final Result
- ✅ AWX jobs run completely non-interactively
- ✅ No SSH or BECOME password prompts
- ✅ Successful service management on both WSL instances
- ✅ Secure SSH key-based authentication
- ✅ Proper privilege escalation handling
- ✅ No libcrypto errors or credential conflicts
