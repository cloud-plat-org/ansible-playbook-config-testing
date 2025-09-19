## 1. **Start Docker Desktop in Windows**

From your WSL terminal:

```bash
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe" &
```

Or just start it from the Start menu.

- **Wait** for Docker Desktop to be fully up (system tray icon stops spinning).

***

## 2. **Start Minikube in WSL Ubuntu**

Check Minikube status:

```bash
minikube status
```

If not running, start it:

```bash
minikube start
```

- Make sure the `docker` driver is used and cluster status shows as Running.

***

## 3. **Start the Minikube Tunnel**

This ensures services with LoadBalancer/Ingress work at `https://localhost`.
Open a separate WSL terminal (not your code editor):

```bash
minikube tunnel
```

- Keep this terminal **open** and running.

***

## 4. **Check AWX Pods and Services**

Make sure AWX is deployed and all pods are running:

```bash
kubectl get pods -n awx
kubectl get svc -n awx
```

- Pods like `awx-web`, `awx-task`, and `awx-postgres` should show `Running` or `Completed`.

***

## 5. **Set Up Port Forwarding (if Required)**

If you’re not using Ingress or want direct access to a specific port:

```bash
sudo kubectl port-forward svc/awx-service -n awx 443:80

```

*(If using Ingress and minikube tunnel, this step may be optional—AWX UI should be at https://localhost.)*

***

## 6. **Access the AWX Web UI**

- In your browser (on Windows), go to:

```
https://localhost
```

Accept any certificate warnings (self-signed cert).

***

## 7. **Run the AWX CLI Login Command in WSL**

Use your configured HTTPS endpoint and the insecure flag for self-signed certs:

```bash
awx --conf.host https://localhost:443 -k login --conf.username admin --conf.password <yourpassword>
```

- To re-use the token:

```bash
export AWX_TOKEN=$(awx --conf.host https://localhost:443 -k login --conf.username admin --conf.password <yourpassword> | jq -r .token)
```

- Example to list hosts:

```bash
awx --conf.host https://localhost:443 -k --conf.token "$AWX_TOKEN" host list
```


***

## 8. **[Optional] Troubleshooting**

- If browser access fails, verify:
    - `minikube tunnel` is running
    - `kubectl get ingress -n awx` shows your ingress with an external address
- If CLI fails, ensure you’re using the same URL and port as your Ingress and web UI.

***

## **Full Workflow Recap**

1. Start Docker Desktop (in Windows, or via WSL with the .exe path).
2. In WSL:
    - `minikube status` and `minikube start` as needed.
    - Run `minikube tunnel` in a dedicated terminal.
    - Check `kubectl get pods -n awx` for Running status.
    - Check `kubectl get svc -n awx` for services.
    - (If needed) Run `kubectl port-forward ...` for direct port mapping.
3. Open the AWX UI at `https://localhost` in your browser.
4. Use AWX CLI with `--conf.host https://localhost:443 -k` for scripting/admin.

***

**Follow all steps in order each time you restart your machine.**
Let me know if you want a shortcut script or hit any errors in the workflow!

