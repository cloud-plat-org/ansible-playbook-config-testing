# Service Management Role

A flexible Ansible role for managing systemd services using systemctl commands.

## Features

- **Multiple Actions**: start, stop, restart, enable, disable, status
- **Debug Mode**: Optional verbose output for troubleshooting
- **Multiple Services**: Support for managing multiple services in one playbook
- **Error Handling**: Graceful handling of service errors
- **Flexible Configuration**: Easy to customize for different use cases

## Usage

### Basic Usage

```yaml
---
- name: Stop SSH service
  hosts: all
  become: true
  become_method: sudo
  roles:
    - service_management
  vars:
    service_name: "ssh"
    service_action: "stop"
```

### With Debug Mode

```yaml
---
- name: Manage service with debug output
  hosts: all
  become: true
  become_method: sudo
  roles:
    - service_management
  vars:
    service_name: "ssh"
    service_action: "restart"
    debug_mode: true
```

### Multiple Services

```yaml
---
- name: Manage multiple services
  hosts: all
  become: true
  become_method: sudo
  roles:
    - service_management
  vars:
    service_name: "ssh"
    service_action: "stop"
    service_actions:
      - "stop"  # Additional services
      - "restart"
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `service_name` | `""` | Name of the service to manage (required) |
| `service_action` | `"status"` | Action to perform: start, stop, restart, enable, disable, status |
| `debug_mode` | `false` | Enable debug output |
| `service_actions` | `[]` | List of additional actions for multiple services |

## Examples

### Check Service Status
```bash
ansible-playbook service_management.yml -e "service_name=ssh service_action=status"
```

### Stop Service
```bash
ansible-playbook service_management.yml -e "service_name=ssh service_action=stop debug_mode=true"
```

### Restart Service
```bash
ansible-playbook service_management.yml -e "service_name=ssh service_action=restart"
```

### Enable Service
```bash
ansible-playbook service_management.yml -e "service_name=ssh service_action=enable"
```

## Role Structure

```
roles/service_management/
├── defaults/main.yml      # Default variables
├── meta/main.yml          # Role metadata
├── tasks/
│   ├── main.yml          # Main orchestration
│   ├── start.yml         # Start service tasks
│   ├── stop.yml          # Stop service tasks
│   ├── restart.yml       # Restart service tasks
│   ├── enable.yml        # Enable service tasks
│   ├── disable.yml       # Disable service tasks
│   └── status.yml        # Check status tasks
└── README.md             # This file
```

## Benefits Over Monolithic Playbooks

1. **Reusability**: Use the same role for different services
2. **Maintainability**: Easy to update individual actions
3. **Testability**: Test individual components separately
4. **Flexibility**: Mix and match actions as needed
5. **Best Practices**: Follows Ansible role conventions
6. **Documentation**: Self-documenting with clear structure