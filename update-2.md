---
theme: solarized
transition: none
title: hyteg + ginkgo update II
author: Marcel Koch
---

# Changes

- Parallel assembly on CPUs
  - Run Solver on single GPU
- Runtime configuration of Ginkgo
  - Using JSON format
  - Flexible Choice of preconditioners

---

![](compare-cgc-runtime.png)

---

![](compare-total-runtime.png)

# WIP

- Solve on multiple GPU
- Enable more preconditioners


# Preconditioner

- Previously:
  - Ginkgo with ILU
  - PETSc without preconditioning
- Now both using Jacobi
- From 130k to ~390 (Jac) / ~130 (ILU) 
- Growth as 2x

---

![V100](runtime-jac-v100.png)

---

![MI100](runtime-jac-mi100.png)

---

![V100](speedup-jac-v100.png)

---

![MI100](speedup-jac-mi100.png)

--- 

![V100](cg-apply-jac-v100.png)

---

![MI100](cg-apply-jac-mi100.png)

# Tokamak App

- Using default parameters
- Good convergence for ~10 iterations (red. < 0.5)
- Worse convergence afterwards (red. ~0.6-0.7)
- True error only reduced in first ~10 it.

# Todo

- Getting the paper ready
- Use Horeka for benchmarks
- Aim for $10^10$ DOFs 
