Ansible Scripts for creating a local KVM lab. Uses cloud images, with cloud-init or Linux ISO's, with kickstart to setup the RHEL/CentOS/Fedora VM's.

The primary requirement for this project is that you have **ansible**, and a RHEL/CentOS/Fedora dnsmasq+NetworkManager setup (setup by ansible):

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

During the setup of the hypervisor you can define an SDN (virtual network), and SDSP (software defined storage pool). These are defined in the inventory of the lab. 

```text
[hypervisor:vars]
libvirt_bridges=[{'name': 'minilab', 'forward': 'nat', 'bridge': 'virbr-100', 'domain': 'minilab.org', 'network': '192.168.100.0', 'broadcast': '192.168.100.255', 'ip_address': '192.168.100.254', 'ip_netmask': '255.255.255.0', 'dhcp_start': '192.168.100.1', 'dhcp_end': '192.168.100.253'}]
libvirt_pools=[{'virt-pool': { 'type': 'dir', 'path': '~/VirtualMachines' }, 'virt-pool2': { 'type': 'lvm', 'path': '/dev/mmcblk0' } }]
```
Because the hypervisor is modified to also use dnsmasq, over the systems resolve.conf configuration (and the networking config) create dnsmasq configurations for each lab network that gets defined.
DNS for all the lab hosts should work out of the box.

DNS can be tested by querying a lab hosts fqdn:

```
# dig host@domain
```

The hypervisor setup is broken up into 3 parts: 

  - hypervisor_setup.yml
  - nat_network.yml
  - storage_pool.yml

The first stage, the `hypervisor_setup.yml`, ensures that your system has the correct packages, as well as the correct NetworkManager Setup for DNS. 
The second and third stanges (are interchangable, order does not matter) and independently defing the networking and storage for your hypervisor. 

The final stage of the lab setup is provisioning (`provision.yml`), where the defined VM's in the `[lab]` group of the inventory are created (provisioned). 

# Defining the Lab
The basic options for defining VM's are defined as follows: 
```
[lab:vars]
cloud_user_passwd="password"
#ssh_pub_key="ssh-rsa KEY user@HOST"
resources={'vcpus': 2, 'ram': 1024, 'disks': [{'size': 10, 'pool': 'virt-pool'}, {'size': 1, 'pool': 'virt-pool'}, {'size': 2, 'pool': 'virt-pool'}], 'network': 'minilab'}

[lab]
fedora_iso.minilab.org image_uri="https://download.fedoraproject.org/pub/fedora/linux/releases/27/Server/x86_64/iso/Fedora-Server-dvd-x86_64-27-1.6.iso" image_checksum="sha256:e383dd414bb57231b20cbed11c4953cac71785f7d4f5990b0df5ad534a0ba95c" 
fedora_cloud.minilab.org image_uri="https://download.fedoraproject.org/pub/fedora/linux/releases/27/CloudImages/x86_64/images/Fedora-Cloud-Base-27-1.6.x86_64.qcow2" image_checksum="sha256:5af84b59b9c8c132adf4989fc8f20c6a0297b1b53ce992014d934a51cccdd4c9"
```

--- Experimental Options ---

- Optional: update: true   ## Defaults to false
- Optional: install_packages: [curl, vim]

```

# Building you Lab 

You can build your lab with the following:

```bash 
ansible-playbook -i INVENTORY provision.yml -K
```

# TODO: Need to write these playbooks 
# Destroying / Cleaning up your Lab

You can destroy / clean up your lab, with the following:

```bash
# ansible-playbook -i INVENTORY cleanup.yml -K
```

- Note: The cloud images (that you define for each host to download), are not removed by default, as you may want to re-use them.
   - you can delete these by setting the **cleanup_cloud_images** variable, in the cleanup.yml file to **true**.

# Recommendations:

SSH to the Host's:

It is recommended that you use `-o "UserKnownHostsFile /dev/null` when sshing to nodes, so that your knonhosts file is not updated when you ssh to the nodes.

Example:
```bash
ssh cloud-user@hostname -o "UserKnownHostsFile /dev/null"
```
