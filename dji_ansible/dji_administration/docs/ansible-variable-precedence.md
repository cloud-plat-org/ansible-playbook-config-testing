## **Ansible Variable Precedence (Highest to Lowest)**

1. **Extra vars** (`-e` or `--extra-vars`) - **HIGHEST**
2. **Task vars** (in playbook tasks)
3. **Block vars** (in playbook blocks)
4. **Role and include vars** (in `vars/main.yml`)
5. **Play vars** (in playbook `vars:` section)
6. **Host facts** (gathered by `gather_facts`)
7. **Set facts** (from `set_fact` tasks)
8. **Registered vars** (from task results)
9. **Host vars** (in inventory host definitions) ← **Your inventory vars**
10. **Group vars** (in inventory group definitions) ← **Your inventory vars**
11. **Role defaults** (in `defaults/main.yml`) ← **Your role defaults** - **LOWEST**

## **Why Variables Are in Both Places:**

### **Role Defaults (`defaults/main.yml`):**
```yaml
# These are "suggested defaults" - can be overridden
service_mgmt_service_name: cron
service_mgmt_service_state: stopped
```

### **Inventory Variables:**
```yaml
# These override the role defaults for specific groups/hosts
vars:
  service_mgmt_service_name: cron
  service_mgmt_service_state: stopped
```

## **The Purpose:**

### **1. Role Defaults = "Safe Defaults"**
- Provide sensible defaults for the role
- Work "out of the box" without configuration
- Can be used by anyone without knowing the variables

### **2. Inventory Variables = "Environment-Specific Overrides"**
- Override defaults for specific environments
- Allow different configurations per host/group
- Provide explicit control over role behavior

## **Example: Different Configurations**

```yaml
# Role defaults (safe defaults)
service_mgmt_service_name: sshd
service_mgmt_service_state: started

# Inventory overrides (environment-specific)
service_test_hosts:
  vars:
    service_mgmt_service_name: cron      # Override: test cron instead
    service_mgmt_service_state: stopped  # Override: stop instead of start

production_servers:
  vars:
    service_mgmt_service_name: nginx     # Override: manage nginx
    service_mgmt_service_state: restarted # Override: restart instead
```
