#!/usr/bin/env python3
"""
AWX Inventory Management Script
"""

import json
import subprocess
import sys
try:
    from awxkit.api import AWXKit  # type: ignore
except ImportError:
    print("Error: awxkit not found. Please activate AWX virtual environment:")
    print("source ~/awx-venv/bin/activate")
    sys.exit(1)

class AWXInventoryManager:
    def __init__(self):
        self.awx = AWXKit(
            host='https://localhost',
            token=self._get_token(),
            verify=False
        )

    def _get_token(self):
        result = subprocess.run([
            'kubectl', 'get', 'secret', 'awx-admin-password', 
            '-n', 'awx', '-o', 'jsonpath={.data.password}'
        ], capture_output=True, text=True, check=True)
        return subprocess.run(['base64', '-d'],
                            input=result.stdout,
                            capture_output=True, text=True, check=True).stdout.strip()

    def create_inventory(self, name="WSL Lab"):
        """Create inventory"""
        inventory = self.awx.inventories.create({
            'name': name,
            'description': 'WSL instances for automation',
            'organization': 1
        })
        print(f"Inventory created: {inventory.name} (ID: {inventory.id})")
        return inventory

    def create_group(self, inventory, group_name="all_servers"):
        """Create group in inventory"""
        group = inventory.related.groups.create({
            'name': group_name
        })
        print(f"Group created: {group.name} (ID: {group.id})")
        return group

    def add_hosts(self, inventory, config):
        """Add hosts to inventory"""
        hosts = []
        for host_name, port in config.items():
            host = inventory.related.hosts.create({
                'name': host_name,
                'variables': json.dumps({
                    'ansible_host': '172.22.192.129',
                    'ansible_port': port,
                    'ansible_user': 'daniv',
                    'ansible_ssh_private_key_file': '/home/daniv/.ssh/id_rsa'
                })
            })
            hosts.append(host)
            print(f"Host created: {host.name} (ID: {host.id})")
        return hosts

    def add_hosts_to_group(self, group, hosts):
        """Add hosts to group - THIS WORKS IN PYTHON!"""
        for host in hosts:
            group.related.hosts.create(host)
            print(f"Added {host.name} to group {group.name}")

    def cleanup_all(self, inventory_name="WSL Lab"):
        """Complete cleanup"""
        try:
            inventory = self.awx.inventories.get(name=inventory_name)
            # Delete all hosts in inventory
            for host in inventory.related.hosts.get():
                host.delete()
                print(f"Deleted host: {host.name}")
            # Delete all groups in inventory
            for group in inventory.related.groups.get():
                group.delete()
                print(f"Deleted group: {group.name}")
            # Delete inventory
            inventory.delete()
            print(f"Deleted inventory: {inventory.name}")
        except (ValueError, AttributeError, KeyError) as error:
            print(f"Cleanup error: {error}")
        except LookupError:
            print("Inventory not found or already deleted")

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

    print("Starting AWX Inventory Setup...")

    # Setup
    inventory = main_manager.create_inventory()
    group = main_manager.create_group(inventory)
    hosts = main_manager.add_hosts(inventory, main_hosts_config)
    main_manager.add_hosts_to_group(group, hosts)  # This actually works!

    print("Setup complete!")
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
