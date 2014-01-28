==========================
Troubleshooting OpenStack
==========================

OpenStack is a complex framework. It is beyond the scope of our documentation to go into it's setup and configuration.
However, we do have a few tips that are helpful when dealing with Phagescan Workers running in OpenStack.

Find Network IPs in Use by Virtual Network Hardware
===================================================

The easiest way is to use the :doc:`OpenStackUI </topics/openstackUI/index>`.
Alternatively, you can use the command line.

On the command line, you can do the following.

Get the list of devices::

    sudo ip netns list

At a minimum, you should see a ``qrouter`` and a ``qdhcp`` device.

Query the status of each device::

    sudo ip netns exec <qrouter-blah-uuid> ifconfig -a
    sudo ip netns exec <qdhcp-blah-uuid> ifconfig -a



Log onto a Worker VM
====================

This can be done either using the :doc:`OpenStack UI's </topics/openstackUI/index>` VNC relay or the command line.

For the command line, it will only work on the Linux VM's and only ssh with public key auth is allowed.
Make sure you have the private key associated with the public key stored in the VM.

If you do not know the IP address of the VM that you want to connect to,
use the :doc:`OpenStack UI </topics/openstackUI/index>`
to find the IP and OS Type of the VM that you want to connect to.

Find the qrouter by doing this::

    $ sudo ip netns list

Using the qrouter value and the username for that VM type, do this::

    $ sudo bash
    $ ip netns exec qrouter-<lots of UUID chars> ssh -i /path/to/.ssh/id_rsa username@vm_ipaddr

Remember this: If you change anything on a VM, your changes will not persist for the long term.
Phagescan destroys VMs and re-creates them from a template VM when you click the "X" or "UP arrow" icons on the server status page.

Odd Networking Issues
=====================

Make sure the virtual router and dhcp service are running::

    $ sudo ip netns list

You should see both a qrouter-<long uuid> and a qdhcp-<long uuid> entry.

Make sure both of them have IP addresses.
If they don't or they're not up then the workers probably can't get to RabbitMQ::

    $ sudo ip netns exec <qrouter-long-uuid> ifconfig -a
    $ sudo ip netns exec <qdhcp-long-uuid> ifconfig -a

Make sure the worker VMs have an IP address and in the proper IP subnet matching the qdhcp and qrouter.
You can log in using the VNC method and then check the interface settings.

Make sure you can ping the Phagescan UI IP Address from the Worker.
Log onto the worker using either VNC or CLI and ping the IP of the Phagescan UI.

While logged onto the worker, look at the worker celery logs.

If none of those seems to help, it might be best to do a proper reboot of the master host.
See "WHAT IS THE BEST WAY TO REBOOT THE MASTER HOST"


Where To Find Logs
==================

OpenStack logs are in::

    /var/log/

You'll often wan the horizon or nova logs if you are investigating VM issues.

