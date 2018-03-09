import boto3
import cloud_providers.aws


class AWSAnalysis:
    def __init__(self):
        None

    def get_ec2_attached_security_groups(self, aws_client):
        ec2_attached_groups = []
        ec2 = aws_client.client('ec2')
        boto_ec2_instances = ec2.describe_instances()
        for instance_json in boto_ec2_instances['Reservations']:
            for instance in instance_json['Instances']:
                for security_group in instance['SecurityGroups']:
                    ec2_attached_groups.append(security_group['GroupId'])
        return list(set(ec2_attached_groups))

    def get_rds_attached_security_groups(self, aws_client):
        rds_attached_groups = []
        rds = aws_client.client('rds')
        boto_rds_instances = rds.describe_db_instances()
        for db_instance_json in boto_rds_instances['DBInstances']:
            for security_group in db_instance_json['VpcSecurityGroups']:
                rds_attached_groups.append(
                    security_group['VpcSecurityGroupId']
                )
        return list(set(rds_attached_groups))


class AWSWhitelist:
    def __init__(self, aws_client):
        self.safe_ips = list(set(self.get_vpc_ranges(aws_client)
                                 + self.get_subnet_ranges(aws_client)
                                 + self.get_vpc_instances_ips(aws_client)
                                 + self.get_elastic_ips(aws_client)))

    def get_vpc_ranges(self, aws_client):
        ec2 = aws_client.client('ec2')
        boto_vpcs = ec2.describe_vpcs()
        vpc_ranges = [
            vpc['CidrBlock'] for vpc in boto_vpcs['Vpcs']
        ]
        return vpc_ranges

    def get_subnet_ranges(self, aws_client):
        ec2 = aws_client.client('ec2')
        boto_subnets = ec2.describe_subnets()
        subnet_ranges = [
            subnet['CidrBlock'] for subnet in boto_subnets['Subnets']
        ]
        return subnet_ranges

    def get_vpc_instances_ips(self, aws_client):
        ec2 = aws_client.client('ec2')
        boto_instances = ec2.describe_instances()
        vpc_instances_ips = []
        for instance_json in boto_instances['Reservations']:
            for instance in instance_json['Instances']:
                for instance_net in instance['NetworkInterfaces']:
                    if 'Association' in instance_net.keys():
                        vpc_instances_ips.append(
                            instance_net['Association']['PublicIp'] + '/32'
                        )
                    if 'PrivateIpAddress' in instance_net.keys():
                        vpc_instances_ips.append(
                            instance_net['PrivateIpAddress'] + '/32'
                        )
                    if 'PrivateIpAddresses' in instance_net.keys():
                        for priv_ip in instance_net['PrivateIpAddresses']:
                            if 'Association' in priv_ip.keys():
                                vpc_instances_ips.append(
                                    priv_ip['Association']['PublicIp'] + '/32'
                                )
                            if 'PrivateIpAddress' in priv_ip.keys():
                                vpc_instances_ips.append(
                                    priv_ip['PrivateIpAddress'] + '/32'
                                )
        return vpc_instances_ips

    def get_elastic_ips(self, aws_client):
        ec2 = aws_client.client('ec2')
        boto_elastic_ips = ec2.describe_addresses()
        elastic_ips = []
        for elastic_ip in boto_elastic_ips['Addresses']:
            if 'PrivateIpAddress' in elastic_ip.keys():
                elastic_ips.append(
                    elastic_ip['PrivateIpAddress'] + '/32'
                )
            elastic_ips.append(
                elastic_ip['PublicIp'] + '/32'
            )
        return elastic_ips


def analyze_security_groups(aws_client, whitelist_file=None):
    response = {
        'SecurityGroups': {
            'UnusedByInstances': [],
            'UnsafeGroups': [],
        }
    }

    if whitelist_file is None:
        whitelist_file = []

    aws_whitelist = AWSWhitelist(aws_client)
    whitelist = whitelist_file + aws_whitelist.safe_ips

    analysis = AWSAnalysis()
    secgroup_services = {
        "ec2": analysis.get_ec2_attached_security_groups(aws_client),
        "rds": analysis.get_rds_attached_security_groups(aws_client),
    }
    all_attached_groups = []
    for secgroup_services, attached_groups in secgroup_services.items():
        all_attached_groups += attached_groups

    ec2 = aws_client.client('ec2')
    all_security_groups = ec2.describe_security_groups()['SecurityGroups']
    for security_group in all_security_groups:
        # Validating if group is unused
        if security_group['GroupId'] not in all_attached_groups:
            if 'VpcId' not in security_group.keys():
                vpc_id = 'no-vpc'
            else:
                vpc_id = security_group['VpcId']
            unused_group = {
                'GroupName': security_group['GroupName'],
                'GroupId': security_group['GroupId'],
                'Description': security_group['Description'],
                'VpcId': vpc_id,
            }
            response['SecurityGroups']['UnusedByInstances'].append(unused_group)
    return response


if __name__ == "__main__":
    """
    analyze_response_analysis = {
        "SecurityGroups": {
            "UnusedByInstances": [
                {
                    "GroupName": str,
                    "GroupId": str,
                    "Description": str,
                    "VpcId": str,
                }
            ],
            "UnsafeGroups": [
                {
                    "GroupName": str,
                    "GroupId": str,
                    "Description": str,
                    "UnsafePorts": [
                        {
                            "FromPort": str,
                            "ToPort": str,
                            "IpProtocol": str,
                            "CidrIp": str,
                        },
                    ]
                },
            ],
        }
    }
    """
    None
