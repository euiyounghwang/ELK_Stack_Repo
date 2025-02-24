#!/bin/bash
set -e

sudo journalctl -u packetbeat_service.service -f
