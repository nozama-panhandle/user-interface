import numpy as np
import pymysql
import pdb
import itertools


port = 8888
frame_rate = 30
host_name = "rpi-6.wifi.local.cmu.edu"
host_port = 7777
db=pymysql.connect(host='localhost',
                   user='strong',
                   password='strong',
                   db='orderdb')
cursor = db.cursor(pymysql.cursors.DictCursor)
cursor.execute("SELECT id, address, red, green, blue FROM orders ")
# cursor.execute("SELECT id, address, red, green, blue FROM orders WHERE pending='0'")
pend_list = cursor.fetchall()



def schedule(orders, max_cap= 50):
    address = [101, 102, 103, 203, 202, 201]
    if len(orders)==0:
        return

    dict_address = {}
    for i, add in enumerate(address):
        order_num=0
        block_num = 0
        oders_by_address = []
        for order in orders:
            if order['address']==add:
                order_num +=1
                block_num += (order['red']+order['green']+order['blue'])
                oders_by_address.append(order)
        dict_address.update({add:(order_num, block_num, oders_by_address)})


    #######  address간 block의 총 조합-> 50개 이하 -> 그중 max 오더수
    # sort_address={k: v for k, v in sorted(dict_address.items(), key=lambda item: item[1], reverse=True)}
    subsets={}
    for L in range(1, len(dict_address) + 1):
        for subset in itertools.combinations(dict_address, L):
            block_num = 0
            order_num = 0
            print(subset)
            for sub in subset:
                order_num+=dict_address[sub][0]  ##order number
                block_num+=dict_address[sub][1]  ##block number
            if block_num<=max_cap and block_num>0:
                subsets.update({subset:(order_num, block_num)})

    print(subsets)
    if len(subsets)!=0:
        sorted_subsets={k: v for k, v in sorted(subsets.items(), key=lambda item: item[1][0], reverse=True)}
        final_subsets = list(sorted_subsets.keys())[0]
        print(final_subsets, sorted_subsets[final_subsets][1])
        max_cap = max_cap - sorted_subsets[final_subsets][1]
        for order_idx, add in enumerate(final_subsets):
            cursor.execute("UPDATE orders SET pending='3', delivery_order='%s' WHERE address='%s'" % (order_idx, add))
            db.commit()
            orders = [re for re in orders if not (re['address'] == add)]
            order_idx_=order_idx

        # while(max_cap>0):
        while (1):
            max_num = 0
            order_idx_+=1
            single_order=[]
            for order in orders:
                block_num = (order['red'] + order['green'] + order['blue'])
                if block_num>max_num and block_num<=max_cap:
                    max_num=block_num
                    single_order= order

            print(single_order)
            if len(single_order) == 0:
                break
            else:
                final_subsets= list(final_subsets)
                final_subsets.append(single_order['address'])

                cursor.execute("UPDATE orders SET pending='3', delivery_order='%s' WHERE id='%s'" % (order_idx_, single_order['id']))
                db.commit()
                max_cap-=max_num
                print("single order",single_order, order_idx_)
                orders = [re for re in orders if not (re['id'] == single_order['id'])]


                for enu, final in enumerate(np.sort(final_subsets)):
                    cursor.execute("UPDATE orders SET pending='3', delivery_order='%s' WHERE address='%s'" % (
                    enu, final))
                    db.commit()

            sorted_final_subsets = []
            temp_sort = set(np.sort(final_subsets))
            temp_sort_1 = temp_sort - set([203, 202, 201])
            temp_sort_2 = temp_sort - set([101, 102, 103])
            pdb.set_trace()
            sorted_final_subsets=list(temp_sort_1)+np.sort(list(temp_sort_2))[::-1]

    #50개에 맞춰 dict_address 첫번때 짜르기
    else:
        order_idx = 0
        for order in orders:
            if order['address'] == list(dict_address.keys())[0]:
                block_num = (order['red'] + order['green'] + order['blue'])
                if block_num<=max_cap:
                    max_cap-=block_num
                    db.commit()
                    cursor.execute("UPDATE orders SET pending='3', delivery_order='%s' WHERE id='%s'" % (order_idx, order['id']))
                    print(order)

schedule(pend_list,300)