# Exploring K3S on Docker using K3D

In this post, I’ll show you how to start with [K3D](https://k3d.io/stable), an awesome tool for running lightweight Kubernetes clusters using [K3S](https://docs.k3s.io/) on Docker. I hope this post will help you quickly set up and understand K3D. Let’s dive in!

## What is K3S?

Before starting with K3D we need to know about K3S. Developed by [Rancher Labs](https://www.rancher.com/products/k3s), K3S is a lightweight Kubernetes distribution designed for IoT and edge environments. It is a fully conformant Kubernetes distribution but optimized to work in resource-constrained settings by reducing its resource footprint and dependencies.

Key highlights of K3S include:

- Optimized for Edge: Ideal for small clusters and resource-limited environments.

- Built-In Tools: Networking (Flannel), ServiceLB Load-Balancer controller and Ingress (Traefik) are included, minimizing setup complexity.

- Compact Design: K3S simplifies Kubernetes by bundling everything into a single binary and removing unnecessary components like legacy APIs.

Now let’s dive into K3D.

## What is K3D?

K3D acts as a wrapper for K3S, making it possible to run K3S clusters inside **Docker containers**. It provides a convenient way to manage these clusters, offering speed, simplicity, and scalability for local Kubernetes environments.

![Docker meme](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/6qo7m0e15ei8nl0dqexi.png)

Here’s why K3D is popular:

- Ease of Use: Quickly spin up and tear down clusters with simple commands.

- Resource Efficiency: Run multiple clusters on a single machine without significant overhead.

- Development Focus: Perfect for local development, CI/CD pipelines, and testing.

Let’s move on to how you can set up K3D and start using it.

### Requirements

Before starting with K3D, make sure you have installed the following prerequisites based on your operating system.

- Docker

    Follow the Docker [installation guide](https://docs.docker.com/engine/install/) for your operating system. Alternatively, you can simplify the process with these commands:

    ```bash
    $ curl -fsSL https://get.docker.com -o get-docker.sh
    $ sudo sh get-docker.sh
    $ sudo usermod -aG docker $USER #add user to the docker group
    $ docker version

    Client: Docker Engine - Community
    Version:           27.4.0
    API version:       1.47
    Go version:        go1.22.10
    Git commit:        bde2b89
    Built:             Sat Dec  7 10:38:40 2024
    OS/Arch:           linux/amd64
    Context:           default
    ...
    ```

- Kubectl

    The Kubernetes command-line tool, kubectl, is required to interact with your K3D cluster. Install it by following the instructions on the [official Kubernetes documentation](https://kubernetes.io/docs/tasks/tools/). Or you can follow this step:

    ```bash
    $ curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    $ sudo install kubectl /usr/local/bin/kubectl
    $ kubectl version --client

    Client Version: v1.32.0
    Kustomize Version: v5.5.0
    ```

- K3D

    Install K3D by referring the [official documentation](https://k3d.io/stable/#installation) or using the following command:

    ```bash
    $ curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
    $ k3d --version

    k3d version v5.7.4
    k3s version v1.30.4-k3s1 (default)
    ```

NB: I use Ubuntu 22.04 to install the requirements.

### Create Your First Cluster

#### Basic

```bash
$ k3d cluster create mycluster

INFO[0000] Prep: Network
INFO[0000] Created network 'k3d-mycluster'
INFO[0000] Created image volume k3d-mycluster-images
INFO[0000] Starting new tools node...
INFO[0001] Creating node 'k3d-mycluster-server-0'
INFO[0002] Pulling image 'ghcr.io/k3d-io/k3d-tools:5.7.4'
INFO[0005] Pulling image 'docker.io/rancher/k3s:v1.30.4-k3s1'
INFO[0006] Starting node 'k3d-mycluster-tools'
INFO[0030] Creating LoadBalancer 'k3d-mycluster-serverlb'
INFO[0033] Pulling image 'ghcr.io/k3d-io/k3d-proxy:5.7.4'
INFO[0045] Using the k3d-tools node to gather environment information
INFO[0045] HostIP: using network gateway 172.18.0.1 address
INFO[0045] Starting cluster 'mycluster'
INFO[0045] Starting servers...
INFO[0045] Starting node 'k3d-mycluster-server-0'
INFO[0053] All agents already running.
INFO[0053] Starting helpers...
INFO[0053] Starting node 'k3d-mycluster-serverlb'
INFO[0060] Injecting records for hostAliases (incl. host.k3d.internal) and for 2 network members into CoreDNS configmap...
INFO[0062] Cluster 'mycluster' created successfully!
INFO[0062] You can now use it like this:
kubectl cluster-info
```

This command will create a cluster named mycluster with one control plane node.

Once the cluster is created, check its status using kubectl:

```bash
$ kubectl cluster-info

Kubernetes control plane is running at https://0.0.0.0:43355
CoreDNS is running at https://0.0.0.0:43355/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
Metrics-server is running at https://0.0.0.0:43355/api/v1/namespaces/kube-system/services/https:metrics-server:https/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

To ensure that the nodes in the cluster are active, run:

```bash
$ kubectl get nodes --output wide

NAME                     STATUS   ROLES                  AGE     VERSION        INTERNAL-IP   EXTERNAL-IP   OS-IMAGE           KERNEL-VERSION     CONTAINER-RUNTIME
k3d-mycluster-server-0   Ready    control-plane,master   5m14s   v1.30.4+k3s1   172.18.0.2    <none>        K3s v1.30.4+k3s1   6.8.0-50-generic   containerd://1.7.20-k3s1
```

To list all the clusters created with K3D, use the following command:

```bash
$ k3d cluster list

NAME        SERVERS   AGENTS   LOADBALANCER
mycluster   1/1       0/0      true
```

Stop, start & delete your cluster, use the following command:

```bash
$ k3d cluster stop mycluster

INFO[0000] Stopping cluster 'mycluster'
INFO[0020] Stopped cluster 'mycluster
```

```bash
$ k3d cluster start mycluster

INFO[0000] Using the k3d-tools node to gather environment information
INFO[0000] Starting new tools node...
INFO[0000] Starting node 'k3d-mycluster-tools'
INFO[0001] HostIP: using network gateway 172.18.0.1 address
INFO[0001] Starting cluster 'mycluster'
INFO[0001] Starting servers...
INFO[0001] Starting node 'k3d-mycluster-server-0'
INFO[0005] All agents already running.
INFO[0005] Starting helpers...
INFO[0005] Starting node 'k3d-mycluster-serverlb'
INFO[0012] Injecting records for hostAliases (incl. host.k3d.internal) and for 2 network members into CoreDNS configmap...
INFO[0014] Started cluster 'mycluster'
```

```bash
$ k3d cluster delete mycluster

INFO[0000] Deleting cluster 'mycluster'
INFO[0001] Deleting cluster network 'k3d-mycluster'
INFO[0001] Deleting 1 attached volumes...
INFO[0001] Removing cluster details from default kubeconfig...
INFO[0001] Removing standalone kubeconfig file (if there is one)...
INFO[0001] Successfully deleted cluster mycluster!
```

If you want to start a cluster with extra server and worker nodes, then extend the creation command like this:

```bash
$ k3d cluster create mycluster --servers 2 --agents 4
```

After creating the cluster, you can verify its status using these commands:

```bash
$ k3d cluster list

NAME        SERVERS   AGENTS   LOADBALANCER
mycluster   2/2       4/4      true
```

```bash
$ kubectl get nodes

NAME                     STATUS   ROLES                       AGE   VERSION
k3d-mycluster-agent-0    Ready    <none>                      51s   v1.30.4+k3s1
k3d-mycluster-agent-1    Ready    <none>                      52s   v1.30.4+k3s1
k3d-mycluster-agent-2    Ready    <none>                      53s   v1.30.4+k3s1
k3d-mycluster-agent-3    Ready    <none>                      51s   v1.30.4+k3s1
k3d-mycluster-server-0   Ready    control-plane,etcd,master   81s   v1.30.4+k3s1
k3d-mycluster-server-1   Ready    control-plane,etcd,master   64s   v1.30.4+k3s1
```

#### Bootstrapping Cluster

Bootstrapping a cluster with configuration files allows you to automate and customize the process of setting up a K3D cluster. By using a configuration file, you can easily specify cluster details such as node count, roles, ports, volumes, and more, making it easy to recreate or modify clusters.

Here’s an example of a basic cluster configuration file `my-cluster.yaml` that sets up a K3D cluster with multiple nodes:

```yaml
apiVersion: k3d.io/v1alpha5
kind: Simple
metadata:
  name: my-cluster
servers: 1
agents: 2
image: rancher/k3s:v1.30.4-k3s1
ports:
- port: 30000-30100:30000-30100
  nodeFilters:
  - server:*
options:
  k3s:
    extraArgs:
    - arg: --disable=traefik
      nodeFilters:
      - server:*
```

A K3D config to create a cluster named my-cluster with 1 server, 2 agents, K3S version v1.30.4-k3s1, host-to-server port mapping (30000-30100), and Traefik disabled on server nodes.

```bash
k3d create cluster --config  my-cluster.yaml
```

The result after creation:

```bash
$  kubectl get nodes

NAME                      STATUS   ROLES                  AGE   VERSION
k3d-my-cluster-agent-0    Ready    <none>                 14s   v1.30.4+k3s1
k3d-my-cluster-agent-1    Ready    <none>                 15s   v1.30.4+k3s1
k3d-my-cluster-server-0   Ready    control-plane,master   19s   v1.30.4+k3s1
```

```bash
$ docker ps

CONTAINER ID   IMAGE                            COMMAND                  CREATED              STATUS          PORTS
                                                                                                 NAMES
9c7a53f40065   ghcr.io/k3d-io/k3d-proxy:5.7.4   "/bin/sh -c nginx-pr…"   About a minute ago   Up 46 seconds   80/tcp,
0.0.0.0:30000-30100->30000-30100/tcp, :::30000-30100->30000-30100/tcp, 0.0.0.0:34603->6443/tcp   k3d-my-cluster-server
lb
41f544fa9f8e   rancher/k3s:v1.30.4-k3s1         "/bin/k3d-entrypoint…"   About a minute ago   Up 55 seconds
                                                                                                 k3d-my-cluster-agent-
1
48acdbaa0734   rancher/k3s:v1.30.4-k3s1         "/bin/k3d-entrypoint…"   About a minute ago   Up 55 seconds
                                                                                                 k3d-my-cluster-agent-
0
0e2799145367   rancher/k3s:v1.30.4-k3s1         "/bin/k3d-entrypoint…"   About a minute ago   Up 59 seconds
                                                                                                 k3d-my-cluster-server
-0
```

#### Create Simple Deployment

Once your K3D cluster is up and running, you can deploy applications onto the cluster. A deployment in Kubernetes ensures that a specified number of pod replicas are running, and it manages updates to those pods.

Use the `kubectl create deployment` command to define and start a deployment. For example:

```bash
$ kubectl create deployment nginx --image=nginx

deployment.apps/nginx created
```

Check deployment status using `kubectl get deplyment` command:

```bash
$  kubectl get deployment

NAME    READY   UP-TO-DATE   AVAILABLE   AGE
nginx   0/1     1            0           2m58s
```

Expose the deployment:

```bash
$ kubectl expose deployment nginx --port=80 --type=LoadBalancer
service/nginx exposed
```

Verify the Pod and Service:

```bash
$ kubectl get pods

NAME                    READY   STATUS    RESTARTS   AGE
nginx-bf5d5cf98-p6mpj   1/1     Running   0          69s

```

```bash
$ kubectl get svc

NAME         TYPE           CLUSTER-IP    EXTERNAL-IP                        PORT(S)        AGE
kubernetes   ClusterIP      10.43.0.1     <none>                             443/TCP        95s
nginx        LoadBalancer   10.43.122.4   172.18.0.2,172.18.0.3,172.18.0.4   80:30893/TCP   66s
```

Try to access using browser by using LoadBalancer EXTERNAL-IP:

```bash
$ http://172.18.0.2:30893
```

![Access service](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/38h139wdsbm5j539qh2o.png)

### Conclusion

K3D simplifies the process of running Kubernetes clusters with K3S on Docker, making it ideal for local development and testing. By setting up essential tools like Docker, kubectl, and K3D, you can easily create and manage clusters. You can deploy applications with just a few commands, expose them, and access them locally. K3D offers a flexible and lightweight solution for Kubernetes, allowing developers to experiment and work with clusters in an efficient way.

Thank you for taking the time to read this guide. I hope it was helpful in getting you started with K3D and Kubernetes!😀
