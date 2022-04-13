---
theme: solarized
transition: none
title: hyteg + ginkgo update III
author: Marcel Koch
---

# Changes

- use `roundRobinVolume` for Tokamak
- same for `AgglomerationWrapper`
- optimized `migratePrimitives` a bit
  - no 'worst possible complexity' anymore

# Paper

- Good coarse grid solver don't scale well (GAMG)
- Solve coarse grid only on subset
- Thesis: better scaling through agglomeration
- Related: PETSc Telescope

# Scaling

- Run on Horeka
- Upto 4000 (9000) cores
- Coarse grid size fixed to ~1500 dofs per core
- Considered PETSc preconditioners:
  - gamg, jacobi, (hypre), icc, ilu, ssor
- Ginkgo requires special queue

---

![](../img/petsc-pre-cgc-rf.png)

---

![](../img/petsc-pre-cgc-tit.png)

---

![](../img/petsc-pre-rt.png)

# Todo

- Figure out parameters for ~9000 cores
- Ginkgo benchmarks with ILU (AMG?)
- Synchronize with Nils previous experience
