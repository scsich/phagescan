
.. _`PyCharm`: http://www.jetbrains.com/pycharm/

===========================================
Make Pycharm use Python SDK in a Vagrant VM
===========================================

Ensure you've completed the steps for :doc:`setting up a development system <index>` before setting up `PyCharm`_.

These instructions will help you start a new development project in PyCharm.
You need PyCharm 2.7.x or newer. Ideally, you'll have a 3.x version.
And we'll configure your project to use the Python virtualenv in the `phagedev` VM as your SDK.

First, make sure the `phagedev` VM is running.

Add a Remote Project SDK
========================

Start up PyCharm and we'll add a Remote Project SDK.

* NOTE: You will have to re-do this each time to shutdown your VM, or create a new VM. Thankfully, it only takes 30 seconds.

1. Go to the Project Structure settings

    * From Quck Start window, Configure->Project Defaults->Project Structure
    * From an open project, File->Project Project Structure

2. In the Project Structure settings, add a new Project SDK of type Python SDK

3. In the Select Interpreter Path window, select "Remote..."

4. In the Configure Remote Python Interpreter window do the following.

  Enter these values::

        Host=127.0.0.1
        Port=2222
        User name=vagrant (not anonymous login)
        Auth type: Key pair (OpenSSH)
        Private key file: ~/.vagrant.d/insecure_private_key
        Passphrase: <leave it blank>
        Python interpreter path: /opt/psvirtualenv/bin/python

  Click the Test connection... button to verify it works.
  Click OK

  At this point, PyCharm will scp all of the PyCharm helpers into the VM.
  This is why you have to re-do this process for each new VM.

  Notes:

  *  You get the Port value from the output when you ran ``vagrant up <vmname>``.
       The line looks like this::

        [vmname] -- 22 => 2222 (adapter 1)

  *  The "Fill from Vagrant config" button will only work if you are using a properly configured Vagrantfile.

5. In the Project Structure settings, enter a path for the Project compiler output.
   Use something like: [Project_root_dir]/output

6. Click Apply and then OK to close the Project Structure window.

Update Project to use New SDK
=============================

If you already have a project created for PhageScan, you can update the SDK used
by your project to be the new Remote Python SDK.

If you don't have a project created, create one now and select the remote SDK when it asks.


Create a New Python Project
---------------------------

Creating a new Python project for Phagescan is quick and easy.

1. Create a new Project

   * from Quick Start window, Create New Project
   * from an open Project, File->New Project

2. In the New Project window, select "Python Module" in the left frame.
   Enter phagescan as the Project Name. The Project location should be [Project_root_dir].
   Click Next.

3. In the Specify Python Interpreter window, select the Remote Python interpreter.

4. In the desired technologies window, check the box next to Django and enter these values::

    Project name: phagescan
    Application name: scaggr
    Templates folder: [Project_root_dir]/templates

5.  Click Finish.

Creating Test to Run in the VM
------------------------------

You can create/run tests on the remote VM, but first you have to map [Project_root_dir]
on your host to the /vagrant dir on the VM.

1. From within your project, go to Run-> Edit Configurations.
2. Select the sideways wrench icon. It should display the Defaults.
3. Under defauls go to Python tests and select Nosetests.
4. At the bottom of the nosetests window is a field named "Path mappings"
5. Add an entry that maps your [Project_root_dir] on your development host to /vagrant on the vm.
   It will be something like this::


        [Project_root_dir]=/vagrant

6. Click Apply, then OK.
7. Now you can create and run nosetests and they will contain this default mapping.
