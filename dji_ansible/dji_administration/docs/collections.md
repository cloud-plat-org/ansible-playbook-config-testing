
# Step 1

In root directory run:
```bash
ansible-galaxy collection init my_namespace.my_collection
```

# Step 2

Remove comment from 'requires_ansible' runtime.yml file.
    my_namespace/my_collection/meta/runtime.yml
    requires_ansible: '>=2.15.0' - updated to 2.15.0 or higher.

















