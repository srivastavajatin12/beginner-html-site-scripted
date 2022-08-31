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

virtualprivatecloud = aws.ec2.Vpc("devopsjunc-vpc", cidr_block="10.0.0.0/16")

publicsubnet = aws.ec2.Subnet("devopsjunc-public-subnet",
    vpc_id=virtualprivatecloud.id,
    cidr_block= "10.0.0.0/16",
    map_public_ip_on_launch=True,
    tags={
        "Name": "devopsjunc-public-subnet",
    })
privatesubnet = aws.ec2.Subnet("devopsjunc-private-subnet",
    vpc_id=virtualprivatecloud.id,
    cidr_block= "10.0.1.0/16",
    map_public_ip_on_launch=False,
    tags={
        "Name": "devopsjunc-private-subnet",
    })

group = aws.ec2.SecurityGroup('web-sg',
    description='Enable HTTP access',
    ingress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ['0.0.0.0/0'] },
        { 'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0'] },
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
 )

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
    db_subnet_group_name = privatesubnet.id,                         
    vpc_security_group_ids=[group.id],
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

























