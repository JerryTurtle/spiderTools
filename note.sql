#根据url去重的sql
DELETE policy_spider_url_info
FROM
 policy_spider_url_info,
 (
  SELECT
   min(id_) id_,url
  FROM
   policy_spider_url_info
  GROUP BY
   url
  HAVING
   count(*) > 1
 ) t2
WHERE
 policy_spider_url_info.url = t2.url
AND policy_spider_url_info.id_ > t2.id_;

db.getCollection('html_data_country').aggregate([{$match:{task_id:44}},
{
$group: { _id: {url: '$url'},count: {$sum: 1},dups: {$addToSet: '$_id'}}
},{$match: {count: {$gt: 1}}}
]).forEach(function(doc){
doc.dups.shift();
db.getCollection('html_data_country').remove({_id: {$in: doc.dups}});
})

人民银行

公安部
审计署

-- dealwith_matters;
-- email_send_log;
-- operation_flow_log;
-- project_achievement;
-- project_event;
-- project_meet_advise;
-- project_meet_person;
-- pan_file;
-- pan_folder;
-- pan_share;
-- task_check_history;
