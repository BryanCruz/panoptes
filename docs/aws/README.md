# Panoptes - AWS

- [Getting Started](README.md#getting-started)
- [Information](README.md#information)
    - [Dynamic Whitelist](README.md#dynamic-whitelist)
    - [Limitations](README.md#limitations)
- [Commands](README.md#commands)
    - [panoptesctl aws analyze](README.md#panoptesctl-aws-analyze)
    - [panoptesctl version](README.md#panoptesctl-version)
    - [panoptesctl analysis view](README.md#panoptesctl-aws-analyze)
- [Integration for Developers](README.md#integration-for-developers)





<br>

----

## [Getting Started](#getting-started)
If you want to see the available options:
```bash
panoptesctl aws analyze --help
```

Generate an analysis with human readable output:
```bash
panoptesctl aws analyze --region <YOUR_REGION_CODE>
```

Generate an analysis with YML output and a Named Profile from AWS CLI:
```bash
panoptesctl aws analyze --region <YOUR_REGION_CODE> --profile <YOUR_PROFILE> --output yml
```
*Check out [AWS Regions](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-available-regions) to see available region codes*

<br>

----

## [Information](#information)
### [Dynamic Whitelist](#dynamic-whitelist)
Panoptes generates automatically a list of IP's which it does not consider harmful from the desired cloud provider. It is generated from the AWS resources below:
- VPC ranges
- Subnet ranges
- Private IPs from EC2 VPC Instances
- Public IPs from EC2 VPC Instances
- Elastic IPs

<br>

### [Limitations](#limitations)
The Automatic AWS Whitelist feature can't whitelist *public* and *private* IP's from **EC2 Classic**.
Make sure that those instances have an *Elastic IP* attached and their Security Groups are pointing to the new *Elastic IP*, instead of the default EC2 Classic ones.

<br>

----

## [Commands](#commands)

## [panoptesctl aws analyze](#panoptesctl-aws-analyze)
Generate the analysis output

##### Options
- **```--region```** : (Required) AWS Region to list the security groups


- **```--profile```** : AWS CLI configured profile which will be used


- **```--output```** : (Default: ```human```) Which kind of output you want the analysis.
    - ```human``` : Colorful human ouput
    - ```json``` : JSON prettified output
    - ```yml``` : YAML prettified output


- **```--whitelist```** : Path to [whitelist](../samples/whitelist_example.txt) with declared safe IPs and CIDR


- **```--file```** : Path to save the analysis file from Panoptes


#### Requirements
You need specific IAM permissions to analyze without headaches. There are some ways to give Panoptes permission to analyze content:

**```The Fast Way```** : Attach the policy ```ReadOnlyAccess``` to the user/role

**```The Compliant Way```** : Create an IAM Policy from [this .json file](aws_analyze_policy.json) and attach it to the user/role


#### Usage
```sh
panoptesctl aws analyze --region us-east-1 --profile my-aws-profile --output json --whitelist /path/to/my/whitelist.txt
```

#### Output
```json
{
    "Metadata": {
        "CloudProvider": {
            "Auth": "arn:aws:iam::accountid:user/youruser",
            "Name": "aws"
        },
        "FinishedAt": "2018-01-01T12:40:20.000000",
        "StartedAt": "2018-01-01T12:40:30.000000"
    },
    "SecurityGroups": {
        "UnsafeGroups": [
            {
                "Description": "All Traffic",
                "GroupId": "sg-060c270f54658459f",
                "GroupName": "all-traffic",
                "UnsafePorts": [
                    {
                        "Status": "alert",
                        "CidrIp": "0.0.0.0/0",
                        "IpProtocol": "-1"
                    }
                ]
            },
            {
                "Description": "Pot 80 open to my house",
                "GroupId": "sg-7a211531",
                "GroupName": "http-public",
                "UnsafePorts": [
                    {
                        "Status": "warning",
                        "CidrIp": "123.123.123.123/32",
                        "IpProtocol": "tcp",
                        "FromPort": 80,
                        "ToPort": 80
                    }
                ]
            }
        ],
        "UnusedGroups": [
            {
                "Description": "Kubernetes - Master Nodes",
                "GroupId": "sg-09e97bab78ee5f82a",
                "GroupName": "k8s-master-nodes",
                "VpcId": "vpc-1a2b3c4d"
            },
            {
                "Description": "Kubernetes - Worker nodes",
                "GroupId": "sg-0fb0837417362d743",
                "GroupName": "k8s-worker-nodes",
                "VpcId": "vpc-1a2b3c4d"
            }
        ]
    }
}
```

## [panoptesctl version](#panoptesctl-version)
Show Panoptes version

#### Usage
```sh
panoptesctl version
```

#### Output
```sh
0.4.0
```

## [panoptesctl analysis view](#panoptesctl-analysis-view)
Print analysis in human output from a previously generated analysis file. 
Make sure that the analysis file has the right file extension.

##### Options
- **```--file```** : Path to analysis file generated from Panoptes

#### Usage
```sh
panoptesctl analysis view --file my-analysis-file.json
```

#### Output
```sh
=============================================================
                      PANOPTES Analysis                      
=============================================================



Cloud provider  ->  AWS
Authentication  ->  arn:aws:iam::accountid:user/youruser
Started at      ->  Jan 01 2018, 12:40:30
Finished at     ->  Jan 01 2018, 12:40:20



01. UNUSED SECURITY GROUPS
sg-09e97bab78ee5f82a   k8s-master-nodes
sg-0fb0837417362d743   k8s-worker-nodes


WARNING: 2 security groups found not being used



02. SECURITY GROUPS WITH UNSAFE INGRESS RULES
sg-060c270f54658459f   all-traffic
    All   All   0.0.0.0/0

sg-7a211531   http-public
    TCP   80   123.123.123.123/32


WARNING: 1 rules found with unknown IPs
ALERT: 1 rules found with public IPs or all traffic enabled
```



<br>

----

## [Integration for Developers](#integration-for-developers)
```python
import panoptes


def main():
    MY_REGION = "us-east-1"
    # MY_PROFILE = "default"
    # PATH_TO_WHITELIST = "/path/to/whitelist.txt"
    # MY_SESSION_TOKEN = generate_magic_session_token()
    """
    Generate Panoptes AWS auth
    OBS: Profile is optional. Don't use it if you are running with
        - AWS Roles
        - AWS Access/Secret environment variables
    """
    aws_session = panoptes.aws.authentication.create_session(
        region=MY_REGION,
        # profile=MY_PROFILE,
        # session_token=MY_SESSION_TOKEN,
    )

    """
    OBS: Whitelist file is optional. You can:
        1- Read the whitelist from a file
        2- Declare the whitelist manually through a list
    """


    """
    1st Way
    """
    #YOUR_WHITELIST = panoptes.generic.helpers.parse_whitelist_file(
    #    whitelist_path=PATH_TO_WHITELIST
    #)
    """
    2nd Way
    """
    #YOUR_WHITELIST = [
    #    '123.123.123.123/32',
    #    '10.0.0.0/24',
    #    '0.0.0.0/0',
    #]

    """
    Generate the analysis
    """
    generated_analysis = panoptes.aws.analysis.analyze_security_groups(
        session=aws_session,
        # whitelist=YOUR_WHITELIST,
    )

    """
    CONGRATULATIONS!!!
    You can do whatever you want with it.
    """
    print(generated_analysis)


if __name__ == "__main__":
    main()
    exit()
```
