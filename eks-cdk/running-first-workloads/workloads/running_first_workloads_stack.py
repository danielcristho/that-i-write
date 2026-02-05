from aws_cdk import (
Stack,
aws_eks as eks,
)

from constructs import Construct

import time 

class RunningFirstWorkloadsStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        cluster: eks.Cluster,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

class RunningFirstWorkloadsStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        cluster: eks.Cluster,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ConfigMap for Caddyfile
        cluster.add_manifest(
            "CaddyConfig",
            {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": "caddy-config"
                },
                "data": {
                    "Caddyfile": """
:80 {
    respond "Hello from Caddy v1"
}
"""
                }
            }
        )

        # Caddy Deployment
        cluster.add_manifest(
            "CaddyDeployment",
            {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "caddy"
                },
                "spec": {
                    "replicas": 2,
                    "selector": {
                        "matchLabels": {
                            "app": "caddy"
                        }
                    },
                    "template": {
                    "metadata": {
                        "labels": { "app": "caddy" },
                        "annotations": {
                            "configmap-reload-ts": str(int(time.time()))
                        }
                    },
                        "spec": {
                            "containers": [
                                {
                                    "name": "caddy",
                                    "image": "caddy:2",
                                    "ports": [
                                        {
                                            "containerPort": 80
                                        }
                                    ],
                                    "volumeMounts": [
                                        {
                                            "name": "caddy-config",
                                            "mountPath": "/etc/caddy"
                                        }
                                    ]
                                }
                            ],
                            "volumes": [
                                {
                                    "name": "caddy-config",
                                    "configMap": {
                                        "name": "caddy-config"
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        )

        # Service to expose Caddy
        cluster.add_manifest(
            "CaddyService",
            {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "caddy-service"
                },
                "spec": {
                    "type": "LoadBalancer",
                    "selector": {
                        "app": "caddy"
                    },
                    "ports": [
                        {
                            "port": 80,
                            "targetPort": 80
                        }
                    ]
                }
            }
        )

