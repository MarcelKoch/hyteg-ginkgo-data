from typing import Dict
import pandas as pd
import re
import json as js
from functools import lru_cache


def get_metadata(filename):
    name_re = re.compile(r"(petsc|ginkgo)-(\d)-(\d)(-noAgg)?")
    match = name_re.search(filename)
    if match:
        return{"solver": match.group(1),
               "min_l": int(match.group(2)),
               "max_l": int(match.group(3)),
               "agg": not bool(match.group(4))}
    else:
        raise RuntimeError


class Database(object):
    def __init__(self, json_files, metadata=get_metadata):
        self.data = []
        for file in json_files:
            json_data = js.load(open(file))
            self.data.append((json_data, metadata(file)))

    @lru_cache()
    def get_df(self, node):
        df_list = []
        for jd, md in self.data:
            vals = find(jd, node)
            new_df = to_df(vals)
            df_list.append(attach_metadata(new_df, md))
        return pd.concat(df_list, sort=False)


def dfs(timingTree, visit=lambda _: True):
    if isinstance(timingTree, dict):
        for k, v in timingTree.items():
            if isinstance(v, dict):
                yield k, v
                if visit(k):
                    yield from dfs(v, visit)


def find(data, key,*, ignore_case=True, cutoff=True):
    if ignore_case:
        matches = lambda cur_key: key.lower() in cur_key.lower()
    else:
        matches = lambda cur_key: key in cur_key

    if cutoff:
        visit = lambda __k: not matches(__k)
    else:
        visit = lambda _: True

    return [{k: v} for k, v in dfs(data, visit) if matches(k)]


def to_df(data):
    assert isinstance(data, list)

    series = []
    for d in data:
        k, v = next(iter(d.items()))
        series.append(pd.Series(v, name=k).drop(index="childs"))
    return pd.DataFrame(series).reset_index().rename(columns={"index": "node"})


def attach_metadata(df, data):
    m_df = pd.DataFrame([pd.Series(data)] * len(df))
    return pd.concat([df, m_df], axis=1)

