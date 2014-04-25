include:
 - baseline.os

salt-master:
  pkg.installed

python-pip:
  pkg.installed

gitpython:
  pip.installed:
    - require:
      - pkg: python-pip