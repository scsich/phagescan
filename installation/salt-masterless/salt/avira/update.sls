avira-update-sigs:
  cmd:
    - name: /usr/lib/AntiVir/guard/avupdate-guard
    - onlyif: test -f /usr/lib/AntiVir/guard/avupdate-guard
    - run
