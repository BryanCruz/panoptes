# Panoptes - AWS

- [Getting Started](README.md#getting-started)
- [Information](README.md#info)
    - [Dynamic Whitelist](README.md#info-dynamic-whitelist)
    - [Limitations](README.md#info-limitations)
- [Commands](README.md#comm)
    - [panoptesctl aws analyze](README.md#comm-analyze)
- [Integration for Developers](README.md#integrating)





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
*Check out [AWS Regions](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html) to see available region codes*

<br>

----

## [Information](#info)
### [Dynamic Whitelist](#info-dynamic-whitelist)
Panoptes generates automatically a list of IP's which it does not consider harmful from the desired cloud provider. It is generated from the AWS resources below:
- VPC ranges
- Subnet ranges
- Private IPs from EC2 VPC Instances
- Public IPs from EC2 VPC Instances
- Elastic IPs

<br>

### [Limitations](#info-limitations)
The Automatic AWS Whitelist feature can't whitelist *public* and *private* IP's from **EC2 Classic**.
Make sure that those instances have an *Elastic IP* attached and their Security Groups are pointing to the new *Elastic IP*, instead of the default EC2 Classic ones.

<br>

----

## [Commands](#comm)

### [panoptesctl aws analyze](#comm-analyze)
Generate the analysis output
##### Options
- **```--region```** : (Required) AWS Region to list the security groups


- **```--profile```** : (Default: ```default```) AWS CLI configured profile which will be used


- **```--output```** : (Default: ```human```) Which kind of output you want the analysis.
    - ```human``` : Colorful human ouput
    - ```json``` : JSON prettified output
    - ```yml``` : YAML prettified output


- **```--whitelist```** : Path to [whitelist](../whitelist_example.txt) with declared safe IPs and CIDR

#### Requirements
You need specific IAM permissions to analyze without headaches. There are some ways to give Panoptes permission to analyze content:

**```The Fast Way```** : Attach the policy ```ReadOnlyAccess``` to the user/role

**```The Compliant Way```** : Create an IAM Policy from [this .json file](aws_analyze_policy.json) and attach it to the user/role


##### Usage
```sh
panoptesctl aws analyze --region us-east-1 --profile my-aws-profile --output yml --whitelist /path/to/my/whitelist.txt
```

<br>

----

## [Integration for Developers](#integrating)
```python
import panoptes


def main():
    MY_REGION = "us-east-1"
    MY_PROFILE = "default"
    # PATH_TO_WHITELIST = "/path/to/whitelist.txt"

    """
    Generate Panoptes AWS auth
    """
    aws_client = panoptes.aws.authentication.get_client(
        region=MY_REGION,
        profile=MY_PROFILE,
    )

    """
    OPTIONAL:
    1- Read the whitelist from a file
    2- Declare the whitelist manually through a list
    """
    #
    # First Way
    #
    #whitelist = panoptes.generic.parser.parse_whitelist_file(
    #    whitelist_path="PATH_TO_WHITELIST"
    #)
    #
    # Second Way
    #
    #whitelist = [
    #    '123.123.123.123/32',
    #    '10.0.0.0/24',
    #    '0.0.0.0/0',
    #]

    """
    Generate the analysis
    """
    generated_analysis = panoptes.aws.analysis.analyze_security_groups(
        aws_client=aws_client,
        # Uncomment below if you declared the whitelist
        # whitelist=whitelist,
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
