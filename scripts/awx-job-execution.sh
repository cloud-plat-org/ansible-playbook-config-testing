#!/bin/bash
# AWX Job Execution Script
# Usage: ./scripts/awx-job-execution.sh

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
export SERVICE_STATE="stopped" # stopped, started, restarted
export DEBUG_EXTRA=false

# Extra Variables JSON
export EXTRA_VARS="{\"service_name\": \"$SERVICE_NAME\", \"service_state\": \"$SERVICE_STATE\", \"debug_extra\": $DEBUG_EXTRA}"

echo "=== AWX Job Execution Script ==="
echo "Configuration:"
echo "  Job Template: $JOB_TEMPLATE_NAME"
echo "  Host Group: $HOST_GROUP"
echo "  Service: $SERVICE_NAME -> $SERVICE_STATE"
echo "  Debug Extra: $DEBUG_EXTRA"
echo

# Function to run diagnostics
run_diagnostics() {
    echo "=== Running Diagnostics ==="
    ./scripts/awx-diagnostics.sh
}

# Function to launch job
launch_job() {
    echo "=== Launching Job ==="
    echo "Launching job with extra variables: $EXTRA_VARS"
    
    JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_templates launch \
      --job_template "$JOB_TEMPLATE_NAME" \
      --credentials 4 \
      --extra_vars "$EXTRA_VARS" | jq -r .id)
    
    echo "Job ID: $JOB_ID"
    export JOB_ID
    return 0
}

# Function to launch job with host limit
launch_job_with_limit() {
    echo "=== Launching Job with Host Limit ==="
    echo "Launching job with limit: $HOST_GROUP"
    
    JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_templates launch \
      --job_template "$JOB_TEMPLATE_NAME" \
      --credentials 4 \
      --limit "$HOST_GROUP" \
      --extra_vars "$EXTRA_VARS" | jq -r .id)
    
    echo "Job ID: $JOB_ID"
    export JOB_ID
    return 0
}

# Function to launch job with explicit inventory
launch_job_with_inventory() {
    echo "=== Launching Job with Explicit Inventory ==="
    INVENTORY_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory list --name "WSL Lab" --format json | jq -r '.results[0].id')
    echo "Using Inventory ID: $INVENTORY_ID"
    
    JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_templates launch \
      --job_template "$JOB_TEMPLATE_NAME" \
      --credentials 4 \
      --inventory "$INVENTORY_ID" \
      --limit "$HOST_GROUP" \
      --extra_vars "$EXTRA_VARS" | jq -r .id)
    
    echo "Job ID: $JOB_ID"
    export JOB_ID
    return 0
}

# Function to monitor job
monitor_job() {
    if [ -z "$JOB_ID" ]; then
        echo "Error: No JOB_ID set. Run launch_job first."
        return 1
    fi
    
    echo "=== Monitoring Job $JOB_ID ==="
    
    # Check job status
    awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '{id, status, started, finished}'
    
    echo
    echo "=== Job Output ==="
    awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"
}

# Function to get job output only
get_job_output() {
    local job_id="${1:-$JOB_ID}"
    
    if [ -z "$job_id" ]; then
        echo "Error: No JOB_ID provided. Usage: get_job_output [JOB_ID]"
        echo "Or set JOB_ID by running launch_job first."
        return 1
    fi
    
    echo "=== Job Output for Job $job_id ==="
    awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$job_id"
}

# Function to update project
update_project() {
    echo "=== Updating Project ==="
    PROJECT_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" projects list --name "$PROJECT_NAME" --format json | jq -r '.results[0].id')
    echo "Updating project ID: $PROJECT_ID"
    
    awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" projects update "$PROJECT_ID" --scm_update_revision
}

# Function to show usage
show_usage() {
    echo "Available functions:"
    echo "  run_diagnostics              - Run AWX diagnostics"
    echo "  launch_job                   - Launch job with extra variables"
    echo "  launch_job_with_limit        - Launch job with host group limit"
    echo "  launch_job_with_inventory    - Launch job with explicit inventory"
    echo "  monitor_job                  - Monitor the last launched job (status + output)"
    echo "  get_job_output [JOB_ID]      - Get output only for a specific job"
    echo "  update_project               - Update the project repository"
    echo
    echo "Examples:"
    echo "  run_diagnostics"
    echo "  launch_job && monitor_job"
    echo "  get_job_output 226"
    echo "  update_project"
}

# If script is run directly, show usage
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    show_usage
    echo
    echo "Script loaded. Use the functions above or source this script:"
    echo "  source ./scripts/awx-job-execution.sh"
fi
