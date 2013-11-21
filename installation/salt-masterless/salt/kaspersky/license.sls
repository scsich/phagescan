kaspersky-newkey:
  file.managed:
    - name: /root/kaspersky/kaspersky.key
    - source: salt://kaspersky/{{ pillar['kaspersky_key'] }}
    - env: {{ pillar['lic_env'] }}
    - makedirs: True

kaspersky-install-newkey:
  cmd.run:
    - name: /opt/kaspersky/kes4lwks/bin/kes4lwks-control --install-active-key /root/kaspersky/kaspersky.key
    - watch:
      - file: kaspersky-newkey


