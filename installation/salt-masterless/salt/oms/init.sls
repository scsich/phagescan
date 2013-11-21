oms-pre-reqts:
  cmd:
    - name: "apt-get update && apt-get upgrade -y"
    - run

oms-debconf-mseula:
  debconf.set:
    - name: ttf-mscorefonts-installer
    - data:
        'msttcorefonts/accepted-mscorefonts-eula': {'type': 'boolean', 'value': True}

oms-reqts:
  cmd:
    - name: "apt-get -y install `grep -v '^#' {{ pillar['ps_root'] }}/engines/officemalscanner/PACKAGES.ubuntu`"
    - run
    - require:
      - cmd: oms-pre-reqts
      - debconf: oms-debconf-mseula

oms-installer:
  file.managed:
    - name: /root/oms/{{ pillar['oms_pkg'] }}
    - source: salt://oms/{{ pillar['oms_pkg'] }}
    - env: {{ pillar['media_env'] }}
    - makedirs: True
    - require:
      - cmd: oms-reqts

oms-mkdir:
  file.directory:
    - name: /opt/oms
    - require:
      - file: oms-installer

oms-extract:
  cmd:
    - cwd: /opt/oms
    - names:
      - unzip -o /root/oms/{{ pillar['oms_pkg'] }}
    - unless: test -d /opt/oms/OfficeMalScanner.exe
    - run
    - require:
      - file: oms-mkdir
