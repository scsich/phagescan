# remove persistent network gen rule 75
centos_rm_persistent_netgen_75:
  file.absent:
    - name: /lib/udev/rules.d/75-persistent-net-generator.rules

# remove persistent network gen rule 70
centos_rm_persistent_netgen_70:
  file.absent:
    - name: /etc/udev/rules.d/70-persistent-net.rules


# clean up ifcfg-eth0 (this only works on RedHat variants)
centos_comment_eth0_uuid:
  file.comment:
    - name: /etc/sysconfig/network-scripts/ifcfg-eth0
    - regex: ^UUID=

centos_comment_eth0_hwaddr:
  file.comment:
    - name: /etc/sysconfig/network-scripts/ifcfg-eth0
    - regex: ^HWADDR

centos_set_hostname_to_UUID:
  file.sed:
    - name: /etc/sysconfig/network
    - before: 'HOSTNAME=.*'
    - after: 'HOSTNAME=`cat /sys/devices/virtual/dmi/id/product_uuid`'
    - limit: HOSTNAME=