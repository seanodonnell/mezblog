#!/bin/sh
fab deploy:prod,HEAD,skip_check=${1:-False} -H app1.blog.odonnell.nu -u mezblog
