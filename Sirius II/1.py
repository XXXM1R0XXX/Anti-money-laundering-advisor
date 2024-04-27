import httpx
import threading
import time

import pandas as pd


def get_feauters_from_users(r):
    address = r['address']
    chain_stats = [i for i in r['chain_stats'].values()]
    mempool_stats = [i for i in r['mempool_stats'].values()]
    mempool_stats.append(address)
    return chain_stats + mempool_stats
def parse_elements(client, bitcoin_address, n, oll_id, trans_list, was, feauters):
    URL_address = f"https://blockstream.info/api/address/{bitcoin_address}"
    was.append(bitcoin_address)
    try:
        r = client.get(URL_address, timeout=10)
    except httpx.RequestError as e:
        print(bitcoin_address, 'loh')
        return -1
    if r.status_code != 200:
        return
    r = r.json()
    feauters.append(get_feauters_from_users(r))
    print(r)
    total_tx = r['chain_stats']['tx_count']
    pipl = min(50, total_tx)
    if pipl == 0:
        return

    URL_last_tx = f"https://blockstream.info/api/address/{bitcoin_address}/txs"
    r_tx = client.get(URL_last_tx, timeout=10)
    r_tx = r_tx
    r_tx_data = r_tx.json()
    s_id = []
    j = 0
    while pipl > 0 and j < len(r_tx_data):
        print(r_tx_data[j])
        vin_list = r_tx_data[j]['vin']
        for vin in vin_list:
            ch = vin['prevout']['scriptpubkey']
            if ch not in oll_id:
                oll_id.append(ch)
                s_id.append(ch)
            ch_address = vin['prevout']['scriptpubkey_address']
            if ch_address not in oll_id:
                oll_id.append(ch_address)
                s_id.append(ch_address)
            trans_list.append([ch, vin['prevout']['value'], ch_address])
            pipl = min(50, total_tx) - len(s_id)
        j += 1
    if n - 1 < 1 or not s_id:
        return

    # Создаем потоки для параллельного выполнения функции parse_elements
    threads = [threading.Thread(target=parse_elements, args=(client, sid, n - 1, oll_id, trans_list, was, feauters)) for sid in s_id]
    # Запускаем потоки
    for thread in threads:
        thread.start()
    # Дожидаемся окончания работы всех потоков
    print(1)
    for thread in threads:
        thread.join()
def parse_other_users(client, s, feauters, incorrect):
    if s == 0:
        return
    URL_address = f"https://blockstream.info/api/address/{s}"
    try:
        r = client.get(URL_address, timeout=15)
        if r.status_code != 200:
            incorrect.append(s)
            return
        r = r.json()
        print(1)
        feauters.append(get_feauters_from_users(r))
    except Exception as e:
        print(s, e)
        return

with httpx.Client() as client:
    elems = []
    oll_id = []
    was = []
    feauters = []
    incorrect = []
    parse_elements(client, "1Ee9ZiZkmygAXUiyeYKRSA3tLe4vNYEAgA", 0, elems, oll_id, was, feauters)
    users_without_features = [i if i not in was else 0 for i in elems]

    treads = [threading.Thread(target=parse_other_users, args=(client, s, feauters, incorrect)) for s in users_without_features if s != 0]
    print(len(treads))
    for thread in treads:
        thread.start()
    for thread in treads:
        thread.join()
    oll_id_df = pd.DataFrame(oll_id)
    feauters_df = pd.DataFrame(feauters)
    oll_id_df = oll_id_df[~oll_id_df.iloc[:, -1].isin(incorrect)]
    oll_id_df = oll_id_df[~oll_id_df.iloc[:, 0].isin(incorrect)]



print(oll_id_df.shape, len(oll_id))