base:
  '*':
    - repos
    #- bash
    - crypto
    - git
    #- postfix
    #- salt.master
    #- salt.minion
    - sysctl
    #- time.ntpd
    - users
    - vim
    - zsh
  'master1.*':
    - sysctl
    - java
    - elasticsearch
