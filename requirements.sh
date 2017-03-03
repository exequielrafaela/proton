#!/bin/bash
set -e

YUM_PACKAGE_NAME="python python-devl python-pip openssl-devel"
DEB_PACKAGE_NAME="python2.7 python-dev python-pip libssl-dev build-essential libffi-dev"

 if cat /etc/*release | grep ^NAME | grep CentOS; then
    echo "====================================="
    echo "Installing packages $YUM_PACKAGE_NAME"
    echo "====================================="
    yum install -y $YUM_PACKAGE_NAME
    pip install --upgrade pip
    pip install -r requirements.txt
 elif cat /etc/*release | grep ^NAME | grep Red; then
    echo "====================================="
    echo "Installing packages $YUM_PACKAGE_NAME"
    echo "====================================="
    yum install -y $YUM_PACKAGE_NAME
    pip install --upgrade pip
    pip install -r requirements.txt
 elif cat /etc/*release | grep ^NAME | grep Fedora; then
    echo "====================================="
    echo "Installing packages $YUM_PACKAGE_NAME"
    echo "====================================="
    yum install -y $YUM_PACKAGE_NAME
    pip install --upgrade pip
    pip install -r requirements.txt
 elif cat /etc/*release | grep ^NAME | grep Ubuntu; then
    echo "====================================="
    echo "Installing packages $DEB_PACKAGE_NAME"
    echo "====================================="
    apt-get update
    apt-get autoremove -y
    apt-get install -y $DEB_PACKAGE_NAME
    pip install --upgrade pip
    pip uninstall six
    pip install --upgrade six
    pip install -r requirements.txt
 elif cat /etc/*release | grep ^NAME | grep Debian ; then
    echo "====================================="
    echo "Installing packages $DEB_PACKAGE_NAME"
    echo "====================================="
    apt-get update
    apt-get autoremove -y
    apt-get install -y $DEB_PACKAGE_NAME
    pip install --upgrade pip
    pip install -r requirements.txt
 elif cat /etc/*release | grep ^NAME | grep Mint ; then
    echo "====================================="
    echo "Installing packages $DEB_PACKAGE_NAME"
    echo "====================================="
    apt-get update
    apt-get autoremove -y
    apt-get install -y $DEB_PACKAGE_NAME
    pip install --upgrade pip
    pip install -r requirements.txt
 elif cat /etc/*release | grep ^NAME | grep Knoppix ; then
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


#YUM_CMD=$(which yum)
#APT_GET_CMD=$(which apt-get)
#YUM_PACKAGE_NAME="python python-devl python-pip"
#DEB_PACKAGE_NAME="python2.7 python-dev python-pip"
#
# if [[ ! -z $YUM_CMD ]]; then
#    echo "====================================="
#    echo "Installing packages $YUM_PACKAGE_NAME"
#    echo "====================================="
#    yum install -y $YUM_PACKAGE_NAME
#    pip install --upgrade pip
#    pip install -r requirements.txt
# elif [[ ! -z $APT_GET_CMD ]]; then
#    echo "====================================="
#    echo "Installing packages $DEB_PACKAGE_NAME"
#    echo "====================================="
#    apt-get update
#    apt-get autoremove -y
#    apt-get install -y $DEB_PACKAGE_NAME
#    pip install --upgrade pip
#    pip install -r requirements.txt
# else
#    echo "error can't install package $PACKAGE"
#    exit 1;
# fi
#
#exit 0
