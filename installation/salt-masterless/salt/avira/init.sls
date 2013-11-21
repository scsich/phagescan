avira-reqts:
  cmd:
    - name: "apt-get -y install `grep -v '^#' {{ pillar['ps_root'] }}/engines/avira/PACKAGES.ubuntu`"
    - run

avira-tarball:
  file.managed:
    - name: /root/avira/{{ pillar['avira_pkg'] }}
    - source: salt://avira/{{ pillar['avira_pkg'] }}
    - env: {{ pillar['media_env'] }}
    - makedirs: True
    - require:
      - cmd: avira-reqts

avira-unattended-inf:
  file.managed:
    - name: /root/avira/unattended.inf
    - source: salt://avira/unattended.inf
    - require:
      - file: avira-tarball

avira-extract:
  cmd:
    - cwd: /root/avira
    - names:
      - tar xzf {{ pillar['avira_pkg'] }}
    - unless: test -d {{ pillar['avira_tardir_name'] }}
    - run
    - require:
      - file: avira-unattended-inf

avira-license:
  file.managed:
    - name: /root/avira/{{ pillar['avira_tardir_name'] }}/hbedv.key
    - source: salt://avira/{{ pillar['avira_lic'] }}
    - env: {{ pillar['lic_env'] }}
    - require:
      - cmd: avira-extract

avira-install:
  cmd:
    - cwd: /root/avira/{{ pillar['avira_tardir_name'] }}
    - names: 
      - ./install --inf=/root/avira/unattended.inf
    - unless: test -x /usr/lib/AntiVir/guard/avscan
    - run
    - require:
      - file: avira-license

avira-start-service:
  cmd:
    - names: 
      - service avguard start > /dev/null 2>&1
    - run
    - require:
      - cmd: avira-install

avira-updater-sudoers:
  file.managed:
    - name: /etc/sudoers.d/avira_sudoers
    - source: salt://avira/avira_sudoers
    - mode: 0440

