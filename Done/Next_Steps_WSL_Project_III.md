## 1. **Create Your AWX Machine Credential**

*(If not already created, otherwise skip to step 2)*

```bash
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential create \
  --name "WSL SSH" \
  --description "SSH login for WSL hosts" \
  --credential_type "Machine" \
  --organization Default \
  --inputs '{"username": "daniv", "password": "<YOUR_PASSWORD>"}'
```

- (Omit or adjust `"password": ...` if using SSH key-based auth.)

***

## 2. **Capture the Credential ID with CLI**

This command captures the **credential ID** for the credential named "WSL SSH" and saves it to a shell variable:

```bash
CRED_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential list --name "WSL SSH" | jq -r '.results[0].id')
```

- This uses `jq` to extract the first credential’s ID matching the name "WSL SSH".

***

## 3. **Assign the Credential to Your Job Template Using the ID**


```bash
JOB_TEMPLATE_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template list --name "Stop Services WSL" | jq -r '.results[0].id')

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template associate --credential "$CRED_ID" "$JOB_TEMPLATE_ID"

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch --job_template "$JOB_TEMPLATE_ID" --extra_vars '{"service_name": "ssh"}'

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslubuntu1 | jq -r .variables



awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host modify --name wslubuntu1 \
  --variables '{"ansible_host": "localhost", "ansible_port": 2223}'


   # Get the host ID first
HOST_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslubuntu1 | jq -r '.id')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host modify "$HOST_ID" --variables '{"ansible_host": "localhost", "ansible_port": 2223}'

HOST_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslkali1 | jq -r '.id')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host modify "$HOST_ID" --variables '{"ansible_host": "localhost", "ansible_port": 2224}'


```


***

## 4. **Ensure Host Variables Are Clean**

Each managed host in your inventory should have only:

```json
{
  "ansible_host": "localhost",
  "ansible_port": 2223
}
```

(No password; username only if it’s different from the credential.)

***

## 5. **Run the Job Template**

