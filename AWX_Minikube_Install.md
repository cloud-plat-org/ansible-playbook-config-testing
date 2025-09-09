## 1. Prerequisites

- **Ubuntu/WSL with Minikube support**
- **Docker** installed and running (required by Minikube)
- **kubectl** (Kubernetes CLI)
- **jq** (json tool)

Recommended resources: **8 GB RAM**, **2+ CPU cores**, **20 GB free space**.

***

## 2. Install kubectl (if missing)

```bash
curl -LO "https://dl.k8s.io/release/v1.30.1/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client

sudo apt update
sudo apt install jq
jq --version  # jq-1.7
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
echo "127.0.1.1 ubuntuAWX" | sudo tee -a /etc/hosts
minikube tunnel


kubectl port-forward svc/awx-service -n awx 8080:80
ps: docker desktop start
## for awx-kit commands:\
"/mnt/c/Program Files/Docker/Docker/Docker Desktop.exe"
minikube status
minikube start
minikube tunnel
kubectl get pods -n awx
kubectl get svc -n awx
# run in terminal outside editor:
kubectl port-forward svc/awx-service -n awx 443:80

```

Then, access `http://localhost:8080` from your browser.

***

## 10. Get the Admin Password

```bash
kubectl get secret awx-admin-password -n awx -o jsonpath="{.data.password}" | base64 --decode; echo
```

Username: **admin**


## 11. Install awxkit
```bash
python3 -m venv ~/awx-venv
source ~/awx-venv/bin/activate
python3 -m pip install --upgrade pip
sudo apt install python3 python3-pip
pip install awxkit
awx --version
export AWX_PASSWORD='PASSWORD LASTPASS'
echo "$AWX_PASSWORD"
AWX_TOKEN=$(awx --conf.host https://localhost:443 -k login --conf.username admin --conf.password "$AWX_PASSWORD" | jq -r .token)
awx --conf.host https://localhost:443 -k --conf.token "$AWX_TOKEN" host list


# Get the token from AWX (you'll need to run this first)
export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath='{.data.password}' | base64 -d)
# Add this line to your ~/.bashrc
echo 'export AWX_TOKEN=$(kubectl get secret awx-admin-password -n awx -o jsonpath="{.data.password}" | base64 -d)' >> ~/.bashrc

# Then reload your bashrc
source ~/.bashrc
```


<!-- For Real HTTPS Access
If you want your AWX to truly use SSL (so HTTPS works on port 443):

You must configure an ingress controller (like NGINX Ingress) with TLS termination and a self-signed or valid certificate.

This is a more advanced Kubernetes operation and requires extra config (Ingress resource and certs). -->