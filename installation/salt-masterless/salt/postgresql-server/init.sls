postgresql:
  pkg:
    - installed
  service:
    - running
    - enable: True
    - require:
      - pkg: postgresql

ps-hstore-extension:
  cmd.run:
    - name: psql -d template1 -c 'CREATE EXTENSION IF NOT EXISTS hstore;'
    - user: postgres
    - shell: /bin/bash
    - cwd: /tmp
    - require:
      - service: postgresql

ps-pguser:
  postgres_user:
    - present
    - name: {{ pillar['phage_scan_db_user_name'] }}
    - createdb: True
    - superuser: True
    - encrypted: True
    - password: {{ pillar['phage_scan_db_user_passwd'] }}
    - runas: postgres
    - require:
      - cmd: ps-hstore-extension

ps-pgdb:
  postgres_database:
    - present
    - name: phage
    - owner: {{ pillar['phage_scan_db_user_name'] }}
    - runas: postgres
    - require:
      - postgres_user: ps-pguser

