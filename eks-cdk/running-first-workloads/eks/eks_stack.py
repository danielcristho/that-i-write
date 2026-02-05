from aws_cdk import (
Stack,
aws_eks as eks,
aws_ec2 as ec2,
)

from aws_cdk.lambda_layer_kubectl_v32 import KubectlV32Layer

from aws_cdk import aws_iam as iam

from constructs import Construct

class CdkEksStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        kubectl_layer = KubectlV32Layer(self, "KubectlLayer")
        
        vpc = ec2.Vpc(
            self,
            "EksVpc",
            max_azs=2 # AZ
        )
        
        self.cluster = eks.Cluster(
            self,
            "EksCluster",
            version=eks.KubernetesVersion.V1_32,
            vpc=vpc,
            default_capacity=0,
            kubectl_layer=kubectl_layer
        )
        
        self.cluster.add_nodegroup_capacity(
            "ManagedNodeGroup",
            desired_size=2,
            min_size=1,
            max_size=3,
            instance_types=[ec2.InstanceType("t3.medium")], # 2vcpu/4gi
        )
        
        self.cluster.aws_auth.add_user_mapping(
            iam.User.from_user_name(
            self,
            "AdminUser",
            "<YOUR_IAM>"
            ),
            groups=["system:masters"],
        )