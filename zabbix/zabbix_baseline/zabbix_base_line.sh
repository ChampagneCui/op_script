#!/bin/bash

mysql -uroot -ppassword -e "
use res;
INSERT IGNORE INTO zabbix_35229_history_line(timestamp,value_7,value_30)
select s1.time_sec,s1.a,s2.a from (
SELECT
        max(TIMESTAMP) + 86400 AS time_sec,
        avg(VALUE) a
FROM
        zabbix_item_history
WHERE
        TIMESTAMP > UNIX_TIMESTAMP(
                date_sub(now(), INTERVAL 7 DAY)
        )
AND TIMESTAMP < UNIX_TIMESTAMP(now())
AND itemid = 35229
GROUP BY
        timestamp_86400)  s1
,
(SELECT
        max(TIMESTAMP) + 86400 AS time_sec,
        avg(VALUE) a
FROM
        zabbix_item_history
WHERE
        TIMESTAMP > UNIX_TIMESTAMP(
                date_sub(now(), INTERVAL 30 DAY)
        )
AND TIMESTAMP < UNIX_TIMESTAMP(now())
AND itemid = 35229
GROUP BY
        timestamp_86400) s2 where s1.time_sec=s2.time_sec;
"
