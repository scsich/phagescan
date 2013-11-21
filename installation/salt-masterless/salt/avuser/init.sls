avuser:
  user.present:
    - fullname: "AV User"
    - shell: /bin/bash
    - home: /home/avuser
    - gid_from_name: True
    - require:
      - group: avuser
  group:
    - present

