import pandas as pd
from process import *
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cycler
import os


_default_cycler = mpl.rcParams["axes.prop_cycle"]
mpl.rcParams["axes.prop_cycle"] = (_default_cycler + cycler(marker=["o", "v", "^", "<", ">", "s", "p", "*",
                                                                   "D", "P", "X"][:len(_default_cycler)]))
default_cycler = mpl.rcParams["axes.prop_cycle"]
dashed_cylcer = (default_cycler + cycler(linestyle=["--"] * len(default_cycler)))


cur_path = "multigrid-a100"
json_files = [f.path for f in os.scandir(cur_path) if f.name.endswith(".json")]
log_files =  [f.path for f in os.scandir(cur_path) if f.name.endswith(".log")]


def get_metadata(filename):
    name_re = re.compile(r"(tdomain|symcube)-(agg|no_agg)-(gamg|hypre|ginkgo)-(\d+)?")
    match = name_re.search(filename)
    if match:
        return{"solver": match.group(3),
               "procs": int(match.group(4)) * 76,
               "mesh": match.group(1),
               "agg": match.group(2) == "agg"}
    else:
        raise RuntimeError


def process_log(filename):
    min_dofs = float("inf")
    max_dofs = 0
    iters = []
    with open(filename) as file:
        for line in file:
            dofs_re = re.compile(r"level\s+\d+:\s+(\d+)")
            it_petsc_re = re.compile(r"\[PETScBlockPreconditionedStokesSolver]\D+(\d+)")
            it_ginkgo_re = re.compile(r"\[Ginkgo Block]\s+converged\s+after\s+(\d+)")
            if match := dofs_re.search(line):
                dof = int(match.group(1))
                max_dofs = max(max_dofs, dof)
                min_dofs = min(min_dofs, dof)
            elif match := it_petsc_re.search(line):
                iters.append(int(match.group(1)))
            elif match := it_ginkgo_re.search(line):
                iters.append(int(match.group(1)))
    return {**get_metadata(filename), "min_dofs": min_dofs, "max_dofs":max_dofs, "gmg_it": len(iters), "it": sum(iters)}


db = Database(json_files, get_metadata)


total_solve = db.get_df("solve").drop(columns=["node"])
timings_total_solve = total_solve.groupby(["mesh", "solver", "agg", "procs"]).sum().sort_index().average
df = timings_total_solve.unstack(["mesh", "agg", "solver"])
for mesh in timings_total_solve.index.get_level_values("mesh").unique():
    fig, ax = plt.subplots(dpi=300)
    ax.set_title(f'{"Easy Mesh" if mesh == "symcube" else "Difficult Mesh"} - Total Runtime')
    for agg in [False, True]:
        ax.set_prop_cycle(default_cycler if agg else dashed_cylcer)
        df_ = df[(mesh, agg)]
        if "ginkgo" in df_.columns:
            df_ = df_[df_.columns[[0, 2, 1]]]
        df_.plot(ax = ax, logx=True)
    ax.set_ylabel("Runtime [s]")
    ax.set_xlabel("Number of Processes")
    fig.savefig(f"img/multigrid-{mesh}-total-runtime.png")


only_solver = pd.concat([db.get_df("solve", cutoff=False).set_index("node").loc["Solve"].reset_index().drop(columns="node"), db.get_df("Ginkgo Block Solver Apply").drop(columns="node")], sort=False)
timings_only_solver = only_solver.groupby(["mesh", "solver", "agg", "procs"]).sum().sort_index()["max"]
df = timings_only_solver.unstack(["mesh", "agg", "solver"])
for mesh in timings_only_solver.index.get_level_values("mesh").unique():
    fig, ax = plt.subplots(dpi=300)
    ax.set_title(f'{"Easy Mesh" if mesh == "symcube" else "Difficult Mesh"} - Solver Apply Runtime')
    for agg in [False, True]:
        ax.set_prop_cycle(default_cycler if agg else dashed_cylcer)
        df_ = df[(mesh, agg)]
        if "ginkgo" in df_.columns:
            df_ = df_[df_.columns[[0, 2, 1]]]
        df_.plot(ax = ax, logx=True)
    ax.set_ylabel("Runtime [s]")
    ax.set_xlabel("Number of Processes")
    fig.savefig(f"img/multigrid-{mesh}-coarse-grid-only-solver.png")


it = pd.DataFrame([process_log(f) for f in log_files])
it_ordered = it.set_index(["mesh", "solver", "agg", "procs"])
it_count = it_ordered.it.unstack(["agg", "mesh", "solver"])[True]
fig, ax = plt.subplots(dpi=300)
ax.set_title(f'Iterations until Convergance')
for mesh in ["symcube", "tdomain"]:
    ax.set_prop_cycle(default_cycler if mesh == "symcube" else dashed_cylcer)
    df_ = it_count[mesh]
    df_.plot(ax = ax, logx=True, logy=True)
ax.set_ylabel("Iterations")
ax.set_xlabel("Number of Processes")
fig.savefig("img/multigrid-convergence.png")


time_per_it = timings_only_solver / it_ordered.it
df = time_per_it.unstack(["mesh", "agg", "solver"])
for mesh in time_per_it.index.get_level_values("mesh").unique():
    fig, ax = plt.subplots(dpi=300)
    ax.set_title(f'{"Easy Mesh" if mesh == "symcube" else "Difficult Mesh"} - Runtime Per Iteration')
    for agg in [False, True]:
        ax.set_prop_cycle(default_cycler if agg else dashed_cylcer)
        df_ = df[(mesh, agg)]
        if "ginkgo" in df_.columns:
            df_ = df_[df_.columns[[0, 2, 1]]]
        df_.plot(ax = ax, logx=True, logy=True)
    ax.set_ylabel("Runtime [s]")
    ax.set_xlabel("Number of Processes")
    fig.savefig(f"img/multigrid-{mesh}-time-per-it.png")

