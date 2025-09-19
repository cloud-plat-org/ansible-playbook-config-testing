## 1. **Create Your AWX Machine Credential**

*(If not already created, otherwise skip to step 2)*

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential create \
  --name "WSL SSH" \
  --description "SSH login for WSL hosts" \
  --credential_type "Machine" \
  --organization Default \
  --inputs '{"username": "daniv", "password": "<YOUR_PASSWORD>","become_password": "<YOUR_PASSWORD>"}'

# update credentials:
CRED_ID=$(awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential list --name "WSL SSH" | jq -r '.results[0].id')

<!-- awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential modify $CRED_ID \
  --inputs '{"username": "daniv", "password": "<YOUR_PASSWORD>","become_password": "<YOUR_PASSWORD>"}' -->

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" credential modify "$CRED_ID" \
  --inputs '{"username": "daniv", "ssh_key_data": "'"$(cat ~/.ssh/awx_wsl_key)"'"}'

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template get "$JOB_TEMPLATE_ID" | jq 'keys' | grep -E "(env|environment|extra_vars)"

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

