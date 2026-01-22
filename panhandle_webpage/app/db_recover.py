import pymysql
 
conn = pymysql.connect(host='localhost', user='strong', password='strong',
                        db='orderdb', charset='utf8')
  
id_curs = conn.cursor(pymysql.cursors.DictCursor)
   
id_sql = "select id, cast(sum(red) as unsigned) red, cast(sum(green) as unsigned) green, cast(sum(blue) as unsigned) blue from scheduling group by id"
id_curs.execute(id_sql)
    
ids = id_curs.fetchall()

print(ids)
for id_ in ids:
    id_curs.execute("update orders set red='%d', green='%d', blue='%d' where id='%d'"%(id_['red'], id_['green'], id_['blue'], id_['id']))
conn.commit()
conn.close()
