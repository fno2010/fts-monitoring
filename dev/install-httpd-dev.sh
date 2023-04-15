#!/bin/bash
set -e

#-----------------------------------------------------------------------
# File: install-httpd-dev.sh
# Description: Install FTS-Monitoring HTTPd config for Development environment.
# Input: ftsmon_dev.conf
# Output: /etc/httpd/conf.d/ftsmon_dev.conf
#-----------------------------------------------------------------------

function usage {
  filename=$(basename $0)
  echo "Install FTS-Monitoring HTTPd file for Development environment."
  echo ""

  exit 1
}

FILENAME=$(readlink -f "$0")
PROJECT_DIR="${FILENAME%fts-monitoring*}fts-monitoring"

sed "s|%%PROJECT_DIR%%|${PROJECT_DIR}|g" ${PROJECT_DIR}/dev/ftsmon_dev.conf > /etc/httpd/conf.d/ftsmon_dev.conf

systemctl restart httpd
