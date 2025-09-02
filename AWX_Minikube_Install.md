## 1. Prerequisites

- **Ubuntu/WSL with Minikube support**
- **Docker** installed and running (required by Minikube)
- **kubectl** (Kubernetes CLI)

Recommended resources: **8 GB RAM**, **2+ CPU cores**, **20 GB free space**.[^1][^2]

***

## 2. Install kubectl (if missing)

```bash
curl -LO "https://dl.k8s.io/release/v1.30.1/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client
```


***

## 3. Install Minikube (if missing)

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube version
```


***

## 4. Start Minikube

```bash
minikube start --driver=docker --cpus=4 --memory=8g --addons=ingress
```

Wait for the cluster to be up and ready.
[^2][^1]

***

## 5. Verify Your Cluster

```bash
kubectl get nodes
kubectl get pods -A
```

You should see all system pods running.

***

## 6. Install AWX Operator


```bash
git clone https://github.com/ansible/awx-operator.git
cd awx-operator
git checkout 2.19.1  # Example: git checkout 2.19.0
```

Deploy the operator:

```bash
export NAMESPACE=awx
kubectl create namespace $NAMESPACE
make deploy
```

Or if `make` is missing:

```bash
kubectl apply -k config/default
```


***

## 7. Deploy AWX Instance

Create a custom resource YAML file (`awx-deploy.yml`):
# vim awx-deploy.yml

```yaml
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx
spec:
  service_type: nodeport
  ingress_type: none
``` > awx-deploy.yml

Apply it:

```bash
kubectl apply -f awx-deploy.yml -n awx
```


***

## 8. Wait for AWX Pods

```bash
kubectl get pods -n awx
```

When all pods show STATUS `Running`, proceed.

***

## 9. Access AWX

Find the NodePort that AWX is using (usually 30080 or 30001):

```bash
kubectl get svc -n awx
```

Forward the port to your localhost:

```bash
kubectl port-forward svc/awx-service -n awx 8080:80
```

Then, access `http://localhost:8080` from your browser.[^3]

***

## 10. Get the Admin Password

```bash
kubectl get secret awx-admin-password -n awx -o jsonpath="{.data.password}" | base64 --decode; echo
```

Username: **admin**

***

**Let me know if you want the detailed contents or layout of the AWX resource YAML, or if you have questions about customizing your deployment!**
<span style="display:none">[^10][^11][^4][^5][^6][^7][^8][^9]</span>

<div style="text-align: center">⁂</div>
