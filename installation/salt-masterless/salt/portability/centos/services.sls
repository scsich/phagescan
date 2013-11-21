acpid:
  service.running:
    - enable: True

postfix:
  service.dead:
    - enable: False

# delete salt-minion keys so they will re-gen on boot.
centos_del_salt_minion_keys:
  cmd.run:
    - name: rm -f /etc/salt/pki/minion/*

# this state will comment out the master defn, which
# will make it default to look for the host named 'salt'.
#ubuntu_comment_salt_master:
#  file.comment:
#    - name: /etc/salt/minion
#    - regex: '^master: '
