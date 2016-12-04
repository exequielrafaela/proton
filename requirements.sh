#!/bin/bash
set -e

YUM_CMD=$(which yum)
APT_GET_CMD=$(which apt-get)
YUM_PACKAGE_NAME="python python-devl python-pip"
DEB_PACKAGE_NAME="python2.7 python-dev python-pip"

 if [[ ! -z $YUM_CMD ]]; then
    echo "====================================="
    echo "Installing packages $YUM_PACKAGE_NAME"
    echo "====================================="
    yum install -y $YUM_PACKAGE_NAME
    pip install --upgrade pip
    pip install -r requirements.txt
 elif [[ ! -z $APT_GET_CMD ]]; then
    echo "====================================="
    echo "Installing packages $DEB_PACKAGE_NAME"
    echo "====================================="
    apt-get update
    apt-get autoremove -y
    apt-get install -y $DEB_PACKAGE_NAME
    pip install --upgrade pip
    pip install -r requirements.txt
 else
    echo "error can't install package $PACKAGE"
    exit 1;
 fi

exit 0
