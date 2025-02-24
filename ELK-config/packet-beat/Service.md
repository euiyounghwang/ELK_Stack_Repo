# Register Packetbeat Service
<i>Beat Service


sudo vi /etc/systemd/system/packetbeat_service.service 

--
[Unit] 
Description=Packetbeat Service 

[Service] 
User=biadmin 
Group=biadmin 
Type=simple 
ExecStart=/bin/bash /apps/packetbeat/packetbeat-service.sh
ExecStop= /usr/bin/killall packetbeat_service 

[Install] 
WantedBy=default.target 

--

- Manually command line
```bash
ExecStart=/bin/bash sudo /apps/packetbeat/packetbeat-5.6.4-linux-x86_64/packetbeat -e -c /apps/packetbeat/packetbeat-5.6.4-linux-x86_64/packetbeat.yml 
```


# Service command
sudo systemctl daemon-reload 
sudo systemctl enable packetbeat_service.service

sudo systemctl start packetbeat_service.service 
sudo systemctl status packetbeat_service.service 
sudo systemctl stop packetbeat_service.service 

sudo service packetbeat_service status
sudo service packetbeat_service start


sudo journalctl -u packetbeat_service.service -f