# This must be a CentOS VM.
include:
  - av-engine-updater

spe-update:
  cmd.script:
    - name: /root/av_sig_updater.sh symantec
    - source: salt://av-engine-updater/av_sig_updater.sh
    - onlyif: test -d /opt/SYMCScan/bin
    - shell: /bin/bash

