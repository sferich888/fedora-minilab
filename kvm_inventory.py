#!/bin/python 

import xml.etree.ElementTree as ET
import libvirt
import argparse

conn = libvirt.open("qemu:///system")
if conn == None:
    print 'Failed to open connection to hypervisor'
    raise SystemExit

def build_inventory():
    inventory = {}
    inventory['_meta'] = {}

    for dom in conn.listAllDomains():
        vm_bridge = ET.fromstring(dom.XMLDesc(0)).find(
                ".//interface//source[@bridge]").attrib['bridge']
        for network in conn.listAllNetworks():
            if not network.name() in inventory:
                inventory[network.name()] = {
                        'hosts': [],
                        }
            if network.bridgeName() == vm_bridge:
                domain_name = ET.fromstring(
                        network.XMLDesc(0)).find(".//domain").attrib['name']
                fqdn = "{}.{}".format(dom.name(), domain_name)
                inventory[network.name()]['hosts'].append(fqdn)

    return inventory

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", action="store_true", 
            help="Produce a list of hosts.")

    args = parser.parse_args()
    
    if args.list:
       print build_inventory() 
