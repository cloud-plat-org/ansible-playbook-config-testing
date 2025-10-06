#!/bin/bash
# AWX Inventory Management Script
# Usage: ./awx-inventory-manager.sh

# Activate AWX virtual environment
source ~/awx-venv/bin/activate

# Extract stored OAuth2 token
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# AWX Configuration Parameters
export INVENTORY_NAME="WSL Lab"
export GROUP_NAME="all_servers"
export ANSIBLE_USER="daniv"
export ANSIBLE_SSH_KEY="/home/daniv/.ssh/id_rsa"
export ANSIBLE_HOST_IP="172.22.192.129"

# Host Configuration Array
declare -A HOSTS
HOSTS[ubuntuAWX]="2225"
HOSTS[argo_cd_mgt]="2226"
HOSTS[wslkali1]="2224"
HOSTS[wslubuntu1]="2223"

# Function 1: Create Inventory
create_inventory() {
  echo "Creating inventory: $INVENTORY_NAME"
  awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory create \
    --name "$INVENTORY_NAME" \
    --description "WSL instances for automation" \
    --organization Default
  
  # Get the inventory ID
  INVENTORY_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory list --name "$INVENTORY_NAME" --format json | jq -r '.results[0].id')
  echo "Inventory ID: $INVENTORY_ID"
}

# Function 2: Create Group
create_group() {
  echo "Creating group: $GROUP_NAME"
  awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" group create \
    --name "$GROUP_NAME" \
    --inventory "$INVENTORY_ID"
}

# Function 3: Add All Hosts
add_hosts() {
  echo "Adding hosts to inventory..."
  for host_name in "${!HOSTS[@]}"; do
    port="${HOSTS[$host_name]}"
    echo "Adding host: $host_name ($ANSIBLE_HOST_IP:$port)"
    
    awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" -f json --conf.color false hosts create \
      --name "$host_name" \
      --inventory "$INVENTORY_ID" \
      --variables "{\"ansible_host\": \"$ANSIBLE_HOST_IP\", \"ansible_port\": $port, \"ansible_user\": \"$ANSIBLE_USER\", \"ansible_ssh_private_key_file\": \"$ANSIBLE_SSH_KEY\"}"
  done
}

# Function 4: Add Hosts to Group (Note: AWX CLI doesn't support this operation)
add_hosts_to_group() {
  echo "Note: AWX CLI doesn't support automatic group host association"
  echo "Please manually add hosts to the '$GROUP_NAME' group via the AWX web interface:"
  echo "1. Go to Inventories → WSL Lab → Groups → all_servers"
  echo "2. Click Hosts tab"
  echo "3. Add the following hosts: ${!HOSTS[*]}"
}

# Function 5: Verify Configuration
verify_configuration() {
  echo "=== Verification ==="
  
  echo "Hosts in Inventory:"
  awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" -f json --conf.color false hosts list --inventory "$INVENTORY_ID" | jq '.results[] | {name, variables}'
  
  echo "Hosts in Group:"
  GROUP_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" -f json --conf.color false groups list --inventory "$INVENTORY_ID" --name "$GROUP_NAME" | jq -r '.results[0].id')
  awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" -f json --conf.color false groups get "$GROUP_ID" | jq '.summary_fields.hosts.results[] | .name'
  
  echo "Groups in Inventory:"
  awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" -f json --conf.color false groups list --inventory "$INVENTORY_ID" | jq '.results[] | {name, inventory_id: .inventory}'
}

# Function 6: Remove Hosts from Group (Note: AWX CLI doesn't support this operation)
remove_hosts_from_group() {
  echo "Note: AWX CLI doesn't support automatic group host removal"
  echo "Please manually remove hosts from the '$GROUP_NAME' group via the AWX web interface if needed"
}

# Function 7: Delete All Hosts
delete_all_hosts() {
  echo "Deleting all hosts (removes from ALL inventories)"
  for host_name in "${!HOSTS[@]}"; do
    echo "Deleting host: $host_name"
    awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" hosts delete "$host_name"
  done
}

# Function 8: Delete Group
delete_group() {
  echo "Deleting group: $GROUP_NAME"
  # Get the group ID first (in case it wasn't set)
  CURRENT_GROUP_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" -f json --conf.color false groups list --name "$GROUP_NAME" | jq -r '.results[0].id // empty')
  if [ -n "$CURRENT_GROUP_ID" ]; then
    awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" groups delete "$CURRENT_GROUP_ID"
    echo "Group deleted!"
  else
    echo "Group '$GROUP_NAME' not found or already deleted"
  fi
}

# Function 9: Delete Inventory
delete_inventory() {
  echo "Deleting inventory: $INVENTORY_NAME"
  # Get the inventory ID first (in case it wasn't set)
  CURRENT_INVENTORY_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" -f json --conf.color false inventory list --name "$INVENTORY_NAME" | jq -r '.results[0].id // empty')
  if [ -n "$CURRENT_INVENTORY_ID" ]; then
    awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory delete "$CURRENT_INVENTORY_ID"
    echo "Inventory deleted!"
  else
    echo "Inventory '$INVENTORY_NAME' not found or already deleted"
  fi
}

# Function 10: Complete Cleanup
cleanup_all() {
  echo "Starting complete cleanup..."
  remove_hosts_from_group
  delete_all_hosts
  delete_group
  delete_inventory
  echo "Cleanup complete!"
}

# Main function
main() {
  echo "Starting AWX Inventory Setup..."
  
  # Step 1: Create inventory
  create_inventory
  
  # Step 2: Create group
  create_group
  
  # Step 3: Add all hosts
  add_hosts
  
  # Step 4: Add hosts to group
  add_hosts_to_group
  
  # Step 5: Verify configuration
  verify_configuration
  
  echo "Setup complete!"
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  # Script is being executed directly
  main
fi
