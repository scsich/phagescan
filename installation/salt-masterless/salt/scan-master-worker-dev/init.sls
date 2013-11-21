include:
  - baseline.os
  - baseline.ps
  - virtualenv
  - clamav
  - scan-worker
  - scan-task-master
  - rabbitmq-server
  - postgresql-server
  - baseline.dev
  - celery

extend:
  baseline-ps-pkgs:
    cmd:
      - require:
        - pkg: baseline-os-pkgs
  ps-virtualenv:
    virtualenv:
      - require:
        - cmd: baseline-ps-pkgs
        - pkg: python-pip
  master-pip-pkgs:
    pip:
      - require:
        - virtualenv: ps-virtualenv
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

     
/etc/hosts:
  file.append:
    - text:
      - 127.0.0.1     scanmaster


