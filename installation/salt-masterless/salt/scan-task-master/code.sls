master_archive:
  file.managed:
    - name: /root/scan_task_master/{{ pillar['scan_task_master_pkg'] }}
    - source: salt://scan_task_master/{{ pillar['scan_task_master_pkg'] }}
    - env: {{ pillar['media_env'] }}
    - makedirs: True

master_extract_archive:
  cmd:
    - cwd: /root
    - name: unzip /root/scan_task_master/{{ pillar['scan_task_master_pkg'] }}
    - unless: test -d {{ pillar['ps_root'] }}/masterceleryconfig.py
    - run
    - require:
      - file: master_archive

master_move_source:
  file.rename:
    - name: {{ pillar['ps_root'] }}
    - source: /root/{{ pillar['scan_task_master_dir_name'] }}
    - force: True
    - require:
      - cmd: master_extract_archive

master_webroot:
  file.directory:
    - name: {{ pillar['ps_root'] }}
    - user: avuser
    - group: avuser
    - recurse:
      - user
      - group
    - require:
      - file: master_move_source
      - group: avuser
      - user: avuser
