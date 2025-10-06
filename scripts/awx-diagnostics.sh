#!/bin/bash
# AWX Diagnostic Script
# Usage: ./scripts/awx-diagnostics.sh

# Activate AWX virtual environment
source ~/awx-venv/bin/activate

# Extract stored OAuth2 token
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)

# AWX Configuration Parameters
export JOB_TEMPLATE_NAME="WSL Service Management"
export PROJECT_NAME="WSL Automation"
export HOST_GROUP="all_servers" 

# Service Configuration Variables
export SERVICE_NAME="cron"
export SERVICE_STATE="stopped"
export DEBUG_EXTRA=false

# Extra Variables JSON
export EXTRA_VARS="{\"service_name\": \"$SERVICE_NAME\", \"service_state\": \"$SERVICE_STATE\", \"debug_extra\": $DEBUG_EXTRA}"

echo "=== AWX Diagnostics ==="
echo "Token: ${AWX_TOKEN:0:10}..."
echo "Job Template: $JOB_TEMPLATE_NAME"
echo "Host Group: $HOST_GROUP"
echo "Service: $SERVICE_NAME -> $SERVICE_STATE"
echo

echo "=== Inventory Information ==="
INVENTORY_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory list --name "WSL Lab" --format json | jq -r '.results[0].id')
echo "Inventory ID: $INVENTORY_ID"

echo
echo "=== Hosts in Inventory ==="
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" hosts list --inventory "$INVENTORY_ID" --format json | jq '.results[] | {name, inventory, variables}'

echo
echo "=== Groups in Inventory ==="
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" groups list --inventory "$INVENTORY_ID" --format json | jq '.results[] | {name, inventory}'

echo
echo "=== Job Template Configuration ==="
JOB_TEMPLATE_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_templates list --name "$JOB_TEMPLATE_NAME" --format json | jq -r '.results[0].id')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_templates get "$JOB_TEMPLATE_ID" --format json | jq '{name, inventory, playbook, ask_inventory_on_launch, become_enabled}'

echo
echo "=== Recent Jobs ==="
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" jobs list --format json | jq '.results[0:3] | .[] | {id, name, status, started, finished}'

echo
echo "=== Diagnostics Complete ==="
