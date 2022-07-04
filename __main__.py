import pulumi
import pulumi_aws as aws

group = aws.ec2.SecurityGroup('web-sg',
    description='Enable HTTP access',
    ingress=[
        { 'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0'] }
    ])

server = aws.ec2.Instance('web-server',
    ami='ami-08d4ac5b634553e16',
    instance_type='t2.micro',
    deployer = aws.ec2.KeyPair("deployer", public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDO01Gb0RjIRmLeYgBDB/SvR/vTBBeQ9f9X7p4K7bKUFT4wV3WO0B2NqPVn/TOZj5n9zkFFVLI5AfHqTndf6vWNQx03NGUB8TszOaSgrw1wLdXukZJBWelP8/NaN4SbIU8mAy4meu6fd6Pc0AlgvXy4qRUDN0f0ZFJLyrJqdoU+d18cplzz2jb9nqZJnrCdnfNf6WlsdfZ82lNKDwma5bAQUfqIJEizCqwue8af9FUiw9nH+lBTMCvLJ5l53UILtYB/Ahx8Ft6PSUeIal7WtWFrHEVmm1Fa8TiqJZsNHsKwCcxfdfO/5a/LPNWSWH5mlmFqNcFrUlEEWf87BoZZ9B02FCgeg/HDxxGO8Dm48+2wQ7wyswCfIVZM5XhFUtKXjfo9eJZW0Bqyt9xOIc+x+aJG5nOV9r5Ji7c+ZOEn5u0Pba0nT6H+BnqRydvHSVz5Lmn8n3DM7Y2hRUHKzMA8Sg+lkNghW+STV2v7fyedlAIKFDbqVjolzvZLS2QXhvG76Sk= root@del1-lhp-n80075")
    vpc_security_group_ids=[group.name] # reference the security group resource above
)

pulumi.export('public_ip', server.public_ip)
pulumi.export('public_dns', server.public_dns)
