Let's start again. Now we will do some practices.

In this part of the Kubernetes series, we will explore how to create a Kubernetes cluster in different environments. Whether you're running Kubernetes locally or in the cloud, understanding how to set up a cluster is fundamental to deploying and managing containerized applications efficiently.

We will cover three different ways to create a Kubernetes cluster:

- Kind (Kubernetes in Docker) - A lightweight way to run Kubernetes clusters locally for testing and development.

- K3D (K3S in Docker) - A more lightweight Kubernetes distribution, optimized for local development and CI/CD workflows.

- EKS (Amazon Elastic Kubernetes Service) - A managed Kubernetes service provided by AWS for running Kubernetes workloads in the cloud.

Each approach has its own use cases, advantages, and trade-offs. Let's dive into each one and see how to set up a cluster.

## Setting Up a Kubernetes Cluster with Kind

![Kind Logo](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/7x44sjqpd4v0ikbgpu2f.png)

Kind (Kubernetes in Docker) is one of the simplest ways to spin up a Kubernetes cluster for local development and testing. It runs Kubernetes clusters inside Docker containers and is widely used for CI/CD and development workflows.

### Prerequisites

- Docker installed on your machine. ([installation guide](https://docs.docker.com/engine/install))
- KIND CLI installed. ([installation guide](https://kind.sigs.k8s.io/docs/user/quick-start/#installation))
- Kubectl CLI installed. ([installation guide](https://kubernetes.io/docs/tasks/tools))

### Create a Cluster with Kind

- Create a new Kind cluster:

```bash
$  kind create cluster --name kind-cluster

Creating cluster "kind-cluster" ...
 ✓ Ensuring node image (kindest/node:v1.31.0) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-kind-cluster"
You can now use your cluster with:

kubectl cluster-info --context kind-kind-cluster

Thanks for using kind! 😊
```

- Check the cluster:

```bash
$   kubectl cluster-info --context kind-kind-cluster

Kubernetes control plane is running at https://127.0.0.1:43417
CoreDNS is running at https://127.0.0.1:43417/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

- List available nodes:

```bash
$ kubectl get nodes

NAME                         STATUS   ROLES           AGE   VERSION
kind-cluster-control-plane   Ready    control-plane   75s   v1.31.0
```

### Create Simple Deployment

- Use the `kubectl` create deployment command to define and start a deployment:

```bash
$  kubectl create deployment nginx --image=nginx

deployment.apps/nginx created
```

- Check deployment status using `kubectl get deployment` command:

```bash
$ kubectl get deployment

NAME    READY   UP-TO-DATE   AVAILABLE   AGE
nginx   0/1     1            0           29s
```

- Expose the deployment:

```bash
$ kubectl expose deployment nginx --port=80 --type=LoadBalancer

service/nginx exposed
```

- Verify the Pod status and then try to access Nginx using your browser:

```bash
$ kubectl get pods

NAME                     READY   STATUS    RESTARTS   AGE
nginx-676b6c5bbc-wd87x   1/1     Running   0          12m
```

![Access Nginx](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/xtltv33114mzja34rr1g.png)

- Delete the cluster when no longer needed

```bash
$  kind delete cluster --name kind-cluster

Deleting cluster "kind-cluster" ...
Deleted nodes: ["kind-cluster-control-plane"]
```

## Setting Up a Kubernetes Cluster with K3D

![K3D Logo](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ad1hu2a7xvrvme945nla.png)

K3D is a tool that allows you to run lightweight Kubernetes clusters using K3S inside Docker. It is a great choice for fast, local Kubernetes development.

### Prerequisites

- Docker installed on your machine. ([installation guide](https://docs.docker.com/engine/install))
- K3D CLI installed. ([installation guide](https://k3d.io/stable/#installation))
- Kubectl CLI installed. ([installation guide](https://kubernetes.io/docs/tasks/tools))

### Create a Cluster with K3D

- Create a new K3D cluster:

```bash
$  k3d cluster create my-k3d-cluster

INFO[0000] Prep: Network
INFO[0000] Created network 'k3d-my-k3d-cluster'
INFO[0000] Created image volume k3d-my-k3d-cluster-images
INFO[0000] Starting new tools node...
INFO[0000] Starting node 'k3d-my-k3d-cluster-tools'
INFO[0001] Creating node 'k3d-my-k3d-cluster-server-0'
INFO[0001] Creating LoadBalancer 'k3d-my-k3d-cluster-serverlb'
INFO[0001] Using the k3d-tools node to gather environment information
INFO[0001] HostIP: using network gateway 172.20.0.1 address
INFO[0001] Starting cluster 'my-k3d-cluster'
INFO[0001] Starting servers...
INFO[0001] Starting node 'k3d-my-k3d-cluster-server-0'
INFO[0008] All agents already running.
INFO[0008] Starting helpers...
INFO[0008] Starting node 'k3d-my-k3d-cluster-serverlb'
INFO[0016] Injecting records for hostAliases (incl. host.k3d.internal) and for 2 network members into CoreDNS configma
p...
INFO[0018] Cluster 'my-k3d-cluster' created successfully!
INFO[0018] You can now use it like this:
kubectl cluster-info
```

- Check the cluster status:

```bash
$ kubectl cluster-info

Kubernetes control plane is running at https://0.0.0.0:46503
CoreDNS is running at https://0.0.0.0:46503/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
Metrics-server is running at https://0.0.0.0:46503/api/v1/namespaces/kube-system/services/https:metrics-server:https/p
roxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

- List available nodes:

```bash
$ kubectl get nodes

NAME                          STATUS   ROLES                  AGE     VERSION
k3d-my-k3d-cluster-server-0   Ready    control-plane,master   2m33s   v1.30.4+k3s1
```

### Create Simple Deployment

- Use the `kubectl` create deployment command to define and start a deployment:

```bash
$ kubectl create deployment httpd --image=httpd
```

- Check deployment status using `kubectl get deployment`  command:

```bash
$ kubectl get deployment

NAME    READY   UP-TO-DATE   AVAILABLE   AGE
httpd   0/1     1            0           45s
```

- Verify the Pod status:

```bash
$  kubectl get pods

NAME                     READY   STATUS    RESTARTS   AGE
httpd-56f946b8c8-84ww8   1/1     Running   0          9m11s
```

- Expose the deployment:

```bash
$ kubectl expose deployment httpd --port=80 --type=LoadBalancer
```

- Try to access using browser:

![Access HTTPD](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/hcz2h6s89xmovj5zxpv5.png)

- Delete the cluster when no longer needed:

```bash
$ k3d cluster delete my-k3d-cluster

INFO[0000] Deleting cluster 'my-k3d-cluster'
INFO[0001] Deleting cluster network 'k3d-my-k3d-cluster'
INFO[0001] Deleting 1 attached volumes...
INFO[0001] Removing cluster details from default kubeconfig...
INFO[0001] Removing standalone kubeconfig file (if there is one)...
INFO[0001] Successfully deleted cluster my-k3d-cluster!
```

## Setting Up a Kubernetes Cluster on AWS EKS

![AWS EKS Logo](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/8stn3qycpy7381a03rj4.png)

Amazon Elastic Kubernetes Service (EKS) is a fully managed Kubernetes service on AWS, designed for running production workloads.

### Prerequisites

- AWS CLI installed and configured. ([installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html))
- EKSCTL CLI installed. ([installation guide](https://eksctl.io/installation))
- Kubectl CLI installed. ([installation guide](https://kubernetes.io/docs/tasks/tools))

### Create a cluster on EKS

To create a Kubernetes cluster in AWS, you can use the AWS Console (dashboard) or the eksctl CLI. For this guide, we will use `eksctl`.

We will provisions an EKS cluster with two `t4g.small` nodes in the `us-east-1` region, making it ready for running Kubernetes workloads.

```bash
$ eksctl create cluster  \
--name cluster-1  \
--region us-east-1 \
--node-type t4g.small \
--nodes 2 \
--nodegroup-name node-group-1

2025-02-01 19:52:35 [ℹ]  eksctl version 0.202.0
2025-02-01 19:52:35 [ℹ]  using region us-east-1
2025-02-01 19:52:37 [ℹ]  setting availability zones to [us-east-1c us-east-1f]

...

2025-02-01 20:02:04 [ℹ]  creating addon
2025-02-01 20:02:04 [ℹ]  successfully created addon
2025-02-01 20:02:05 [ℹ]  creating addon
2025-02-01 20:02:06 [ℹ]  successfully created addon
2025-02-01 20:02:07 [ℹ]  creating addon
2025-02-01 20:02:07 [ℹ]  successfully created addon
"us-east-1" region is ready
```

- Access AWS console, navigate to the EKS service and you can see the cluster is successfully created.

![After cluster creation](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/u6fea9eyql10rn2kvp9f.png)

- List available nodes:

```bash
kubectl get nodes
NAME                             STATUS   ROLES    AGE   VERSION
ip-192-168-xx-yy.ec2.internal   Ready    <none>   17m   v1.30.8-eks-aeac579
ip-192-168-xx-yy.ec2.internal   Ready    <none>   17m   v1.30.8-eks-aeac57
```

### Create Simple Deployment

- Use the kubectl create deployment command to define and start a deployment:

```bash
$ kubectl create deployment nginx --image=nginx

deployment.apps/nginx create
```

- Check deployment status using `kubectl get deployment` command:

```bash
$  kubectl get deployment

NAME     READY   UP-TO-DATE   AVAILABLE   AGE
nginx    1/1     1            1           23s
```

- Verify the Pod status:

```bash
$ kubectl get pods

NAME                     READY   STATUS         RESTARTS   AGE
nginx-bf5d5cf98-9dld5    1/1     Running        0          43s
```

- Expose the service:

```bash
$ kubectl expose deployment nginx --type=LoadBalancer --port=80 --name=nginx-service
```

- Try to access using the browser:

![Access the service](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/s3c2ul7c18ntg8x5tq4r.png)

- Delete the cluster when no longer needed:

```bash
$  eksctl delete cluster --name cluster-1 --region us-east-1

2025-02-01 20:51:59 [ℹ]  deleting EKS cluster "cluster-1"
2025-02-01 20:52:02 [ℹ]  will drain 0 unmanaged nodegroup(s) in cluster "cluster-1"
2025-02-01 20:52:02 [ℹ]  starting parallel draining, max in-flight of 1
2025-02-01 20:52:04 [ℹ]  deleted 0 Fargate profile(s)
2025-02-01 20:52:13 [✔]  kubeconfig has been updated
2025-02-01 20:52:13 [ℹ]  cleaning up AWS load balancers created by Kubernetes objects of Kind Service or Ingress
2025-02-01 20:52:56 [ℹ]
...

2025-02-01 21:02:00 [ℹ]  waiting for CloudFormation stack "eksctl-cluster-1-nodegroup-node-group-1"
2025-02-01 21:02:01 [ℹ]  will delete stack "eksctl-cluster-1-cluster"
2025-02-01 21:02:04 [✔]  all cluster resources were deleted
```

Conclusion

Setting up a Kubernetes cluster is the first step in running containerized applications at scale. In this guide, we've explored three different ways to create a Kubernetes cluster and do a simple deployment: using Kind and K3D for local development and using EKS for cloud-based deployments. Each method has its own advantages depending on your use case.

Stay tuned!

References:

- KUBERNETES UNTUK PEMULA. https://github.com/ngoprek-kubernetes/buku-kubernetes-pemula.

- How do I install AWS EKS CLI (eksctl)?. https://learn.arm.com/install-guides/eksctl
