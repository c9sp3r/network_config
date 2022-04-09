from netmiko import ConnectHandler
from textfsm import TextFSM
import os


def connect(device_type, ip, username, password, port, secret):
    device = {
        'device_type': device_type,
        'ip': ip,
        'username': username,
        'password': password,
        'port': port,
        'secret': secret,
    }

    return ConnectHandler(**device)


def get_interfaces_list(device):
    output_interfaces = device.send_command('show interfaces')
    current_dir = os.getcwd()
    template_file = open(current_dir + "/controller/show_interface.template", "r")
    template = TextFSM(template_file)
    parsed_interfaces = template.ParseText(output_interfaces)

    interface_list = []
    for interface_data in parsed_interfaces:
        resultDict = {}
        resultDict["interface"] = interface_data[0]
        resultDict["mac address"] = interface_data[1]
        resultDict["ip address"] = interface_data[2]
        resultDict["MTU"] = interface_data[3]
        resultDict["bandwith"] = interface_data[4]

        interface_list.append(resultDict)

    return interface_list


def get_ip_route(device):
    output_ip_route = device.send_command('show ip route')
    config_lines = output_ip_route.splitlines()


    return config_lines[10:]

def get_arp(device):
    output_arp = device.send_command('show arp')
    current_dir = os.getcwd()
    template_file = open(current_dir + "/controller/show_arp.template", "r")
    template = TextFSM(template_file)
    parsed_interfaces = template.ParseText(output_arp)

    arp_list = []
    for arp_data in parsed_interfaces:
        resultDict = {}
        resultDict["Protocol"] = arp_data[0]
        resultDict["Address"] = arp_data[1]
        resultDict["Age"] = arp_data[2]
        resultDict["Hardware"] = arp_data[3]
        resultDict["Type"] = arp_data[4]
        resultDict["Interface"] = arp_data[5]

        arp_list.append(resultDict)

    return arp_list[1:]


def get_prefix_list(device):
    device.enable()
    output_prefix = device.send_command('show running-config | section prefix-list', delay_factor=2,cmd_verify=False)
    config_lines = output_prefix.splitlines()
    print(config_lines)
    prefix_lists = {}
    for line in config_lines:
        line = line.strip()
        word_list = line.split()
        if word_list:
            if (word_list[0] == "ip" or word_list[0] == "ipv6") and word_list[1] == "prefix-list":
                if word_list[2] in prefix_lists.keys():
                    prefix_lists[word_list[2]].append(" ".join(word_list[3:]))
                else:
                    prefix_lists[word_list[2]] = [" ".join(word_list[3:])]
    print(prefix_lists)
    return prefix_lists






