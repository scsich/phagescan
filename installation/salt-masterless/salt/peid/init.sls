peid-reqts:
  pip.installed:
    - requirements: {{ pillar['ps_root'] }}/engines/peid/PACKAGES.pip
    - bin_env: {{ pillar['virt_env_dir'] }}
