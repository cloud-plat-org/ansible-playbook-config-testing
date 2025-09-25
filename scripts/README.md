# Scripts Directory

This directory contains automation scripts for managing WSL instances and AWX configuration.

## Available Scripts

### `setup_ssh_connections.py`

Automated SSH connection setup for WSL instances.

**Purpose**: Configures SSH access to WSL instances based on the `wsl_hosts.yml` configuration file.

**Usage**:
```bash
# Show help
python3 scripts/setup_ssh_connections.py --help

# View what would be configured (dry-run)
python3 scripts/setup_ssh_connections.py --dry-run --status pending

# Configure all pending hosts
python3 scripts/setup_ssh_connections.py --status pending

# Configure specific hosts
python3 scripts/setup_ssh_connections.py --hosts ubuntuAWX,argo_cd_mgt

# Verbose output
python3 scripts/setup_ssh_connections.py --verbose --status pending
```

**Features**:
- Reads configuration from `wsl_hosts.yml`
- Installs SSH server on WSL instances
- Configures hostnames and SSH ports
- Deploys SSH keys for authentication
- Tests connectivity
- Dry-run mode for testing
- Flexible host selection
- Comprehensive status reporting

**Prerequisites**:
- WSL instances must be running
- SSH key must exist at `~/.ssh/awx_wsl_key_traditional`
- Python 3 with PyYAML module

**Configuration**:
The script reads host configuration from `../wsl_hosts.yml`. Edit this file to:
- Add new WSL instances
- Modify SSH ports
- Update hostnames
- Change package lists

## Configuration Files

### `../wsl_hosts.yml`
Main configuration file defining:
- WSL instance names and hostnames
- SSH port assignments
- Network configuration
- Package lists
- Host status tracking

## Integration with AWX

After SSH setup completes successfully, use AWX to run the `configure_new_wsl_instances.yml` playbook for complete system configuration.

## Troubleshooting

1. **"WSL instance not running"**: Start the instance with `wsl -d <instance-name>`
2. **"SSH key not found"**: Generate SSH key with documented commands
3. **"Permission denied"**: Check SSH key permissions and WSL instance user access
4. **"Connection refused"**: Verify SSH service is running and port is correct
