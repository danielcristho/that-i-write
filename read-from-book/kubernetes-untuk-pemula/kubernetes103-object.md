Let's start again. Now I'm going to talk about Controllers in Kubernetes. In Kubernetes, a Controller is like a cluster's brain, constantly working to ensure the system maintains its desired state. By monitoring objects such as Pods, Deployments, or DaemonSets, Controllers automate tasks and handle changes dynamically. Understanding Controllers is key to grasping how Kubernetes orchestrates and manages workloads seamlessly.

## Common Kubernetes Controllers
Here are some of the most commonly used Controllers in Kubernetes:

## 1. Deployment
Deployments **manage updates to Pods and ReplicaSets declaratively by transitioning the current state to the desired state step-by-step.** They can create new ReplicaSets, adopt existing resources, or remove old Deployments.

![Deployment Diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/rqs2kfd890pb086t69fj.png)

Common uses for Deployments include:

a. Releasing a ReplicaSet and monitoring its status.
b. Updating Pod specifications to declare a new desired state.
c. Scaling up to handle increased load.
d. Rolling back to a previous version if the current state is unstable.
e. Cleaning up unused ReplicaSets.

## 2. ReplicaSet

ReplicaSets (RS) function as controllers in Kubernetes, responsible for maintaining a consistent number of running Pods for a specific workload. Acting as the mechanism behind the scenes, the ReplicaSet controller continuously monitors the state of the Pods and ensures the desired replica count is maintained. If a Pod crashes, is evicted, or fails for any reason, the ReplicaSet controller swiftly creates new Pods to restore the desired state, ensuring resilience and uninterrupted service.

In practical use, ReplicaSets are not typically managed directly by users. Instead, they are controlled through Deployments, which leverage the ReplicaSet controller while providing additional features such as rolling updates, rollbacks, and declarative workload management. This abstraction allows users to benefit from the reliability and scalability of ReplicaSet controllers without dealing with their complexities directly.

![ReplicaSet Diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/6kzhidqggm8mlepb6uwu.png)

## 3. DaemonSet

## 4. StatefulSet

## 5. Job

References:

- KUBERNETES UNTUK PEMULA. https://github.com/ngoprek-kubernetes/buku-kubernetes-pemula.

- Kubernetes Controllers. https://www.uffizzi.com/kubernetes-multi-tenancy/kubernetes-controllers