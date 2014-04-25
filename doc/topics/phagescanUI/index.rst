============================
Phagescan Web User Interface
============================

The Phagescan web user interface is where a user spends most of his time.

Accessing
=========

Access the Phagescan Web User Interface on localhost by going to this URL::

    http://127.0.0.1:9000

A production master will have a Nginx front-end, so you'll want to access via
the public IP address or domain name that Nginx is listening on.
It may be on port 80 or 443 depending on SSl configuration::

    http://1.2.3.4
    http://phagescan.example.com
    https://1.2.3.4
    https://phagescan.example.com

Usage
=====

Most of the links at the top should be self-explanatory.
However, the Server Status page needs some explanation.
See the :doc:`Server Status </topics/phagescanUI/server_status>` documentation for assistance.

TODO: Add more about the UI.