include:
  - baseline.os
  - avuser
  - scan-worker.code
  - baseline.ps
  {% if grains['os'] == 'CentOS' %}
  - python27
  {% endif %}
  - virtualenv
  - scan-worker
  - celery
  - celery.worker
  {% if grains['os'] == 'Ubuntu' %}
    {% set engine_list = pillar['ubuntu_engines'] %}
  {% elif grains['os'] == 'CentOS' %}
    {% set engine_list = pillar['centos_engines'] %}
  {% endif %}
  {% for engine in engine_list %}
  - {{ engine['engine'] }}
  {% endfor %}

extend:
  # scan_worker.code
  worker_webroot:
    file:
      - require:
        - user: avuser
        - group: avuser
  # baseline.ps
  baseline-ps-pkgs:
    cmd:
      - require:
        - pkg: baseline-os-pkgs
        - file: worker_webroot
  # python27
  {% if grains['os'] == 'CentOS' %}
  python27-centos:
    cmd:
      - require:
        - cmd: baseline-ps-pkgs
  {% endif %}
  # virtualenv
  ps-virtualenv:
    virtualenv:
      - require:
        - cmd: baseline-ps-pkgs
        - pkg: python-pip
        {% if grains['os'] == 'CentOS' %}
        - cmd: python27-virtualenv
        {% endif %}
  # scan-worker
  worker-pip-pkgs:
    pip:
      - require:
        - virtualenv: ps-virtualenv
  # celery
  celery-updated:
    pip:
      - require:
        - virtualenv: ps-virtualenv
  # celery.worker
  celeryd-config:
    file.managed:
      - require:
        - file: worker_webroot
  # scan engines
  {% for engine in engine_list %}
  {{ engine['name'] }}:
    {{ engine['type'] }}:
      - require:
        - pip: worker-pip-pkgs
  {% endfor %}

