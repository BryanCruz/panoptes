""" Panoptes - Cloud Output - AWS

Collection of functions to print AWS analysis output.
"""

import json
import yaml
from colorama import init, Fore, Back, Style


def output_json(analysis):
    """
    Prints in the screen a prettified JSON version from AWS analysis dictionary
    """
    output = json.dumps(
        analysis,
        indent=4,
        sort_keys=True
    )
    print(output)
    return None


def output_yml(analysis):
    """
    Prints in the screen an YML version from AWS analysis dictionary
    """
    output = yaml.dump(
        analysis,
        default_flow_style=False,
        allow_unicode=True,
    )
    print(output)
    return None


def output_human(analysis):
    """
    Converts the AWS analysis dictionary into human readable output
    """
    def generate_info_message(content):
        return (Fore.LIGHTCYAN_EX
                + "INFO: {}".format(content)
                + Style.RESET_ALL)

    def generate_warning_message(content):
        return (Fore.YELLOW
                + "WARNING: {}".format(content)
                + Style.RESET_ALL)

    def generate_alert_message(content):
        return (Fore.LIGHTRED_EX
                + "ALERT: {}".format(content)
                + Style.RESET_ALL)

    def generate_section_message(content):
        return (Style.RESET_ALL
                + "\n\n\n"
                + Style.BRIGHT
                + Fore.WHITE
                + content
                + Style.RESET_ALL
                + "\n")

    unused_groups_list = analysis['SecurityGroups']['UnusedGroups']
    unsafe_groups_list = analysis['SecurityGroups']['UnsafeGroups']

    init()
    print("""
=============================================================
||                                                         ||
||                  PANOPTES AWS Analysis                  ||
||                                                         ||
=============================================================""")

    print(
        generate_section_message(
            "1. UNUSED SECURITY GROUPS"
        )
    )

    if unused_groups_list:
        for unused_group in unused_groups_list:
            unused_group_message = (
                Fore.LIGHTYELLOW_EX + unused_group['GroupId']
                + "   "
                + Fore.WHITE + unused_group['GroupName']
                + Style.RESET_ALL
            )
            print(unused_group_message)

        print("")
        amount_unused_msg = (
            "There are "
            + str(len(unused_groups_list))
            + " security groups not being used"
        )
        print(generate_warning_message(amount_unused_msg))
    else:
        all_attached_msg = (
            "All security groups are attached and being used"
        )
        print(generate_info_message(all_attached_msg))

    print(
        generate_section_message(
            "2. SECURITY GROUPS WITH UNSAFE INGRESS RULES"
        )
    )
    if unsafe_groups_list:
        for unsafe_group in unsafe_groups_list:
            print("")

    return None


if __name__ == "__main__":
    pass
