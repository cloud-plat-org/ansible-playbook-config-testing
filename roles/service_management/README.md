# Service Management Role

A streamlined, production-ready Ansible role for managing systemd services.

## Features

- **Clean Output**: No debug clutter in production
- **Multiple Actions**: start, stop, restart, enable, disable, status
- **Efficient Design**: Single task file with conditional execution
- **Production Ready**: Follows Ansible best practices
- **Error Handling**: Graceful handling of service operations

## Usage

### Basic Service Lifecycle Example

```yaml
---
- name: Stop service on target hosts
  hosts: all
  become: true
  become_method: sudo
  roles:
    - service_management
  vars:
    service_name: "{{ target_service | default('cron') }}"
    service_action: "stop"

- name: Start service on target hosts
  hosts: all
  become: true
  become_method: sudo
  roles:
    - service_management
  vars:
    service_name: "{{ target_service | default('cron') }}"
    service_action: "start"
```

### Single Service Operations

```yaml
---
- name: Restart nginx service
  hosts: webservers
  become: true
  roles:
    - service_management
  vars:
    service_name: "nginx"
    service_action: "restart"
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `service_name` | `""` | Name of the service to manage (required) |
| `service_action` | `"status"` | Action: start, stop, restart, enable, disable, status |

## AWX Job Template Usage

```bash
# Launch with variable service name
awx job_template launch --job_template "Service Management" \
  --extra_vars '{"target_service": "cron"}'

# Available service actions
--extra_vars '{"target_service": "nginx", "service_action": "restart"}'
```

## Role Structure

```
roles/service_management/
├── defaults/main.yml      # Default variables
├── meta/main.yml          # Role metadata  
├── tasks/main.yml         # Consolidated service management logic
└── README.md             # This documentation
```

## Production Benefits

1. **Clean Output**: Only essential task information displayed
2. **Fast Execution**: Single task file, no unnecessary includes
3. **Maintainable**: Simple, focused codebase
4. **Reliable**: Uses systemd module directly
5. **Scalable**: Works with any systemd service