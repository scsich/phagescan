#!/bin/bash
# this downloads the boxes for the vmware fusion provider ... not the virtual box
# its a bit faster on macs..
vagrant box add precise64 http://files.vagrantup.com/precise64_vmware_fusion.box
vagrant box add centos6.3_64 https://dl.dropbox.com/u/5721940/vagrant-boxes/vagrant-centos-6.4-x86_64-vmware_fusion.box