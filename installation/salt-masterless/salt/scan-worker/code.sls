worker_archive:
  file.managed:
    - name: /root/scan_worker/{{ pillar['scan_worker_pkg'] }}
    - source: salt://scan_worker/{{ pillar['scan_worker_pkg'] }}
    - env: {{ pillar['media_env'] }}
    - makedirs: True

worker_extract_archive:
  cmd:
    - cwd: /root
    - name: unzip /root/scan_worker/{{ pillar['scan_worker_pkg'] }}
    - run
    - require:
      - file: worker_archive

worker_move_source:
  file.rename:
    - name: {{ pillar['ps_root'] }}
    - source: /root/{{ pillar['scan_worker_dir_name'] }}
    - force: True
    - require:
      - cmd: worker_extract_archive

worker_webroot:
  file.directory:
    - name: {{ pillar['ps_root'] }}
    - user: avuser
    - group: avuser
    - recurse:
      - user
      - group
    - require:
      - file: worker_move_source

