# AWX Interactive Mode Guide

This guide covers all the interactive capabilities of the `awx_inventory_manager.py` script.

## **Starting Interactive Mode**

```bash
source ~/awx-venv/bin/activate
python3 -i awx_inventory_manager.py --interactive
```

**Expected startup output:**
```
Starting interactive mode...
Manager available as 'manager' variable
Example: manager.cleanup_all()
>>>
```

This gives you a Python shell with the `manager` object ready to use.

## **Complete Setup (Create Everything)**

### **Option 1: Use the main() function**
```python
# This creates everything: inventory, hosts, groups, project, job template
main()

# Expected output:
# Starting AWX Complete Setup...
# === Setting up Inventory and Hosts ===
# Inventory created: WSL Lab (ID: 15)
# Group created: all_servers (ID: 13)
# Host created: ubuntuAWX (ID: 52)
# ... (more host creation messages)
# === Setting up Project ===
# Project created: WSL Automation (ID: 42)
# Updating project to sync repository...
# Project update started successfully
# Waiting for project update to complete...
# Project update status: pending
# Project update status: running
# Project update completed successfully
# === Setting up Job Template ===
# Job template created: WSL Service Management (ID: 43)
# === Setup Complete! ===
# Inventory: WSL Lab (ID: 15)
# Project: WSL Automation (ID: 42)
# Job Template: WSL Service Management (ID: 43)
# Hosts: ubuntuAWX, argo_cd_mgt, wslkali1, wslubuntu1
# <__main__.AWXInventoryManager object at 0x797326daa930>
```

**Note:** The last line `<__main__.AWXInventoryManager object at 0x...>` is normal Python behavior showing the returned manager object. You can ignore it or store it in a variable.

### **Option 2: Step-by-step creation**
```python
# Configuration
hosts_config = {
    'ubuntuAWX': 2225,
    'argo_cd_mgt': 2226, 
    'wslkali1': 2224,
    'wslubuntu1': 2223
}

# Step 1: Create inventory
inventory = manager.create_inventory("WSL Lab")

# Step 2: Create group
group = manager.create_group(inventory, "all_servers")

# Step 3: Add hosts
hosts = manager.add_hosts(inventory, hosts_config)

# Step 4: Add hosts to group
manager.add_hosts_to_group(group, hosts)

# Step 5: Create project
project = manager.create_project("WSL Automation")

# Step 6: Wait for project sync (if needed)
manager.wait_for_project_update(project['id'])

# Step 7: Create job template
job_template = manager.create_job_template(project, inventory, "WSL Service Management")
```

## **Complete Cleanup (Delete Everything)**

```python
# Delete everything: job template, project, inventory, hosts, groups
manager.cleanup_all()

# Expected output:
# Starting complete cleanup...
# === Deleting Job Template ===
# Deleted job template: WSL Service Management
# === Deleting Project ===
# Deleted project: WSL Automation
# === Deleting Inventory ===
# Deleted host: ubuntuAWX
# Deleted host: argo_cd_mgt
# Deleted host: wslkali1
# Deleted host: wslubuntu1
# Deleted group: all_servers
# Deleted inventory: WSL Lab
# === Cleanup Complete! ===

# Or specify custom names
manager.cleanup_all(
    inventory_name="My Custom Inventory",
    project_name="My Custom Project", 
    template_name="My Custom Template"
)
```

## **Individual Operations**

### **Inventory Management**

```python
# Create inventory
inventory = manager.create_inventory("My Inventory")
inventory = manager.create_inventory()  # Uses default "WSL Lab"

# The create_inventory method automatically:
# - Checks if inventory already exists (reuses if found)
# - Creates new one if it doesn't exist
# - Returns inventory object with ID
```

### **Group Management**

```python
# Create group (requires existing inventory)
group = manager.create_group(inventory, "web_servers")
group = manager.create_group(inventory)  # Uses default "all_servers"

# Groups are automatically created in the specified inventory
```

### **Host Management**

```python
# Configuration for hosts
hosts_config = {
    'server1': 2222,
    'server2': 2223,
    'server3': 2224
}

# Add multiple hosts at once
hosts = manager.add_hosts(inventory, hosts_config)

# Each host gets these variables automatically:
# - ansible_host: 172.22.192.129
# - ansible_port: (from config)
# - ansible_user: daniv
# - ansible_ssh_private_key_file: /home/daniv/.ssh/id_rsa

# Add hosts to group
manager.add_hosts_to_group(group, hosts)
```

### **Project Management**

```python
# Create project with default settings
project = manager.create_project()

# Create project with custom settings
project = manager.create_project(
    name="My Custom Project",
    scm_type="git",
    scm_url="https://github.com/myuser/myrepo",
    scm_branch="main"
)

# Wait for project to sync (useful after creation)
success = manager.wait_for_project_update(project['id'], timeout=600)
if success:
    print("Project synced successfully")
else:
    print("Project sync failed or timed out")
```

### **Job Template Management**

