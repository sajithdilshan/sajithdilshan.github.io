---
layout: post
title: "Network Configuration with VirtualBox"
date: 2015-11-15 10:15:29 +0530
comments: true
categories: [virtualbox, network, nat, host only, bridged ]
---

When using VirtualBox there are mainly four types of network configurations we could use.

1. Host-Only Adapter
2. NAT
3. NAT Network
3. Bridged Adapter

### Host-Only Adapter
Host-Only Adapter can be used to create a network within the guest OS and the host OS. First go to File -> Preferences and go to the Network section. The go to Host-only Network and add a new host only network as shown below.

{% img https://dl.dropboxusercontent.com/u/30358512/blog/netwok-1.png %}

<!-- more -->

Next edit the vboxnet0 adapter and enable the DHCP server as shown below. As you can see, the virtual machines will get assigned an IP address in the range of 192.168.56.101/24 and 192.168.56.254/24. Further, after adding this adapter, you will see a new network interface 'vboxnet0' in your host OS.

{% img https://dl.dropboxusercontent.com/u/30358512/blog/network-2.png %}

Now open the settings of your virtual machine and go to network section. Under any Adapter tab, select Host-Only Adapter for the 'Attached to' and vboxnet0 for the 'name'. 
 
{% img https://dl.dropboxusercontent.com/u/30358512/blog/network-3.png %}

Now after you boot up the guest OS, it will be assigned an IP address in the range of 192.168.56.101/24 and 192.168.56.254/24 and using this IP, the guest OS and the host OS can communicate with each other.

### NAT

Network Address Translation (NAT), as the name implies, allow external users to access your virtual machine through port forwarding. First, go to File -> Preferences and go to the network section. Then under NAT Networks add a new NATNetwork as shown below.

{% img https://dl.dropboxusercontent.com/u/30358512/blog/network-4.png %}

Next under, the network section in the properties of your virtual machine, select NAT for 'Attached to'. Then click on the 'Port Forwarding' button. For this example, let's assume you want to expose a HTTP server in the virtual machine to external users

{% img https://dl.dropboxusercontent.com/u/30358512/blog/network-5.png %}

Assume the HTTP server in the virual machine runs on the port 9800 and you want to expose it via port 8082 in your host machine. Then add a new port forwarding rule as shown below. You can leave the Host IP and Guest IP to be empty and VirtualBox will correctly resolve those. Just specify the ports correctly. Now if you go to 'http://localhost:8082' in your host OS, you will be forwarded to the HTTP server in your virtual machine.

{% img https://dl.dropboxusercontent.com/u/30358512/blog/network-6.png %}

### NAT Network

NAT Network is similar to the NAT, but using a NAT network you can create an internal network within the virtual machines. First you have to create a NAT Network under File -> Preferences as previously. Next under Network section in the properties of your virtual machine, select 'NAT Network' for 'Attached to'. 

### Bridged Adapter

Bridged adapter can be used get an IP address to the virtual machine in the same network as your host machine is. Assume your host machine is connected to a Wi-Fi router, then using a Bridged adapter, your virtual machine can connect to the same router and obtain an IP address from the router. In-order to create a bridged adapter, go to properties of your virtual machine and click on the Network section. Next select an Adapter tab and add Bridged Adapter for 'Attached to' property and for the 'Name' select the network interface your host machine is using to connect to the external router as shown below. 

{% img https://dl.dropboxusercontent.com/u/30358512/blog/network-7.png %}

With these four types of network adapters, you can create any kind of network within the virtual box and feel free to comment if you have anything to clarify.



