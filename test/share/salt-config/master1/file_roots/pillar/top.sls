base:
  '*':
    - bash
    - users
    - zsh
    - common
    - schedule
  'master1.*':
    - elasticsearch
    - logstash
