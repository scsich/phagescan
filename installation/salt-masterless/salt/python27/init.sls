{% if grains['os'] == 'CentOS' %}
python-tarball:
  file.managed:
    - name: /root/python-build/{{ pillar['python27_tarball'] }}
    - source: http://www.python.org/ftp/python/{{ pillar['python27_version'] }}/{{ pillar['python27_tarball'] }}
    - source_hash: sha256={{ pillar['python27_sha256'] }}
    - makedirs: True

distribute-tarball:
  file.managed:
    - name: /root/python-build/{{ pillar['distribute_tarball'] }}
    - source: http://pypi.python.org/packages/source/d/distribute/{{ pillar['distribute_tarball'] }}
    - source_hash: sha256={{ pillar['distribute_sha256'] }}
    - makedirs: True
    - require:
      - file: python-tarball

python-extract-tarball:
  cmd:
    - cwd: /root/python-build
    - names:
      - tar xjf {{ pillar['python27_tarball'] }}
      - tar xzf {{ pillar['distribute_tarball'] }}
    - run
    - require:
      - file: distribute-tarball

python27-centos:
  cmd:
    - cwd: /root/python-build/{{ pillar['python27_tarball_dirname'] }}
    - names:
      - ./configure --prefix=/usr/local
      - make && make altinstall
    - run
    - require:
      - cmd: python-extract-tarball

python27-distribute-install:
  cmd:
    - cwd: /root/python-build/{{ pillar['distribute_tarball_dirname'] }}
    - names:
      - /usr/local/bin/python2.7 setup.py install
    - run
    - require:
      - cmd: python27-centos

python27-virtualenv:
  cmd:
    - cwd: /root/python-build
    - names:
      - /usr/local/bin/easy_install-2.7 virtualenv
    - run
    - require:
      - cmd: python27-distribute-install

{% endif %}

