# K3D: Getting Started with ArgoCD

Originally published at [danielcristho.site](https://danielcristho.site/blog/k3d-getting-started-with-argocd) & [Medium](https://medium.com/@danielpepuho/k3d-getting-started-with-argocd-dd1acb18e933).

## Intro

ArgoCD is a GitOps tool with a straightforward but powerful objective: to declaratively deploy applications to Kubernetes by managing application resources directly from version control systems, such as Git repositories. Every commit to the repository represents a change, which ArgoCD can apply to the Kubernetes cluster either manually or automatically. This approach ensures that deployment processes are fully controlled through version-controlled files, fostering an explicit and auditable release process.

For example, releasing a new application version involves updating the image tag in the resource files and committing the changes to the repository. ArgoCD syncs with the repository and seamlessly deploys the new version to the cluster.

Since ArgoCD itself operates on Kubernetes, it is straightforward to set up and integrates seamlessly with lightweight Kubernetes distributions like K3s. In this tutorial, we will demonstrate how to configure a local Kubernetes cluster using K3D and deploy applications with ArgoCD, utilizing the argocd-example-apps repository as a practical example.

## Prerequisites

- Docker
- Kubectl
- K3D
- ArgoCD CLI

Before we begin, ensure you have the following installed:

### Step 1: Set Up a K3D Cluster

Create a new Kubernetes cluster using K3D:

```bash
$ k3d cluster create argocluster --agents 2

INFO[0000] Prep: Network
INFO[0000] Created network 'k3d-argocluster'
INFO[0000] Created image volume k3d-argocluster-images
INFO[0000] Starting new tools node...
INFO[0000] Starting node 'k3d-argocluster-tools'
INFO[0001] Creating node 'k3d-argocluster-server-0'
INFO[0001] Creating node 'k3d-argocluster-agent-0'
INFO[0001] Creating node 'k3d-argocluster-agent-1'
INFO[0001] Creating LoadBalancer 'k3d-argocluster-serverlb'
INFO[0001] Using the k3d-tools node to gather environment information
INFO[0001] HostIP: using network gateway 172.18.0.1 address
INFO[0001] Starting cluster 'argocluster'
INFO[0001] Starting servers...
INFO[0002] Starting node 'k3d-argocluster-server-0'
INFO[0009] Starting agents...
INFO[0009] Starting node 'k3d-argocluster-agent-0'
INFO[0009] Starting node 'k3d-argocluster-agent-1'
INFO[0017] Starting helpers...
INFO[0017] Starting node 'k3d-argocluster-serverlb'
INFO[0024] Injecting records for hostAliases (incl. host.k3d.internal) and for 4 network members into CoreDNS configmap...
INFO[0026] Cluster 'argocluster' created successfully!
INFO[0026] You can now use it like this:
kubectl cluster-info
```

Verify that your cluster is running:

```bash
$ kubectl get nodes

NAME                       STATUS   ROLES                  AGE   VERSION
k3d-argocluster-agent-0    Ready    <none>                 63s   v1.30.4+k3s1
k3d-argocluster-agent-1    Ready    <none>                 62s   v1.30.4+k3s1
k3d-argocluster-server-0   Ready    control-plane,master   68s   v1.30.4+k3s1
```

### Step 2: Install ArgoCD

Install ArgoCD in your K3D cluster:

```bash
$ kubectl create namespace argocd

$ kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

customresourcedefinition.apiextensions.k8s.io/applications.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/applicationsets.argoproj.io created
customresourcedefinition.apiextensions.k8s.io/appprojects.argoproj.io created
serviceaccount/argocd-application-controller created
serviceaccount/argocd-applicationset-controller created
serviceaccount/argocd-dex-server created
serviceaccount/argocd-notifications-controller created
serviceaccount/argocd-redis created
serviceaccount/argocd-repo-server created
serviceaccount/argocd-server created
role.rbac.authorization.k8s.io/argocd-application-controller created
role.rbac.authorization.k8s.io/argocd-applicationset-controller created
role.rbac.authorization.k8s.io/argocd-dex-server created
role.rbac.authorization.k8s.io/argocd-notifications-controller created
role.rbac.authorization.k8s.io/argocd-redis created
role.rbac.authorization.k8s.io/argocd-server created
...
```

Check the status of ArgoCD pods:

```bash
$ kubectl get pods -n argocd

NAME                                                READY   STATUS    RESTARTS   AGE
argocd-application-controller-0                     1/1     Running   0          29m
argocd-applicationset-controller-684cd5f5cc-78cc8   1/1     Running   0          29m
argocd-dex-server-77c55fb54f-bw956                  1/1     Running   0          29m
argocd-notifications-controller-69cd888b56-g7z4r    1/1     Running   0          29m
argocd-redis-55c76cb574-72mdh                       1/1     Running   0          29m
argocd-repo-server-584d45d88f-2mdlc                 1/1     Running   0          29m
argocd-server-8667f8577-prx6s                       1/1     Running   0          29m
```

Expose the ArgoCD API server locally, then try to accessing the dashboard:

```bash
$ kubectl port-forward svc/argocd-server -n argocd 8080:443
```

![ArgoCD](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/3stdlm3paa6ng2c7x273.png)

### Step 3: Configure ArgoCD

#### Log in to ArgoCD

Retrieve the initial admin password:

```bash
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d
```

Log in using the `admin` username and the password above.

![Log in into ArgoCD Dashboard](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/szt6ouai79s137s4kg26.png)

#### Connect a Git Repository

Just clone the argocd-example-apps repository:

```bash
git clone https://github.com/argoproj/argocd-example-apps.git
```

Specify the ArgoCD server address in your CLI configuration:

```bash
$ argocd login localhost:8080

WARNING: server certificate had error: tls: failed to verify certificate: x509: certificate signed by unknown authorit
y. Proceed insecurely (y/n)? y
Username: admin
Password:
'admin:login' logged in successfully
Context 'localhost:8080' updated
```

Create a new ArgoCD application using the repository:

```bash
$ $ argocd app create example-app \
  --repo https://github.com/argoproj/argocd-example-apps.git \
  --path ./guestbook \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace default

  application 'example-app' created
```

Sync the application:

```bash
$ argocd app sync example-app

TIMESTAMP                  GROUP        KIND   NAMESPACE                  NAME    STATUS    HEALTH        HOOK  MESSAG
E
2025-01-10T11:31:11+07:00            Service     default          guestbook-ui  OutOfSync  Missing
2025-01-10T11:31:11+07:00   apps  Deployment     default          guestbook-ui  OutOfSync  Missing
2025-01-10T11:31:11+07:00            Service     default          guestbook-ui    Synced  Healthy
2025-01-10T11:31:11+07:00            Service     default          guestbook-ui    Synced   Healthy              service/guestbook-ui created
2025-01-10T11:31:11+07:00   apps  Deployment     default          guestbook-ui  OutOfSync  Missing              deployment.apps/guestbook-ui created
2025-01-10T11:31:11+07:00   apps  Deployment     default          guestbook-ui    Synced  Progressing              deployment.apps/guestbook-ui created
...
```

### Step 4: Verify the Deployment

Check that the application is deployed successfully:

```bash
$ kubectl get pods

NAME                            READY   STATUS    RESTARTS   AGE
guestbook-ui-649789b49c-zwjt8   1/1     Running   0          5m36s
```

Access the deployed application by exposing it via a NodePort or LoadBalancer:

```bash
$ kubectl port-forward svc/guestbook-ui 8081:80

Forwarding from 127.0.0.1:8081 -> 80
Forwarding from [::1]:8081 -> 80
```

![Guestbook UI](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/1wptph3fhlgwiqimxdoh.png)

![Dashboard App List](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ggpgivtv43xd45w6t5v9.png)

![Dashboard App](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/3s82wrd6kt2dv31ayojf.png)

### Conclusion

In this tutorial, you’ve set up a local Kubernetes cluster using K3D and deployed applications with ArgoCD. This setup provides a simple and powerful way to practice GitOps workflows locally. By leveraging tools like ArgoCD, you can ensure your deployments are consistent, auditable, and declarative. Happy GitOps-ing!