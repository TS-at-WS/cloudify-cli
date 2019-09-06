#!/usr/bin/env bash
KEY1=409B6B1796C275462A1703113804BB82D39DC0E3
KEY2=7D2BAF1CF37B13E2069D6956105BD0E739499BDB
for server in hkp://pool.sks-keyservers.net \
              hkp://p80.pool.sks-keyservers.net:80 \
              keyserver.ubuntu.com \
              hkp://keyserver.ubuntu.com:80 \
              pgp.mit.edu; do
    gpg2 --keyserver "$server" --recv-keys $KEY1 $KEY2 && break || echo "Trying next server"
done
