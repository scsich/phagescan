baseline-os-pkgs:
  pkg.installed:
    - pkgs:
      - htop
      - unzip
      - curl
      - wget
      - mosh
      - bash-completion
      - acpid
      - pciutils
      {% if grains['os'] == 'CentOS' %}
      - vim-enhanced
      {% elif grains['os'] == 'Ubuntu' %}
      - debconf-utils
      - vim-nox
      - python-software-properties
      - ipython
      {% endif %}
    - order: 1

# this has to be separate!
python-pip:
  pkg.installed
