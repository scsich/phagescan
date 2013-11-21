av-engine-updater:
  file.managed:
    - name: /root/av_sig_updater.sh
    - source: salt://av-engine-updater/av_sig_updater.sh
    - mode: 700

