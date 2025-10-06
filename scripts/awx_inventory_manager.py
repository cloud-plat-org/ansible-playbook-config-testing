#!/usr/bin/env python3
"""
AWX Inventory Management Script
"""

import json
import subprocess
import sys
import time
import requests
import urllib3

# Suppress SSL warnings for localhost
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Request timeout in seconds
REQUEST_TIMEOUT = 30

class AWXInventoryManager:
    def __init__(self):
        # Set up authentication token
        self.token = self._get_token()

        # Store connection details
        self.base_url = 'https://localhost'

    def _make_request(self, method, url, timeout=REQUEST_TIMEOUT, **kwargs):
        """Make HTTP request with timeout"""
        kwargs.setdefault('verify', False)
        return requests.request(method, url, timeout=timeout, **kwargs)

    def _get_token(self):
        result = subprocess.run([
            'kubectl', 'get', 'secret', 'awx-admin-password', 
            '-n', 'awx', '-o', 'jsonpath={.data.password}'
        ], capture_output=True, text=True, check=True)
        return subprocess.run(['base64', '-d'],
                            input=result.stdout,
                            capture_output=True, text=True, check=True).stdout.strip()

    def create_inventory(self, name="WSL Lab"):
        """Create or get existing inventory"""
        # First check if inventory already exists
        url = f"{self.base_url}/api/v2/inventories/"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        # Get existing inventories
        response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        inventories = response.json()

        # Check if inventory already exists
        for inv in inventories['results']:
            if inv['name'] == name:
                print(f"Using existing inventory: {inv['name']} (ID: {inv['id']})")
                return inv

        # Create new inventory if it doesn't exist
        data = {
            'name': name,
            'description': 'WSL instances for automation',
            'organization': 1
        }
        response = requests.post(url, json=data, headers=headers,
          verify=False, timeout=REQUEST_TIMEOUT)
        if response.status_code != 201:
            print(f"Error creating inventory: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        inventory = response.json()
        print(f"Inventory created: {inventory['name']} (ID: {inventory['id']})")
        return inventory

    def create_group(self, inventory, group_name="all_servers"):
        """Create or get existing group in inventory"""
        url = f"{self.base_url}/api/v2/groups/"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        # Check if group already exists
        response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        groups = response.json()

        # Check if group already exists in this inventory
        for grp in groups['results']:
            if grp['name'] == group_name and grp['inventory'] == inventory['id']:
                print(f"Using existing group: {grp['name']} (ID: {grp['id']})")
                return grp

        # Create new group if it doesn't exist
        data = {
            'name': group_name,
            'inventory': inventory['id']
        }
        response = requests.post(url, json=data, headers=headers,
          verify=False, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        group = response.json()
        print(f"Group created: {group['name']} (ID: {group['id']})")
        return group

    def add_hosts(self, inventory, config):
        """Add hosts to inventory"""
        hosts = []
        url = f"{self.base_url}/api/v2/hosts/"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        # Get existing hosts first
        response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        existing_hosts = response.json()

        for host_name, port in config.items():
            # Check if host already exists
            existing_host = None
            for host in existing_hosts['results']:
                if host['name'] == host_name and host['inventory'] == inventory['id']:
                    existing_host = host
                    break

            if existing_host:
                print(f"Using existing host: {existing_host['name']} (ID: {existing_host['id']})")
                hosts.append(existing_host)
                continue

            # Create new host
            data = {
                'name': host_name,
                'inventory': inventory['id'],
                'variables': json.dumps({
                    'ansible_host': '172.22.192.129',
                    'ansible_port': port,
                    'ansible_user': 'daniv',
                    'ansible_ssh_private_key_file': '/home/daniv/.ssh/id_rsa'
                })
            }
            response = requests.post(url, json=data, headers=headers,
              verify=False, timeout=REQUEST_TIMEOUT)
            if response.status_code != 201:
                print(f"Error creating host {host_name}: {response.status_code}")
                print(f"Response: {response.text}")
                continue
            host = response.json()
            hosts.append(host)
            print(f"Host created: {host['name']} (ID: {host['id']})")
        return hosts

    def add_hosts_to_group(self, group, hosts):
        """Add hosts to group"""
        url = f"{self.base_url}/api/v2/groups/{group['id']}/hosts/"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        for host in hosts:
            data = {'id': host['id']}
            response = requests.post(url, json=data, headers=headers,
              verify=False, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            print(f"Added {host['name']} to group {group['name']}")

    def create_project(self, name="WSL Automation", scm_type="git",
                      scm_url="https://github.com/cloud-plat-org/ansible-playbook-config-testing",
                      scm_branch="main"): # CLPLAT-2230, main
        """Create or get existing project"""
        url = f"{self.base_url}/api/v2/projects/"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        # Check if project already exists
        response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        projects = response.json()

        # Check if project already exists
        for proj in projects['results']:
            if proj['name'] == name:
                print(f"Using existing project: {proj['name']} (ID: {proj['id']})")
                return proj

        # Create new project if it doesn't exist
        data = {
            'name': name,
            'description': 'WSL automation project',
            'organization': 1,
            'scm_type': scm_type,
            'scm_url': scm_url,
            'scm_branch': scm_branch,
            'scm_update_on_launch': True,
            'scm_clean': True
        }
        response = requests.post(url, json=data, headers=headers,
          verify=False, timeout=REQUEST_TIMEOUT)
        if response.status_code != 201:
            print(f"Error creating project: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        project = response.json()
        print(f"Project created: {project['name']} (ID: {project['id']})")

        # Update the project to sync the repository
        print("Updating project to sync repository...")
        url = f"{self.base_url}/api/v2/projects/{project['id']}/update/"
        update_response = requests.post(url, json=data, headers=headers,
         verify=False, timeout=REQUEST_TIMEOUT)
        if update_response.status_code == 202:
            print("Project update started successfully")
        else:
            print(f"Warning: Project update failed: {update_response.status_code}")

        return project

    def wait_for_project_update(self, project_id, timeout=300):
        """Wait for project update to complete"""
        url = f"{self.base_url}/api/v2/project_updates/"
        headers = {'Authorization': f'Bearer {self.token}'}

        print("Waiting for project update to complete...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            updates = response.json()

            # Find the most recent update for this project
            project_updates = [u for u in updates['results'] if u['project'] == project_id]
            if project_updates:
                latest_update = max(project_updates, key=lambda x: x['id'])
                status = latest_update['status']

                if status == 'successful':
                    print("Project update completed successfully")
                    return True
                if status in ['failed', 'error', 'canceled']:
                    print(f"Project update failed with status: {status}")
                    return False
                print(f"Project update status: {status}")

            time.sleep(5)

        print("Timeout waiting for project update")
        return False

    def create_job_template(self, project, inventory, name="WSL Service Management",
                           playbook="playbooks/service_management.yml"):
        """Create or get existing job template"""
        url = f"{self.base_url}/api/v2/job_templates/"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        # Check if job template already exists
        response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        job_templates = response.json()

        # Check if job template already exists
        for job_template in job_templates['results']:
            if job_template['name'] == name:
                print(f"Using existing job template: {job_template['name']} "
                      f"(ID: {job_template['id']})")
                return job_template

        # Create new job template if it doesn't exist
        data = {
            'name': name,
            'description': 'Service management job template for WSL instances',
            'project': project['id'],
            'inventory': inventory['id'],
            'playbook': playbook,
            'job_type': 'run',
            'verbosity': 0,
            'become_enabled': True,
            'ask_variables_on_launch': True,
            'ask_inventory_on_launch': False,
            'ask_credential_on_launch': False
        }
        response = requests.post(url, json=data, headers=headers,
          verify=False, timeout=REQUEST_TIMEOUT)
        if response.status_code != 201:
            print(f"Error creating job template: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        job_template = response.json()
        print(f"Job template created: {job_template['name']} (ID: {job_template['id']})")
        return job_template

    def delete_project(self, project_name="WSL Automation"):
        """Delete project by name"""
        try:
            url = f"{self.base_url}/api/v2/projects/"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            projects = response.json()

            for proj in projects['results']:
                if proj['name'] == project_name:
                    delete_url = f"{self.base_url}/api/v2/projects/{proj['id']}/"
                    requests.delete(delete_url, headers=headers, verify=False,
                      timeout=REQUEST_TIMEOUT)
                    print(f"Deleted project: {proj['name']}")
                    return True
            print(f"Project '{project_name}' not found")
            return False
        except (ValueError, AttributeError, KeyError, requests.RequestException) as error:
            print(f"Error deleting project: {error}")
            return False

    def delete_job_template(self, template_name="WSL Service Management"):
        """Delete job template by name"""
        try:
            url = f"{self.base_url}/api/v2/job_templates/"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            job_templates = response.json()

            for template in job_templates['results']:
                if template['name'] == template_name:
                    delete_url = f"{self.base_url}/api/v2/job_templates/{template['id']}/"
                    requests.delete(delete_url, headers=headers,
                      verify=False, timeout=REQUEST_TIMEOUT)
                    print(f"Deleted job template: {template['name']}")
                    return True
            print(f"Job template '{template_name}' not found")
            return False
        except (ValueError, AttributeError, KeyError, requests.RequestException) as error:
            print(f"Error deleting job template: {error}")
            return False

    def cleanup_all(self, inventory_name="WSL Lab", project_name="WSL Automation", 
                   template_name="WSL Service Management"):
        """Complete cleanup - deletes inventory, project, and job template"""
        print("Starting complete cleanup...")

        # Delete job template first (depends on project)
        print("\n=== Deleting Job Template ===")
        self.delete_job_template(template_name)

        # Delete project (depends on inventory)
        print("\n=== Deleting Project ===")
        self.delete_project(project_name)

        # Delete inventory, hosts, and groups
        print("\n=== Deleting Inventory ===")
        try:
            # Get inventory by name
            url = f"{self.base_url}/api/v2/inventories/"
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(url, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            inventories = response.json()

            inventory = None
            for inv in inventories['results']:
                if inv['name'] == inventory_name:
                    inventory = inv
                    break

            if inventory:
                # Delete all hosts in inventory
                hosts_url = f"{self.base_url}/api/v2/inventories/{inventory['id']}/hosts/"
                hosts_response = requests.get(hosts_url, headers=headers,
                  verify=False, timeout=REQUEST_TIMEOUT)
                hosts_response.raise_for_status()
                hosts = hosts_response.json()

                for host in hosts['results']:
                    delete_url = f"{self.base_url}/api/v2/hosts/{host['id']}/"
                    requests.delete(delete_url, headers=headers,
                      verify=False, timeout=REQUEST_TIMEOUT)
                    print(f"Deleted host: {host['name']}")

                # Delete all groups in inventory
                groups_url = f"{self.base_url}/api/v2/inventories/{inventory['id']}/groups/"
                groups_response = requests.get(groups_url, headers=headers,
                 verify=False, timeout=REQUEST_TIMEOUT)
                groups_response.raise_for_status()
                groups = groups_response.json()

                for group in groups['results']:
                    delete_url = f"{self.base_url}/api/v2/groups/{group['id']}/"
                    requests.delete(delete_url, headers=headers, verify=False,
                      timeout=REQUEST_TIMEOUT)
                    print(f"Deleted group: {group['name']}")

                # Delete inventory
                delete_url = f"{self.base_url}/api/v2/inventories/{inventory['id']}/"
                requests.delete(delete_url, headers=headers, verify=False,
                  timeout=REQUEST_TIMEOUT)
                print(f"Deleted inventory: {inventory['name']}")
            else:
                print("Inventory not found")
        except (ValueError, AttributeError, KeyError) as error:
            print(f"Cleanup error: {error}")
        except LookupError:
            print("Inventory not found or already deleted")
        
        print("\n=== Cleanup Complete! ===")

def main():
    """Main setup function"""
    main_manager = AWXInventoryManager()

    # Configuration
    main_hosts_config = {
        'ubuntuAWX': 2225,
        'argo_cd_mgt': 2226, 
        'wslkali1': 2224,
        'wslubuntu1': 2223
    }

    print("Starting AWX Complete Setup...")

    # Setup Inventory and Hosts
    print("\n=== Setting up Inventory and Hosts ===")
    inventory = main_manager.create_inventory()
    group = main_manager.create_group(inventory)
    hosts = main_manager.add_hosts(inventory, main_hosts_config)
    main_manager.add_hosts_to_group(group, hosts)

    # Setup Project
    print("\n=== Setting up Project ===")
    project = main_manager.create_project()

    # Wait for project update to complete (if it was created)
    if project and project.get('id'):
        update_success = main_manager.wait_for_project_update(project['id'])
        if not update_success:
            print("Warning: Project update failed, job template creation may fail")

    # Setup Job Template
    print("\n=== Setting up Job Template ===")
    job_template = main_manager.create_job_template(project=project, inventory=inventory)

    print("\n=== Setup Complete! ===")
    print(f"Inventory: {inventory['name']} (ID: {inventory['id']})")
    print(f"Project: {project['name']} (ID: {project['id']})")
    if job_template:
        print(f"Job Template: {job_template['name']} (ID: {job_template['id']})")
    else:
        print("Job Template: Failed to create (project may need to sync first)")
    print(f"Hosts: {', '.join([host['name'] for host in hosts])}")

    return main_manager

# Usage
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Interactive mode - make manager available globally
        print("Starting interactive mode...")
        print("Manager available as 'manager' variable")
        print("Example: manager.cleanup_all()")

        manager = AWXInventoryManager()
        hosts_config = {
            'ubuntuAWX': 2225,
            'argo_cd_mgt': 2226, 
            'wslkali1': 2224,
            'wslubuntu1': 2223
        }

        # Make variables available in interactive mode
        globals()['manager'] = manager
        globals()['hosts_config'] = hosts_config

    else:
        # Normal execution
        main()
