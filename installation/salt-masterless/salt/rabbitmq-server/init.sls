rabbitmq-server:
  pkg:
    - installed
  service:
    - running
    - enable: True
    - require:
      - pkg: rabbitmq-server

guest:
  rabbitmq_user.absent:
    - require:
      - service: rabbitmq-server

no-slash:
  rabbitmq_vhost.absent:
    - name: /
    - require:
      - rabbitmq_user: guest

mq_masteruser:
  rabbitmq_user.present:
    - name: {{ pillar['mq_master_user_name'] }}
    - password: {{ pillar['mq_master_user_passwd'] }}
    - force: True
    - require:
      - rabbitmq_vhost: no-slash

mq_workeruser:
  rabbitmq_user.present:
    - name: {{ pillar['mq_worker_user_name'] }}
    - password: {{ pillar['mq_worker_user_passwd'] }}
    - force: True
    - require:
      - rabbitmq_user: mq_masteruser

masteruser_vhost:
  rabbitmq_vhost.present:
    - name: {{ pillar['mq_master_vhost_name'] }}
    - user: {{ pillar['mq_master_user_name'] }}
    - conf: ".*"
    - write: ".*"
    - read: ".*"
    - require:
      - rabbitmq_user: mq_workeruser
    
workeruser_vhost:
  rabbitmq_vhost.present:
    - name: {{ pillar['mq_worker_vhost_name'] }}
    - user: {{ pillar['mq_worker_user_name'] }}
    - conf: ".*"
    - write: ".*"
    - read: ".*"
    - require:
      - rabbitmq_vhost: masteruser_vhost

