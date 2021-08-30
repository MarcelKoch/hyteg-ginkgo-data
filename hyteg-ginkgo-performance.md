# Performance Notes

- consider Tokamak example
  - 3D mesh
  - P1 discretization (scalar)
  - coarse grid with 56 DOFs
  - maxLevel 6 -> ~6M DOFs
  - each level increases the #DOFs (interior) by ~10x


- parameters

|                      | range              |   |
|----------------------|--------------------|---|
| minLevel             | 0 -                |   |
| maxlevel             | minLevel -         |   |
| refineCoarseMesh     | 0 -                |   |
| coarseGridSolverType | cg_ginkgo/cg_petsc |   |
| useAgglomeration     | true/false         |   |

- increasing refineCoarseMesh is not the same as
  increasing the minLevel
  - it has slightly more DOFs
  - it's significantly slower

- test variants:
  - only coarse grid solve: minLevel == maxLevel
	- biased since petsc does not use preconditioner
	- minLevel = maxLevel = 5 works -> 800k DOFs
  - vary minLevel in [0, maxLevel]
	- more realistic use case
  - useAgglomeration on/off
	- off only possible for petsc

- baseline results:
- min=0,max=5, petsc, agg=off -> 15s
- min=0,max=6, petsc, agg=off -> 108s, 15gb
- min=0,max=7, petsc, agg=off -> 950s, 100gb

- interesting metrics:
  - total runtime
  - total coarse grid solver runtime
  - only coarse grid runtime  
  - runtime 1st gmg it
  - average runtime gmg it (except 1st)
  - runtime per level (1st & avg)
  - coarse grid solve time
  - ginkgo set-up/assemly time
