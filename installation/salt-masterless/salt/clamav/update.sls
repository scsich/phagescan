clamav-update:
  cmd:
    - name: /usr/bin/freshclam
    - onlyif: test -f /usr/bin/freshclam
    - run

clamav-daemon:
  cmd:
    - name: service clamav-daemon restart
    - onlyif: test -f /usr/bin/freshclam
    - run
    - require:
      - cmd: clamav-update
