# Ok, I have two instances in wsl wslkali1 Port 2224 for ssh, wslubuntu1 Port 2223 for ssh, and the host awx is running on UbuntuAWX, Because they are in wsl, they all have the same ip 172.22.192.129.   This is a fresh install of AWX, how do I get these hosts listed in AWX using the command line?

To add your WSL hosts (`wslkali1` and `wslubuntu1`) to AWX using the command line, you need to use the **AWX CLI (`awx` command)** or AWX’s REST API. For most CLI usage, the `awx` tool is the modern, recommended way.

### Assumptions:

- Your AWX credentials are set up, and the CLI is authenticated.
- You want each host to appear with its correct SSH port, even though they share the same IP.

***

## 1. Create an Inventory

```bash
awx inventory create --name "WSL Lab" --organization Default
```

This creates an inventory called "WSL Lab" in the "Default" organization.

***

## 2. Add Hosts with Custom SSH Ports

You want each host (`wslubuntu1` and `wslkali1`) to connect to `localhost` but on a unique port.

```bash
awx host create --name wslubuntu1 \
  --inventory "WSL Lab" \
  --variables '{"ansible_host": "localhost", "ansible_port": 2223, "ansible_user": "<youruser>", "ansible_password": "<yourpassword>"}'
```

```bash
awx host create --name wslkali1 \
  --inventory "WSL Lab" \
  --variables '{"ansible_host": "localhost", "ansible_port": 2224, "ansible_user": "<youruser>", "ansible_password": "<yourpassword>"}'
```

For the AWX host itself (if desired):

```bash
awx host create --name UbuntuAWX \
  --inventory "WSL Lab" \
  --variables '{"ansible_host": "localhost", "ansible_port": 22, "ansible_user": "<youruser>", "ansible_password": "<yourpassword>"}'
```

Replace `<youruser>` and `<yourpassword>` with the correct user credentials for each WSL instance.

***

## 3. Verify Hosts

To list hosts in your inventory:

```bash
# awx host list --inventory "WSL Lab"
awx --conf.host http://localhost:8080 host list --inventory "WSL Lab"

```


***

## Summary Table

| Hostname | ansible_host | ansible_port | Description |
| :-- | :-- | :-- | :-- |
| wslubuntu1 | localhost | 2223 | WSL Ubuntu (target) |
| wslkali1 | localhost | 2224 | WSL Kali Linux (target) |
| UbuntuAWX | localhost | 22 | AWX server host itself |


***

**Tips:**

- You can always update variables for a host with `awx host modify`.
- If using SSH keys instead of password, set up a credential in AWX and reference it in your job templates.

This method lets AWX connect to each WSL instance individually via unique SSH ports, even though their IP is shared.
Let me know if you need help connecting AWX CLI, authentication, or job template setup!
<span style="display:none">[^1][^10][^11][^12][^2][^3][^4][^5][^6][^7][^8][^9]</span>

<div style="text-align: center">⁂</div>

[^1]: https://docs.ansible.com/ansible-tower/latest/html/towercli/index.html

[^2]: https://www.reddit.com/r/ansible/comments/f9c3t6/how_to_associate_hosts_to_group_with_the_new_awx/

[^3]: https://stackoverflow.com/questions/55473188/how-to-add-remote-hosts-in-ansible-awx-tower

[^4]: https://access.redhat.com/solutions/3933571

[^5]: https://stackoverflow.com/questions/57315855/how-to-associate-a-group-to-a-host-with-ansible-tower-awx-rest-api

[^6]: https://dmsimard.com/2016/03/15/changing-the-ssh-port-with-ansible/

[^7]: https://forum.ansible.com/t/can-i-have-a-separate-port-for-specific-hosts-for-ansible-to-connect-through/41314

[^8]: https://forum.ansible.com/t/how-to-bulk-add-hosts-in-ansible-awx-using-api/4481

[^9]: https://docs.callgoose.com/general/custom_ssh_port_when_using_ansible

[^10]: https://www.reddit.com/r/ansible/comments/mmko9f/awx_delegate_to_custom_ip_and_port/

[^11]: https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html

[^12]: https://forum.ansible.com/t/setting-host-too-use-custom-port/27751

