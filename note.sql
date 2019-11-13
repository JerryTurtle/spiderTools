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
退役军人事务部
科技部
公安部
审计署

