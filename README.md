Ansible Scripts for creating a local KVM lab. Uses Cloud images (pulled from Red Hat Internal Resources) and cloud-init to setup the VM's.

The primary requirement for this project is that you have **ansible**, and a python dns module if your running Fedora:

```bash
dnf install ansible python2-dnf -y
```
The **minilab** is setup so that you define, inventories (lab environments), like the **example**.

# Defining a Lab

## Defining a Hypervisor

Each lab, or inventory file, must define a hypervisor like so:

```text
[hypervisor]
127.0.0.1 ansible_connection=local
```
- If this is not defined like this, your lab will not work.

Each lab (assumes that it should be isolated to the hypervisor - from a networking perspective).
Meaning that only the "hypervisor" can access the VM's (from a NAT'ed Bridge). - Currently the only networking option.

During the setup of this SDN (virtual network), a definition of the hosts is provided to the network (using a custom filter), so that libvirt's integration with dnsmasq can be used to provide DNS for the VM's.
As a result every `libvirt_bridges` needs to define `dns_names: "{{ groups.lab | create_dns_names(hostvars) }}"` if the DNS name setup is to function properly.

This is done by letting libvirt's network (a dnsmasq process) handle DNS for the network.

Because the hypervisor is modified to also use dnsmasq, over the systems resolve.conf configuration (and the networking config) create dnsmasq configurations for each lab network that gets defined.
DNS for all the lab hosts should work out of the box.

DNS can be tested by querying a lab hosts fqdn:

```
# dig host@domain
```

# Defining the Lab

Your lab, must be defined as a host group, labeled **lab**.

Example:
```text
[lab]
test1
test2
```

The only think you have to define in this file are the host names for each system. However is you so choose, you can pass variables with the hosts as well.

If you look in the **host_vars** folder in the example you can see a set of variables that are required / or that are optional.

```text
ip: 192.168.100.1
host_image_uri: "http://mirror.cc.vt.edu/pub/fedora/linux/releases/26/CloudImages/x86_64/images/Fedora-Cloud-Base-26-1.5.x86_64.qcow2"
ram: 512MB                       ## Needs to be in a #MB, as it will be translated into a #, MB is the only supprted value definition. 

# Optional: cloud_usr_passwd: password     ### Note for RHEL systems the user is cloud-user
# Optional: ssh_pub_key="ssh-rsa KEY user@HOST"
   - While these are optional one of them wil need to be specified, in order for you to be given access to the VM.

# Optional: storage_extend: 2GB  ## Needs to be in #{SIZE} format
# Optional: extra_disk: 20GB     ## Needs to be in a #GB, as it will be translated into a # defining the size of an extra volume, mounted as /dev/sdb. It should only be supplied once. 
# Optional: run_cmds: [['echo', '1234'], ['curl', 'www.google.com']]

--- Experimental ---

# Optional: update: true   ## Defaults to false
# Optional: install_packages: [curl, vim]

```

# Building you Lab 

You can build your lab with the following:

```bash 
ansible-playbook -i INVENTORY main.yml -K
```

# Destroying / Cleaning up your Lab

You can destroy / clean up your lab, with the following:

```bash
# ansible-playbook -i INVENTORY cleanup.yml -K
```

- Note: The cloud images (that you define for each host to download), are not removed by default, as you may want to re-use them.
   - you can delete these by setting the **cleanup_cloud_images** variable, in the cleanup.yml file to **true**.

Recommendations:

SSH to the Host's:

It is recommended that you use `-o "UserKnownHostsFile /dev/null` when sshing to nodes, so that your knonhosts file is not updated when you ssh to the nodes.

Example:
```bash
ssh cloud-user@hostname -o "UserKnownHostsFile /dev/null"
```
