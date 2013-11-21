yara-reqts:
  pip.installed:
    - requirements: {{ pillar['ps_root'] }}/engines/yara/PACKAGES.pip
    - bin_env: {{ pillar['virt_env_dir'] }}

