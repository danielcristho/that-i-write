#!/usr/bin/env python3
import aws_cdk as cdk

from eks.eks_stack import CdkEksStack
from workloads.running_first_workloads_stack import RunningFirstWorkloadsStack

app = cdk.App()

# 1. Create EKS cluster stack
eks_stack = CdkEksStack(
    app,
    "EksStack",
)

# 2. Deploy workloads on top of the cluster
RunningFirstWorkloadsStack(
    app,
    "RunningFirstWorkloadsStack",
    cluster=eks_stack.cluster,
)

app.synth()
