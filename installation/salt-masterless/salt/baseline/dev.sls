dev-pip-pkgs:
  pip.installed:
    - requirements: {{ pillar['ps_root'] }}/installation/dev/PACKAGES.pip
    - bin_env: {{ pillar['virt_env_dir'] }}

