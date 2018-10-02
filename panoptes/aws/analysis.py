""" Panoptes - AWS - Analysis

Responsible to the entire AWS analysis. Here the dynamic whitelist,
the logic behind unknown ingress rules and unused security groups are created.
"""

import panoptes.aws.authentication
import panoptes.aws.whitelist
import panoptes.aws.attached
import panoptes.generic.analysis
import boto3


CLOUD_PROVIDER = "aws"


def generate_unused_secgroup_entry(security_group):
    """
    Generates a dictionary from an unused security group to the analysis
    response
    """
    unused_group = {
        'GroupName': security_group['GroupName'],
        'GroupId': security_group['GroupId'],
        'Description': security_group['Description'],
        'VpcId': security_group.get('VpcId') or 'no-vpc',
    }
    return unused_group


def generate_unsafe_secgroup_entry(security_group, unsafe_ingress_entries):
    """
    Generates a dictionary from an unsafe security group, receiving all
    unsafe ingress entries related to this security group to the analysis
    response
    """
    unsafe_group = {
        "GroupName": security_group['GroupName'],
        "GroupId": security_group['GroupId'],
        "Description": security_group['Description'],
        "UnsafePorts": unsafe_ingress_entries,
    }
    return unsafe_group


def generate_unsafe_ingress_entry(ingress_entry, unsafe_ip):
    """
    Generates a dictionary from an unsafe ingress entry to the analysis
    response
    """
    unsafe_ingress = {
        "IpProtocol": ingress_entry["IpProtocol"],
        "CidrIp": unsafe_ip,
    }
    if "FromPort" in ingress_entry.keys():
        unsafe_ingress["FromPort"] = ingress_entry["FromPort"]
    if "ToPort" in ingress_entry.keys():
        unsafe_ingress["ToPort"] = ingress_entry["ToPort"]
    return unsafe_ingress


def analyze_security_groups(session, whitelist=[]):
    """
    The main analysis function

    Parameters:
        - aws_session:
            Type: boto3.Session
            Description: Client object from cloud_authentication modules

        - whitelist:
            Type: list
            Description: List of whitelisted CIDR from optional input file

    DesiredReturn:
        {
            "Metadata": {
                "StartedAt": str[ISO 8601 Date],
                "FinishedAt": str[ISO 8601 Date],
                "CloudProvider": {
                    "Name": str,
                    "Auth": str,
                },
            },
            "SecurityGroups": {
                "UnusedGroups": [
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
                                "FromPort": int,
                                "ToPort": int,
                                "IpProtocol": str,
                                "CidrIp": str,
                            },
                        ]
                    },
                ],
            },
        }
    """
    response = {
        'SecurityGroups': {
            'UnusedGroups': [],
            'UnsafeGroups': [],
        },
        'Metadata': {
            'StartedAt': '',
            'FinishedAt': '',
            'CloudProvider': {
                'Name': '',
                'Auth': '',
            },
        },
    }
    response['Metadata']['StartedAt'] = panoptes.generic.analysis.get_current_time()

    whitelist += panoptes.aws.whitelist.list_all_safe_ips(session)
    all_security_groups = session.client('ec2').describe_security_groups()['SecurityGroups']
    all_attached_groups = panoptes.aws.attached.list_all_attached_secgroups(session)

    for security_group in all_security_groups:
        # Validating if group is unused
        if (
                security_group['GroupName'] not in all_attached_groups and
                security_group['GroupId'] not in all_attached_groups
        ):
            response['SecurityGroups']['UnusedGroups'].append(
                generate_unused_secgroup_entry(
                    security_group=security_group
                )
            )

        # Validating if group is unsafe
        unsafe_ingress_entries = []
        for ingress_entry in security_group['IpPermissions']:
            for allowed_ip in ingress_entry['IpRanges']:
                if allowed_ip['CidrIp'] not in whitelist:
                    unsafe_ingress_entries.append(
                        generate_unsafe_ingress_entry(
                            ingress_entry=ingress_entry,
                            unsafe_ip=allowed_ip['CidrIp'],
                        )
                    )
        if unsafe_ingress_entries:
            response['SecurityGroups']['UnsafeGroups'].append(
                generate_unsafe_secgroup_entry(
                    security_group=security_group,
                    unsafe_ingress_entries=unsafe_ingress_entries,
                )
            )

    response['Metadata']['FinishedAt'] = panoptes.generic.analysis.get_current_time()
    response['Metadata']['CloudProvider']['Name'] = CLOUD_PROVIDER
    response['Metadata']['CloudProvider']['Auth'] = panoptes.aws.authentication.get_session_info(session)

    return response


if __name__ == "__main__":
    pass
