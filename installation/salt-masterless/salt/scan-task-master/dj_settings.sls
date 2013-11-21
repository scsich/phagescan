# TODO: fix this ...
# instead of maintaining a copy of settings.py,
#  just update the values within the default settings.py.

settings:
  file.managed:
    - name: {{ pillar['master_root'] }}/scaggr/settings.py
    - source: salt://scan-task-master/settings.py
    - template: jinja
    - user: avuser
    - group: avuser
    - mode: 644
    - require:
      - file: master_webroot
      - group: avuser
      - user: avuser

