from tokamak_helpers import *

json_path = "tokamak-v100"
json_files = [f.path for f in os.scandir(json_path) if f.name.endswith(".json")]

json_path = "tokamak-mi100/"
json_mi100_files = [f.path for f in os.scandir(json_path) if f.name.endswith(".json")]

json_no_pre_files = filter(lambda f: f.endswith(".json"), map(lambda f: f.path,
                                                              [f for f in os.scandir("tokamak-v100/") if
                                                               "petsc" in f.name] + [f for f in
                                                                                     os.scandir("tokamak-no-pre/")
                                                                                     if "ginkgo" in f.name]))

json_mi100_no_pre_files = filter(lambda f: f.endswith(".json"), map(lambda f: f.path,
                                                                    [f for f in os.scandir("tokamak-mi100/") if
                                                                     "petsc" in f.name] + [f for f in os.scandir(
                                                                        "tokamak-mi100-no-pre/") if
                                                                                           "ginkgo" in f.name]))

json_mi100_pa_files = filter(lambda f: f.endswith(".json"), map(lambda f: f.path,
                                                                [f for f in os.scandir("tokamak-mi100/") if
                                                                 "petsc" in f.name] + [f for f in os.scandir(
                                                                    "tokamak-pa-mi100/")]))

jac_mi100 = [f.path for f in os.scandir("tokamak-jacobi-mi100") if ".json" in f.name]

jac_v100 = [f.path for f in os.scandir("tokamak-jacobi-v100") if ".json" in f.name]

pa_mi100 = [f.path for f in os.scandir("tokamak-pa-mi100") if ".json" in f.name]

pa_v100 = [f.path for f in os.scandir("tokamak-pa-v100") if ".json" in f.name]

for files, suffix in [
        # (json_files, ""),
        # (json_mi100_files, "-mi100"),
        # (json_no_pre_files, "-no-pre"),
        # (json_mi100_no_pre_files, "-mi100-no-pre"),
    (jac_mi100, "-jac-mi100"),
    (jac_v100, "-jac-v100"),
    (pa_v100, "-pa-v100"),
    (pa_mi100, "-pa-mi100")
]:
    _db = Database(files)

    speedup = level_6_speedup(_db)
    plot_level_6_speedup(speedup, "img/speedup" + suffix)
    print(speedup)

    runtime = level_6_total_runtime(_db)
    plot_level_6_total_runtime(runtime, "img/runtime" + suffix)
    print(runtime)

    rt_detail = ginkgo_non_solve_cost(_db)
    plot_cgc_breakdown(rt_detail, "img/cost-breakdown" + suffix)
    print(rt_detail)

    rt_cg = cg_apply(_db)
    plot_cg_apply(rt_cg, "img/cg-apply" + suffix)
    print(rt_cg)

    breakdown = total_runtime_breakdown(_db)
    plot_total_runtime_breakdown(breakdown, "img/runtime-breakdown" + suffix)
    print("Breakdown:\n", breakdown)
