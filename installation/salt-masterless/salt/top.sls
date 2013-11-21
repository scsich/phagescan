base:
  'phagedev*':
    - scan-master-worker-dev

  'worker*':
    - scan-worker-dev

  'salt*':
    - salt-master

  'prod.worker*':
    - scan-worker-prod

  '.*-.*-.*-.*-.*':
    - scan-worker-prod

  's-.*-.*-.*-.*-.*':
    - scan-worker-prod
