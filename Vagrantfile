# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Define Ubuntu salt master
  # start as: vagrant up saltmaster
  config.vm.define :saltmaster do |saltmaster_conf|
    saltmaster_conf.vm.box = "precise64"
    saltmaster_conf.vm.box_url = "http://files.vagrantup.com/precise64.box"
    saltmaster_conf.vm.hostname = "salt"
    saltmaster_conf.vm.network :private_network, ip: "192.168.33.15"
    saltmaster_conf.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", "2048"]
    end
    # Enable provisioning with Salt stand alone. Salt minion config and
    # states are in a directory relative to this Vagrantfile.
    saltmaster_conf.vm.provision :salt do |salt|
      ## Minion config is set to ``file_client: local`` for masterless
      salt.minion_config = "installation/salt-masterless/minion"
      ## Users our states in "salt/"
      salt.run_highstate = true
    end
  end

  # Define Ubuntu scanworker to use for testing production scanworker build
  # start as: vagrant up prod_uworker
  config.vm.define :prod_uworker do |prod_uworker_conf|
    prod_uworker_conf.vm.box = "precise64"
    prod_uworker_conf.vm.box_url = "http://files.vagrantup.com/precise64.box"
    prod_uworker_conf.vm.hostname = "prod.worker.ubuntu"
    prod_uworker_conf.vm.network :private_network, ip: "192.168.33.16"
    prod_uworker_conf.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", "2048"]
    end
    # Enable provisioning with Salt stand alone. Salt minion config and
    # states are in a directory relative to this Vagrantfile.
    prod_uworker_conf.vm.provision :salt do |salt|
      ## This minion requires a master at 192.168.33.15
      salt.minion_config = "installation/salt-production/minion"
      ## Users our states in "salt/"
      salt.run_highstate = true
    end
  end

  # Define CentOS scanworker to use for testing production scanworker build
  # start as: vagrant up prod_cworker
  config.vm.define :prod_cworker do |prod_cworker_conf|
    prod_cworker_conf.vm.box = "centos6.4_64_dev"
    prod_cworker_conf.vm.box_url = "http://shonky.info/centos64.box"
    prod_cworker_conf.vm.hostname = "prod.worker.centos"
    prod_cworker_conf.vm.network :private_network, ip: "192.168.33.17"
    prod_cworker_conf.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", "4096"]
    end
    # Enable provisioning with Salt stand alone. Salt minion config and
    # states are in a directory relative to this Vagrantfile.
    prod_cworker_conf.vm.provision :salt do |salt|
      ## This minion requires a master at 192.168.33.15
      salt.minion_config = "installation/salt-production/minion"
      ## Users our states in "salt/"
      salt.run_highstate = true
    end
  end

  # Define Ubuntu scanworker
  # start as: vagrant up uworker
  config.vm.define :uworker do |uworker_conf|
    uworker_conf.vm.box = "precise64"
    uworker_conf.vm.box_url = "http://files.vagrantup.com/precise64.box"
    uworker_conf.vm.hostname = "worker.ubuntu"
    uworker_conf.vm.network :private_network, ip: "192.168.33.11"
    uworker_conf.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", "2048"]
    end
    # Enable provisioning with Salt stand alone. Salt minion config and
    # states are in a directory relative to this Vagrantfile.
    uworker_conf.vm.provision :salt do |salt|
      ## Minion config is set to ``file_client: local`` for masterless
      salt.minion_config = "installation/salt-masterless/minion"
      ## Users our states in "salt/"
      salt.run_highstate = true
    end
  end

  # Define CentOS scanworker
  # start as: vagrant up cworker
  config.vm.define :cworker do |cworker_conf|
    cworker_conf.vm.box = "centos6.4_64_dev"
    cworker_conf.vm.box_url = "http://shonky.info/centos64.box"
    cworker_conf.vm.hostname = "worker.centos"
    cworker_conf.vm.network :private_network, ip: "192.168.33.12"
    cworker_conf.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", "4096"]
    end
    # Enable provisioning with Salt stand alone. Salt minion config and
    # states are in a directory relative to this Vagrantfile.
    cworker_conf.vm.provision :salt do |salt|
      ## Minion config is set to ``file_client: local`` for masterless
      salt.minion_config = "installation/salt-masterless/minion"
      ## Users our states in "salt/"
      salt.run_highstate = true
    end
  end

  # Define Ubuntu combined scanmaster / scanworker
  # start as: vagrant up phagedev
  config.vm.define :phagedev, primary: true do |phagedev_conf|
    phagedev_conf.vm.box = "precise64"
    phagedev_conf.vm.box_url = "http://files.vagrantup.com/precise64.box"
    phagedev_conf.vm.hostname = "phagedev.ubuntu"
    phagedev_conf.vm.network :forwarded_port, guest: 8000, host: 8090
    phagedev_conf.vm.network :private_network, ip: "192.168.33.10"
    phagedev_conf.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", "2048"]
    end
    # Enable provisioning with Salt stand alone. Salt minion config and
    # states are in a directory relative to this Vagrantfile.
    phagedev_conf.vm.provision :salt do |salt|
      ## Minion config is set to ``file_client: local`` for masterless
      salt.minion_config = "installation/salt-masterless/minion"
      ## Users our states in "salt/"
      salt.run_highstate = true
    end
  end

  # Every Vagrant virtual environment requires a box to build off of.
  #config.vm.box = "phagedev"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  # config.vm.box_url = "http://domain.com/path/to/above.box"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  #config.vm.network :forwarded_port, guest: 8000, host: 8090
  #config.vm.provider "virtualbox" do |v|
  #  v.customize ["modifyvm", :id, "--memory", "2048"]
  #end

  # Enable provisioning with Salt stand alone. Salt minion config and
  # states are in a directory relative to this Vagrantfile.
  #config.vm.provision :salt do |salt|

    ## Minion config is set to ``file_client: local`` for masterless
    #salt.minion_config = "installation/salt-masterless/minion"

    ## Installs our example formula in "salt/"
    #salt.run_highstate = true

  #end
  # for steve, dont remove!
  config.vm.provider "vmware_fusion" do |v|
    v.vmx["memsize"] = "1024"
    v.vmx["numvcpus"] = "2"
  end

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  #config.vm.network :private_network, ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network :public_network

  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  # config.ssh.forward_agent = true

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  # config.vm.provider :virtualbox do |vb|
  #   # Don't boot with headless mode
  #   vb.gui = true
  #
  #   # Use VBoxManage to customize the VM. For example to change memory:
  # vb.customize ["modifyvm", :id, "--memory", "2048"]
  # end
  #
  # View the documentation for the provider you're using for more
  # information on available options.

end
