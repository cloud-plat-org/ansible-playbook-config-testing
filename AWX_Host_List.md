Here’s your workflow updated for **HTTPS Ingress**, self-signed certificate, and password/token handling in AWX CLI.
The **`-k` flag** (insecure for the self-signed cert) and **`--conf.password "$AWX_PASSWORD"`** are included for every command that needs authentication.

***

## **0. Export Your AWX Password**

For secure scripting:

```bash
export AWX_PASSWORD='your-actual-awx-password'
```


***

## 1. **Create an Inventory**

```bash
awx --conf.host https://localhost -k login --conf.username admin --conf.password "$AWX_PASSWORD"
awx --conf.host https://localhost -k inventory create --name "WSL Lab" --organization Default
```


***

## 2. **Add Hosts with Custom SSH Ports**

**FYI:** You only need to include `--conf.password "$AWX_PASSWORD"` with `login`, NOT with every subsequent command using a valid token.
When scripting, capture the token (see below), or always relogin per sequence.

**Example using password:**

```bash

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" inventory create --name "WSL Lab" --organization Default


awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host create --name wslubuntu1 \
  --inventory "WSL Lab" \
  --variables '{"ansible_host": "localhost", "ansible_port": 2223, "ansible_user": "<youruser>", "ansible_password": "<yourpassword>"}'

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host create --name wslkali1 \
  --inventory "WSL Lab" \
  --variables '{"ansible_host": "localhost", "ansible_port": 2224, "ansible_user": "<youruser>", "ansible_password": "<yourpassword>"}'

awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host create --name UbuntuAWX \
  --inventory "WSL Lab" \
  --variables '{"ansible_host": "localhost", "ansible_port": 22, "ansible_user": "<youruser>", "ansible_password": "<yourpassword>"}'
```


## 4. **List Hosts in Inventory**
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab"

```bash
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab" | \
jq -r '.results[] | {name, inventory, id}'


# command to filter out:
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab" | \
jq -r '.results[] | {name, inventory, id}'

### print Columns:
awx --conf.host https://localhost -k --conf.token "$AWX_TOKEN" host list --inventory "WSL Lab" | \
jq -r '.results[] | [.name, .inventory, .id] | @tsv'

```