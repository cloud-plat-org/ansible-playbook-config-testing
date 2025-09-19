
bash```
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project create \
  --name "WSL Project" \
  --description "Playbooks for WSL Lab" \
  --organization Default \
  --scm_type git \
  --scm_url "https://github.com/cloud-plat-org/ansible-playbook-config-testing.git"
  
 #  \
 #  --scm_branch CLPLAT-2221

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | \
jq -r '.results[] | {name, status, last_job_run, last_job_failed}'

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" project list | \
jq -r '.results[] | [.name, .status, .last_job_run, .last_job_failed] | @tsv'
```

## 1. Ensure Inventory Groups Match (all_servers)

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" group create --name all_servers --inventory "WSL Lab"
<!-- awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" group associate --group all_servers --host wslubuntu1
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" group associate --group all_servers --host wslkali1 -->
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host modify --name wslubuntu1 --groups all_servers
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host modify --name wslkali1 --groups all_servers


2. Create the Job Template to Run the Playbook

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template create \
  --name "Stop Services WSL" \
  --project "WSL Project" \
  --inventory "WSL Lab" \
  --playbook "stop_services.yml" \
  --credential "WSL SSH"

3. Launch the Job

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job launch --job_template "Stop Services WSL"

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab" | jq -r '.results[] | "\(.id) \(.name)"'

<!-- 4 UbuntuAWX
3 wslkali1
2 wslubuntu1
"name": "WSL Lab"
 "id": 1, -->




You're running AWX version 24.6.1.

With this version, the AWX CLI (awx) is still somewhat limited in direct host–group management compared to the API and web UI. There is no direct subcommand like group associate or group hosts add in the awx CLI—even in 24.6.1.

Recommended Actions for AWX 24.6.1
1. Use the Web UI (Easiest)
Go to your "WSL Lab" inventory in the AWX web UI.

Click on Groups → all_servers.

Add the desired hosts (wslubuntu1, wslkali1) to the group with the GUI.





## Command to add each host to the group:

bash```
curl -k -H "Authorization: Bearer $AWX_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  https://localhost/api/v2/groups/1/hosts/ \
  -d '{"id": 2}'


curl -k -H "Authorization: Bearer $AWX_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  https://localhost/api/v2/groups/1/hosts/ \
  -d '{"id": 3}'
```

<!-- curl -k -H "Authorization: Bearer $AWX_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST \
  https://localhost/api/v2/groups/1/hosts/ \
  -d '{"id": 4}' -->


bash```

curl -k -H "Authorization: Bearer $AWX_TOKEN" \
  https://localhost/api/v2/groups/1/hosts/ | jq -r '.results[] | "\(.id) \(.name)"'
```


Next Steps
1. Create/Check Your Job Template
Ensure your job template is set to:

Inventory: WSL Lab

Project: WSL Project

Playbook: stop_services.yml (the playbook filename in your repo)

Credential: Appropriate for your WSL hosts

If you haven't done this yet, here’s the CLI command:

bash
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job_template create \
  --name "Stop Services WSL" \
  --project "WSL Project" \
  --inventory "WSL Lab" \
  --playbook "stop_services.yml" \
  --credential "WSL SSH"
2. Launch the Job
Run your playbook against the group via AWX:

bash
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job launch --job_template "Stop Services WSL"
3. Monitor Job Progress
Check results in the AWX Web UI (Jobs page) for real-time status and detailed output.

Or via CLI:

bash
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job list
Find the latest job’s ID, then:

bash
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job stdout <job_id>
4. Verify Service Stoppage
Your playbook displays status with the debug task, so look for messages like:

text
Service <service_name> stopped on <host> (Debian)
Reminder on service_name
Ensure you launch the job/template with an extra variable for service_name.

In the AWX UI: Add service_name: <your_service> in the "Extra Variables" textbox when launching.

In CLI, use:

bash
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" job launch --job_template "Stop Services WSL" --extra_vars '{"service_name": "ssh"}'
You are now fully set to automate service control on your WSL targets via AWX!
Let me know if you need to troubleshoot failed jobs, set up notifications, or want an example for using Windows hosts!












