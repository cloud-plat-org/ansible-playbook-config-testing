# AWX Integration Guide

This guide explains how to integrate your `dji_ansible.dji_administration` collection with AWX for managing WSL instances.

## Prerequisites

- AWX server running and accessible
- WSL instances configured with SSH access
- SSH keys configured for passwordless access

## AWX Configuration Steps

### 1. **Create Project**

1. Navigate to **Projects** in AWX
2. Click **Add** → **Project**
3. Configure:
   - **Name**: `WSL Management`
   - **Organization**: Select your organization
   - **Source Control Type**: `Git`
   - **Source Control URL**: Your Git repository URL
   - **Branch/Tag/Commit**: `main` (or your branch)
   - **Update Revision on Launch**: ✅ Checked

### 2. **Create Inventory**

1. Navigate to **Inventories** in AWX
2. Click **Add** → **Inventory**
3. Configure:
   - **Name**: `WSL Instances`
   - **Organization**: Select your organization

#### Add Hosts to Inventory:

1. Click **Hosts** tab
2. Click **Add** → **Host**
3. Add each WSL instance:
   - **Name**: `ubuntuAWX`
   - **Variables** (JSON format):
     ```json
     {
       "ansible_host": "192.168.1.100",
       "ansible_port": 2222,
       "ansible_user": "daniv",
       "ansible_ssh_private_key_file": "/home/daniv/.ssh/id_rsa"
     }
     ```

4. Repeat for `argo_cd_mgt` and other instances

#### Create Host Groups:

1. Click **Groups** tab
2. Click **Add** → **Group**
3. Create groups:
   - **Name**: `wsl_instances`
   - **Name**: `service_test_hosts`

### 3. **Create Credentials**

1. Navigate to **Credentials** in AWX
2. Click **Add** → **Credential**
3. Configure:
   - **Name**: `WSL SSH Key`
   - **Credential Type**: `Machine`
   - **Username**: `daniv`
   - **SSH Private Key**: Paste your private key content

### 4. **Create Job Templates**

#### Service Management Template:

1. Navigate to **Templates** in AWX
2. Click **Add** → **Job Template**
3. Configure:
   - **Name**: `Service Management - WSL`
   - **Job Type**: `Run`
   - **Inventory**: `WSL Instances`
   - **Project**: `WSL Management`
   - **Playbook**: `playbooks/service_management.yml`
   - **Credentials**: `WSL SSH Key`
   - **Verbosity**: `1 (Verbose)`
   - **Extra Variables**:
     ```yaml
     service_name: cron
     service_state: stopped
     ```

#### WSL Configuration Template:

1. Click **Add** → **Job Template**
2. Configure:
   - **Name**: `WSL Configuration`
   - **Job Type**: `Run`
   - **Inventory**: `WSL Instances`
   - **Project**: `WSL Management`
   - **Playbook**: `configure_new_wsl_instances.yml`
   - **Credentials**: `WSL SSH Key`
   - **Verbosity**: `1 (Verbose)`

### 5. **Create Workflow Templates** (Optional)

1. Navigate to **Templates** → **Workflows**
2. Click **Add** → **Workflow Template**
3. Configure:
   - **Name**: `WSL Complete Setup`
   - **Organization**: Select your organization
4. Add nodes:
   - **Node 1**: `WSL Configuration` (Run Always)
   - **Node 2**: `Service Management - WSL` (Run on Success)

## Usage Examples

### Run Service Management:

1. Navigate to **Templates**
2. Click **Launch** on `Service Management - WSL`
3. Optionally override variables:
   - `service_name`: `nginx`
   - `service_state`: `started`

### Run WSL Configuration:

1. Click **Launch** on `WSL Configuration`
2. Optionally override variables:
   - `sudoers_type`: `full`
   - `awx_user`: `daniv`

## File Structure for AWX

```
your-repo/
├── playbooks/
│   └── service_management.yml
├── inventory/
│   └── wsl_instances.yml
├── dji_ansible/
│   └── dji_administration/
├── requirements.yml
└── configure_new_wsl_instances.yml
```

## Troubleshooting

### Common Issues:

1. **Collection not found**:
   - Ensure `requirements.yml` is in project root
   - Check AWX project sync status

2. **SSH connection failed**:
   - Verify SSH key is correct
   - Check host IP addresses and ports
   - Ensure SSH service is running on WSL

3. **Permission denied**:
   - Verify sudoers configuration
   - Check `become` settings in playbook

4. **Service not found**:
   - Verify service names are correct
   - Check if services are installed on target hosts

### Debug Commands:

```bash
# Test SSH connection
ssh -i ~/.ssh/id_rsa -p 2222 daniv@192.168.1.100

# Test sudo access
ssh -i ~/.ssh/id_rsa -p 2222 daniv@192.168.1.100 "sudo whoami"

# Check service status
ssh -i ~/.ssh/id_rsa -p 2222 daniv@192.168.1.100 "sudo systemctl status cron"
```

## Best Practices

1. **Use host groups** for different WSL instance types
2. **Set up notifications** for job failures
3. **Use surveys** for interactive variable input
4. **Schedule regular maintenance** jobs
5. **Monitor job history** for troubleshooting

## Next Steps

1. Test the setup with a single WSL instance
2. Gradually add more instances
3. Create additional job templates for specific tasks
4. Set up monitoring and alerting
5. Document any customizations for your environment
