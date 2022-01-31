#!/usr/bin/env python
# coding: utf-8

import os
import re

import pandas as pd

from process import *
from tokamak_helpers import *
import matplotlib as mpl
from matplotlib.rcsetup import cycler
import itertools as iter

default_cycler = mpl.rcParams["axes.prop_cycle"]
mpl.rcParams["axes.prop_cycle"] = (default_cycler + cycler(marker=["o", "v", "^", "<", ">", "s", "p", "*",
                                                                   "D", "P", "X"][:len(default_cycler)]))


def get_metadata(file):
    name_re = re.compile(r"pre-(\w+-)?(\w+)-(\d)-(\d+)")
    match = name_re.search(file)
    if match:
        return{"pre": match.group(2),
               "min_l": int(match.group(3)),
               "nodes": int(match.group(4)),
               "agg": bool(match.group(1))}
    else:
        raise RuntimeError


def process_log(filename):
    min_dofs = float("inf")
    max_dofs = 0
    iters = []
    with open(filename) as file:
        for line in file:
            dofs_re = re.compile(r"\)\s+(\d+)\s+\|\s+\d+\s+\|\s+(\d+)")
            it_petsc_re = re.compile(r"\[PETSc CG]\D+(\d+)")
            it_ginkgo_re = re.compile(r"\[Ginkgo CG]\s+converged\s+after\s+(\d+)")
            if match := dofs_re.search(line):
                dof = int(match.group(2))
                max_dofs = max(max_dofs, dof)
                min_dofs = min(min_dofs, dof)
            elif match := it_petsc_re.search(line):
                iters.append(int(match.group(1)))
            elif match := it_ginkgo_re.search(line):
                iters.append(int(match.group(1)))
    return {**get_metadata(filename), "min_dofs": min_dofs, "max_dofs":max_dofs, "gmg_it": len(iters), "it": sum(iters)}


files = [f.path for f in iter.chain(os.scandir("petsc-pre-l0"), os.scandir("gko-pre")) if f.name.endswith(".json")]
logs = [f.path for f in iter.chain(os.scandir("petsc-pre-l0"), os.scandir("gko-pre")) if f.name.endswith(".log")]

db = Database(files, get_metadata)

it = pd.DataFrame([process_log(f) for f in logs])
it = it.set_index(["pre", "min_l", "nodes", "agg"])

solve = db.get_df("solve").drop(columns=["node"])
solve = solve.groupby(["pre", "min_l", "nodes", "agg"]).median()
solve = pd.concat([solve, it], axis=1).reset_index().set_index(["pre", "count", "agg"])

cgc = db.get_df("coarse grid").drop(columns=["node"])
cgc = cgc.groupby(["pre", "min_l", "nodes", "agg"]).median()
cgc = pd.concat([cgc, it], axis=1).reset_index().set_index(["pre", "count", "agg"])

print(solve)
print(cgc)

tit = cgc.average / cgc.it

print(tit)

default_cycler = mpl.rcParams["axes.prop_cycle"]
dashed_cylcer = (default_cycler + cycler(linestyle=["--"] * len(default_cycler)))
fig, ax = plt.subplots(dpi=300)
for agg in [True, False]:
    tit_agg = tit.unstack("agg")[agg].unstack("pre")
    ax.set_prop_cycle(default_cycler if not agg else dashed_cylcer)
    tit_agg.plot(ax=ax)
ax.set_yscale("log")
ax.set_xscale("log")
ax.set_ylabel("Time/It [s]")
ax.set_xlabel("Processors")
ax.set_title("Coarse Grid Solve Time [Weak Scaling]")
ax.get_xaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
ax.legend()
fig.savefig("img/pre-cgc-tit-l0")

rt = cgc.average
fig, ax = plt.subplots(dpi=300)
for agg in [True, False]:
    rt_agg = rt.unstack("agg")[agg].unstack("pre")
    ax.set_prop_cycle(default_cycler if not agg else dashed_cylcer)
    rt_agg.plot(ax=ax)
ax.set_yscale("log")
ax.set_xscale("log")
ax.set_ylabel("Time [s]")
ax.set_xlabel("Processors")
ax.set_title("Coarse Grid Solve Time [Weak Scaling]")
ax.get_xaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
ax.legend()
fig.savefig("img/pre-cgc-rf-l0")

rt = solve.average  # / solve.gmg_it
fig, ax = plt.subplots(dpi=300)
for agg in [True, False]:
    rt_agg = rt.unstack("agg")[agg].unstack("pre")
    ax.set_prop_cycle(default_cycler if not agg else dashed_cylcer)
    rt_agg.plot(ax=ax)
ax.set_xscale("log")
ax.set_ylabel("Time [s]")
ax.set_xlabel("Processors")
ax.set_title("Solve Time Per V-Cycle [Weak Scaling]")
ax.get_xaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
ax.legend()
fig.savefig("img/pre-rt-l0")


