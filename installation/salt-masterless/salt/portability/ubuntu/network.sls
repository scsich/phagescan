
# ubuntu cloud image does this sanely now
#ubuntu_set_hostname_to_UUID:
#  file.sed:
#    - name: /etc/init/hostname.conf
#    - before: '^exec hostname .*'
#    - after: 'exec hostname -b -F /sys/devices/virtual/dmi/id/product_uuid'
#    - limit: exec hostname