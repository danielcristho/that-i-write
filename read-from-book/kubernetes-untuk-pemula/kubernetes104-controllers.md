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

**ReplicaSets (RS) function as controllers in Kubernetes, responsible for maintaining a consistent number of running Pods for a specific workload**. Acting as the mechanism behind the scenes, the ReplicaSet controller continuously monitors the state of the Pods and ensures the desired replica count is maintained. If a Pod crashes, is evicted, or fails for any reason, the ReplicaSet controller swiftly creates new Pods to restore the desired state, ensuring resilience and uninterrupted service.

In practical use, ReplicaSets are not typically managed directly by users. Instead, they are controlled through Deployments, which leverage the ReplicaSet controller while providing additional features such as rolling updates, rollbacks, and declarative workload management. This abstraction allows users to benefit from the reliability and scalability of ReplicaSet controllers without dealing with their complexities directly.

![ReplicaSet Diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/6kzhidqggm8mlepb6uwu.png)

## 3. DaemonSet

**DaemonSet (DS) ensures that every or specific nodes in a cluster run a copy of a particular Pod**. When a new node is added, DaemonSet automatically creates a Pod on that node. Conversely, when a node is removed, the associated Pod is deleted by the `garbage collector`. Deleting the DaemonSet removes all Pods it created.

![DaemonSet Diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/03t2uvmtrhse6lovati2.png)

Common uses of DaemonSet:

1. Running storage daemons across nodes, such as Glusterd or Ceph.

2. Running log collection daemons across nodes, such as Fluentd or LogStash.

3. Running node monitoring daemons, such as Prometheus Node Exporter, Flowmill, or New Relic Agent.

DaemonSet is ideal for tasks that require processes to run on every node, such as log collection, monitoring, or providing local volumes.

## 4. StatefulSet

**A StatefulSet is a Kubernetes controller used for managing stateful applications. Unlike Deployments, which focus on stateless workloads, StatefulSet is designed for applications that require persistent identity and stable storage**. It ensures that each Pod it manages has a unique, stable network identity and maintains a strict order during creation, scaling, or deletion.

Key Features of StatefulSet:

1. Stable Network Identity: Each Pod gets a unique and persistent DNS name (e.g., `pod-0`, `pod-1`), which remains consistent even after rescheduling.

2. Ordered Pod Deployment and Scaling: Pods are created and scaled in a sequential order. For example, `pod-0` must be created before `pod-1`, and the same applies during deletion.

3. Persistent Storage: StatefulSet works closely with PersistentVolumeClaim (PVC). Each Pod gets a dedicated PersistentVolume that remains intact even after the Pod is deleted or rescheduled.

![StatefulSet Diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/xc9ekn6rrwkg1akmw7a6.png)

Common Use Cases:

1. Databases like MySQL, PostgreSQL, and MongoDB, where stable storage and network identity are critical.

2. Distributed Systems like Cassandra, Kafka, or ZooKeeper, where maintaining order and state is essential.

3. Caching Systems like Redis, requiring predictable storage and replication across nodes.

## 5. Job

**A Job is a Kubernetes controller designed to manage tasks that run to completion**. Unlike Deployments or StatefulSets, which manage long-running or stateful applications, Jobs are used for short-lived workloads that need to be executed only once or a specific number of times.

Key Features of a Job:

1. Ensures Completion: A Job creates one or more Pods to perform a task and ensures that the task is completed successfully. If a Pod fails, the Job controller automatically creates a replacement until the task succeeds.

2. Parallelism: Jobs support parallel execution, allowing multiple Pods to run concurrently, controlled by the parallelism and completions parameters.

3. Retries: Jobs retry failed Pods until the task is successful or a specified backoff limit is reached.

Common Use Cases:

- Batch Processing: Data transformation, ETL pipelines, or video encoding.

- Database Operations: Running migrations, backups, or clean-up scripts.

- One-Time Tasks: Performing diagnostics, generating reports, or initializing configurations.

Thank you for reading this post.😀

References:

- KUBERNETES UNTUK PEMULA. https://github.com/ngoprek-kubernetes/buku-kubernetes-pemula.

- Kubernetes Documentation: Jobs. https://kubernetes.io/docs/concepts/workloads/controllers/job.

- Kubernetes Controllers. https://www.uffizzi.com/kubernetes-multi-tenancy/kubernetes-controllers.

- Kubernetes: DaemonSet. https://opstree.com/blog/2021/12/07/kubernetes-daemonset.

- Kubernetes StatefulSet vs Kubernetes Deployment. https://devtron.ai/blog/deployment-vs-statefulset.