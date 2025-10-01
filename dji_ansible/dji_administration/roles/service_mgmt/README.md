# Service Management Role

A simple Ansible role for managing system services (start, stop, restart, status).git 

## Description

This role provides a standardized way to manage system services across different Linux distributions. It uses the built-in `ansible.builtin.service` module to handle service operations.

## Requirements

- Ansible 2.15.0 or higher
- Target systems must use systemd (systemctl)
- Root privileges (use `become: true`)

## Role Variables

Available variables are listed below, along with default values:

| Variable | Default | Description |
|----------|---------|-------------|
| `service_name` | `cron` | Name of the service to manage |
| `service_state` | `stopped` | Desired state of the service (`started`, `stopped`, `restarted`, `reloaded`) |

## Dependencies

None. This role uses only Ansible built-in modules.

## Example Playbooks

### Basic Usage

```yaml
---
- hosts: localhost
  become: true
  roles:
    - role: service_mgmt
      vars:
        service_name: nginx
        service_state: started
```

### Stop a Service

```yaml
---
- hosts: webservers
  become: true
  roles:
    - role: service_mgmt
      vars:
        service_name: apache2
        service_state: stopped
```

### Restart Multiple Services

```yaml
---
- hosts: all
  become: true
  tasks:
    - name: Restart SSH service
      include_role:
        name: service_mgmt
      vars:
        service_name: ssh
        service_state: restarted
    
    - name: Restart NTP service
      include_role:
        name: service_mgmt
      vars:
        service_name: ntp
        service_state: restarted
```

## Platform Support

- Debian 12
- Ubuntu 20.04, 22.04, 24.04
- RHEL/CentOS 8, 9
- Kali Linux Rolling

## License

MIT-0

## Author Information

Created by Dan Iverson - Your Computer Guy
