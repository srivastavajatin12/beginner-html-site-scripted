import pulumi
from pulumi_azure_native import storage
from pulumi_azure_native import resources
from pulumi_azure_native import network
from pulumi_azure_native import containerservice
from pulumi_azure_native import compute


prefix_name = "pulumiAKS"

vnet_ip_range = "192.168.0.0/16"
vm_ip_range = "192.168.16.0/24"

private_key="azure.pem"

# Create an Azure Resource Group
resource_group = resources.ResourceGroup(
    prefix_name+"-rg",
    resource_group_name=(prefix_name+"-rg"))

#Network security Groups
nsg = network.NetworkSecurityGroup(
    resource_name=(prefix_name+"-nsg"),
    network_security_group_name=(prefix_name+"-nsg"),
    resource_group_name=resource_group.name,
    security_rules=[network.SecurityRuleArgs(
        access="Allow",
        destination_address_prefix="*",
        destination_port_range="22",
        direction="Inbound",
        name="Allow-SSH",
        priority=130,
        protocol="*",
        source_address_prefix="*",
        source_port_range="*",
    )])

#Vnets and subnets
vnet = network.VirtualNetwork(
    prefix_name+"-vnet",
    address_space=network.AddressSpaceArgs(
        address_prefixes=[vnet_ip_range],
    ),
    resource_group_name=resource_group.name,
    virtual_network_name=(prefix_name+"-vnet"))

vm_subnet = network.Subnet(
    "vm-subnet",
    address_prefix=vm_ip_range,
    resource_group_name=resource_group.name,
    subnet_name="vm-subnet",
    virtual_network_name=vnet.name,
    network_security_group=network.NetworkSecurityGroupArgs(
        id=nsg.id
    ))

#virtual Machine
pip = network.PublicIPAddress(
    resource_name=(prefix_name+"-pip"),
    public_ip_address_name=(prefix_name+"-pip"),
    resource_group_name=resource_group.name
)

nic = network.NetworkInterface(
    resource_name=(prefix_name+"-nic"),
    ip_configurations=[network.NetworkInterfaceIPConfigurationArgs(
        name="ipconfig1",
        public_ip_address=network.PublicIPAddressArgs(
            id=pip.id,
        ),
        subnet=network.SubnetArgs(
            id=vm_subnet.id,
        ),
    )],
    network_interface_name=(prefix_name+"-nic"),
    resource_group_name=resource_group.name
)

vm = compute.VirtualMachine(
    resource_name=(prefix_name + "-vm"),
    hardware_profile=compute.HardwareProfileArgs(
        vm_size="Standard_B1s",
    ),
    network_profile=compute.NetworkProfileArgs(
    network_interfaces=[compute.NetworkInterfaceReferenceArgs(
            id=nic.id,
            primary=True,
        )],
    ),
    os_profile=compute.OSProfileArgs(
        admin_username="global",
        computer_name=(prefix_name + "-vm"),
        linux_configuration=compute.LinuxConfigurationArgs(
            disable_password_authentication=True,
            ssh=compute.SshConfigurationArgs(
                public_keys=[compute.SshPublicKeyArgs(
                    key_data=private_key,
                    path = "/home/global/.ssh/authorized_keys",
                )],
            ),
        ),
    ),
    resource_group_name=resource_group.name,
    storage_profile=compute.StorageProfileArgs(
        image_reference=compute.ImageReferenceArgs(
            offer="UbuntuServer",
            publisher="Canonical",
            sku="18.04-LTS",
            version="latest",
        ),
        os_disk=compute.OSDiskArgs(
            caching="ReadWrite",
            create_option="FromImage",
            managed_disk=compute.ManagedDiskParametersArgs(
                storage_account_type="StandardSSD_LRS",
            ),
            name=(prefix_name + "-vm-osdisk"),
        ),
    ),
    vm_name=(prefix_name + "-vm")
)
# Create an Azure resource (Storage Account)
account = storage.StorageAccount('sa',
    resource_group_name=resource_group.name,
    sku=storage.SkuArgs(
        name=storage.SkuName.STANDARD_LRS,
    ),
    kind=storage.Kind.STORAGE_V2)

# Export the primary key of the Storage Account
primary_key = pulumi.Output.all(resource_group.name, account.name) \
    .apply(lambda args: storage.list_storage_account_keys(
        resource_group_name=args[0],
        account_name=args[1]
    )).apply(lambda accountKeys: accountKeys.keys[0].value)

pulumi.export("primary_storage_key", primary_key)
