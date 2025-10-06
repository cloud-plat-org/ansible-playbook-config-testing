# Ansible Galaxy Tagging Guide

This guide explains Ansible Galaxy's tagging system and how to properly categorize collections for discovery and compliance.

## Why Galaxy Requires Tags

Galaxy requires specific tags for:

### **1. Discovery & Organization**
- Users can **browse collections by category**
- **Search filtering** by infrastructure type
- **Galaxy homepage** organization by category

### **2. Quality Assurance**
- Ensures collections are **properly categorized**
- Helps **moderators review** collections
- **Prevents misclassified** collections

### **3. User Experience**
- **Clear expectations** about what the collection does
- **Easier navigation** on Galaxy website
- **Better search results**

## Required Galaxy Tags

Ansible Galaxy requires collections to use at least one of these tags:

| Tag | Purpose | Example Collections |
|-----|---------|-------------------|
| `infrastructure` | Infrastructure automation | Service management, system configuration |
| `linux` | Linux-specific content | Systemd, package management |
| `tools` | Utilities and tools | Development tools, monitoring utilities |
| `cloud` | Cloud platforms | AWS, Azure, GCP |
| `database` | Database management | MySQL, PostgreSQL |
| `networking` | Network configuration | Firewall, routing |
| `security` | Security tools | Authentication, encryption |
| `application` | Application deployment | Web apps, microservices |
| `eda` | Event-driven automation | Event processing, workflows |
| `monitoring` | Monitoring and observability | Metrics, logging, alerting |
| `storage` | Storage management | File systems, block storage |
| `windows` | Windows-specific content | PowerShell, Windows services |

## Our Collection Tags

Our `dji_ansible.dji_administration` collection uses:

- **`infrastructure`** - Service management is infrastructure automation
- **`linux`** - Targets Linux systems with systemd
- **`tools`** - Service management utilities and tools

### Why These Tags:
- **`infrastructure`** - Service management is infrastructure automation
- **`linux`** - Our collection targets Linux systems (systemd)
- **`tools`** - Service management tools/utilities

These tags help users discover our collection when searching for infrastructure automation tools on Linux systems.

## Tag Selection Guidelines

### **Choose Tags Based On:**
1. **Primary functionality** of your collection
2. **Target operating systems** (linux, windows)
3. **Use case category** (infrastructure, tools, etc.)
4. **User expectations** when searching

### **Avoid:**
- **Too many tags** (stick to 2-4 relevant ones)
- **Generic tags** without specific purpose
- **Tags that don't match** your collection's actual functionality

### **Examples:**
```yaml
# Service management collection
tags: [infrastructure, linux, tools]

# Database management collection
tags: [database, linux, infrastructure]

# Cloud automation collection
tags: [cloud, infrastructure, tools]

# Windows-specific collection
tags: [windows, infrastructure, tools]
```

## Galaxy Compliance

To ensure Galaxy compliance:

1. **Use at least one** required tag
2. **Choose relevant tags** that match your collection's purpose
3. **Keep tags simple** and descriptive
4. **Test your collection** with the chosen tags

## Resources

- [Ansible Galaxy Documentation](https://galaxy.ansible.com/docs/)
- [Collection Requirements](https://docs.ansible.com/ansible/latest/galaxy/user_guide.html#collection-requirements)
- [Tagging Best Practices](https://galaxy.ansible.com/docs/contributing/creating_collections.html#tags)
