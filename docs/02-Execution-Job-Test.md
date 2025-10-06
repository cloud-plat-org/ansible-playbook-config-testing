# AWX Job Execution Test Script
# Usage: ./scripts/awx-job-execution.sh

This script sets up all required variables and provides commands for:
- Running diagnostics
- Launching AWX jobs
- Monitoring job execution
- Updating projects

## Prerequisites

**IMPORTANT: SSH Credential Setup Required**
Before running any AWX jobs, you must create the SSH credential manually:

1. **SSH Key**: Uses `awx_wsl_key_traditional` (specifically designed for AWX)
2. **Manual Creation Required**: 
   - Go to AWX Web UI → Credentials → Add
   - Select "Machine" credential type
   - Name: "WSL SSH KEY"
   - Username: "daniv"
   - SSH Private Key: Copy content from `~/.ssh/awx_wsl_key_traditional`
3. **Why Manual**: CLI credential creation fails due to SSH key formatting issues

**Configuration Variables** (defined in the script):
- JOB_TEMPLATE_NAME="WSL Service Management"
- PROJECT_NAME="WSL Automation" 
- HOST_GROUP="all_servers"
- SERVICE_NAME="cron" (for `launch_job`)
- SERVICE_STATE="started" (for `launch_job`)
- DEBUG_EXTRA=false
- CREDENTIAL_ID=9 (references "WSL SSH KEY")

**Available Functions:**
- `launch_job` - Launch with script variables (cron → started)
- `launch_job_defaults` - Launch with playbook defaults (sshd → started)
- `launch_job_interactive` - Launch with interactive prompts for service name/state
- `launch_job_with_limit` - Launch with host group limit
- `launch_job_with_inventory` - Launch with explicit inventory
- `monitor_job` - Monitor job execution
- `get_job_output [JOB_ID]` - Get specific job output
- `update_project` - Update project repository
- `run_diagnostics` - Run AWX diagnostics

### 0. Diagnostic Commands (Run First)
```bash
source ~/awx-venv/bin/activate
# Run the diagnostic script to check AWX configuration
./scripts/awx-diagnostics.sh
```

This script will show:
- Inventory information and ID
- All hosts in the inventory with their variables
- Groups in the inventory
- Job template configuration
- Recent job history

**Note**: The `awx-diagnostics.sh` script has been removed. Use the `run_diagnostics` function instead.

### 1. Launch Job Options

#### Option A: Launch with Script Variables (Extra Variables)
```bash
source ~/awx-venv/bin/activate
# Source the script to load functions and variables
source ./scripts/awx-job-execution.sh

# Launch with script configuration: service_name=cron, service_state=started
launch_job
```

#### Option B: Launch with Playbook Defaults (No Extra Variables)
```bash
source ~/awx-venv/bin/activate
# Source the script to load functions and variables
source ./scripts/awx-job-execution.sh

# Launch with playbook defaults: service_name=sshd, service_state=started
launch_job_defaults
```

#### Option C: Launch with Interactive Prompts
```bash
source ~/awx-venv/bin/activate
# Source the script to load functions and variables
source ./scripts/awx-job-execution.sh

# Launch with interactive prompts for service name and state
launch_job_interactive
```

**Difference Between Launch Options:**
- **`launch_job`**: Uses script variables (service_name=cron, service_state=started) - passes extra variables to AWX
- **`launch_job_defaults`**: Uses playbook defaults (service_name=sshd, service_state=started) - no extra variables passed
- **`launch_job_interactive`**: Prompts for service name, state, and debug mode - creates custom extra variables

### 2. Monitor Job Execution
```bash
# Monitor the last launched job (shows status and output)
# Get full monitoring info
monitor_job

# Or get just the output later
get_job_output

# Or get output for any specific job
get_job_output 244
```

### 3. Launch with Host Limit
```bash
# Launch with specific host limit
launch_job_with_limit
```

### 4. Launch with Explicit Inventory (Alternative)
```bash
# If the job template doesn't have the correct inventory set, specify it explicitly
launch_job_with_inventory
```

### 5. Update Project
```bash
# Update the project to pull the latest changes from your repository
update_project
```