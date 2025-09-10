# Red Hat Ansible Automation Platform Service on AWS.
# This is using windows wsl Ubuntu

Emergent’s Ansible as a Service leverages managed Ansible expertise for AWS deployments.

# 1. Install python3-venv
sudo apt install python3-venv

# 2. Create dedicated virtual environment
python3 -m venv ~/.venvs/ansible

# 3. Activate and install ansible-lint
source ~/.venvs/ansible/bin/activate
pip install ansible-lint

# To activate it on new sesstion of code editors:
source ~/.venvs/ansible/bin/activate
ansible-lint your_playbook.yml

# add to vim ~/.bashrc
export ANSIBLE_CACHE_PLUGIN_CONNECTION=$(pwd)/.ansible

######################################################################

bash```
cd ~/ansible/test2

# Create inventory file
cat > inventory.ini << 'EOF'
[wsl_hosts]
wslubuntu1 ansible_host=172.22.192.129 ansible_port=2223 ansible_user=daniv
wslkali1 ansible_host=172.22.192.129 ansible_port=2224 ansible_user=daniv

[local]
localhost ansible_connection=local
EOF

# Create role structure
ansible-galaxy init roles/system_info

# Create test playbook
cat > test_system_info.yml << 'EOF'
---
- name: Test system_info role
  hosts: wsl_hosts
  become: false
  roles:
    - system_info
  vars:
    report_title: "WSL System Information Report"
    include_network_details: true
    include_disk_details: true
    include_memory_details: true
EOF

# Optional: Create requirements file
cat > requirements.yml << 'EOF'
# External roles from Ansible Galaxy can be listed here
# Local roles in roles/ directory are automatically available
EOF


```