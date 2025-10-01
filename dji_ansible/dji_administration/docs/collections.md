
# Step 1

In root directory run:
```bash
ansible-galaxy collection init my_namespace.my_collection
```

# Step 2

Remove comment from 'requires_ansible' runtime.yml file.
    my_namespace/my_collection/meta/runtime.yml
    requires_ansible: '>=2.15.0' - updated to 2.15.0 or higher.


# Step 3

Fill out galaxy.yml file with pertinent information.
    my_namespace/my_collection/galaxy.yml


This creates a complete role structure with all necessary directories and files.

# Step 4

Build the collection:

```bash
cd dji_ansible/dji_administration/
ansible-galaxy collection build
```









# Step ###

Install the collection locally:

```bash
ansible-galaxy collection install dji_ansible-dji_administration-1.0.0.tar.gz
```