Use your familiar launch command:
### HERE TO RUN ###
```bash

### VERIFY AWX PICKS UP CHANGES TO PLAYBOOK  ###
   # Check if AWX has the latest project revision
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq '.results[] | {name, id, last_job_run, last_job_failed, status}'
# Show the WSL Project details
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq '.results[] | select(.name == "WSL Project")'
# Then capture just the ID
PROJECT_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | jq -r '.results[] | select(.name == "WSL Project") | .id')
echo "WSL Project ID: $PROJECT_ID"
### Compair the hash#
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '.scm_revision'
git log -1 --format="%H"

# verify branch AWX is pulling:
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '{scm_branch, scm_url}'
# How to add or change a branch:
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project modify "$PROJECT_ID" --scm_branch "CLPLAT-2221"
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_cwd'
# Check the project's local path
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '.local_path'
# Check the job's working directory
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_cwd'

# Enable automatic sync when job is launched
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project modify "$PROJECT_ID" --scm_update_on_launch true
# Force sync:
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '.modified'

# Check progress update
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project_update get 21 | jq '{status, started, finished, elapsed}'
# Monitor the project update
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project_update stdout 21
   awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project get "$PROJECT_ID" | jq '.scm_revision'


#TESTING: {See TroubleShooting_Password_AWX.md}
   # Check current job template settings
   awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get 9 | jq '{ask_credential_on_launch, ask_variables_on_launch}'
   # Set the job template to use stored credentials (not ask on launch)
   awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template modify 9 --ask_credential_on_launch false


awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq 'keys' | grep -E "(env|environment|extra_vars|become)"
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template modify "$JOB_TEMPLATE_ID" --become_enabled true
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '{become_enabled, ask_credential_on_launch}'


awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list | jq '.results[] | {name: .name, variables: .variables}'
# UbuntuAWX variables only
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name UbuntuAWX | jq '.variables'

# wslubuntu1 variables only  
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslubuntu1 | jq '.variables'

# wslkali1 variables only
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslkali1 | jq '.variables'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list | jq -r '.results[] | "\(.name): \(.variables)"'

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host modify 4 --variables '{"ansible_host": "localhost", "ansible_port": 22, "ansible_user": "daniv", "ansible_password": "<yourpassword>"}'  ## Not needed
# Config ansible_host and ansible_user without password, gotten from credentials.
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host modify 4 --variables '{"ansible_host": "localhost", "ansible_port": 22, "ansible_user": "daniv"}'

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host delete 4[]
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list | jq '.results[] | {name: .name, variables: .variables}'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" hosts delete 4












# Disassociate the old credential (ID 3)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template disassociate --credential "3" "$JOB_TEMPLATE_ID"

# Associate the new SSH key credential (ID 4)
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template associate --credential "4" "$JOB_TEMPLATE_ID"

# Verify the credential is now the SSH key credential
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq '.summary_fields.credentials'

# Launch a new job with the SSH key credential
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "ssh"}' | jq -r .id)

echo "New Job ID: $JOB_ID"

# Check the job output
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"


### THIS IS TO KICK OFF PLAYBOOKS  ###
JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "ssh"}' | jq -r .id)
echo $JOB_ID
## to monitor:
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID"
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout "$JOB_ID"



wsl --distribution Ubuntu-24.04 --user daniv
wsl --distribution Kali-Linux --user daniv
ssh -p 2223 daniv@localhost
ssh -p 2224 daniv@localhost
ssh -p 2223 -o StrictHostKeyChecking=no daniv@localhost
ssh-keyscan -p 2223 localhost >> ~/.ssh/known_hosts
ssh-keyscan -p 2224 localhost >> ~/.ssh/known_hosts

sudo service ssh status
sudo service ssh start

sudo systemctl start ssh
sudo systemctl status ssh
sudo systemctl restart ssh

MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"

   # Update wslubuntu1 to use the WSL IP (172.22.192.129)
HOST_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslubuntu1 | jq -r '.id')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host modify "$HOST_ID" --variables '{"ansible_host": "172.22.192.129", "ansible_port": 2223}'

# Update wslkali1 to use the WSL IP (172.22.192.129)
HOST_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslkali1 | jq -r '.id')
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host modify "$HOST_ID" --variables '{"ansible_host": "172.22.192.129", "ansible_port": 2224}'

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslubuntu1 | jq -r .variables
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host get --name wslkali1 | jq -r .variables
## this doen't test the awx instance in minikube
ssh -p 2223 daniv@172.22.192.129
ssh -p 2224 daniv@172.22.192.129

JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "ssh"}' | jq -r .id)

# Get the AWX task pod name
kubectl get pods -n awx | grep awx-task

# Execute commands inside the AWX pod
kubectl exec -n awx -it awx-task-7b9c887444-jb9vd -- ssh -p 2223 daniv@172.22.192.129
kubectl exec -n awx -it awx-task-7b9c887444-jb9vd -- ssh -p 2224 daniv@172.22.192.129

wsl --distribution Ubuntu-24.04 --user daniv
echo "daniv ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/daniv
exit

wsl --distribution kali-linux --user daniv
echo "daniv ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/daniv
exit


# Test in Ubuntu-24.04
wsl --distribution Ubuntu-24.04 --user daniv
sudo systemctl status ssh
exit

# Test in Kali-Linux
wsl --distribution kali-linux --user daniv
sudo systemctl status ssh
exit

## Job AWX veriables:
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_env'
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_env' | grep -i password
## job AWX Assignment:
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_args'
## verify credential associated:
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.summary_fields.credentials'
## Check if the credential has become_password:
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential get "$CRED_ID" | jq '.inputs'



# Common Causes and Solutions
# 1. Key Format
# Ansible’s paramiko and OpenSSH typically want a PEM-format private key (header: -----BEGIN RSA PRIVATE KEY----- and footer: -----END RSA PRIVATE KEY-----).

# Your command with -m PEM is correct for legacy format.
# But later Python/cryptography libraries might reject some older, passwordless PEM keys (test with a passphrase if issues persist).

# 2. Proper Key Upload (No Corrupted Newlines/Escape)
# When uploading a key via CLI, careful quoting is required—especially so newlines in your PEM key remain intact.

# Direct $(cat ...) in JSON can convert linebreaks to spaces, corrupting the key.

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential modify 4 \
  --inputs "{\"username\": \"daniv\", \"ssh_key_data\": \"$(awk 'NF{printf "%s\\n",$0;}' ~/.ssh/awx_wsl_key_traditional)\"}"

# Update credential with the working traditional RSA key

# awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential modify "$CRED_ID" --inputs '{
#   "username": "daniv", 
#   "password": "your_password", 
#   "become_password": "your_password"
# }'

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential get "$CRED_ID" | jq '.inputs'


JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "ssh"}' | jq -r .id)

# Check if the job arguments now include become password handling
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_args'

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_args'

