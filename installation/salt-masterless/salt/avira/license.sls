avira-key:
  file.managed:
    - name: /usr/lib/AntiVir/guard/avira.new.key
    - source: salt://avira/{{ pillar['avira_lic'] }}
    - env: {{ pillar['lic_env'] }}
    - makedirs: True

avira-guard-restart:
  cmd.run:
    - name: service avguard restart
    - watch:
      - file: avira-key
