import numpy as np
import pymysql
import pdb
import itertools
import time
# is_streaming = False
# port = 8888
# frame_rate = 30
# host_name = "rpi-6.wifi.local.cmu.edu"
# host_port = 7777
# db=pymysql.connect(host='localhost',
#                    user='strong',
#                    password='strong',
#                    db='orderdb')
# cursor = db.cursor(pymysql.cursors.DictCursor)
# cursor.execute("SELECT * FROM orders")
# orders = cursor.fetchall()
def schedule(orders, max_cap= 30):
    start=time.time()
    r_cap=25
    g_cap=25
    b_cap=25
    address = [101, 102, 103, 203, 202, 201]
    raddress ={101:0,102:1,103:2,203:3,202:4,201:5}
    update_list = []
    if len(orders)==0:
        print("schedule: No remain orders")
        return

    dict_address = {}
    for addr in address:
        order_num=0
        r_num=0
        g_num=0
        b_num=0
        block_num = 0
        orders_by_address = []
        for order in orders:
            if order['address']==addr:
                order_num +=1
                block_num += (order['red']+order['green']+order['blue'])
                r_num += order['red']
                g_num += order['green']
                b_num += order['blue']
                orders_by_address.append(order)
        if order_num!=0:
            dict_address.update({addr:(order_num, block_num, r_num, g_num, b_num, orders_by_address)})

    #######  address간 block의 총 조합-> 50개 이하 -> 그중 max 오더수
    # sort_address={k: v for k, v in sorted(dict_address.items(), key=lambda item: item[1], reverse=True)}
    subsets={}
    for L in range(1, len(dict_address) + 1):
        for subset in itertools.combinations(dict_address, L):
            r_num = 0
            g_num = 0
            b_num = 0
            block_num = 0
            order_num = 0
            for sub in subset:
                order_num+=dict_address[sub][0]  ##order number
                block_num+=dict_address[sub][1]  ##block number
                r_num+=dict_address[sub][2]
                g_num+=dict_address[sub][3]
                b_num+=dict_address[sub][4]
            if block_num<=max_cap and block_num>0 and r_num<=r_cap and g_num<=g_cap and b_num<=b_cap:
                subsets.update({subset:(order_num, block_num, r_num, g_num, b_num)})
    added=[]
    final_subsets=([],[])
    if len(subsets)!=0:
        final_subsets=max(subsets.items(), key=lambda item: item[1][0])
        max_cap = max_cap - final_subsets[1][1]
        r_cap = r_cap - final_subsets[1][2]
        g_cap = g_cap - final_subsets[1][3]
        b_cap = b_cap - final_subsets[1][4]
        added = [re for re in orders if re['address'] in final_subsets[0]]
        orders = [re for re in orders if not re['address'] in final_subsets[0]]
        
 
    #50개에 맞춰 dict_address 첫번때 짜르기
    if max_cap>0:
        print("else", dict_address.keys())
        order_idx = 0
        for addr in set(address)-set(final_subsets[0]):
            for order in orders:
                if order['address'] == addr:
                    block_num = (order['red'] + order['green'] + order['blue'])
                    r_num = order['red']
                    g_num = order['green']
                    b_num = order['blue']
                    if block_num<=max_cap and r_num<=r_cap and g_num<=g_cap and b_num<=b_cap:
                        max_cap-=block_num
                        r_cap-=r_num
                        g_cap-=g_num
                        b_cap-=b_num
                        added.append(order)



    for order in added:
        order['pending'] = 3
        order['delivery_order'] = raddress[order['address']]
        order['is_last'] = 1

        update = order.copy()
        update['red'] = 0
        update['green'] = 0
        update['blue'] = 0
        update_list.append(update)


    ####### partial delivery
    if max_cap > 0:
        print("partial", dict_address.keys())
        rgb_cap = [r_cap, g_cap, b_cap]
        for addr in set(address) - set(final_subsets[0]):
            for order in orders:
                if order['address'] == addr:
                    rgb_num = [0, 0, 0]
                    rgb_num_later = [ order['red'], order['green'], order['blue']]
                    print("partial delivery order", order)
                    if max_cap > 0:
                        for i in range(len(rgb_num)):
                            if max_cap>0:
                                # print("1. rgb_num", rgb_num)
                                # print("1. rgb_num_later", rgb_num_later)
                                if rgb_cap[i]>max_cap:
                                    max_cap_temp = max_cap - rgb_num_later[i]
                                else:
                                    max_cap_temp = rgb_cap[i]- rgb_num_later[i]
                                if max_cap_temp > 0:
                                    rgb_cap[i]=rgb_cap[i]-rgb_num_later[i]
                                    rgb_num[i]=rgb_num_later[i]
                                    rgb_num_later[i]=0
                                else:
                                    rgb_num[i] = max_cap_temp + rgb_num_later[i]
                                    rgb_num_later[i] = -max_cap_temp
                                # print("2. rgb_num",rgb_num)
                                # print("2. rgb_num_later",rgb_num_later)
                                max_cap=max_cap-rgb_num[i]

                        update=order.copy()
                        update['red']=rgb_num_later[0]
                        update['green']=rgb_num_later[1]
                        update['blue']=rgb_num_later[2]
                        update_list.append(update)
                        # print("update: ",update)

                        sch=order.copy()
                        sch['red']=rgb_num[0]
                        sch['green']=rgb_num[1]
                        sch['blue']=rgb_num[2]
                        sch['pending']=3
                        sch['delivery_order']=raddress[order['address']]
                        sch['is_last']=0
                        added.append(sch)
                        # print("sch: ",sch)





    print("scheduling time: ", time.time()-start," order N: ", len(orders))
    return update_list, added


# schedule(orders)