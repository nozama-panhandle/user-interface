def find_opt(orders_by_address, color, dp_table, pre_table, value_table, num_table, remain, max_cap):
    address = [101, 102, 103, 203, 202, 201]
    raddress = {101:0, 102:1, 103:2, 203:3, 202:4, 201:5}
    colors={'red','green','blue'}
    if len(remain)==0 or max_cap==0:
        return (0, [], [])
    last=[-1 for i in range(len(address))]
    value=[0 for i in range(len(address))]
    cp_table=[0 for i in range(len(address))]
    for i in remain:
        cp = max_cap
        for j in range(max_cap, 0, -1):
            if dp_table[i][j] != dp_table[i][j-1]:
                cp=j
                break
        value[i]=dp_table[i][cp]
        if (dp_table[i][max_cap]==0) or cp < max_cap:
            max_value=0
            max_index=-1
            pre_set=set(pre_table[i][cp]) ##
            for j in range(len(value_table[i])):
                if  j not in pre_set and value_table[i][j]/(num_table[i][j]+1) > max_value:
                    max_value = value_table[i][j]/(num_table[i][j]+1)
                    max_index = j
            last[i]=max_index
            value[i]+=max_value*(max_cap-cp)
        cp_table[i]=cp
    addr_idx=-1
    addr_value=0
    cp=-1
    for i in remain:
        if value[i]>addr_value:
            addr_value=value[i]
            addr_idx=i
            cp=cp_table[i]
    if addr_idx==-1:
        return (0,[],[])
    update_list=[]
    schedule_list=[]
    orders=orders_by_address[addr_idx]
    for j in pre_table[addr_idx][cp]:
        order=orders[j]
        part=order.copy()
        part['red']=0
        part['green']=0
        part['blue']=0
        part[color]=order[color]
        r={'id':order['id'], 'red':order['red']-part['red'], 'green':order['green']-part['green'],'blue':order['blue']-part['blue']}
        if r['red']+r['green']+r['blue']==0:
            part['is_last']=1
        else:
            part['is_last']=0
        part['delivery_order']=addr_idx
        update_list.append(r)
        schedule_list.append(part)
    #update_list = [{'id':orders_by_address[addr_idx][j]['id'], 'red':order['red']-part['red'], 'green':order['green']-part['green'],'blue':0} for j in pre_table[addr_idx][cp]]
    #schedule_list = [dict(orders_by_address[addr_idx][j], delivery_order=addr_idx, is_last=1) for j in pre_table[addr_idx][cp]]
    if last[addr_idx]!=-1:
        order = orders_by_address[addr_idx][last[addr_idx]]
        part={'red':0, 'green':0, 'blue':0, 'is_last':0, 'address':order['address'], 'id':order['id'], 'delivery_order': addr_idx}
        part[color]=max_cap-cp
        schedule_list.append(part)
        update_list.append({'id':order['id'],'red':order['red']-part['red'],'green':order['green']-part['green'],'blue':order['blue']-part['blue']})
        if order['red']==part['red'] and order['green']==part['green'] and order['blue']==part['blue']:
            print("Something's wrong -> It is not part delivery")
    else:
        v, up, sc = find_opt(orders_by_address, color, dp_table, pre_table, value_table, num_table, remain-{addr_idx}, max_cap-cp)
        update_list.extend(up)
        schedule_list.extend(sc)
        addr_value = addr_value + v
    return (addr_value, update_list, schedule_list)

def schedule(orders, max_cap):
    address = [101, 102, 103, 203, 202, 201]
    raddress = {101:0, 102:1, 103:2, 203:3, 202:4, 201:5}
    colors = {'red','green','blue'}
    if len(orders)==0:
        print("schedule: No remain orders")
        return ([],[])
    orders_by_address = [sorted([order for order in orders if order['address']==addr], key=lambda o: o['red']+o['green']+o['blue']) for addr in address]
    for o_ in orders_by_address:
        print("orders: ", o_)
#dptable dp[addridx][cap] previous[addridx][cap] added[addridx][cap]
    good_color = None
    good_value = 0
    schedule_list=None
    update_list=None
    for color in colors:
        dp_table=[]
        pre_table=[]
        value_table=[]
        num_table=[]
        for orderlst in orders_by_address:
            value=[]
            num=[]
            for order in orderlst:
                v = order[color]
                n = order[color]
                for c in colors:
                    v=v/(order[c]+1)
                value.append(v)
                num.append(n)
            dp=[0 for _ in  range(max_cap+1)]
            pre=[[] for _ in range(max_cap+1)]
            for i in range(len(orderlst)):
                for j in range(max_cap, 0, -1):
                    if j<num[i]: break
                    if(dp[j-num[i]]+value[i]>dp[j]):
                        dp[j]=dp[j-num[i]]+value[i]
                        pre[j]=pre[j-num[i]].copy()
                        pre[j].append(i)
            dp_table.append(dp)
            pre_table.append(pre)
            value_table.append(value)
            num_table.append(num)
        value, up, sc = find_opt(orders_by_address, color, dp_table, pre_table, value_table, num_table, set(range(len(orders_by_address))), max_cap)
        if value > good_value:
            good_value = value
            good_color = color
            schedule_list = sc
            update_list = up
    print("update: ", update_list)
    print("schedule: ", schedule_list)
    return (update_list, schedule_list)

if __name__=="__main__":
    #import pymysql
    #db=pymysql.connect(host='localhost', user='strong', password='strong', db= 'orderdb')
    #cursor=db.cursor(pymysql.cursors.DictCursor)
    #cursor.execute("select id, address, red, green,blue from orders where pending='0'")
    #pend_list=cursor.fetchall()
    pend_list = [{'id': 118, 'address': 102, 'red': 8, 'green': 6, 'blue': 0}, {'id': 124, 'address': 103, 'red': 0, 'green': 0, 'blue': 1}, {'id': 116, 'address': 203, 'red': 0, 'green': 11, 'blue': 0}, {'id': 120, 'address': 203, 'red': 0, 'green': 10, 'blue': 13}, {'id': 122, 'address': 202, 'red': 7, 'green': 0, 'blue': 0}, {'id': 121, 'address': 202, 'red': 6, 'green': 4, 'blue': 0}, {'id': 119, 'address': 202, 'red': 6, 'green': 9, 'blue': 7}]


    update_list, schedule_list = schedule([p for p in pend_list if p['red']+p['green']+p['blue']!=0], 24)
