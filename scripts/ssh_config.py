#!/usr/bin/env python3
import subprocess
import sys
import os
if len(sys.argv) != 3:
    print("Usage: python3 ssh_config.py <hostname> <port>")
    sys.exit(1)
hostname, port, user = sys.argv[1], sys.argv[2], os.environ.get('USER', 'daniv')
print(f"Configuring SSH: {hostname}:{port}")
for cmd in [
    "sudo apt update -y && sudo apt install -y openssh-server",
    f"sudo hostnamectl set-hostname {hostname}",
    f"sudo sed -i 's/#Port 22/Port {port}/; s/#ListenAddress 0.0.0.0/ListenAddress 0.0.0.0/; s/#PubkeyAuthentication yes/PubkeyAuthentication yes/; s/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config",
    "mkdir -p ~/.ssh && chmod 700 ~/.ssh",
    f'echo "{user} ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/{user}-nopasswd',
    "sudo systemctl enable ssh && sudo systemctl restart ssh"
]:
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=False)
print(f"\nDone! Next: ssh-copy-id -i ~/.ssh/awx_wsl_key_traditional.pub "
      f"-p {port} {user}@172.22.192.129")
