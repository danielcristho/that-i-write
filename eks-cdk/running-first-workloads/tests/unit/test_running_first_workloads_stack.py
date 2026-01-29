import aws_cdk as core
import aws_cdk.assertions as assertions

from running_first_workloads.running_first_workloads_stack import RunningFirstWorkloadsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in running_first_workloads/running_first_workloads_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RunningFirstWorkloadsStack(app, "running-first-workloads")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
