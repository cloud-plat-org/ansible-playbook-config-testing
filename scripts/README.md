# Scripts Directory

This directory contains automation scripts for managing WSL instances and AWX configuration.

## SSH Configuration Script

### `ssh_config.py`

Simple, self-contained SSH configuration script for WSL instances.

**Purpose**: Configures SSH access on individual WSL instances via copy-paste method.

**Features**:
- Self-contained (no external dependencies)
- Installs SSH server
- Configures hostname and SSH port
- Sets up passwordless sudo
- Enables and starts SSH service
- Clear status reporting
- Works within any WSL instance

## Step-by-Step Setup Guide

### Step 1: Copy Script to Each WSL Instance

On each WSL instance that needs SSH configuration:

```bash
vim ssh_config.py
# Copy and paste the content from scripts/ssh_config.py in the repository
```

### Step 2: Configure Each Instance

Make executable and run with hostname and port:

```bash
chmod +x ssh_config.py
python3 ssh_config.py <hostname> <port>
```

### Step 3: Configuration Commands for Each Instance

| Instance | WSL Name | Hostname | Port | Command |
|----------|----------|----------|------|---------|
| Current | Ubuntu | ubuntuAWX | 2225 | `python3 ssh_config.py ubuntuAWX 2225` |
| New | Ubuntu-2 | argo_cd_mgt | 2226 | `python3 ssh_config.py argo_cd_mgt 2226` |
| Existing | Ubuntu-24.04 | wslubuntu1 | 2223 | Already configured |
| Existing | kali-linux | wslkali1 | 2224 | Already configured |

### Step 4: Deploy SSH Keys

After running the script on each instance, from the AWX host:

```bash
# Copy SSH public key to each configured instance
ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p 2225 daniv@172.22.192.129  # ubuntuAWX
ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p 2226 daniv@172.22.192.129  # argo_cd_mgt
```

### Step 5: Test SSH Connections

```bash
# Test connections from AWX host
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2225 daniv@172.22.192.129  # ubuntuAWX
ssh -i ~/.ssh/awx_wsl_key_traditional -p 2226 daniv@172.22.192.129  # argo_cd_mgt
```

### Step 6: Complete Configuration with AWX

Once SSH is working, use AWX to run the configuration playbook:

```bash
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Configure New WSL Instances" \
  --limit "ubuntuAWX,argo_cd_mgt"
```

## What the Script Does

The `ssh_config.py` script automatically:
- Updates package cache
- Installs OpenSSH server
- Configures hostname
- Sets SSH port and security settings
- Creates passwordless sudo access
- Enables and starts SSH service
- Provides verification commands

## Related Files

- **`ssh_config.py`**: SSH configuration script
- **`../configure_new_wsl_instances.yml`**: AWX playbook for post-SSH configuration

## Troubleshooting

### Common Issues
1. **Permission denied**: Ensure you have sudo access
2. **Port already in use**: Check if another service is using the port
3. **SSH service won't start**: Check configuration syntax
4. **Key authentication fails**: Verify SSH key format and permissions

### Verification Commands
```bash
# Check SSH service status
sudo systemctl status ssh

# Check SSH port listening
sudo netstat -tlnp | grep :<port>

# Check hostname
hostname

# Test sudo access
sudo whoami
```
