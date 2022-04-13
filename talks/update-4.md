---
theme: solarized
transition: none
title: hyteg + ginkgo update IV
author: Marcel Koch
---

# Changes

- Target Stokes application with ginkgo backend
- Coarse grid solver should be more expensive
- Uses block preconditioner
  - AMG on velocity, Jacobi on pressure
- Needed extensive additions to ginkgo

# Agglomeration

- Good coarse grid solver don't scale well (GAMG)
- Solve coarse grid only on subset
- Ginkgo always uses agglomeration (to 1 GPU)
- Good early results from Nils
- Run Nils' benchmark with ginkgo

# Scaling

- Up to 14k cores
- Coarse grid size fixed to ~5-10 dofs per core
- Agglomerate to 1 or 2 nodes
- Consider two different grids
  - `symmetricCube` and `tDomain`
  - Coarse problem for `symmetricCube` significantly easier 

---

![](../img/multigrid-symcube-coarse-grid-only-solver.png)

---

![](../img/multigrid-symcube-total-runtime.png)

---

![](../img/multigrid-tdomain-coarse-grid-only-solver.png)

---

![](../img/multigrid-tdomain-total-runtime.png)

---

![](../img/multigrid-convergence.png)

---

![](../img/multigrid-symcube-time-per-it.png)

---

![](../img/multigrid-tdomain-time-per-it.png)

# Take-Aways

- Stokes more interesting than Tokamak
- `symmetricCube` significantly faster than on SuperMUC
  - Coarse grid solve does not explode
- `tDomain` more difficult coarse grid solve
  - Up to 1/3 of runtime
  - Convergence depends on coarse grid size
- Need to lower ginkgo's AMG iteration cost 


# Todo

- Update ginkgo to newest AMG improvements
- Clean up ginkgo integration
