opaf-reqts:
  cmd:
    - name: "apt-get -y install `grep -v '^#' {{ pillar['ps_root'] }}/engines/opaf/PACKAGES.ubuntu`"
    - run
  pip.installed:
    - requirements: {{ pillar['ps_root'] }}/engines/opaf/PACKAGES.pip
    - bin_env: {{ pillar['virt_env_dir'] }}
    - require:
      - cmd: opaf-reqts

