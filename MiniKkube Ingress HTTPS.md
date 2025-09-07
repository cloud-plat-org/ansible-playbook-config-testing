<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Ok, give me directions on how to do this.  remember I am using awx on minikube on docker-desktop and on a wsl Ubuntu instance with the host name of ubuntuAWX

For Real HTTPS Access
If you want your AWX to truly use SSL (so HTTPS works on port 443):

You must configure an ingress controller (like NGINX Ingress) with TLS termination and a self-signed or valid certificate.

This is a more advanced Kubernetes operation and requires extra config (Ingress resource and certs). -->

Here’s a **step-by-step guide to enable real HTTPS (SSL/TLS)** for AWX running on Minikube with Docker Desktop on your WSL Ubuntu (ubuntuAWX) using the NGINX Ingress Controller and a self-signed certificate. This method works for your stack and results in secure `https://localhost` access for both browser and AWX CLI.[^1][^2][^3][^4]

***

## Step 1: Enable the NGINX Ingress Controller on Minikube

```bash
minikube addons enable ingress
```

> If it was already enabled, you can skip this step, or run `minikube addons disable ingress` and then re-enable to reset.

***

## Step 2: Create a Self-Signed TLS Certificate

On your host (in WSL Ubuntu):

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -out awx-ingress.crt \
  -keyout awx-ingress.key \
  -subj "/CN=localhost/O=awx-ingress"
```


***

## Step 3: Create a Kubernetes Secret from the Certificate

```bash
kubectl create secret tls awx-ingress-tls \
  --namespace awx \
  --key awx-ingress.key \
  --cert awx-ingress.crt
```


***

## Step 4: Create an Ingress Resource for AWX

Save the following as `awx-ingress.yaml` (edit if your AWX service or port is different):
See file:


Apply it:

```bash
kubectl apply -f awx-ingress.yaml
```


***

## Step 5: Start the Minikube Tunnel (for Port 443 Direct Access)

This is required for ingress resources to be accessible on privileged ports:

```bash
minikube tunnel
```

> **Leave this terminal window open** while you use AWX. Use `sudo` if prompted.

***

## Step 6: Access AWX Over HTTPS
```bash
echo "127.0.1.1 ubuntuAWX" | sudo tee -a /etc/hosts
```

- In your browser:
Visit `https://localhost`
You will receive a “self-signed certificate” warning—proceed anyway.
- In AWX CLI:
Use:

```bash
awx --conf.host https://localhost -k <command>
```

The `-k` or `--conf.insecure` flag tells the CLI to ignore SSL warnings for self-signed certs.

Update your `~/.awx/config` if desired:

```
[defaults]
host = https://localhost
```


***

## Notes

- If NodePort is used in your ingress instead of default, you may need to use `https://localhost:<nodeport>` and adjust firewall accordingly.
- You can specify a custom domain (e.g. `awx.local`) but you'll need to update `/etc/hosts` as well.

***

## References

- Minikube Addon for Ingress:
- Ingress TLS Walkthrough:
- AWX-specific self-signed and ingress examples:

***
