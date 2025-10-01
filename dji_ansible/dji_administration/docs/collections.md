
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


# Step 4

Create a role named `services_mgmt` with scaffolding by running the following commands:

```bash
cd dji_ansible/dji_administration/roles/
ansible-galaxy role init services_mgmt
```

This creates a complete role structure with all necessary directories and files.

# Step 5

Build the collection:

```bash
cd dji_ansible/dji_administration/
ansible-galaxy collection build
```

# Step 6

Install the collection locally:

```bash
ansible-galaxy collection install dji_ansible-dji_administration-1.0.0.tar.gz
```











