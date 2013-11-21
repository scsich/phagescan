# Set PermitRootLogin to no
centos_no_root_login:
  file.sed:
    - name: /etc/ssh/sshd_config
    - before: 'PermitRootLogin yes'
    - after: 'PermitRootLogin no'
    - limit: PermitRootLogin

# cause sshd keys to be re-gen upon boot
ubuntu_del_ssh_keys:
  cmd.run:
    - name: rm -f /etc/ssh/ssh_host_*

ubuntu_gen_new_ssh_keys:
  cmd.run:
    - name: ssh-keygen -A
    - require:
      - cmd: ubuntu_del_ssh_keys
