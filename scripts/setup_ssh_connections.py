#!/usr/bin/env python3
"""
WSL SSH Connection Setup Script

This script establishes SSH connections to WSL instances based on configuration
defined in wsl_hosts.yml. After this runs successfully, AWX will handle the 
rest of the configuration via Ansible.

Usage: python3 scripts/setup_ssh_connections.py [options]

Options:
  --config FILE     Configuration file path (default: wsl_hosts.yml)
  --hosts HOST1,HOST2  Comma-separated list of hosts to configure (default: all pending)
  --status STATUS   Only configure hosts with this status (default: pending)
  --dry-run         Show what would be done without making changes
  --verbose         Enable verbose output
"""

import subprocess
import sys
import os
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Optional

class WSLSSHSetup:
    def __init__(self, config_file: str = "wsl_hosts.yml", verbose: bool = False, dry_run: bool = False):
        self.config_file = config_file
        self.verbose = verbose
        self.dry_run = dry_run
        self.config = self._load_config()
        self.results = {}
        
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"[ERROR] Configuration file not found: {self.config_file}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"[ERROR] Error parsing configuration file: {e}")
            sys.exit(1)
            
    def _get_ssh_key_path(self) -> Path:
        """Get SSH key path from config"""
        ssh_key_path = self.config['network']['ssh_key_path']
        return Path(ssh_key_path).expanduser()
        
    def _log(self, message: str, force: bool = False):
        """Log message if verbose mode is enabled"""
        if self.verbose or force:
            print(message)
            
    def run_wsl_command(self, wsl_name: str, command: str) -> Optional[subprocess.CompletedProcess]:
        """Execute a command in a specific WSL instance"""
        if self.dry_run:
            self._log(f"[DRY-RUN] Would run in {wsl_name}: {command}")
            return None
            
        try:
            cmd = ["wsl", "-d", wsl_name, "--", "bash", "-c", command]
            self._log(f"[INFO] Running: {command}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if self.verbose and result.stderr:
                self._log(f"   stderr: {result.stderr.strip()}")
            if self.verbose and result.stdout:
                self._log(f"   stdout: {result.stdout.strip()}")
                
            return result
        except subprocess.TimeoutExpired:
            print(f"[WARNING]  Command timed out in {wsl_name}")
            return None
        except Exception as e:
            print(f"[ERROR] Error executing command in {wsl_name}: {e}")
            return None

    def check_wsl_instance_running(self, wsl_name: str) -> bool:
        """Check if WSL instance is running"""
        try:
            result = subprocess.run(["wsl", "-l", "-v"], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if wsl_name in line and "Running" in line:
                        return True
            return False
        except Exception:
            return False

    def install_ssh_server(self, wsl_name: str) -> bool:
        """Install and enable SSH server in WSL instance"""
        print(f"[INFO] Installing SSH server in {wsl_name}...")
        
        commands = [
            "sudo apt update",
            "sudo apt install -y openssh-server",
            "sudo systemctl enable ssh"
        ]
        
        for cmd in commands:
            result = self.run_wsl_command(wsl_name, cmd)
            if not self.dry_run and result and result.returncode != 0:
                print(f"[WARNING]  Warning: Command failed in {wsl_name}: {cmd}")
                print(f"   Error: {result.stderr}")
                return False
        
        print(f"[SUCCESS] SSH server installed in {wsl_name}")
        return True

    def configure_ssh_port(self, wsl_name: str, port: int, hostname: str) -> bool:
        """Configure SSH to listen on specific port"""
        print(f"[INFO] Configuring SSH port {port} in {wsl_name}...")
        
        # Get SSH config from YAML
        ssh_cfg = self.config['ssh_config']
        
        # Backup original config
        backup_cmd = "sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup"
        result = self.run_wsl_command(wsl_name, backup_cmd)
        
        # Configure SSH port and settings
        ssh_config_cmd = f"""
sudo sed -i 's/#Port 22/Port {port}/' /etc/ssh/sshd_config
sudo sed -i 's/#ListenAddress 0.0.0.0/ListenAddress {ssh_cfg['listen_address']}/' /etc/ssh/sshd_config
sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication {ssh_cfg['pubkey_authentication'].lower()}/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication {ssh_cfg['password_authentication'].lower()}/' /etc/ssh/sshd_config
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin {ssh_cfg['permit_root_login'].lower()}/' /etc/ssh/sshd_config
"""
        
        result = self.run_wsl_command(wsl_name, ssh_config_cmd)
        if not self.dry_run and result and result.returncode != 0:
            print(f"[ERROR] Failed to configure SSH in {wsl_name}")
            return False
            
        print(f"[SUCCESS] SSH port {port} configured in {wsl_name}")
        return True

    def setup_hostname(self, wsl_name: str, hostname: str) -> bool:
        """Set hostname for WSL instance"""
        print(f"[INFO] Setting hostname to {hostname} in {wsl_name}...")
        
        commands = [
            f"sudo hostnamectl set-hostname {hostname}",
            f"sudo sed -i 's/DansMyOffice.localdomain.*DansMyOffice/{hostname}.localdomain\\t{hostname}/' /etc/hosts"
        ]
        
        for cmd in commands:
            result = self.run_wsl_command(wsl_name, cmd)
            if not self.dry_run and result and result.returncode != 0:
                self._log(f"[WARNING]  Warning: Hostname command failed in {wsl_name}: {cmd}")
                
        print(f"[SUCCESS] Hostname set to {hostname} in {wsl_name}")
        return True

    def setup_ssh_keys(self, wsl_name: str) -> bool:
        """Setup SSH key authentication"""
        print(f"[INFO] Setting up SSH keys in {wsl_name}...")
        
        ssh_key_path = self._get_ssh_key_path()
        
        # Check if SSH key exists
        if not ssh_key_path.exists():
            print(f"[ERROR] SSH key not found: {ssh_key_path}")
            print("   Please generate SSH key first:")
            print(f"   ssh-keygen -t rsa -b 2048 -f {ssh_key_path} -N '' -m PEM")
            return False
            
        # Read public key
        pub_key_path = f"{ssh_key_path}.pub"
        try:
            with open(pub_key_path, 'r') as f:
                public_key = f.read().strip()
        except FileNotFoundError:
            print(f"[ERROR] Public key not found: {pub_key_path}")
            return False
            
        # Setup .ssh directory and authorized_keys
        ssh_setup = f"""
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '{public_key}' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
"""
        
        result = self.run_wsl_command(wsl_name, ssh_setup)
        if not self.dry_run and result and result.returncode != 0:
            print(f"[ERROR] Failed to setup SSH keys in {wsl_name}")
            return False
            
        print(f"[SUCCESS] SSH keys configured in {wsl_name}")
        return True

    def restart_ssh_service(self, wsl_name: str) -> bool:
        """Restart SSH service"""
        print(f"[INFO] Restarting SSH service in {wsl_name}...")
        
        result = self.run_wsl_command(wsl_name, "sudo systemctl restart ssh")
        if not self.dry_run and result and result.returncode != 0:
            print(f"[ERROR] Failed to restart SSH in {wsl_name}")
            return False
            
        print(f"[SUCCESS] SSH service restarted in {wsl_name}")
        return True

    def test_ssh_connection(self, hostname: str, port: int) -> bool:
        """Test SSH connection to WSL instance"""
        print(f"[INFO] Testing SSH connection to {hostname}:{port}...")
        
        if self.dry_run:
            print(f"[DRY-RUN] Would test SSH connection to {hostname}:{port}")
            return True
            
        ssh_key_path = self._get_ssh_key_path()
        wsl_ip = self.config['network']['wsl_ip']
        username = self.config['network']['username']
        
        try:
            cmd = [
                "ssh", "-i", str(ssh_key_path), 
                "-p", str(port),
                "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=10",
                f"{username}@{wsl_ip}",
                "echo 'SSH connection successful'"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print(f"[SUCCESS] SSH connection to {hostname}:{port} successful")
                return True
            else:
                print(f"[ERROR] SSH connection to {hostname}:{port} failed")
                print(f"   Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] SSH test failed for {hostname}:{port}: {e}")
            return False

    def configure_instance(self, host_key: str, host_config: Dict) -> bool:
        """Configure a single WSL instance"""
        print(f"\n[INFO] Configuring {host_key} ({host_config['wsl_name']})...")
        print(f"   Description: {host_config['description']}")
        print(f"   Target hostname: {host_config['hostname']}")
        print(f"   SSH port: {host_config['ssh_port']}")
        
        wsl_name = host_config['wsl_name']
        hostname = host_config['hostname']
        port = host_config['ssh_port']
        
        # Check if WSL instance is running
        if not self.check_wsl_instance_running(wsl_name):
            print(f"[ERROR] WSL instance {wsl_name} is not running")
            print(f"   Please start it with: wsl -d {wsl_name}")
            return False
            
        success = True
        
        # Install SSH server
        if not self.install_ssh_server(wsl_name):
            success = False
            
        # Configure hostname
        if success and not self.setup_hostname(wsl_name, hostname):
            success = False
            
        # Configure SSH port
        if success and not self.configure_ssh_port(wsl_name, port, hostname):
            success = False
            
        # Setup SSH keys
        if success and not self.setup_ssh_keys(wsl_name):
            success = False
            
        # Restart SSH service
        if success and not self.restart_ssh_service(wsl_name):
            success = False
            
        # Test connection
        if success:
            success = self.test_ssh_connection(hostname, port)
            
        self.results[host_key] = {
            'configured': success,
            'hostname': hostname,
            'port': port,
            'wsl_name': wsl_name,
            'description': host_config['description']
        }
        
        return success

    def print_summary(self):
        """Print configuration summary"""
        print("\n" + "="*80)
        print("[INFO] WSL SSH Configuration Summary")
        print("="*80)
        
        print(f"{'Host Key':<15} | {'Hostname':<12} | {'Port':<6} | {'WSL Instance':<15} | {'Status'}")
        print("-" * 80)
        
        for host_key, result in self.results.items():
            status = "[SUCCESS] SUCCESS" if result['configured'] else "[ERROR] FAILED"
            print(f"{host_key:<15} | {result['hostname']:<12} | {result['port']:<6} | {result['wsl_name']:<15} | {status}")
            
        print("\n[INFO] Next Steps:")
        successful_instances = [k for k, v in self.results.items() if v['configured']]
        
        if successful_instances:
            print("1. [SUCCESS] SSH connections established for:")
            for host_key in successful_instances:
                result = self.results[host_key]
                print(f"   - {result['hostname']} (port {result['port']})")
                
            print("\n2. [INFO] Use AWX to complete configuration:")
            print("   - Create/run 'Configure New WSL Instances' job template")
            print("   - Apply system configurations via Ansible")
            print("   - Test service lifecycle management")
            
        failed_instances = [k for k, v in self.results.items() if not v['configured']]
        if failed_instances:
            print(f"\n[WARNING]  Manual intervention needed for: {', '.join(failed_instances)}")
            
        wsl_ip = self.config['network']['wsl_ip']
        print(f"\n[INFO] AWX Inventory Configuration:")
        for host_key, result in self.results.items():
            print(f"   {result['hostname']}: ansible_host={wsl_ip}, ansible_port={result['port']}")

def main():
    parser = argparse.ArgumentParser(description='Setup SSH connections to WSL instances')
    parser.add_argument('--config', default='wsl_hosts.yml', help='Configuration file path')
    parser.add_argument('--hosts', help='Comma-separated list of hosts to configure')
    parser.add_argument('--status', default='pending', help='Only configure hosts with this status')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    print("[INFO] WSL SSH Connection Setup")
    print("=" * 40)
    print("This script will configure SSH access to WSL instances.")
    print("After this completes, use AWX for remaining configuration.\n")
    
    setup = WSLSSHSetup(config_file=args.config, verbose=args.verbose, dry_run=args.dry_run)
    
    # Determine which hosts to configure
    wsl_hosts = setup.config.get('wsl_hosts', {})
    
    if args.hosts:
        # Configure specific hosts
        host_list = [h.strip() for h in args.hosts.split(',')]
        hosts_to_configure = {k: v for k, v in wsl_hosts.items() if k in host_list}
    else:
        # Configure hosts with specified status
        hosts_to_configure = {k: v for k, v in wsl_hosts.items() if v.get('status') == args.status}
    
    if not hosts_to_configure:
        print(f"[ERROR] No hosts found to configure with status '{args.status}'")
        if args.hosts:
            print(f"   Requested hosts: {args.hosts}")
        print(f"   Available hosts: {', '.join(wsl_hosts.keys())}")
        sys.exit(1)
        
    print(f"[INFO] Hosts to configure: {', '.join(hosts_to_configure.keys())}")
    print(f"[INFO] Configuration file: {args.config}")
    
    if args.dry_run:
        print("[INFO] DRY-RUN MODE: No changes will be made\n")
    else:
        print()
        
    # Configure each instance
    all_success = True
    for host_key, host_config in hosts_to_configure.items():
        success = setup.configure_instance(host_key, host_config)
        if not success:
            all_success = False
            
    # Print summary
    setup.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if all_success else 1)

if __name__ == "__main__":
    main()
