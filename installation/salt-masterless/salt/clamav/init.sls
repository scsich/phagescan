clamav-reqts:
  cmd:
    - name: "apt-get -y install `grep -v '^#' {{ pillar['ps_root'] }}/engines/clamav/PACKAGES.ubuntu`"
    - run

clamav-daemon:
  pkg.installed:
    - require:
      - cmd: clamav-reqts
  service:
    - running
    - enable: True
    - require:
      - pkg: clamav-daemon

clamav-freshclam:
  service:
    - dead
    - enable: False
    - require:
      - pkg: clamav-daemon

clamav-updater-sudoers:
  file.managed:
    - name: /etc/sudoers.d/clamav_sudoers
    - source: salt://clamav/clamav_sudoers
    - mode: 0440

clamav-crontab:
  cron.present:
    - name: /usr/bin/freshclam --quiet --daemon-notify
    - user: 'root'
    - minute: random
    - hour: '1,7,13,19'

