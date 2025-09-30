#!/bin/bash

# Install AWX collection first
ansible-galaxy collection install awx.awx

# Update requirements
ansible-galaxy collection install -r requirements.yml

# Run the playbook
export AWX_OAUTH_TOKEN="your_token_here"
ansible-playbook manage_awx_templates.yml

# Or pass token as variable
ansible-playbook manage_awx_templates.yml -e "awx_token=your_token"