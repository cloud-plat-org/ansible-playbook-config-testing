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
minikube tunnel  # maybe?
```

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
argocd login localhost:8080 --username admin --password Thisisit! --insecure
```

### Example Apps:
    https://github.com/argoproj/argocd-example-apps
    

- Use `--insecure` due to self-signed certs.

***

## 8. **Deploy a Sample/Your Application**

- Either create an `Application` manifest and apply with `kubectl`, or
- Use the Argo CD UI ("New App") to register your Git repo and sync your first app.

***

### **Notes**

- You can run port-forward for both AWX and Argo CD at the same time, each in a different terminal, with **different local ports**.
- If you use Minikube Ingress and `minikube tunnel`, you can skip port-forwarding for production-like URLs, but port-forwarding is quick for local testing.
- No need to use `sudo` with Argo CD port-forward unless your Linux setup requires it for binding local ports below 1024.
