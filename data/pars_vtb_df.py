# import libraries
import requests
import pandas as pd
from time import sleep

# df with blocks
df_txs = []

cnt_blocks = 100

# iteration by blocks
for num_blocks in range(cnt_blocks):

    # df with transactoins
    df_transactions = []

    # block
    block = requests.get(f"https://blockchain.info/block-height/{830000 + num_blocks}?format=json").json()
    block = block['blocks'][0]

    # transactions
    transactions = block['tx']

    # iteration by transactions
    for txs in transactions[1:]:

        # iteration by transaction
        arr_tx = []
        inputs = txs['inputs'][0]
        outputs = txs['out'][0]

        # tr hash
        hash_txs = txs['hash']
        arr_tx.append(hash_txs)

        try:
            # for input
            addr_inp = inputs['prev_out']['addr']
            value_inp = inputs['prev_out']['value']

            arr_tx.append(addr_inp)
            arr_tx.append(value_inp)

            # for outputs
            addr_out = outputs['addr']
            value_out = outputs['value']
            arr_tx.append(addr_out)
            arr_tx.append(value_out)
            
            # save tr to main df
            df_transactions.append(arr_tx)
        
        except KeyError:
            continue
    
    # save to df with txs
    if len(df_txs) == 0:
        df_txs = pd.DataFrame(df_transactions, columns=['tr_hash', 'addr_inp', 'value_inp', 'addr_out', 'value_out'])
    else:
        df_txs = pd.concat([df_txs, pd.DataFrame(df_transactions, columns=['tr_hash', 'addr_inp', 'value_inp', 'addr_out', 'value_out'])], 
                           axis=0, ignore_index=True)
    
    df_txs.to_csv('data_blockchain_f_pars.csv')