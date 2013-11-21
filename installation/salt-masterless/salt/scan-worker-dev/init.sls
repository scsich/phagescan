include:
  - baseline.os
  - baseline.ps
  {% if grains['os'] == 'CentOS' %}
  - python27
  {% endif %}
  - virtualenv
  - scan-worker
  - baseline.dev
  - celery

extend:
  baseline-ps-pkgs:
    cmd:
      - require:
        - pkg: baseline-os-pkgs
  {% if grains['os'] == 'CentOS' %}
  python27-centos:
    cmd:
      - require:
        - cmd: baseline-ps-pkgs
  {% endif %}
  ps-virtualenv:
    virtualenv:
      - require:
        - cmd: baseline-ps-pkgs
        - pkg: python-pip
        {% if grains['os'] == 'CentOS' %}
        - cmd: python27-virtualenv
        {% endif %}
  worker-pip-pkgs:
    pip:
      - require:
        - virtualenv: ps-virtualenv
  dev-pip-pkgs:
    pip:
      - require:
        - virtualenv: ps-virtualenv
  celery-updated:
    pip:
      - require:
        - virtualenv: ps-virtualenv
