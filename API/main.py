from typing import Union
# from ..data.preprocessing import *
import numpy as np
import pandas as pd
from fastapi import FastAPI
app = FastAPI()
def get_predict(hash):
    arr=np.load('../data/predicted.npy')
    df=pd.read_csv('../data/data_blockchain_f_pars.csv')

    return arr[df.index[df['tr_hash']==hash]]




@app.get("/")
def read_item(Hash: Union[str, None] = None):
    return {"predict": get_predict(Hash)}

