FROM debian:stable

ENV HOME=/root

# Install packages needed for next steps and upgrade system
RUN \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get -y install --no-install-recommends \
    lua5.1 liblua5.1-0-dev libjson-c-dev ca-certificates \
    git cmake make pkg-config gcc \
    && \
  apt-get clean

# Compile libubox
RUN \
  git clone git://git.openwrt.org/project/libubox.git ~/libubox && \
  cd ~/libubox && \
  cmake CMakeLists.txt && \
  make install && \
  cd .. && \
  rm -rf libubox

# Compile uci
RUN \
  git clone git://git.openwrt.org/project/uci.git ~/uci && \
  cd ~/uci && \
  cmake cmake CMakeLists.txt && \
  make install && \
  cd .. && \
  rm -rf uci

# Install packages needed for PyUci
RUN \
  apt-get update && \
  apt-get -y install --no-install-recommends \
    python-dev python-setuptools python-pip python-pytest \
    python3-dev python3-setuptools python3-pip python3-pytest \
    python3-pytest-cov lcov \
    && \
  apt-get clean

CMD [ "bash" ]
