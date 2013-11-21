sophos-update-step1:
  cmd:
    - cwd: /root
    - name: wget -q  http://downloads.sophos.com/downloads/ide/{{ pillar['sophos_sig_pkg'] }}
    - onlyif: test -d /usr/local/sav
    - run

sophos-update-step2:
  cmd:
    - name: unzip -quo /root/{{ pillar['sophos_sig_pkg'] }} -d /usr/local/sav
    - run
    - watch:
      - cmd: sophos-update-step1
