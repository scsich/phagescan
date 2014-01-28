============================
OpenStack Web User Interface
============================

The OpenStack Web UI is where you will do initial setup and possibly troubleshooting.

Log onto UI
===========

The OpenStack UI is at something like::

    https://10.10.10.10:8080/horizon/project/instances

Note: This UI requires separate credentials from the Phagescan Web UI.

Find IP Addresses for Virtual Network Devices
=============================================

Log into the OpenStack interface and look at the Network page for the description of the virtual network hardware.
For an individual VM, you should look on the Instances page.

Log onto a Worker VM
====================

Go to the OpenStack UI, and click on the "Instances" link.
On the Instances page, click on the Instance that you want to log onto.
Then at the top there are three tabs, click the right-most tab, which is a VNC session to that Instance.
Here you can log in.
