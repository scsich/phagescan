bitdefender-uninstall:
  pkg.purged:
    - sources:
      - bitdefender-scanner:i386

bitdefender-delete-dir:
  file.absent:
    - name: /opt/BitDefender-scanner/
    - require:
      - pkg: bitdefender-uninstall
