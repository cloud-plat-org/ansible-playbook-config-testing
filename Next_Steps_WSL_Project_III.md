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






awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential modify "$CRED_ID" --inputs '{
  "username": "daniv", 
  "password": "your_password", 
  "become_password": "your_password"
}'

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential get "$CRED_ID" | jq '.inputs'


JOB_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch \
  --job_template "Stop Services WSL" --extra_vars '{"service_name": "ssh"}' | jq -r .id)

# Check if the job arguments now include become password handling
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_args'

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job get "$JOB_ID" | jq '.job_args'









```






















***

## **Full Example Script**

Here’s a bash-ready snippet you can copy-paste:

```bash
CRED_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential list --name "WSL SSH" | jq -r '.results[0].id')
echo "Assigning credential ID $CRED_ID to job template 9"
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template modify 9 --credential $CRED_ID
```


***

**Summary:**

- Use the credential’s **ID** (not name) for robust scripting.
- Always sanitize host variables so passwords are not exposed.
- The script above makes credential assignment to your job template bulletproof in AWX.

Let me know if you want to script template ID lookup, mass credential updates, or have multi-credential scenarios!

Here’s a concise, correct, and working workflow for securely and repeatably assigning an AWX Machine credential to a job template, cleaning up inventory variables, and running jobs. This list avoids ambiguity, uses only working subcommands, and is ready for copy-paste scripting.

***

## 1. **Create Your AWX Machine Credential**

```bash
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential create \
  --name "WSL SSH" \
  --description "SSH login for WSL hosts" \
  --credential_type "Machine" \
  --organization Default \
  --inputs '{"username": "daniv", "password": "<YOUR_PASSWORD>"}'
```

- Omit or adjust `"password"` if using SSH keys.

***

## 2. **Capture the Credential ID**

```bash
CRED_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential list --name "WSL SSH" | jq -r '.results[0].id')
```


***

## 3. **Associate the Credential with Your Job Template**

(Assuming your job template ID is **9**.)

```bash
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template associate --credential "$CRED_ID" 9
```


***

## 4. **Clean Up Host Variables**

Each host should only need unique data (NO passwords):

```json
{
  "ansible_host": "localhost",
  "ansible_port": 2223
}
```

- Add `ansible_user` only if per-host username is different from credential.

***

## 5. **Launch the Job Template**

```bash
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template launch --job_template "Stop Services WSL" --extra_vars '{"service_name": "ssh"}'
```


***

## **Full Example Script**

```bash
CRED_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential list --name "WSL SSH" | jq -r '.results[0].id')
echo "Associating credential ID $CRED_ID to job template 9"
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template associate --credential "$CRED_ID" 9
```


***

### **Key Tips**

- Use only the credential’s ID for scripting reliability.
- Remove all passwords from host vars—keep your setup secure and repeatable.
- Always associate credentials via the `associate` subcommand, not `modify`.

***

Let me know if you want scripts for template ID lookup, batch credential assignment, or different workflows!

