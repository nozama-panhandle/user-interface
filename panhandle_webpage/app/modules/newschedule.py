import numpy as np
import pymysql
import pdb
import itertools
import time
from collections import Counter


def schedule(orders, max_cap):
    start=time.time()
    cap={'red':24, 'green':24, 'blue':24}
    address = [101, 102, 103, 203, 202, 201]
    raddress ={101:0,102:1,103:2,203:3,202:4,201:5}
    if len(orders)==0:
        print("schedule: No remain orders")
        return ([],[])
    orders_by_address = [sorted([order for order in orders if order['address']==addr], key=lambda o: o['red']+o['green']+o['blue']) for addr in address]
    print("orders: ", orders_by_address)
    #######  address간 block의 총 조합-> 50개 이하 -> 그중 max 오더수
    max_orderN=-len(address)-2
    totalN=max_cap+1
    max_c={'red':0,'green':0,'blue':0}
    scheduled={}
    for L in range(1, len(address) + 1):
        for subset in itertools.combinations(orders_by_address, L):
            num_c={'red':0,'green':0,'blue':0}
            idx = {i:0 for i in range(L)}
            isCont=True
            bestm=-1
            best={'red':26,'green':26,'blue':26}
            while isCont:
                min_address = sorted(idx.items(), key=lambda e: subset[e[0]][e[1]]['red']+subset[e[0]][e[1]]['green']+subset[e[0]][e[1]]['blue'] if e[1] in subset[e[0]] else max_cap+1)
                isCont=False
                for m in min_address:
                    if m[1] < len(subset[m[0]]):
                        s=subset[m[0]][m[1]]
                        if s['red']+s['green']+s['blue']+sum(num_c.values())>max_cap:
                            break
                        if s['red']+num_c['red']>cap['red'] or s['green']+num_c['green']>cap['green'] or s['blue']+num_c['blue']>cap['blue']:
                            continue
                        isCont=True
                        best['red']=s['red']
                        best['green']=s['green']
                        best['blue']=s['blue']
                        bestm=m[0]
                        break
                
                if isCont:
                    num_c['red']+=best['red']
                    num_c['green']+=best['green']
                    num_c['blue']+=best['blue']
                    idx[bestm]+=1
            if 0 in set(idx.items()):
                continue
            if sum(idx.values())-L > max_orderN or (sum(idx.values())-L==max_orderN and totalN>sum(num_c.values())):
                max_orderN = sum(idx.values())-L
                totalN=sum(num_c.values())
                scheduled = {s[0]['address']:idx[i] for i,s in zip(idx, subset) if idx[i]!=0}
                max_c=num_c.copy()
    update_list=[]
    schedule_list=[]
    for addr, idx in scheduled.items():
        addrN=raddress[addr]
        update_list.extend([{'id':order['id'], 'red':0,'green':0,'blue':0} for order in orders_by_address[addrN][0:idx]])
        schedule_list.extend([dict(order, delivery_order=raddress[addr], is_last=1) for order in orders_by_address[addrN][0:idx]])
   
    print("0, max_c: ", max_c)
    print("scheduled: ", schedule_list)
    ####### partial delivery for the same address
    for addr, idx in scheduled.items():
        if idx==0:
            continue
        if max_cap - sum(max_c.values()) == 0:
            break
        addrN=raddress[addr]
        for order in orders_by_address[addrN][idx:]:
            if max_cap -sum(max_c.values()) == 0:
                break
            a=sorted(max_c.items(), key=lambda k:k[1])
            part={'red':0,'green':0,'blue':0}
            for color, num in a:
                part[color]=min(max_cap-sum(max_c.values())-sum(part.values()), cap[color]-max_c[color], order[color])
                if max_cap - sum(max_c.values()) == 0:
                    break
            max_c['red']+=part['red']
            max_c['green']+=part['green']
            max_c['blue']+=part['blue']
            part['id']=order['id']
            if order['red']==part['red'] and order['green']==part['green'] and order['blue']==part['blue']:
                part['is_last']=1
            else:
                part['is_last']=0
            part['address']=order['address']
            part['delivery_order']=raddress[part['address']]
            schedule_list.append(part)
            update_list.append({'id':order['id'],'red':order['red']-part['red'],'green':order['green']-part['green'],'blue':order['blue']-part['blue']})
    print("1, max_c: ", max_c)
    print("scheduled: ", schedule_list)
    ####### partial delivery for different address
    #for addr, idx in scheduled.items():
    for addr in set(address)-set(scheduled.keys()):
        if max_cap - sum(max_c.values()) == 0:
            break
        addrN=raddress[addr]
        for order in orders_by_address[addrN]:
            if max_cap - sum(max_c.values()) == 0:
                break
            a=sorted(max_c.items(), key=lambda k:k[1])
            part={'red':0,'green':0,'blue':0}
            for color, num in a:
                part[color]=min(max_cap-sum(max_c.values())-sum(part.values()), cap[color]-max_c[color], order[color])
                if max_cap -sum(max_c.values()) == 0:
                    break
            max_c['red']+=part['red']
            max_c['green']+=part['green']
            max_c['blue']+=part['blue']
            part['id']=order['id']
            if order['red']==part['red'] and order['green']==part['green'] and order['blue']==part['blue']:
                part['is_last']=1
            else:
                part['is_last']=0
            part['address']=order['address']
            part['delivery_order']=raddress[part['address']]
            schedule_list.append(part)
            update_list.append({'id':order['id'],'red':order['red']-part['red'],'green':order['green']-part['green'],'blue':order['blue']-part['blue']})
    print("2, max_c: ", max_c)
    print("scheduled: ", schedule_list)
    return (update_list, schedule_list)
