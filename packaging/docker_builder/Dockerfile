FROM centos:6
RUN yum install -y http://opensource.wandisco.com/centos/6/git/x86_64/wandisco-git-release-6-1.noarch.rpm
RUN yum install -y git fakeroot python-devel rpm-build
RUN yum update -y nss
RUN curl -sSL https://rvm.io/pkuczynski.asc | gpg2 --import -
COPY get_keys.sh /tmp/get_keys.sh
RUN /usr/bin/env bash /tmp/get_keys.sh


RUN curl -sSL https://get.rvm.io | bash -s stable
RUN /bin/bash -c '''\
    source /etc/profile.d/rvm.sh && \
    rvm install 2.4.4 && rvm use 2.4.4 && \
    gem install bundler -v '=1.16.0' --no-ri --no-rdoc && \
    gem install mixlib-cli -v 1.7.0 --no-ri --no-rdoc && \
    gem install omnibus --no-ri --no-rdoc \
'''
RUN yum install sudo -y
