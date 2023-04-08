#! /bin/bash
set -o errexit
set -o nounset

. /root/.bash_profile \
  && nvm install $1 \
  && nvm alias default $1 \
  && nvm use default