# Ansible Collection Examples and Tools Guide

This document contains practical examples and tool usage for the `dji_ansible.dji_administration` collection.

## Table of Contents

1. [Template Examples](#template-examples)
2. [Role Structure Examples](#role-structure-examples)
3. [Playbook Examples](#playbook-examples)
4. [Service Management Examples](#service-management-examples)
5. [Collection Development Workflow](#collection-development-workflow)

## Template Examples

### Sudoers Configuration Template

**File:** `templates/sudoers.j2`
```jinja2
#SPDX-License-Identifier: MIT
{% if sudoers_type == "full" %}
{{ awx_user }} ALL=(ALL) NOPASSWD: ALL
{% elif sudoers_type == "systemctl" %}
{{ awx_user }} ALL=(ALL) NOPASSWD: /bin/systemctl stop *, /bin/systemctl start *, /bin/systemctl restart *, /bin/systemctl status *, /bin/systemctl enable *, /bin/systemctl disable *
{% elif sudoers_type == "minimal" %}
{{ awx_user }} ALL=(ALL) NOPASSWD: /bin/systemctl stop cron, /bin/systemctl start cron, /bin/systemctl restart cron, /bin/systemctl status cron
{{ awx_user }} ALL=(ALL) NOPASSWD: /bin/systemctl stop systemd-resolved, /bin/systemctl start systemd-resolved, /bin/systemctl restart systemd-resolved, /bin/systemctl status systemd-resolved
{{ awx_user }} ALL=(ALL) NOPASSWD: /bin/systemctl stop systemd-networkd, /bin/systemctl start systemd-networkd, /bin/systemctl restart systemd-networkd, /bin/systemctl status systemd-networkd
{% endif %}
```

**Usage in Playbook:**
```yaml
- name: Configure sudoers file
  ansible.builtin.template:
    src: sudoers.j2
    dest: "/etc/sudoers.d/{{ awx_user }}-{{ sudoers_type }}"
    mode: '0440'
    owner: root
    group: root
    validate: 'visudo -cf %s'
  register: sudoers_result
```

### System Summary Template

**File:** `templates/system-summary.j2`
```jinja2
#SPDX-License-Identifier: MIT
[SUCCESS] Configuration Summary for {{ inventory_hostname }}:

System: {{ system_summary.hostname }} ({{ system_summary.distribution }})
SSH Port: {{ system_summary.ssh_port }}
SSH Service: {{ system_summary.ssh_service }}
Sudo Access: {{ system_summary.sudo_access }}
Packages Updated: {{ system_summary.packages_updated }}
Sudoers Configured: {{ system_summary.sudoers_configured }}
Timezone Configured: {{ system_summary.timezone_configured }}
Kernel Optimized: {{ system_summary.sysctl_optimized }}
SSH Keys Managed: {{ system_summary.ssh_key_managed }}

Status: Ready for AWX service management!
```

### Service Test Results Template

**File:** `templates/service-test-results.j2`
```jinja2
#SPDX-License-Identifier: MIT
Service Management Test Results for {{ inventory_hostname }}:

Service: {{ test_service }}
Initial State: {{ initial_status.status.ActiveState | default('unknown') }}
Stop Operation: {{ 'SUCCESS' if stop_result.changed else 'FAILED' }}
Start Operation: {{ 'SUCCESS' if start_result.changed else 'FAILED' }}
Final State: {{ final_status.status.ActiveState | default('unknown') }}

Result: {{ 'PASS [SUCCESS]' if (final_status.status.ActiveState == 'active') else 'FAIL FAIL' }}
```

## Role Structure Examples

### Service Management Role Tasks

**File:** `roles/service_mgmt/tasks/main.yml`
```yaml
#SPDX-License-Identifier: MIT
---
- name: Stop service "{{ service_name }}", if started
  ansible.builtin.service:
    name: "{{ service_name }}"
    state: "{{ service_state }}"
  register: stop_result

- name: Show service output
  ansible.builtin.debug:
    msg: "{{ stop_result }}"
```

### Role Defaults

**File:** `roles/service_mgmt/defaults/main.yml`
```yaml
#SPDX-License-Identifier: MIT
---
service_name: cron
service_state: stopped
```

### Role Variables

**File:** `roles/service_mgmt/vars/main.yml`
```yaml
#SPDX-License-Identifier: MIT
---
# Internal role variables (not meant to be overridden)
service_config_dir: /etc/systemd/system
service_log_dir: /var/log
```

### Role Metadata

**File:** `roles/service_mgmt/meta/main.yml`
```yaml
#SPDX-License-Identifier: MIT
galaxy_info:
  author: Dan Iverson
  description: Manage system services (start, stop, restart, status)
  company: Your Computer Guy
  license: MIT-0
  min_ansible_version: 2.15.0

  platforms:
    - name: EL
      versions:
        - 7
        - 8
        - 9
    - name: Ubuntu
      versions:
        - 20.04
        - 22.04
        - 24.04
    - name: Debian
      versions:
        - 10
        - 11
        - 12

  galaxy_tags:
    - service
    - management
    - systemd
    - restart
    - stop
    - start
    - status

dependencies: []
```

## Playbook Examples

### Basic Service Management

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

### WSL Configuration with Templates

```yaml
---
- name: Configure new WSL instances for AWX management
  hosts: all
  become: true
  become_method: ansible.builtin.sudo
  gather_facts: true
  vars:
    awx_user: "daniv"
    sudoers_type: "systemctl"  # Options: "full", "systemctl", "minimal"
    essential_packages:
      - curl
      - wget
      - git
      - vim
      - jq
      - openssl
      - htop
      - tree
      - unzip

  tasks:
    - name: Configure sudoers file
      ansible.builtin.template:
        src: sudoers.j2
        dest: "/etc/sudoers.d/{{ awx_user }}-{{ sudoers_type }}"
        mode: '0440'
        owner: root
        group: root
        validate: 'visudo -cf %s'
      register: sudoers_result

    - name: Install essential packages
      ansible.builtin.apt:
        name: "{{ essential_packages }}"
        state: present
      register: package_install
      failed_when: false

    - name: Display configuration summary
      ansible.builtin.debug:
        msg: |
          [SUCCESS] Configuration Summary for {{ inventory_hostname }}:
          Sudoers Configured: {{ sudoers_result.changed | default(false) }}
          Packages Updated: {{ package_install.changed | default(false) }}
          Status: Ready for AWX service management!
```

## Service Management Examples

### Using the Service Management Role

```yaml
# Test service management capabilities
- name: Test service management
  hosts: ubuntuAWX,argo_cd_mgt
  become: true
  become_method: ansible.builtin.sudo
  gather_facts: false
  vars:
    test_service: "cron"

  tasks:
    - name: Test service management - Get current status
      ansible.builtin.systemd:
        name: "{{ test_service }}"
      register: initial_status
      failed_when: false

    - name: Test service management - Stop service
      ansible.builtin.systemd:
        name: "{{ test_service }}"
        state: stopped
      register: stop_result
      failed_when: false

    - name: Test service management - Start service
      ansible.builtin.systemd:
        name: "{{ test_service }}"
        state: started
      register: start_result
      failed_when: false
```

## Collection Development Workflow

### 1. Initialize Collection
```bash
ansible-galaxy collection init dji_ansible.dji_administration
```

### 2. Configure Runtime Requirements
```yaml
# meta/runtime.yml
requires_ansible: '>=2.15.0'
```

### 3. Configure Collection Metadata
```yaml
# galaxy.yml
namespace: dji_ansible
name: dji_administration
version: 1.0.0
description: Ansible collection for testing and stopping services
license:
  - MIT-0
license_file: LICENSE
```

### 4. Create Role
```bash
cd dji_ansible/dji_administration/roles/
ansible-galaxy role init service_mgmt
```

### 5. Develop Role Content
- Add tasks to `roles/service_mgmt/tasks/main.yml`
- Define variables in `roles/service_mgmt/defaults/main.yml`
- Create templates in `roles/service_mgmt/templates/`
- Add handlers in `roles/service_mgmt/handlers/main.yml`

### 6. Test with Lint
```bash
# Activate environment
source ~/awx-venv/bin/activate

# Lint collection
ansible-lint dji_ansible/dji_administration/

# Lint specific files
ansible-lint dji_ansible/dji_administration/roles/service_mgmt/tasks/main.yml
```

### 7. Build Collection
```bash
cd dji_ansible/dji_administration/
ansible-galaxy collection build
```

### 8. Install Collection
```bash
ansible-galaxy collection install dji_ansible-dji_administration-1.0.0.tar.gz
```

## Collection Structure

```
dji_ansible/dji_administration/
├── galaxy.yml
├── meta/
│   └── runtime.yml
├── roles/
│   └── service_mgmt/
│       ├── defaults/main.yml
│       ├── handlers/main.yml
│       ├── meta/main.yml
│       ├── tasks/main.yml
│       ├── templates/
│       │   ├── sudoers.j2
│       │   ├── system-summary.j2
│       │   └── service-test-results.j2
│       ├── vars/main.yml
│       └── README.md
├── docs/
│   ├── collections.md
│   ├── examples-and-tools.md
│   └── galaxy_tagging.md
└── LICENSE
```

## Best Practices

### Template Best Practices
- Always include SPDX license identifier
- Use descriptive variable names
- Add comments for complex logic
- Test templates with different variable values

### Role Best Practices
- Use `defaults/` for user-configurable variables
- Use `vars/` for role-internal constants
- Document all variables in README
- Include platform support information

### Playbook Best Practices
- Use `become: true` for system operations
- Include error handling with `failed_when: false`
- Use descriptive task names
- Register results for conditional logic

### Development Best Practices
- Use descriptive task names
- Include error handling with `failed_when: false`
- Register results for conditional logic
- Test templates with different variable values
