bitdefender-update-sigs:
  cmd:
    - name: /usr/bin/bdscan --update
    - onlyif: test -f /usr/bin/bdscan
    - run
