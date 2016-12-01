#!/bin/sh
fab deploy:vagrant,HEAD,dev_mode=True,skip_check=${1:-False} -H app1.mezblog.odonnell.nu -u mezblog
