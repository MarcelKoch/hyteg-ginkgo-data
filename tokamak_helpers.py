import os

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import ticker

from process import *

iter_re = re.compile("converged after (\d+) iterations")


def apply_filter(df: pd.DataFrame):
    #df = df[~(df["agg"] & (df.solver == "petsc"))].drop(columns="agg")
    df = df[df.max_l == 6].drop(columns="max_l")
    return df


def level_6_speedup(db: Database):
    df = db.get_df("coarse grid solver")

    # filter stupid petsc results
    df = apply_filter(df)

    # get total runtime of cgs over all iterations
    rt = df.groupby(["min_l", "solver"]).sum()

    # seems to be the most reasonable choice (rel low variance)
    rt = rt["max"].unstack("solver")

    speedup = rt.apply(lambda s: rt.petsc / s)
    speedup = speedup.drop(columns="petsc")

    return speedup


def level_6_total_runtime(db: Database):
    df = db.get_df("solve")

    df = apply_filter(df)

    rt = df.set_index(["min_l", "solver"])
    rt = rt["max"].unstack("solver")

    return rt


def level_6_cgc_runtime(db: Database):
    df = db.get_df("coarse grid solver")

    df = apply_filter(df)

    # get total runtime of cgs over all iterations
    rt = df.groupby(["min_l", "solver"]).sum()

    rt = rt.unstack("solver").average

    return rt


def level_6_only_cg_apply(db: Database):
    df = db.get_df("cg solver apply")

    df = apply_filter(df)

    rt = df.groupby(["min_l", "solver"]).sum()
    rt = rt["max"].unstack()

    return rt


def cg_apply_per_iteration(db: Database):
    df = db.get_df("cg solver apply")

    df = df.reset_index().rename(columns={"index": "iteration"})
    df = df.set_index(["min_l", "iteration", "solver"])["max"].unstack(["min_l", "solver"])

    return df


def cg_apply(db: Database):
    df = cg_apply_per_iteration(db)

    return df.sum().unstack("solver")


def plot_cg_apply(df: pd.DataFrame, outname: str):
    fig, ax = plt.subplots()

    df.plot(ax=ax)

    ax.set_yscale("log")
    ax.set_ylabel("Runtime of CG Apply [s]")
    ax.set_xlabel("Coarse Grid Level")
    ax.set_title("Tokamak Max. Level 6 [CG Apply]")
    #ax.get_yaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
    ax.legend()

    fig.savefig(outname)


def ginkgo_setup_cost(db: Database):
    df_assembly = db.get_df("assembly")
    df_setup = db.get_df("set-up")

    df_assembly.node = "assembly"
    df_setup.node = "setup"

    df = pd.concat([df_assembly, df_setup], sort=False)

    df = apply_filter(df)

    df = df.set_index(["min_l", "node"]).unstack("node").average

    return df


def ginkgo_non_solve_cost(db: Database):
    df_assembly = db.get_df("assembly")
    df_setup = db.get_df("set-up")
    df_cg_apply = db.get_df("cg solver apply")
    df_cgc = db.get_df("coarse grid solver")

    df_assembly.node = "assembly"
    df_setup.node = "setup"
    df_cg_apply.node = "cg_apply"
    df_cgc.node = "total"

    df = pd.concat([df_assembly, df_setup, df_cg_apply, df_cgc], sort=False)

    df = apply_filter(df)
    df = df[df.solver == "ginkgo"].drop(columns="solver")

    rt = df.groupby(["min_l", "node"]).sum()["max"].unstack("node")

    rt = rt.assign(rest=lambda df: df.total - (df.setup + df.assembly + df.cg_apply))

    return rt


