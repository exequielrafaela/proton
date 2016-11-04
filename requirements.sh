#!/bin/bash

YUM_CMD=$(which yum)
APT_GET_CMD=$(which apt-get)
$YUM_PACKAGE_NAME = "python-2.7 python-pip"
$DEB_PACKAGE_NAME = "python2.7 python-pip"

 if [[ ! -z $YUM_CMD ]]; then
    yum install $YUM_PACKAGE_NAME
    pip install -r requirements.txt
 elif [[ ! -z $APT_GET_CMD ]]; then
    apt-get install $DEB_PACKAGE_NAME
    pip install -r requirements.txt
 else
    echo "error can't install package $PACKAGE"
    exit 1;
 fi