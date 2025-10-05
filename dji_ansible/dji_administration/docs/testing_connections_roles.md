`service_test_hosts` is the group that would be used when running local tests against your WSL instances.

Looking at your `wsl_instances.yml`, the `service_test_hosts` group contains:
- `ubuntuAWX`
- `argo_cd_mgt`

## **How to Use service_test_hosts for Local Testing:**

### **1. Test with Ansible Playbook**
```bash
# Run your service management playbook against service_test_hosts
ansible-playbook -i inventory/wsl_instances.yml playbooks/service_management.yml --limit service_test_hosts
```

### **2. Test Specific Hosts**
```bash
# Test against just one host
ansible-playbook -i inventory/wsl_instances.yml playbooks/service_management.yml --limit ubuntuAWX

# Test against both hosts
ansible-playbook -i inventory/wsl_instances.yml playbooks/service_management.yml --limit "ubuntuAWX,argo_cd_mgt"
```

### **3. Check Connectivity First**
```bash
# Test SSH connectivity to service_test_hosts
ansible service_test_hosts -i inventory/wsl_instances.yml -m ping
```

### **4. Dry Run (Check Mode)**
```bash
# See what would happen without making changes
ansible-playbook -i inventory/wsl_instances.yml playbooks/service_management.yml --limit service_test_hosts --check
```

## **Why service_test_hosts?**

The `service_test_hosts` group is specifically designed for:
- **Testing your collection** before deploying to all instances
- **Safe experimentation** on a subset of hosts
- **Validation** of playbooks and roles
- **Development workflow** (test locally, then run in AWX)

## **Variables Applied to service_test_hosts:**

```yaml
service_test_hosts:
  hosts:
    ubuntuAWX:
    argo_cd_mgt:
  vars:
    service_mgmt_service_name: cron
    service_mgmt_service_state: stopped
```

This means when you run tests against `service_test_hosts`, it will:
1. Target only `ubuntuAWX` and `argo_cd_mgt`
2. Use `cron` as the default service
3. Set the service state to `stopped` by default

Perfect for testing your service management collection safely!