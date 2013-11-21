kaspersky-update-step1:
  cmd.run:
    - name: /opt/kaspersky/kes4lwks/bin/kes4lwks-control --set-settings Update -N CommonSettings.SourceType=KLServers
    - onlyif: test -f /var/opt/kaspersky/kes4lwks/installer.dat

kaspersky-update-step2:
  cmd.run:
    - name: /opt/kaspersky/kes4lwks/bin/kes4lwks-control --start-task Update -N -F /tmp/kes4lwks-update.log
    - onlyif: test -f /var/opt/kaspersky/kes4lwks/installer.dat
    - require:
      - cmd: kaspersky-update-step1

kaspersky-update-step3:
  cmd.run:
    - name: /opt/kaspersky/kes4lwks/bin/kes4lwks-control --progress Update -N
    - onlyif: test -f /var/opt/kaspersky/kes4lwks/installer.dat
    - require:
      - cmd: kaspersky-update-step2

