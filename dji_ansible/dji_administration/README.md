# Ansible Collection - dji_ansible.dji_administration

This collection provides automation tools for system administration tasks, specifically designed for WSL (Windows Subsystem for Linux) environments and AWX integration.

## Collection Information

- **Author**: Dan Iverson
- **License**: MIT-0
- **Min Ansible Version**: 2.15.0
- **Supported Platforms**: Ubuntu, Debian

## Roles

### service_mgmt

Manages system services (start, stop, restart, status) using systemd.

#### Features

- Start, stop, restart, or check status of system services
- Clean output formatting with service state information
- Verbose debug mode for detailed service information
- Compatible with systemd-based Linux distributions

#### Requirements

- Target hosts must support systemd
- Requires sudo privileges for service management
- Python 3.x on target hosts

#### Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `service_name` | `cron` | Name of the service to manage |
| `service_state` | `stopped` | Desired service state: `started`, `stopped`, `restarted` |
| `debug_extra` | `false` | Enable verbose debug output |

#### Usage Examples

**Basic Service Management:**
```yaml
- name: Manage SSH service
  hosts: all
  become: true
  roles:
    - role: dji_ansible.dji_administration.service_mgmt
      vars:
        service_name: sshd
        service_state: started
```

**Multiple Services:**
```yaml
- name: Manage multiple services
  hosts: all
  become: true
  roles:
    - role: dji_ansible.dji_administration.service_mgmt
      vars:
        service_name: sshd
        service_state: started
    
    - role: dji_ansible.dji_administration.service_mgmt
      vars:
        service_name: cron
        service_state: stopped
```

**With Verbose Debug:**
```yaml
- name: Manage service with debug output
  hosts: all
  become: true
  roles:
    - role: dji_ansible.dji_administration.service_mgmt
      vars:
        service_name: sshd
        service_state: restarted
        debug_extra: true
```

#### Output Examples

**Standard Output:**
```
Service: sshd
Action: started
Changed: YES
Current State: active
Sub State: running
```

**Verbose Output (debug_extra: true):**
```
{
  "changed": true,
  "status": {
    "ActiveState": "active",
    "SubState": "running",
    "LoadState": "loaded"
  }
}
```

## Installation

```bash
# Install from local collection
ansible-galaxy collection install dji_ansible-dji_administration-1.0.0.tar.gz

# Or install from requirements.yml
ansible-galaxy collection install -r requirements.yml
```

## AWX Integration

This collection is designed to work with AWX for automated deployment. See the main project documentation for:

- AWX setup and configuration
- SSH credential management
- Job template creation
- WSL instance management

## License

MIT-0 - See LICENSE file for details.

## Support

For issues and questions, please refer to the main project documentation or create an issue in the project repository.
