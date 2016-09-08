#!/bin/sh
fab deploy:vagrant,HEAD,skip_check=${1:-False} -H app1.mezblog.odonnell.nu -u mezblog
