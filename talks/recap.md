---
theme: solarized
transition: none
title: hyteg + ginkgo recap
author: Marcel Koch
---

# Implementation

- Ginkgo CG and Minres solver
- Parallel assembly on CPU
- Solve on single GPU

# Paper Idea

- Good coarse grid solver don't scale well (GAMG)
- Solve coarse grid only on subset
- Thesis: better scaling through agglomeration

# Tokamak Benchmark

- Run on Horeka, up to 9k cores
- Compare Ginkgo and Petsc coarse grid solver
- Both with Jacobi preconditioner

# Tokamak Results

- Need at least medium sized coarse grid to see benefit of GPU, ~100k DOFs
- CGC has only limited impact on total runtime

# Stokes Benchmark

- Again on Horeka, up to 14k cores
- Found configuration with high CGC cost, ~40% of runtime
- Considered AMG and Jacobi preconditioner for velocity block

# Stokes Results

- AMG (Petsc) significantly benefits from agglomeration
  - Largest speedup of ~1.4 
  - but only GAMG, not Hypre 
- Jacobi is fastest preconditioner, only little benefit from agglomeration

# Current Issues

- Not able to scale to larger sizes
- No good use case to demonstrate agglomeration

# Open Ends

- Larger Ginkgo overhead compared to Petsc
- Outdated implementation
