kaspersky-reqts:
  cmd:
    - name: "apt-get -y install `grep -v '^#' {{ pillar['ps_root'] }}/engines/kaspersky/PACKAGES.ubuntu`"
    - run

kaspersky-key:
  file.managed:
    - name: /root/kaspersky/kaspersky.key
    - source: salt://kaspersky/{{ pillar['kaspersky_key'] }}
    - env: {{ pillar['lic_env'] }}
    - makedirs: True
    - require:
      - cmd: kaspersky-reqts

kaspersky-post-install-script:
  file.managed:
    - name: /root/kaspersky/post_install.conf
    - source: salt://kaspersky/post_install.conf
    - makedirs: True
    - require:
      - file: kaspersky-key

kaspersky-installer:
  file.managed:
    - name: /root/kaspersky/{{ pillar['kaspersky_pkg'] }}
    - source: salt://kaspersky/{{ pillar['kaspersky_pkg'] }}
    - env: {{ pillar['media_env'] }}
    - require:
      - file: kaspersky-post-install-script

kaspersky-installation:
  cmd.run:
    - name: dpkg -i /root/kaspersky/{{ pillar['kaspersky_pkg'] }}
    - unless: test -f /var/opt/kaspersky/kes4lwks/installer.dat
    - require:
      - file: kaspersky-installer

kaspersky-init-setup:
  cmd.run:
    - name: /opt/kaspersky/kes4lwks/bin/kes4lwks-setup.pl --auto-install=/root/kaspersky/post_install.conf
    - unless: test -f /var/opt/kaspersky/kes4lwks/installer.dat
    - require:
      - cmd: kaspersky-installation

kes4lwks-updater-sudoers:
  file.managed:
    - name: /etc/sudoers.d/kaspersky_sudoers
    - source: salt://kaspersky/kaspersky_sudoers
    - mode: 0440

