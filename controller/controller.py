from netmiko import ConnectHandler
from textfsm import TextFSM
import os
import app

IP = "ip"
IPV4 = "ipv4"
IPV6 = "ipv6"
PREFIXLIST = "prefix-list"


def connect(device_type, ip, username, password, port, secret):
    device = {
        'device_type': device_type,
        'ip': ip,
        'username': username,
        'password': password,
        'port': port,
        'fast_cli' : False,
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
    output_prefix = device.send_command('show running-config | section prefix-list', read_timeout=20, delay_factor=2,
                                        cmd_verify=False)
    config_lines = output_prefix.splitlines()

    prefix_lists = {}
    for line in config_lines:
        line = line.strip()
        word_list = line.split()
        if word_list:
            if (word_list[0] == IP or word_list[0] == IPV6) and word_list[1] == PREFIXLIST:
                if word_list[2] in prefix_lists.keys():
                    prefix_lists[word_list[2]].append(" ".join(word_list[3:]))
                else:
                    prefix_lists[word_list[2]] = [" ".join(word_list[3:])]
    print(prefix_lists)
    return prefix_lists


def get_hostname(device):
    output_hostname = device.send_command_timing('sh running-config | section hostname', read_timeout=25,
                                                 delay_factor=2, cmd_verify=False)
    return output_hostname


def get_vlans(device):
    output_vlan = device.send_command('sh vlan brief')
    # config_lines = output_vlan.splitlines()
    current_dir = os.getcwd()
    template_file = open(current_dir + "/controller/show_vlan.template", "r")
    template = TextFSM(template_file)
    parsed_interfaces = template.ParseText(output_vlan)
    vlan_list = []
    for vlan_data in parsed_interfaces:
        vlanDict = {}
        vlanDict["vlan"] = vlan_data[0]
        vlanDict["name"] = vlan_data[1]
        vlanDict["status"] = vlan_data[2]
        vlanDict["ports"] = vlan_data[3]
        vlan_list.append(vlanDict)
    print(vlan_list)
    return vlan_list
