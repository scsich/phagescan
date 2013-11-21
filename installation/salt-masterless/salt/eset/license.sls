eset-copy-new-license:
  file.managed:
    - name: /root/eset/esets_nod32.lic
    - source: salt://eset/{{ pillar['eset_lic'] }}
    - env: {{ pillar['lic_env'] }}
    - makedirs: True

eset-install-new-license:
  cmd.run:
    - name: /opt/eset/esets/sbin/esets_lic --import=/path/to/new/license/file
    - watch:
      - file: eset-copy-new-license

eset-service-restart:
  cmd:
    - names:
      - service esets restart
    - run
    - watch:
      - cmd: eset-install-new-license
