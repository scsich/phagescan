eset-update-sigs:
  cmd:
    - name: /opt/eset/esets/sbin/esets_update
    - onlyif: test -f /etc/opt/eset/esets/license/esets_nod32.lic
    - run
