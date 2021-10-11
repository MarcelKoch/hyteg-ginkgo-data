#!/usr/bin/env python
# coding: utf-8

import os
import re

import pandas as pd

from process import *
from tokamak_helpers import *


def get_metadata(file):
    name_re = re.compile(r"(\w+)-(\d)-(\d+)")
    match = name_re.search(file)
    if match:
        return{"pre": match.group(1),
               "min_l": int(match.group(2)),
               "nodes": int(match.group(3)),}
    else:
        raise RuntimeError


files = [f.path for f in os.scandir("petsc-pre") if f.name.endswith(".json")]

db = Database(files, get_metadata)

solve = db.get_df("solve").drop(columns=["node"])
solve = solve.groupby(["pre", "min_l", "nodes"]).median()

cgc = db.get_df("coarse grid").drop(columns=["node"])
cgc = cgc.groupby(["pre", "min_l", "nodes"]).median()


def process_log(filename):
    min_dofs = float("inf")
    max_dofs = 0
    iters = []
    with open(filename) as file:
        for line in file:
            dofs_re = re.compile(r"\)\s+(\d+)\s+\|\s+\d+\s+\|\s+(\d+)")
            it_re = re.compile(r"\[PETSc CG]\D+(\d+)")
            if match := dofs_re.search(line):
                dof = int(match.group(2))
                max_dofs = max(max_dofs, dof)
                min_dofs = min(min_dofs, dof)
            elif match := it_re.search(line):
                iters.append(int(match.group(1)))
    return {**get_metadata(filename), "min_dofs": min_dofs, "max_dofs":max_dofs, "gmg_it": len(iters), "it": sum(iters)}


logs = [f.path for f in os.scandir("petsc-pre") if f.name.endswith(".log")]
it = pd.DataFrame([process_log(f) for f in logs])
it = it.set_index(["pre", "min_l", "nodes"])

df = pd.concat([cgc, it], axis=1).reset_index()
df = df[df.pre != "hypre"]
df = df.set_index(["pre", "count"])

tit = df.average / df.it
tit = tit.unstack("pre")

fig, ax = plt.subplots()
tit.plot(ax=ax)
ax.set_yscale("log")
ax.set_xscale("log")
ax.set_ylabel("Time/It [s]")
ax.set_xlabel("Processors")
ax.set_title("Coarse Grid Solve Time [Weak Scaling]")
ax.get_xaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
ax.legend()
fig.savefig("petsc-pre-cgc-tit")

rt = df.average
rt = rt.unstack("pre")
fig, ax = plt.subplots()
rt.plot(ax=ax)
ax.set_yscale("log")
ax.set_xscale("log")
ax.set_ylabel("Time [s]")
ax.set_xlabel("Processors")
ax.set_title("Coarse Grid Solve Time [Weak Scaling]")
ax.get_xaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
ax.legend()
fig.savefig("petsc-pre-cgc-rf")


df = pd.concat([solve, it], axis=1).reset_index()
df = df[df.pre != "hypre"]
df = df.set_index(["pre", "count"])

rt = df.average
rt = rt.unstack("pre")
fig, ax = plt.subplots()
rt.plot(ax=ax)
ax.set_xscale("log")
ax.set_ylabel("Time [s]")
ax.set_xlabel("Processors")
ax.set_title("Solve Time [Weak Scaling]")
ax.get_xaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
ax.legend()
fig.savefig("petsc-pre-rt")


