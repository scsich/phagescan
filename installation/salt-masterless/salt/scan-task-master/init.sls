master-os-pkgs:
  cmd:
    - name: "apt-get -y install `grep -v '^#' {{ pillar['ps_root'] }}/installation/scanmaster/PACKAGES.ubuntu`"
    - run

master-pip-pkgs:
  pip.installed:
    - name: ''
    - requirements: {{ pillar['ps_root'] }}/installation/scanmaster/PACKAGES.pip
    - bin_env: {{ pillar['virt_env_dir'] }}
    - require:
      - cmd: master-os-pkgs


