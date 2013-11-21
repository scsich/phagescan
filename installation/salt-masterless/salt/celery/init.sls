celery-updated:
  pip.installed:
    - name: celery >= 3.0.24, < 3.1.0
    - bin_env: {{ pillar['virt_env_dir'] }}
    - upgrade: True
