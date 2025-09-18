<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# \#\# 1. **Start Docker Desktop in Windows**

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
```Here are the steps I used for AWX.  Can you give me a list of steps for argo cd the will work with this?

Below is a curated set of step-by-step instructions to run and access Argo CD alongside your AWX setup on Docker Desktop/Minikube/WSL Ubuntu, matching the format and compatibility with your AWX workflow.

***

## 1. **Install Argo CD in Your Cluster**

Create the namespace and apply the official manifest (which you've already done):

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

- Wait a minute or two for all pods/services to be created.

***

## 2. **Check Argo CD Pods and Services**

Verify that the deployment was successful:

```bash
kubectl get pods -n argocd
kubectl get svc -n argocd
```

- Key pods like `argocd-server`, `argocd-application-controller`, and others should be `Running`.
- Confirm the `argocd-server` service exists and is of type `ClusterIP` (not `LoadBalancer` by default).[^1]

***

## 3. **Expose the Argo CD API Server**

To access the Argo CD UI, port-forward from your WSL terminal (in a new tab/window):

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

- Keep this terminal **open** and running.
- If 8080 is in use, pick another free local port.

***

## 4. **Access the Argo CD Web UI**

- In your Windows browser, open:

```
https://localhost:8080
```

- Accept the self-signed certificate warning.

***

## 5. **Retrieve the Initial Admin Password**

Get the randomly-generated admin password:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 --decode && echo
```

- Username: `admin`
- Use this password to log in to the Argo CD web UI for the first time.

***

## 6. **(Optional) Install the Argo CD CLI**

Install the CLI (in WSL Ubuntu):

```bash
# Download latest CLI (Linux AMD64 example)
VERSION=$(curl -s https://api.github.com/repos/argoproj/argo-cd/releases/latest | grep tag_name | cut -d '"' -f 4)
curl -sSL -o argocd "https://github.com/argoproj/argo-cd/releases/download/${VERSION}/argocd-linux-amd64"
chmod +x argocd
sudo mv argocd /usr/local/bin/
```


***

## 7. **Login Using the CLI**

```bash
argocd login localhost:8080 --username admin --password <password-from-step-5> --insecure
```

- Use `--insecure` due to self-signed certs.

***

## 8. **Deploy a Sample/Your Application**

- Either create an `Application` manifest and apply with `kubectl`, or
- Use the Argo CD UI ("New App") to register your Git repo and sync your first app.

***

### **Notes**

- You can run port-forward for both AWX and Argo CD at the same time, each in a different terminal, with **different local ports**.[^2][^3][^4]
- If you use Minikube Ingress and `minikube tunnel`, you can skip port-forwarding for production-like URLs, but port-forwarding is quick for local testing.
- No need to use `sudo` with Argo CD port-forward unless your Linux setup requires it for binding local ports below 1024.

***

**Summary:**
Follow the steps above to install, verify, access, and use Argo CD in a workflow directly compatible with your existing AWX developer environment. This minimizes conflicts and maximizes convenience for Kubernetes GitOps and automation trials.[^3][^4][^1][^2]

<div style="text-align: center">⁂</div>

[^1]: https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

[^2]: https://stackoverflow.com/questions/72980275/kubectl-port-forward-multiple-services

[^3]: https://www.plural.sh/blog/kubernetes-port-forward-guide/

[^4]: https://stackoverflow.com/questions/70727355/why-am-i-not-able-to-create-an-app-or-port-forward-in-argocd

