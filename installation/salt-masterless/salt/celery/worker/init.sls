celeryd-defaults:
  file.managed:
    - name: /etc/default/celeryd
    - source: salt://celery/worker/celeryd.defaults.linux
    - template: jinja
    - user: root
    - group: root
    - mode: 644

celeryd-init:
  file.managed:
    - name: /etc/init.d/celeryd
    - source: salt://celery/worker/celeryd.initd
    - user: root
    - group: root
    - mode: 755

celeryd-config:
  file.managed:
    - name: {{ pillar['ps_root'] }}/workerceleryconfig.py
    - source: salt://celery/worker/workerceleryconfig.py
    - user: avuser
    - group: avuser
    - mode: 600
    - template: jinja
    - context:
      mq_user: "{{ pillar['mq_worker_user_name'] }}"
      mq_password: "{{ pillar['mq_worker_user_passwd'] }}"
      mq_vhost: "{{ pillar['mq_worker_vhost_name'] }}"
      mq_host: "{{ pillar['master_address'] }}"

celeryd:
  service:
    - running
    - enable: True
    - order: last

