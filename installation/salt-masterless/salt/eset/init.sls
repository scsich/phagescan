eset-reqts:
  cmd:
    - name: "apt-get -y install `grep -v '^#' {{ pillar['ps_root'] }}/engines/eset/PACKAGES.ubuntu`"
    - run

eset-installer:
  file.managed:
    - name: /root/eset/{{ pillar['eset_pkg'] }}
    - source: salt://eset/{{ pillar['eset_pkg'] }}
    - env: {{ pillar['media_env'] }}
    - require:
      - cmd: eset-reqts

eset-installation:
  cmd.run:
    - name: dpkg -i /root/eset/{{ pillar['eset_pkg'] }}
    - unless: test -f /etc/opt/eset/esets/license/esets_nod32.lic
    - require:
      - file: eset-installer

eset-import-license:
  file.managed:
    - name: /etc/opt/eset/esets/license/esets_nod32.lic
    - source: salt://eset/{{ pillar['eset_lic'] }}
    - env: {{ pillar['lic_env'] }}
    - require:
      - cmd: eset-installation

eset-config-uncomment-username:
  file.uncomment:
    - name: /etc/opt/eset/esets/esets.cfg
    - regex: ^av_update_username = ""
    - require:
      - file: eset-import-license
    
eset-config-set-username:
  file.sed:
    - name: /etc/opt/eset/esets/esets.cfg
    - before: \"\"
    - after: \"{{ pillar['eset_update_username'] }}\"
    - limit: '^av_update_username ='
    - require:
      - file: eset-config-uncomment-username

eset-config-uncomment-password:
  file.uncomment:
    - name: /etc/opt/eset/esets/esets.cfg
    - regex: ^av_update_password = ""
    - require:
      - file: eset-config-set-username
    
eset-config-set-password:
  file.sed:
    - name: /etc/opt/eset/esets/esets.cfg
    - before: \"\"
    - after: \"{{ pillar['eset_update_password'] }}\"
    - limit: '^av_update_password ='
    - require:
      - file: eset-config-uncomment-password

eset-service-restart:
  cmd:
    - names:
      - service esets restart
    - run
    - require:
      - file: eset-config-set-password

eset-initial-scan:
  cmd:
    - names:
      - /opt/eset/esets/sbin/esets_scan --clean-mode=none --no-quarantine /etc/opt/eset/esets/esets.cfg
    - run
    - require:
      - cmd: eset-service-restart

eset-updater-sudoers:
  file.managed:
    - name: /etc/sudoers.d/eset_sudoers
    - source: salt://eset/eset_sudoers
    - mode: 0440

