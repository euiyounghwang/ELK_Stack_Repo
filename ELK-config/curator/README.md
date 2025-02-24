
# Elasticsearch Curator

<i>Elasticsearch Curator helps you curate, or manage, your Elasticsearch indices and snapshots by:
- Obtaining the full list of indices (or snapshots) from the cluster, as the actionable list
- Iterate through a list of user-defined filters to progressively remove indices (or snapshots) from this actionable list as needed.
- Perform various actions on the items which remain in the actionable list.
- Curator-Airflow Example(<i>https://github.com/occidere/airflow-example/blob/master/dags/curator_example.py, https://ikeptwalking.com/taking-elasticsearch-snapshots-using-curator/</i>)
- Installation Local: Curator is breaking into version dependent releases. Curator 6.x will work with Elasticsearch 6.x, Curator 7.x will work with Elasticsearch 7.x, and when it is released, Curator 8.x will work with Elasticsearch 8.x.
- Search Guard with Curator : https://docs.search-guard.com/latest/elasticsearch-curator-search-guard

```bash
(.venv) ➜  python-elasticsearch git:(master) ✗ poetry add elasticsearch-curator       
Using version ^8.0.8 for elasticsearch-curator

Updating dependencies
Resolving dependencies... (0.8s)

Package operations: 6 installs, 0 updates, 0 removals

  • Installing elastic-transport (8.12.0)
  • Installing elasticsearch8 (8.8.2)
  • Installing voluptuous (0.14.1)
  • Installing ecs-logging (2.0.2)
  • Installing es-client (8.8.2.post1)
  • Installing elasticsearch-curator (8.0.8)

Writing lock file
```


### Run Curator
- Test : /usr/bin/curator --dry-run /home/biadmin/utils/curator-config-dev/delete.yml --config /home/biadmin/utils/curator-config-dev/config.yml
```bash
2024-07-12 17:38:48,887 INFO      Preparing Action ID: 1, "delete_indices"
2024-07-12 17:38:48,902 INFO      Trying Action ID: 1, "delete_indices": Delete indices older than 100 days (based on index name), for packetbeat- prefixed indices. Ignore the error if the filter does not result in an actionable list of indices (ignore_empty_list) and exit cleanly.
2024-07-12 17:38:49,058 INFO      Skipping action "delete_indices" due to empty list: <class 'curator.exceptions.NoIndices'>
2024-07-12 17:38:49,058 INFO      Action ID: 1, "delete_indices" completed.
2024-07-12 17:38:49,058 INFO      Job completed.
```[QA1]
- Run : /usr/bin/curator /home/biadmin/utils/curator-config-dev/delete.yml --config /home/biadmin/utils/
```bash
2024-07-12 17:37:55,039 INFO      Preparing Action ID: 1, "delete_indices"
2024-07-12 17:37:55,054 INFO      Trying Action ID: 1, "delete_indices": Delete indices older than 100 days (based on index name), for packetbeat- prefixed indices. Ignore the error if the filter does not result in an actionable list of indices (ignore_empty_list) and exit cleanly.
2024-07-12 17:37:55,368 INFO      DRY-RUN MODE.  No changes will be made.
2024-07-12 17:37:55,368 INFO      (CLOSED) indices may be shown that may not be acted on by action "delete_indices".
2024-07-12 17:37:55,368 INFO      DRY-RUN: delete_indices: packetbeat-2024.07.10 with arguments: {}
2024-07-12 17:37:55,369 INFO      Action ID: 1, "delete_indices" completed.
2024-07-12 17:37:55,369 INFO      Job completed.
```



### Configure Curator Cronjob
```bash
## Delete older index of Elasticsearch
00 00,12 * * * /usr/bin/curator --dry-run /home/biadmin/utils/curator-config-env8/delete.yml --config /home/biadmin/utils/curator-config-env8/config.yml
```


#### Example for Crontab
- All Linux distributions are equipped with the cron utility, which allows users to schedule jobs to run at certain fixed times.
- The system-wide root cron jobs are located in the /etc/crontab file. The file contents can be displayed using any text editor, or utilities like cat and more. sudo is not required to display the system cron jobs.
```bash
# Example of job definition:
# .---------------- minute (0 - 59)
# |  .------------- hour (0 - 23)
# |  |  .---------- day of month (1 - 31)
# |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
# |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
# |  |  |  |  |
# *  *  *  *  * user-name command to be executed
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )