bitdefender-reqts:
  cmd:
    - name: "apt-get -y install `grep -v '^#' {{ pillar['ps_root'] }}/engines/bitdefender/PACKAGES.ubuntu`"
    - run

bitdefender-installer:
  file.managed:
    - name: /root/bitdefender/{{ pillar['bitdefender_pkg'] }}
    - source: salt://bitdefender/{{ pillar['bitdefender_pkg'] }}
    - env: {{ pillar['media_env'] }}
    - require:
      - cmd: bitdefender-reqts

bitdefender-installation:
  cmd.run:
    - name: dpkg -i /root/bitdefender/{{ pillar['bitdefender_pkg'] }}
    - unless: test -f /etc/BitDefender-scanner/bdscan.conf
    - require:
      - file: bitdefender-installer

bitdefender-config-set-license:
  file.sed:
    - name: /etc/BitDefender-scanner/bdscan.conf
    - before: '^Key = .*'
    - after: 'Key = {{ pillar['bitdefender_license'] }}'
    - require:
      - cmd: bitdefender-installation

bitdefender-config-accept-license:
  file.append:
    - name: /etc/BitDefender-scanner/bdscan.conf
    - text: 
      - LicenseAccepted = True
    - require:
      - file: bitdefender-config-set-license

bitdefender-crontab:
  cron.present:
    - names:
      - /usr/bin/bdscan --update
    - user: 'root'
    - minute: random
    - hour: '2,8,14,20'

bitdefender-updater-sudoers:
  file.managed:
    - name: /etc/sudoers.d/bitdefender_sudoers
    - source: salt://bitdefender/bitdefender_sudoers
    - mode: 0440