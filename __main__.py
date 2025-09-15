import pulumi
import pulumi_aws as aws

web_sg = aws.ec2.SecurityGroup("web-sg",
    description="Allow web inbound traffic",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"]
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"]
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=3000,
            to_port=3000,
            cidr_blocks=["0.0.0.0/0"]
        ),
    ],
    egress=[aws.ec2.SecurityGroupEgressArgs(
        protocol="-1",
        from_port=0,
        to_port=0,
        cidr_blocks=["0.0.0.0/0"]
    )]
)

cluster = aws.ecs.Cluster("api-students-cluster")

task_def = aws.ecs.TaskDefinition("api-students-task",
    family="api-students-task",
    network_mode="awsvpc",
    requires_compatibilities=["FARGATE"],
    cpu="256",
    memory="512",
    execution_role_arn="arn:aws:iam::630273685312:role/LabRole",
    task_role_arn="arn:aws:iam::630273685312:role/LabRole",
    container_definitions=pulumi.Output.secret(pulumi.Output.json_dumps([
        {
            "name": "api-students",
            "image": "630273685312.dkr.ecr.us-east-1.amazonaws.com/api-students:latest",
            "essential": True,
            "portMappings": [
                {
                    "containerPort": 3000,
                    "hostPort": 3000,
                    "protocol": "tcp",
                }
            ]
        }
    ]))
)


service = aws.ecs.Service("api-students-service",
    cluster=cluster.arn,
    task_definition=task_def.arn,
    desired_count=1,
    launch_type="FARGATE",
    network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
        subnets=["subnet-09a0d25bfd8fb1cec", "subnet-0d50da2c56a0fce2d"],
        assign_public_ip=True,
        security_groups=[web_sg.id]
    ),
    opts=pulumi.ResourceOptions(depends_on=[task_def])
)

pulumi.export("cluster_name", cluster.name)
pulumi.export("service_name", service.name)
