# K3D: Monitoring Your Service using Kubernetes Dashboard or Octant

![Cover](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/z1f5ezna2e3vwm2fu038.png)

K3D is a lightweight wrapper around k3s that allows you to run Kubernetes clusters inside Docker containers. While K3D is widely used for local development and testing, effective monitoring of services running on Kubernetes clusters is essential for debugging, performance tuning, and understanding resource usage.

In this blog, I will explore two popular monitoring tools for Kubernetes: Kubernetes Dashboard, the official web-based UI for Kubernetes, and Octant, a local, real-time, standalone dashboard developed by VMware. Both tools have unique strengths, and this guide will help you understand when to use one over the other.

## Setting Up Kubernetes Dashboard On K3D

First you need to create a cluster using `k3d cluster create`:

```bash
$  k3d cluster create dashboard --servers 1 --agents 2

INFO[0000] Prep: Network
INFO[0000] Created network 'k3d-dashboard'
INFO[0000] Created image volume k3d-dashboard-images
INFO[0000] Starting new tools node...
INFO[0000] Starting node 'k3d-dashboard-tools'
INFO[0001] Creating node 'k3d-dashboard-server-0'
INFO[0001] Creating node 'k3d-dashboard-agent-0'
INFO[0001] Creating node 'k3d-dashboard-agent-1'
INFO[0001] Creating LoadBalancer 'k3d-dashboard-serverlb'
INFO[0001] Using the k3d-tools node to gather environment information
INFO[0001] HostIP: using network gateway 172.18.0.1 address
INFO[0001] Starting cluster 'dashboard'
INFO[0001] Starting servers...
INFO[0001] Starting node 'k3d-dashboard-server-0'
INFO[0008] Starting agents...
INFO[0008] Starting node 'k3d-dashboard-agent-0'
INFO[0008] Starting node 'k3d-dashboard-agent-1'
INFO[0015] Starting helpers...
INFO[0016] Starting node 'k3d-dashboard-serverlb'
INFO[0022] Injecting records for hostAliases (incl. host.k3d.internal) and for 4 network members into CoreDNS configmap...
INFO[0024] Cluster 'dashboard' created successfully!
INFO[0024] You can now use it like this:
kubectl cluster-info
```

Next, deploy Kubernetes Dashboard:

```bash
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
```

Ensure the pods are running.

```bash
$ kubectl get pods -n kubernetes-dashboard

NAME                                         READY   STATUS    RESTARTS   AGE
dashboard-metrics-scraper-795895d745-kcbkw   1/1     Running   0          10m
kubernetes-dashboard-56cf4b97c5-fg92n        1/1     Running   0          10m
```

Then, create a service account and bind role, to access the dashboard, you need a service account with the proper permissions. Create a service account and cluster role binding using the following YAML:

```yml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
```

Apply this configuration:

```bash
$ kubectl apply -f admin-user.yaml

serviceaccount/admin-user created
clusterrolebinding.rbac.authorization.k8s.io/admin-user created
```

Then, Retrieve the token for login using:

```bash
$ kubectl -n kubernetes-dashboard create token admin-user
```

Use `kubectl proxy` to access the dashboard:

```bash
$ kubectl proxy

Starting to serve on 127.0.0.1:8001
```

Finally, open your browser and navigate to:

```bash
http://127.0.0.1:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/login
```

Note: Don't forget to copy and paste the token when prompted.

## Setting Up Octant on K3D

First, you need to install Octant, You can install Octant using a package manager or download it directly from the [official releases](https://github.com/vmware-archive/octant/releases/tag/v0.25.1). For example, on macOS, you can use Homebrew:

```bash
brew install octant
```

Next, on Linux just download the appropriate binary and move it to your path:

```bash
$ wget https://github.com/vmware-tanzu/octant/releases/download/v0.25.1/octant_0.25.1_Linux-64bit.tar.gz

$ tar -xvzf octant_0.25.1_Linux-64bit.tar.gz && mv octant_0.25.1_Linux-64bit octant

$ rm octant_0.25.1_Linux-64bit.tar.gz
```

Then, to start Octant,simply run the binary:

```bash
$ cd octant
$ ./octant
```

Finally you can see the dashboard:

![Octant Dashboard](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/gfsbx3ktdmowevi5dsaa.png)

### Comparison: Kubernetes Dashboard vs Octant

|Feature |Kubernetes Dashboard  | Octant|
|--------|----------------------|-------|
|Installation| Requires deployment on the cluster| Local installation|
|Access| Via web proxy| Localhost|
|Real-Time Updates|Partial (requires manual refresh)|Full real-time updates|
|Ease of Setup|Moderate (requires token and RBAC)|Easy (just run the binary)|

### Conclusion

Both Kubernetes Dashboard and Octant offer valuable features for monitoring Kubernetes clusters in K3D. If you need a quick and easy way to monitor your local cluster with minimal setup, Octant is a great choice. On the other hand, if you want an experience closer to managing a production environment, Kubernetes Dashboard is the better option.

References:

- Deploy and Access the Kubernetes Dashboard. https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard.

- K3D Install Dashboard. https://gist.github.com/smijar/64e76808c8a349eb64f56c71dc03d8d8.

- Setting Up Kubernetes Dashboard on K3D Cluster. https://medium.com/@mamoonaaslam/setting-up-kubernetes-dashboard-on-k3d-cluster-7bd2e261e42a.

