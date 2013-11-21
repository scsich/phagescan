include:
  {% if grains['os'] == 'CentOS' %}
  - portability.centos
  {% elif grains['os'] == 'Ubuntu' %}
  - portability.ubuntu
  {% endif %}