def plot_cgc_breakdown(df: pd.DataFrame, outname):
    fig, ax = plt.subplots()

    dfp = df.apply(lambda s: s / df.total * 100)

    ax.bar(dfp.index, dfp.cg_apply, label="CG Apply")
    ax.bar(dfp.index, dfp.assembly, bottom=dfp.cg_apply, label="Assembly")
    ax.bar(dfp.index, dfp.setup, bottom=dfp.cg_apply + dfp.assembly, label="Setup")
    ax.bar(dfp.index, dfp.rest, bottom=dfp.cg_apply + dfp.assembly + dfp.setup, label="Rest")

    ax.set_title("Tokamak Max. Level 6")
    ax.set_xlabel("Coarse Grid Level")
    ax.set_ylabel("Runtime [%]")
    ax.set_title("Tokamak Max. Level 6 [Cost Break-down]")
    ax.legend()

    # ax.set_yscale("log")
    ax.get_yaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))

    fig.savefig(outname)


def plot_ginkgo_setup_cost(df: pd.DataFrame, outname):
    fig, ax = plt.subplots()

    ax.bar(df.index, df.assembly, label="Assembly")
    ax.bar(df.index, df.setup, bottom=df.assembly, label="Setup")

    ax.set_title("Tokamak Max. Level 6")
    ax.set_xlabel("Coarse Grid Level")
    ax.set_ylabel("Runtime [%]")
    ax.set_title("Tokamak Max. Level 6 [Set-Up Costs]")
    ax.legend()

    # ax.set_yscale("log")
    ax.get_yaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))

    fig.savefig(outname)


def plot_level_6_speedup(df: pd.DataFrame, outname):
    fig, ax = plt.subplots()

    df.plot(ax=ax, label=None)

    ax.axhline(1, c="r", ls="--", label="Speedup 1x")

    # ax.set_yscale("log")
    ax.set_ylabel("Speedup against PETSc")
    ax.set_xlabel("Coarse Grid Level")
    ax.set_title("Tokamak Max. Level 6 [Speedup]")
    ax.get_yaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
    ax.legend()

    fig.savefig(outname)


def plot_level_6_total_runtime(df: pd.DataFrame, outname):
    fig, ax = plt.subplots()

    df.plot(ax=ax)

    ax.set_ylabel("GMG Runtime [s]")
    ax.set_xlabel("Coarse Grid Level")
    ax.set_title("Tokamak Max. Level 6 [Total Runtime]")
    ax.get_yaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
    ax.legend()

    fig.savefig(outname)


def plot_level_6_cgc_runtime(df: pd.DataFrame, outname):
    fig, ax = plt.subplots()

    df.plot(ax=ax)

    ax.axhline(df.petsc[0], c="r", ls="--", label="PETSc min_l=0")

    ax.set_yscale("log")
    ax.set_ylabel("Coarse Grid Solve Runtime [s]")
    ax.set_xlabel("Coarse Grid Level")
    ax.set_title("Tokamak Max. Level 6 [Coarse Grid Runtime]")
    ax.get_yaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
    ax.legend()

    fig.savefig(outname)


def compare_cuda_hip(db_v100: Database, db_mi100: Database):
    df_v100 = db_v100.get_df("cg solver apply")
    df_mi100 = db_mi100.get_df("cg solver apply")

    df_v100.node = "v100"
    df_mi100.node = "mi100"

    df = pd.concat([df_v100, df_mi100], sort=False)

    df = apply_filter(df)

    df = df.groupby(["min_l", "node"]).sum().average.unstack("node")

    return df


def plot_compare_cuda_hip(df: pd.DataFrame, outname):
    fig, ax = plt.subplots()

    s = df.mi100 / df.v100
    s.plot(ax=ax)

    ax.axhline(1, c="r", ls="--", label="v100")

    ax.set_ylabel("Runtime Relative to V100")
    ax.set_xlabel("Coarse Grid Level")
    ax.set_title("Tokamak Max. Level 6 [V100 - MI100 Comparison]")
    # ax.get_yaxis().set_major_formatter(ticker.StrMethodFormatter("{x:g}"))
    ax.legend()

    fig.savefig(outname)
