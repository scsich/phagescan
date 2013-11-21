avast-update-sigs:
  cmd:
    - name: /usr/bin/avastvpsupdate.sh
    - onlyif: test -f /usr/bin/avastvpsupdate.sh
    - run
