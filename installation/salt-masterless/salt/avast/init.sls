avast-reqts:
  cmd:
    - name: "apt-get -y install `grep -v '^#' {{ pillar['ps_root'] }}/engines/avast/PACKAGES.ubuntu`"
    - run

avast-kernel-shmmax-now:
  cmd:
    - name: sysctl -w kernel.shmmax=128000000
    - run
    - require:
      - cmd: avast-reqts

avast-kernel-shmmax-persist:
  cmd:
    - names: 
      - echo "kernel.shmmax=128000000" >> /etc/sysctl.conf
    - unless: grep -q  '^kernel.shmmax=128000000' /etc/sysctl.conf
    - run
    - require:
      - cmd: avast-kernel-shmmax-now

avast-installer:
  file.managed:
    - name: /root/avast/{{ pillar['avast_pkg'] }}
    - source: salt://avast/{{ pillar['avast_pkg'] }}
    - env: {{ pillar['media_env'] }}
    - require:
      - cmd: avast-kernel-shmmax-persist

avast-installation:
  cmd.run:
    - name: dpkg -i /root/avast/{{ pillar['avast_pkg'] }}
    - unless: test -f /var/lib/avast4/{{ pillar['avast_lic'] }}
    - require:
      - file: avast-installer

avast-lic:
  file.managed:
    - name: /var/lib/avast4/{{ pillar['avast_lic'] }}
    - source: salt://avast/{{ pillar['avast_lic'] }}
    - env: {{ pillar['lic_env'] }}
    - user: root
    - group: root
    - mode: 644
    - require:
      - cmd: avast-installation

avast-server-tarball:
  file.managed:
    - name: /root/avast/{{ pillar['avastsrv_pkg'] }}
    - source: salt://avast/{{ pillar['avastsrv_pkg'] }}
    - env: {{ pillar['media_env'] }}
    - makedirs: True
    - require:
      - file: avast-lic

avastcmd-extract:
  cmd:
    - cwd: /root/avast
    - names:
      - tar -zxf {{ pillar['avastsrv_pkg'] }} {{ pillar['avastsrv_tardir_name'] }}/bin/avastcmd
    - unless: test -f {{ pillar['avastsrv_tardir_name'] }}/bin/avastcmd
    - run
    - require:
      - file: avast-server-tarball

avastcmd-install:
  file.rename:
    - name: /opt/avast/bin/avastcmd
    - source: /root/avast/{{ pillar['avastsrv_tardir_name'] }}/bin/avastcmd
    - makedirs: True
    - require:
      - cmd: avastcmd-extract

avast-updater-sudoers:
  file.managed:
    - name: /etc/sudoers.d/avast_sudoers
    - source: salt://avast/avast_sudoers
    - mode: 0440

