import time

import fastapi
from fastapi import Request
from graph_model import Graph_model
from db import Database
from fastapi.responses import JSONResponse
import torch
from torch_geometric.data import Data, DataLoader
import uvicorn
import requests
import pandas as pd
model = Graph_model()
database = Database()
database.auto_migrate()
import threading
import httpx

def parse_elements(client, bitcoin_address, n, oll_id, trans_list):
    URL_address = f"https://blockstream.info/api/address/{bitcoin_address}"
    try:
        r = client.get(URL_address, timeout=5)
    except httpx.RequestError as e:
        print(bitcoin_address, 'loh')
        return -1
    r = r
    if r.status_code != 200:
        return
    total_tx = r.json()['chain_stats']['tx_count']
    pipl = min(50, total_tx)
    if pipl == 0:
        return

    URL_last_tx = f"https://blockstream.info/api/address/{bitcoin_address}/txs"
    r_tx = client.get(URL_last_tx, timeout=5)
    r_tx = r_tx
    r_tx_data = r_tx.json()
    s_id = []
    j = 0
    while pipl > 0 and j < len(r_tx_data):
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
            print(ch, vin['prevout']['value'], ch_address)
            pipl = min(50, total_tx) - len(s_id)
        j += 1
    if n - 1 < 1 or not s_id:
        return

    # Создаем потоки для параллельного выполнения функции parse_elements
    threads = [threading.Thread(target=parse_elements, args=(client, sid, n - 1, oll_id, trans_list)) for sid in s_id]
    # Запускаем потоки
    for thread in threads:
        thread.start()
    # Дожидаемся окончания работы всех потоков
    print(1)
    for thread in threads:
        thread.join()





def elems_to_graph(df):
    df['sender'] = df['sender'].factorize()[0]
    df['target'] = df['target'].factorize()[0]
    edge_index = torch.tensor([df['sender'].values, df['target'].values], dtype=torch.long)
    edge_features = torch.tensor(df['feature1'].values, dtype=torch.float).unsqueeze(1)

    unique_nodes = torch.unique(edge_index)
    node_features = unique_nodes.unsqueeze(1).float()

    data = Data(x=node_features, edge_index=edge_index, edge_attr=edge_features)
    return data
def get_trans_info(api_token, user_hash, transaction_hash):
    print("starting")
    user = database.check_api_key(api_token)
    if not user:
        return None

    st = time.time()
    with httpx.Client() as client:
        elems = []
        oll_id = []
        parse_elements(client, user_hash, 3, elems, oll_id)
    df = pd.DataFrame(oll_id, columns=['sender', 'feature1', 'target'])
    graph = elems_to_graph(df)
    result = model.predict(graph)
    print(time.time() - st)
    #database.write_log(api_token, transaction_hash)
    return result
def create_api_key(login, password):
    try:
        api_key = database.create_api_key(login, password)
        return api_key
    except:
        return None
def register(login, password):
    user = database.register(login, password)
    if not user:
        return JSONResponse(status_code=401, content={"message": "User already exists"})
    return JSONResponse(status_code=200, content={"message": "User created"})
def login(login, password):
    user = database.login(login, password)
    if not user:
        return JSONResponse(status_code=401, content={"message": "Invalid login or password"})
    return JSONResponse(status_code=200, content={"message": "Login successful"})
def check_api_key(login, password):
    api_key = database.check_api_key(login, password)
    return api_key
