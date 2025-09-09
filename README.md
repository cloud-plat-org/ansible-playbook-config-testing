# Red Hat Ansible Automation Platform Service on AWS.
# This is using windows wsl Ubuntu


## Install ansible-lint

# 1. Install python3-venv
sudo apt install python3-venv

# 2. Create dedicated virtual environment
python3 -m venv ~/.venvs/ansible

# 3. Activate and install ansible-lint
## no source ~/.venvs/ansible/bin/activate
source ~/awx-venv/bin/activate
pip install ansible-lint

# To activate it on new sesstion of code editors:
source ~/.venvs/ansible/bin/activate
ansible-lint your_playbook.yml

# add to vim ~/.bashrc
export ANSIBLE_CACHE_PLUGIN_CONNECTION=$(pwd)/.ansible

