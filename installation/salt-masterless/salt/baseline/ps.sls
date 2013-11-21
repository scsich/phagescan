baseline-ps-pkgs:
  cmd:
    {% if grains['os'] == 'Ubuntu' %}
    - name: "apt-get -y install `grep -v '^#' {{ pillar['ps_root'] }}/PACKAGES.ubuntu`"
    {% elif grains['os'] == 'CentOS' %}
    - name: "yum -y install `grep -v '^#' {{ pillar['ps_root'] }}/PACKAGES.centos`"
    {% endif %}
    - run
