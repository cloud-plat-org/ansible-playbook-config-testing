

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





