
# Ansible Collection Development Guide

This guide documents the complete process of creating the `dji_ansible.dji_administration` collection with the `service_mgmt` role.

## Step 1: Initialize Collection

In root directory run:
```bash
ansible-galaxy collection init dji_ansible.dji_administration
```

## Step 2: Configure Runtime Requirements

Update the `meta/runtime.yml` file:
```yaml
requires_ansible: '>=2.15.0'
```

## Step 3: Configure Collection Metadata

Fill out `galaxy.yml` with collection information:
- Set namespace and name
- Add description: "Ansible collection for testing and stopping services"
- Set license to MIT-0
- Add author information
- Configure repository URLs
- Set license_file to LICENSE

## Step 4: Create Service Management Role

Create the role structure:
```bash
cd dji_ansible/dji_administration/roles/
ansible-galaxy role init service_mgmt
```

## Step 5: Develop Role Content

### Tasks (`roles/service_mgmt/tasks/main.yml`)
```yaml
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

### Defaults (`roles/service_mgmt/defaults/main.yml`)
```yaml
---
service_name: cron
service_state: stopped
```

### Role Metadata (`roles/service_mgmt/meta/main.yml`)
- Set author: Dan Iverson
- Set description: Manage system services (start, stop, restart, status)
- Set license: MIT-0
- Set min_ansible_version: 2.15.0
- Add platforms: Debian 12, Ubuntu 20.04/22.04/24.04, RHEL/CentOS 8/9
- Add tags: service, management, systemd, restart, stop, start, status

### Documentation (`roles/service_mgmt/README.md`)
- Professional README with usage examples
- Platform support information
- Variable documentation
- Multiple playbook examples

## Step 6: Test the Role

Create test playbooks to verify functionality:
```bash
# Test stopping a service
ansible-playbook test_service_lifecycle.yml
```

## Step 7: AWX Integration Setup

### Create Inventory (`inventory/wsl_instances.yml`)
```bash
mkdir inventory
```

Create inventory file for WSL instances:
```yaml
# inventory/wsl_instances.yml
---
all:
  children:
    wsl_instances:
      hosts:
        ubuntuAWX:
          ansible_host: 192.168.1.100
          ansible_port: 2222
          ansible_user: daniv
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
          
        argo_cd_mgt:
          ansible_host: 192.168.1.101
          ansible_port: 2223
          ansible_user: daniv
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
          
      vars:
        ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
        ansible_python_interpreter: /usr/bin/python3
        awx_user: daniv
        sudoers_type: "systemctl"
        
    service_test_hosts:
      hosts:
        ubuntuAWX:
        argo_cd_mgt:
      vars:
        service_mgmt_service_name: cron
        service_mgmt_service_state: stopped
```

### Create Playbooks (`playbooks/service_management.yml`)
```bash
mkdir playbooks
```

Create playbook using the collection:
```yaml
# playbooks/service_management.yml
---
- name: Manage services on WSL instances
  hosts: service_test_hosts
  become: true
  become_method: ansible.builtin.sudo
  gather_facts: true
  
  vars:
    service_mgmt_service_name: "{{ service_name | default('cron') }}"
    service_mgmt_service_state: "{{ service_state | default('stopped') }}"
    
  roles:
    - role: dji_ansible.dji_administration.service_mgmt
      
  post_tasks:
    - name: Verify service state
      ansible.builtin.systemd:
        name: "{{ service_mgmt_service_name }}"
      register: final_service_state
```

### Update Requirements (`requirements.yml`)
```yaml
collections:
  - name: community.general
    version: ">=7.0.0"
    
  - name: ansible.posix
    version: ">=1.5.0"
    
  # Local collection for service management
  - name: dji_ansible.dji_administration
    source: "{{ playbook_dir }}/dji_ansible/dji_administration"
    type: dir
```

## Step 8: Build and Install Collection

Build the collection:
```bash
cd dji_ansible/dji_administration/
ansible-galaxy collection build --force
```

Install locally:
```bash
ansible-galaxy collection install dji_ansible-dji_administration-1.0.0.tar.gz
```

## Project Structure

### Collection Structure
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
│   ├── ansible-lint-examples.md
│   └── galaxy_tagging.md
└── LICENSE
```

### Complete Project Structure
```
test2/
├── inventory/
│   └── wsl_instances.yml          # WSL instance inventory
├── playbooks/
│   └── service_management.yml     # Playbook using collection
├── dji_ansible/
│   └── dji_administration/         # Collection source
├── requirements.yml               # Collection dependencies
├── configure_new_wsl_instances.yml # Existing WSL config playbook
├── docs/
│   └── awx-integration.md         # AWX setup guide
└── .ansible-lint                  # Linting configuration
```

## Why External Directories?

### `inventory/` Directory
- **Purpose**: Contains host definitions and groups for AWX
- **Location**: Outside collection because it's environment-specific
- **Reasoning**: 
  - Collections are reusable across environments
  - Inventory contains your specific WSL instance IPs/ports
  - AWX expects inventory files at project root level

### `playbooks/` Directory
- **Purpose**: Contains playbooks that use the collection
- **Location**: Outside collection because it's use-case specific
- **Reasoning**:
  - Collections provide roles/modules, not complete workflows
  - Playbooks combine collections for specific scenarios
  - AWX scans for playbooks at project root level

### `requirements.yml` 
- **Purpose**: Tells AWX which collections to install
- **Location**: At project root for AWX to discover
- **Reasoning**: AWX requirement for collection dependencies

## Directory Separation Benefits

1. **Reusability**: Collection can be used by different teams/environments
2. **AWX Compatibility**: Standard directory structure AWX expects
3. **Separation of Concerns**: 
   - Collection = Reusable components
   - Playbook = Specific workflows
   - Inventory = Environment configuration
4. **Version Control**: Different parts can be versioned independently

## Documentation

- [Collection Development Guide](collections.md) - This file
- [Examples and Tools](examples-and-tools.md) - Template and role examples
- [Ansible Lint Examples](ansible-lint-examples.md) - Linting guidelines
- [Galaxy Tagging Guide](galaxy_tagging.md) - Tag requirements and selection
