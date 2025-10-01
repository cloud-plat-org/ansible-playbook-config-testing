
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

## Step 7: Build and Install Collection

Build the collection:
```bash
cd dji_ansible/dji_administration/
ansible-galaxy collection build
```

Install locally:
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
│       ├── vars/main.yml
│       └── README.md
├── docs/
│   └── collections.md
└── LICENSE
```
