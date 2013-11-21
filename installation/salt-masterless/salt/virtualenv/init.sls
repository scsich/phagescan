ps-virtualenv:
  virtualenv.managed:
    - name: {{ pillar['virt_env_dir'] }}
    - distribute: True
    {% if grains['os'] == 'CentOS' %}
    - venv_bin: /usr/local/bin/virtualenv-2.7
    - python: /usr/local/bin/python2.7
    {% endif %}

