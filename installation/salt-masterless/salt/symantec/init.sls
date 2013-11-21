# This must be a CentOS VM.
{% if grains['os'] == 'CentOS' %}
include:
  - av-engine-updater

centos-pkg-update:
  cmd:
    - name: "yum -y update"
    - run

symantec-reqts:
  cmd:
    - name: "yum -y install `grep -v '^#' {{ pillar['ps_root'] }}/engines/symantec/PACKAGES.centos`"
    - run
    - require:
      - cmd: centos-pkg-update

java-rpm-installer:
  file.managed:
    - name: /root/symantec/{{ pillar['jre_pkg'] }}
    - source: salt://symantec/{{ pillar['jre_pkg'] }}
    - env: {{ pillar['media_env'] }}
    - require:
      - cmd: symantec-reqts

java-rpm-installation:
  cmd.run:
    - name: rpm -i /root/symantec/{{ pillar['jre_pkg'] }}
    - require:
      - file: java-rpm-installer

spe-tarball:
  file.managed:
    - name: /root/symantec/{{ pillar['symantec_pkg'] }}
    - source: salt://symantec/{{ pillar['symantec_pkg'] }}
    - env: {{ pillar['media_env'] }}
    - makedirs: True
    - require:
      - cmd: java-rpm-installation

spe-extract:
  cmd:
    - cwd: /root
    - name: unzip -q /root/symantec/{{ pillar['symantec_pkg'] }}
    - unless: test -d {{ pillar['symantec_pkg_dirname'] }}
    - run
    - require:
      - file: spe-tarball

spe-no-ask-qs:
  file.managed:
    - name: /tmp/no-ask-questions
    - source: salt://symantec/no-ask-questions
    - template: jinja
    - user: root
    - group: root
    - mode: 600
    - require:
      - cmd: spe-extract

spe-install:
  cmd:
    - cwd: /root/{{ pillar['symantec_pkg_dirname'] }}/Symantec_Protection_Engine/RedHat
    - names:
      - ./SymantecProtectionEngine.sh
    - unless: test -d /opt/SYMCScan/bin
    - run
    - require:
      - file: spe-no-ask-qs

spe-license:
  file.managed:
    - name: /opt/Symantec/Licenses/{{ pillar['symantec_lic'] }}
    - source: salt://symantec/{{ pillar['symantec_lic'] }}
    - env: {{ pillar['lic_env'] }}
    - require:
      - cmd: spe-install

# liveupdate is broken, disable it.
disable-liveupdate:
  cmd:
    - cwd: /opt/SYMCScan/bin
    - names:
      - java -jar xmlmodifier.jar -s /liveupdate/schedules/enabled/@value false liveupdate.xml
    - run
    - require:
      - file: spe-license

spe-restart:
  cmd:
    - name: service symcscan restart
    - run
    - require:
      - cmd: disable-liveupdate

spe-crontab:
  cron.present:
    - name: /root/av_sig_updater.sh symantec
    - user: 'root'
    - minute: random
    - hour: '3,9,15,21'

symantec-updater-sudoers:
  file.managed:
    - name: /etc/sudoers.d/symantec_sudoers
    - source: salt://symantec/symantec_sudoers
    - mode: 0440


{% endif %}

