import pandas as pd

from tokamak_helpers import *


def combine(df_seq, df_par):
    if "petsc" in df_par.columns:
        df_par = df_par.drop(columns="petsc")
    return pd.concat([df_par.rename(columns={"ginkgo": "ginkgo-par-asm"}),
                      df_seq.rename(columns={"ginkgo": "ginkgo-seq-asm"})],
                     axis=1)

json_mi100_files = [f.path for f in os.scandir("tokamak-mi100") if f.name.endswith(".json")]
json_mi100_pa_files = filter(lambda f: f.endswith(".json"), map(lambda f: f.path,
                                                                [f for f in os.scandir("tokamak-mi100/") if
                                                                 "petsc" in f.name] + [f for f in os.scandir(
                                                                    "tokamak-pa-mi100/") if "petsc" not in f.name]))
json_v100_files = [f.path for f in os.scandir("tokamak-v100") if ".json" in f.name]
json_v100_pa_files = [f.path for f in os.scandir("tokamak-pa-v100") if ".json" in f.name and "petsc" not in f.name] + [f for f in json_v100_files if "petsc" in f]

for seq_files, par_files, name in [(json_v100_files, json_v100_pa_files, "v100"),
                                   (json_mi100_files, json_mi100_pa_files, "mi100")]:

    db_par = Database(par_files)
    db_seq = Database(seq_files)

    speedup_seq = level_6_speedup(db_seq)
    speedup_par = level_6_speedup(db_par)
    speedup = combine(speedup_seq, speedup_par)
    plot_level_6_speedup(speedup, f"speedup-{name}-with-par-asm")
    print(speedup)

    runtime_seq = level_6_total_runtime(db_seq)
    runtime_par = level_6_total_runtime(db_par)
    runtime = combine(runtime_seq, runtime_par)
    plot_level_6_total_runtime(runtime, f"runtime-{name}-with-par-asm")
    print(runtime)

    cost_breakdown = ginkgo_non_solve_cost(db_par)
    plot_cgc_breakdown(cost_breakdown, f"cost-breakdown-{name}-with-par-asm")
    print(cost_breakdown)
