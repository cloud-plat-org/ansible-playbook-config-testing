Yes, exactly! You need to set up SSH key authentication between your WSL instances. Here's how to fix this:

## **1. Generate SSH Key (if you don't have one)**

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "daniv@ubuntuAWX"
# Press Enter to accept default location (~/.ssh/id_rsa)
# Optionally set a passphrase or press Enter for no passphrase
```

## **2. Copy Public Key to Target Hosts**

```bash
# Copy your public key to each WSL instance
ssh-copy-id -p 2225 daniv@172.22.192.129  # ubuntuAWX
ssh-copy-id -p 2226 daniv@172.22.192.129  # argo_cd_mgt
ssh-copy-id -p 2224 daniv@172.22.192.129  # wslkali1
ssh-copy-id -p 2223 daniv@172.22.192.129  # wslubuntu1
```

## **3. Alternative: Manual Copy**

If `ssh-copy-id` doesn't work, do it manually:

```bash
# Copy your public key
cat ~/.ssh/id_rsa.pub

# Then SSH to each host and add it to authorized_keys
ssh -p 2225 daniv@172.22.192.129
mkdir -p ~/.ssh
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
exit
```

## **4. Test SSH Connection**

```bash
# Test connection to each host
ssh -p 2225 daniv@172.22.192.129 "echo 'SSH to ubuntuAWX works!'"
ssh -p 2226 daniv@172.22.192.129 "echo 'SSH to argo_cd_mgt works!'"
```

## **5. Update Inventory (if needed)**

Make sure your inventory has the SSH key path:

```yaml
# inventory/wsl_instances.yml
ubuntuAWX:
  ansible_host: 172.22.192.129
  ansible_port: 2225
  ansible_user: daniv
  ansible_ssh_private_key_file: ~/.ssh/id_rsa  # Add this line
```

## **6. Test with Ansible**

```bash
# Test connectivity first
ansible service_test_hosts -i inventory/wsl_instances.yml -m ping

# Then run your playbook
ansible-playbook -i inventory/wsl_instances.yml playbooks/service_management.yml --limit service_test_hosts
```

Start with `ssh-copy-id` - it's the easiest method!