```python
# Create job template (requires project and inventory)
job_template = manager.create_job_template(
    project=project,
    inventory=inventory,
    name="My Service Management",
    playbook="playbooks/my_playbook.yml"
)

# Default job template settings:
# - Job type: run
# - Verbosity: 0
# - Become enabled: True
# - Ask variables on launch: True
# - Ask inventory on launch: False
# - Ask credential on launch: False
```

## **Individual Deletion Operations**

```python
# Delete specific project
manager.delete_project("WSL Automation")
manager.delete_project()  # Uses default name

# Delete specific job template
manager.delete_job_template("WSL Service Management")
manager.delete_job_template()  # Uses default name

# Delete everything (inventory, project, template, hosts, groups)
manager.cleanup_all()
```

## **Verification and Inspection**

```python
# Check what was created by examining returned objects
print(f"Inventory ID: {inventory['id']}")
print(f"Project ID: {project['id']}")
print(f"Job Template ID: {job_template['id']}")
print(f"Hosts created: {[host['name'] for host in hosts]}")

# The objects returned contain full AWX API data
# You can inspect any field from the API response
```

## **Custom Configurations**

### **Different Host Configurations**

```python
# Web servers
web_hosts = {
    'web1': 2222,
    'web2': 2223
}

# Database servers
db_hosts = {
    'db1': 2224,
    'db2': 2225
}

# Create separate inventories
web_inventory = manager.create_inventory("Web Servers")
db_inventory = manager.create_inventory("Database Servers")

# Add hosts to respective inventories
web_host_objects = manager.add_hosts(web_inventory, web_hosts)
db_host_objects = manager.add_hosts(db_inventory, db_hosts)
```

### **Multiple Projects**

```python
# Development project
dev_project = manager.create_project(
    name="Development Project",
    scm_branch="develop"
)

# Production project
prod_project = manager.create_project(
    name="Production Project", 
    scm_branch="main"
)
```

### **Multiple Job Templates**

```python
# Service management template
service_template = manager.create_job_template(
    project=project,
    inventory=inventory,
    name="Service Management",
    playbook="playbooks/service_management.yml"
)

# System configuration template
config_template = manager.create_job_template(
    project=project,
    inventory=inventory,
    name="System Configuration",
    playbook="playbooks/system_config.yml"
)
```

## **Error Handling**

All methods include error handling and will:
- Print helpful error messages
- Return `None` or `False` on failure
- Continue execution instead of crashing

```python
# Safe to call even if resources don't exist
result = manager.delete_project("Non-existent Project")
# Prints: "Project 'Non-existent Project' not found"

# Check return values
inventory = manager.create_inventory()
if inventory:
    print(f"Created inventory: {inventory['name']}")
else:
    print("Failed to create inventory")
```

## **Common Interactive Workflows**

### **Quick Setup and Test**
```python
# 1. Create everything
main()

# 2. Test it works (check AWX web interface)

# 3. Clean up
manager.cleanup_all()
```

### **Development Workflow**
```python
# 1. Create base setup
inventory = manager.create_inventory("Dev Lab")
project = manager.create_project("Dev Project")

# 2. Test with different configurations
# (Modify playbooks, test, iterate)

# 3. Clean up when done
manager.cleanup_all("Dev Lab", "Dev Project", "Dev Template")
```

### **Multi-Environment Setup**
```python
# Development environment
dev_inventory = manager.create_inventory("Dev Environment")
dev_project = manager.create_project("Dev Project", scm_branch="develop")

# Staging environment  
staging_inventory = manager.create_inventory("Staging Environment")
staging_project = manager.create_project("Staging Project", scm_branch="staging")

# Production environment
prod_inventory = manager.create_inventory("Production Environment")
prod_project = manager.create_project("Production Project", scm_branch="main")
```

## **Key Benefits of Interactive Mode**

1. **Immediate Feedback** - See results instantly
2. **Flexible Configuration** - Customize any parameter
3. **Error Recovery** - Fix issues and retry easily
4. **Exploration** - Test different configurations
5. **Debugging** - Inspect objects and troubleshoot
6. **Learning** - Understand AWX API interactions

## **Pro Tips**

- **Use tab completion** in Python shell for method names
- **Store objects in variables** for reuse (e.g., `inventory`, `project`)
- **Check return values** to verify operations succeeded
- **Use descriptive names** for custom resources
- **Clean up regularly** to avoid clutter in AWX
- **Test incrementally** - create one resource at a time

## **Troubleshooting**

```python
# If something fails, check the error message
# Most common issues:
# 1. AWX not running - check kubectl get pods -n awx
# 2. Network issues - check AWX_URL and token
# 3. Resource conflicts - use different names or cleanup first

# Debug by examining the manager object
print(f"Base URL: {manager.base_url}")
print(f"Token: {manager.token[:10]}...")  # Show first 10 chars
```

This interactive mode gives you complete control over AWX resources with the flexibility to experiment and iterate quickly!

