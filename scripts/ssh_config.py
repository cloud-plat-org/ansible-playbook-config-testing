#!/usr/bin/env python3
"""
Simple SSH Configuration Script for WSL Instances

Copy this script to each WSL instance, make it executable, and run it.
Usage: python3 ssh_config.py <hostname> <port>

Example:
  python3 ssh_config.py ubuntuAWX 2225
  python3 ssh_config.py argo_cd_mgt 2226
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print status"""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[SUCCESS] {description}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"[ERROR] {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"[ERROR] {description} failed: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 ssh_config.py <hostname> <port>")
        print()
        print("Examples:")
        print("  python3 ssh_config.py ubuntuAWX 2225")
        print("  python3 ssh_config.py argo_cd_mgt 2226")
        print("  python3 ssh_config.py wslubuntu1 2223")
        print("  python3 ssh_config.py wslkali1 2224")
        sys.exit(1)
    
    hostname = sys.argv[1]
    port = sys.argv[2]
    
    print(f"[INFO] Configuring SSH for hostname: {hostname}, port: {port}")
    print("=" * 60)
    
    # Update package cache
    if not run_command("sudo apt update", "Updating package cache"):
        print("[WARNING] Package update failed, continuing anyway")
    
    # Install SSH server
    if not run_command("sudo apt install -y openssh-server", "Installing SSH server"):
        print("[ERROR] Failed to install SSH server")
        sys.exit(1)
    
    # Backup original SSH config
    run_command("sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup", 
                "Backing up SSH config")
    
    # Set hostname
    if not run_command(f"sudo hostnamectl set-hostname {hostname}", 
                      f"Setting hostname to {hostname}"):
        print("[WARNING] Hostname setting failed, continuing anyway")
    
    # Update /etc/hosts
    hosts_cmd = f"sudo sed -i 's/DansMyOffice.localdomain.*DansMyOffice/{hostname}.localdomain\\t{hostname}/' /etc/hosts"
    run_command(hosts_cmd, "Updating /etc/hosts")
    
    # Configure SSH settings
    ssh_commands = [
        f"sudo sed -i 's/#Port 22/Port {port}/' /etc/ssh/sshd_config",
        "sudo sed -i 's/#ListenAddress 0.0.0.0/ListenAddress 0.0.0.0/' /etc/ssh/sshd_config",
        "sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config",
        "sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config",
        "sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config"
    ]
    
    print("[INFO] Configuring SSH settings...")
    for cmd in ssh_commands:
        subprocess.run(cmd, shell=True, capture_output=True)
    print("[SUCCESS] SSH settings configured")
    
    # Create SSH directory and setup for current user
    user = os.environ.get('USER', 'daniv')
    run_command("mkdir -p ~/.ssh", "Creating .ssh directory")
    run_command("chmod 700 ~/.ssh", "Setting .ssh permissions")
    
    # Setup sudoers for current user
    sudoers_cmd = f'echo "{user} ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/{user}-nopasswd'
    run_command(sudoers_cmd, f"Configuring passwordless sudo for {user}")
    
    # Enable and start SSH service
    if not run_command("sudo systemctl enable ssh", "Enabling SSH service"):
        print("[ERROR] Failed to enable SSH service")
        sys.exit(1)
    
    if not run_command("sudo systemctl start ssh", "Starting SSH service"):
        print("[ERROR] Failed to start SSH service")
        sys.exit(1)
    
    # Check SSH status
    run_command("sudo systemctl status ssh --no-pager -l", "Checking SSH status")
    
    # Verify SSH is listening on the correct port
    run_command(f"sudo netstat -tlnp | grep :{port}", f"Verifying SSH listening on port {port}")
    
    print()
    print("=" * 60)
    print("[SUCCESS] SSH Configuration Complete!")
    print(f"Hostname: {hostname}")
    print(f"SSH Port: {port}")
    print(f"User: {user}")
    print()
    print("Next Steps:")
    print("1. From AWX host, copy SSH public key:")
    print(f"   ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub -p {port} {user}@172.22.192.129")
    print("2. Test SSH connection:")
    print(f"   ssh -i ~/.ssh/awx_wsl_key_traditional -p {port} {user}@172.22.192.129")
    print("3. Use AWX to run configuration playbook")

if __name__ == "__main__":
    main()
