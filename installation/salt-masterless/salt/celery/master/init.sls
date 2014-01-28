master-celeryd-defaults:
  file.managed:
    - name: /etc/default/celeryd-master
    - source: salt://celery/master/default/celeryd-master
    - user: root
    - group: root
    - mode: 644

master-celeryd-init:
  file.managed:
    - name: /etc/init.d/celeryd-master
    - source: salt://celery/master/init.d/celeryd-master
    - user: root
    - group: root
    - mode: 755

master-celeryconfig-copy:
  file.copy:
    - name: {{ pillar['ps_root'] }}/masterceleryconfig.py
    - source: {{ pillar['ps_root'] }}/installation/scanmaster/masterceleryconfig.py
    - force: True

periodic-celeryd-defaults:
  file.managed:
    - name: /etc/default/celeryd-periodic
    - source: salt://celery/master/default/celeryd-periodic
    - user: root
    - group: root
    - mode: 644

periodic-celeryd-init:
  file.managed:
    - name: /etc/init.d/celeryd-periodic
    - source: salt://celery/master/init.d/celeryd-periodic
    - user: root
    - group: root
    - mode: 755

periodic-celeryconfig-copy:
  file.copy:
    - name: {{ pillar['ps_root'] }}/periodicceleryconfig.py
    - source: {{ pillar['ps_root'] }}/installation/scanmaster/periodicceleryconfig.py
    - force: True

result-celeryd-defaults:
  file.managed:
    - name: /etc/default/celeryd-result
    - source: salt://celery/master/default/celeryd-result
    - user: root
    - group: root
    - mode: 644

result-celeryd-init:
  file.managed:
    - name: /etc/init.d/celeryd-result
    - source: salt://celery/master/init.d/celeryd-result
    - user: root
    - group: root
    - mode: 755

result-celeryconfig-copy:
  file.copy:
    - name: {{ pillar['ps_root'] }}/resultsceleryconfig.py
    - source: {{ pillar['ps_root'] }}/installation/scanmaster/resultsceleryconfig.py
    - force: True

celeryd-result:
  service:
    - running
    - enable: True
    - order: last

celeryd-periodic:
  service:
    - running
    - enable: True
    - order: last

celeryd-master:
  service:
    - running
    - enable: True
    - order: last


