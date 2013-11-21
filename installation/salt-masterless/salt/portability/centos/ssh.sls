# Set PermitRootLogin to no
centos_no_root_login:
  file.sed:
    - name: /etc/ssh/sshd_config
    - before: '#PermitRootLogin yes'
    - after: 'PermitRootLogin no'
    - limit: PermitRootLogin

# delete ssh keys, so they will re-gen on next boot
centos_del_ssh_keys:
  cmd.run:
    - name: rm -f /etc/ssh/ssh_host_*
