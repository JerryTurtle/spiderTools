#根据url去重的sql
DELETE temp
FROM
 temp,
 (
  SELECT
   min(id_) id_,url
  FROM
   temp
  GROUP BY
   url
  HAVING
   count(*) > 1
 ) t2
WHERE
 temp.url = t2.url
AND temp.id_ > t2.id_;