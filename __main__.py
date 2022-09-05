import pulumi
import pulumi_aws as aws

config = pulumi.Config()
key_name = config.get('keyName')
 
public_key = config.get('publicKey')

def decode_key(key):
    try:
        key = base64.b64decode(key.encode('ascii')).decode('ascii')
    except:
        pass
    if key.startswith('-----BEGIN RSA PRIVATE KEY-----'):
        return key
    return key.encode('ascii')

private_key = config.require_secret('Id.pem').apply(decode_key)

virtualprivatecloud = aws.ec2.Vpc("devopsjunc-vpc", 
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames = True,
    enable_dns_support = True,
    )

publicsubnet = aws.ec2.Subnet("devopsjunc-public-subnet",
    vpc_id=virtualprivatecloud.id,
    cidr_block= "10.0.0.0/24",
    map_public_ip_on_launch=True,
    tags={
        "Name": "devopsjunc-public-subnet",
    })
privatesubnet = aws.ec2.Subnet("devopsjunc-private-subnet",
    vpc_id=virtualprivatecloud.id,
    cidr_block= "10.0.0.0/24",
    map_public_ip_on_launch=False,
    availability_zone = "us-east-1b",                           
    tags={
        "Name": "devopsjunc-private-subnet",
    })
privatesubnet2 = aws.ec2.Subnet("devopsjunc-private-subnet2",
    vpc_id=virtualprivatecloud.id,
    cidr_block= "10.0.0.0/24",
    map_public_ip_on_launch=False,
    availability_zone = "us-east-1a",                           
    tags={
        "Name": "devopsjunc-private-subnet2",
    })

group = aws.ec2.SecurityGroup('web-sg',
    description='Enable HTTP access',
    ingress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
    },
    ],
    egress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
    }
    ], 
    vpc_id=virtualprivatecloud.id
 )

server = aws.ec2.Instance('web-server',
    ami='ami-08d4ac5b634553e16',
    instance_type='t2.micro',
    key_name='Id',
    vpc_security_group_ids=[group.id],# reference the security group resource above
    subnet_id=publicsubnet.id,
    iam_instance_profile = "AmazonSSMRoleForInstancesQuickSetup",
    private_dns_name_options ={
       "enable_resource_name_dns_a_record" : "True"
    },     
    user_data = """#!/bin/bash
                 set -ex
                 cd /tmp
                 sudo yum install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm
                 sudo systemctl enable amazon-ssm-agent
                 sudo systemctl start amazon-ssm-agent """
 )

default = aws.rds.SubnetGroup("default",
    subnet_ids=[
        privatesubnet.id,
        privatesubnet2.id
    ],
    tags={
        "Name": "My DB subnet group",
    })

rds_server = aws.rds.Instance("db-server",
    allocated_storage=10,
    engine="mysql",
    engine_version="5.7",
    instance_class="db.t3.micro",
    db_name="mydb",
    parameter_group_name="default.mysql5.7",
    password="pulumidata",
    skip_final_snapshot=True,
    username="pulumi",                      
    db_subnet_group_name = default.id,
    vpc_security_group_ids = [group.id],
                             
)

bucket = aws.s3.Bucket("bucket",
    acl="public-read",
    tags={
        "Environment": "Dev",
        "Name": "My bucket",
    })


#pulumi.export("vpcId", vpc.vpc_id)
#pulumi.export("publicSubnetIds", vpc.public_subnet_ids)
#pulumi.export("privateSubnetIds", vpc.private_subnet_ids)    
pulumi.export('bucket_name',  bucket.id)
#pulumi.export('public_ip_db', default.public_id)
#pulumi.export('public_dns_db', default.public_dns)
pulumi.export('public_ip', server.public_ip)
pulumi.export('public_dns', server.public_dns)   

























