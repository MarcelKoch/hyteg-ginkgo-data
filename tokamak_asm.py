import pandas as pd

from tokamak_helpers import *

json_mi100_files = [f.path for f in os.scandir("tokamak-mi100") if f.name.endswith(".json")]
json_mi100_pa_files = filter(lambda f: f.endswith(".json"), map(lambda f: f.path,
                                                                [f for f in os.scandir("tokamak-mi100/") if
                                                                 "petsc" in f.name] + [f for f in os.scandir(
                                                                    "tokamak-pa-mi100/")]))

db_mi100_par = Database(json_mi100_pa_files)
db_mi100_seq = Database(json_mi100_files)


def combine(df_seq, df_par):
    if "petsc" in df_par.columns:
        df_par = df_par.drop(columns="petsc")
    return pd.concat([df_par.rename(columns={"ginkgo": "ginkgo-par-asm"}),
                      df_seq.rename(columns={"ginkgo": "ginkgo-seq-asm"})],
                     axis=1)


speedup_seq = level_6_speedup(db_mi100_seq)
speedup_par = level_6_speedup(db_mi100_par)
speedup = combine(speedup_seq, speedup_par)
plot_level_6_speedup(speedup, "speedup-mi100-with-par-asm")
print(speedup)

runtime_seq = level_6_total_runtime(db_mi100_seq)
runtime_par = level_6_total_runtime(db_mi100_par)
runtime = combine(runtime_seq, runtime_par)
plot_level_6_total_runtime(runtime, "runtime-mi100-with-par-asm")
print(runtime)

cost_breakdown = ginkgo_non_solve_cost(db_mi100_par)
plot_cgc_breakdown(cost_breakdown, "cost-breakdown-mi100-with-par-asm")
print(cost_breakdown)
