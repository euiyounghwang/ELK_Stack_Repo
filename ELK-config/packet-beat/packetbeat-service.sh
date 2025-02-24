#!/bin/bash
set -e

sudo /apps/packetbeat/packetbeat-5.6.4-linux-x86_64/packetbeat -e -c /apps/packetbeat/packetbeat-5.6.4-linux-x86_64/packetbeat.yml -strict.perms=false "publish"
