worker-pip-pkgs:
  pip.installed:
    - requirements: {{ pillar['ps_root'] }}/installation/scanworker/PACKAGES.pip
    - bin_env: {{ pillar['virt_env_dir'] }}
