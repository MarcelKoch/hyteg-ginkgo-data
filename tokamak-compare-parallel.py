#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json as js


# In[3]:


import os
import re

import pandas as pd

from process import *
from tokamak_helpers import *


# In[7]:


seq_v100 = [f.path for f in os.scandir("tokamak-v100") if ".json" in f.name and "ginkgo" in f.name]
par_v100 = [f.path for f in os.scandir("tokamak-pa-v100") if ".json" in f.name and "ginkgo" in f.name]
par_mi100 = [f.path for f in os.scandir("tokamak-pa-mi100") if ".json" in f.name and "ginkgo" in f.name]
seq_mi100 = [f.path for f in os.scandir("tokamak-mi100") if ".json" in f.name and "ginkgo" in f.name]


# In[8]:


db_seq_v100 = Database(seq_v100)
db_par_v100 = Database(par_v100)
db_seq_mi100 = Database(seq_mi100)
db_par_mi100 = Database(par_mi100)


# In[21]:


def compare_rt(db_seq, db_par, node):
    df_seq = db_seq.get_df(node).groupby("min_l").sum()["max"].rename("seq")
    df_par = db_par.get_df(node).groupby("min_l").sum()["max"].rename("par")
    return pd.concat([df_seq, df_par], axis=1)

def speedup(df):
    return df.seq / df.par


# In[37]:


total_rt_v100 = compare_rt(db_seq_v100, db_par_v100, "solve")
total_rt_mi100 = compare_rt(db_seq_mi100, db_par_mi100, "solve")

total_rt = pd.concat([speedup(total_rt_v100).rename("v100"), speedup(total_rt_mi100).rename("mi100")], axis=1)


# In[38]:

fig, ax = plt.subplots()
total_rt.plot(ax=ax, logy=False, title="Speedup [Total Runtime]", xlabel="Coarse Grid Level", ylabel="Speedup against Seq.")
fig.savefig("img/compare-total-runtime")


# In[40]:

cgc_rt_v100 = compare_rt(db_seq_v100, db_par_v100, "coarse grid solver")
cgc_rt_mi100 = compare_rt(db_seq_mi100, db_par_mi100, "coarse grid solver")

cgc_rt = pd.concat([speedup(cgc_rt_v100).rename("v100"), speedup(cgc_rt_mi100).rename("mi100")], axis=1)

# In[34]:


fig, ax = plt.subplots()
cgc_rt.plot(ax=ax, logy=False, title="Speedup [Coarse Grid Runtime]", xlabel="Coarse Grid Level", ylabel="Speedup against Seq.")
fig.savefig("img/compare-cgc-runtime")


