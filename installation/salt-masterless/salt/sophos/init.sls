include:
  - av-engine-updater

sophos-reqts:
  cmd:
    - name: "apt-get -y install `grep -v '^#' {{ pillar['ps_root'] }}/engines/sophos/PACKAGES.ubuntu`"
    - run

sophos-tarball:
  file.managed:
    - name: /root/sophos/{{ pillar['sophos_pkg'] }}
    - source: salt://sophos/{{ pillar['sophos_pkg'] }}
    - env: {{ pillar['media_env'] }}
    - makedirs: True
    - require:
      - cmd: sophos-reqts

sophos-extract:
  cmd:
    - cwd: /root/sophos
    - names:
      - tar xzf {{ pillar['sophos_pkg'] }}
    - unless: test -d sav-install
    - run
    - require:
      - file: sophos-tarball

sophos-install:
  cmd:
    - cwd: /root/sophos/sav-install
    - names: 
      - ./install.sh
    - unless: test -x /usr/local/bin/sweep
    - run
    - require:
      - cmd: sophos-extract

sophos-updater-sudoers:
  file.managed:
    - name: /etc/sudoers.d/sophos_sudoers
    - source: salt://sophos/sophos_sudoers
    - mode: 0440

sophos-cronab:
  cron.present:
    - name: /root/av_sig_updater.sh sophos
    - user: 'root'
    - minute: random
    - hour: '3,9,15,21'

sophos-ides-ver:
  file.sed:
    - name: /root/av_sig_updater.sh
    - before: '[0-9]{3}_ides.zip'
    - after: '{{ pillar['sophos_sig_pkg'] }}'
    - limit: '^SOPHOS_IDES_FILE='
    - require:
      - file: av-engine-updater
