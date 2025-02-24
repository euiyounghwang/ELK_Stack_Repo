# Log-Management
<i>Log-Management

- Log Delete Cronjob : `00 00 * * * /home/devuser/UtilityScripts/purgeogs.sh`
- Test : Change the creation time - `touch -t 202407101000 es-job-interface-restful-api.log`
```bash
sudo find /apps/var/spark/logs/*log* -mtime +2 -exec rm {} \;

-bash-4.2$ sudo find /home/biadmin/log-test-cron/*log*
/home/devuser/log-test-cron/es-job-interface-restful-api.log
/home/devuser/log-test-cron/supplychain-logging-prod14-2024-07-03.log

```