master-celeryd-defaults:
  file.managed:
    - name: /etc/default/celeryd
    - source: salt://celery/master/celeryd
    - template: jinja
    - user: root
    - group: root
    - mode: 644

master-celeryd-init:
  file.managed:
    - name: /etc/init.d/celeryd
    - source: salt://celery/master/celeryd.initd
    - user: root
    - group: root
    - mode: 755

master-celeryconfig-copy:
  file.copy:
    - name: {{ pillar['ps_root'] }}/masterceleryconfig.py
    - source: {{ pillar['ps_root'] }}/installation/scanworker/masterceleryconfig.py
    - force: True

celeryconfig-master-username:
  file.sed:
    - name: {{ pillar['ps_root'] }}/masterceleryconfig.py
    - before: 'masteruser'
    - after: '{{ pillar['mq_master_user_name'] }}'
    - limit: "^  'uid' 	: "
    - requre:
      - file: master-celeryconfig-copy

celeryconfig-master-password:
  file.sed:
    - name: {{ pillar['ps_root'] }}/masterceleryconfig.py
    - before: 'longmasteruserpassword'
    - after: '{{ pillar['mq_master_user_passwd'] }}'
    - limit: "^  'pass' 	: "
    - requre:
      - file: master-celeryconfig-copy

celeryconfig-master-vhost:
  file.sed:
    - name: {{ pillar['ps_root'] }}/masterceleryconfig.py
    - before: 'phage'
    - after: '{{ pillar['mq_master_vhost_name'] }}'
    - requre:
      - file: master-celeryconfig-copy

celeryd:
  service:
    - running
    - enable: True
    - order: last


