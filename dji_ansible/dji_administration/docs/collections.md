
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

## Next Steps

After creating your role, you can:
- Add tasks to `roles/services_mgmt/tasks/main.yml`
- Define variables in `roles/services_mgmt/defaults/main.yml`
- Create templates in `roles/services_mgmt/templates/`
- Add handlers in `roles/services_mgmt/handlers/main.yml`

Once you've developed your role content, you can then build and install the collection.











