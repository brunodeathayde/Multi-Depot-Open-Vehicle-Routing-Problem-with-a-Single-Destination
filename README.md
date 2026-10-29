# 🚚 Multi-Depot Open Vehicle Routing Problem with a Singel Destination

This repository presents the research and implementation related to the Distributed Permutation Flowshop Problem (DPFSP) with transport times. It includes mathematical and constraint programming models, benchmark test instances, experimental results, and the conference article submitted to CIE52.

---

## 🧠 Problem Overview

The Distributed Permutation Flowshop Problem (DPFSP) extends the classical flowshop scheduling problem by distributing machines across multiple locations and introducing transport times between them. The objective is to optimize job sequencing across distributed machines while minimizing metrics such as makespan and total tardiness.

---

## 📁 Repository Structure

### `CIE52/`
Contains the official conference article presented at CIE52.

- `CIE52_171.pdf`: Full paper detailing the problem formulation, models, experimental setup, and results.

### `Models/`
Includes Python implementations of optimization models.

- `MILP.py`: Mixed Integer Linear Programming model using Gurobi/CPLEX.
- `CP_IBM.py`: Constraint Programming model using IBM ILOG CPLEX CP Optimizer.
- `CP_HEXALY.py`: Constraint Programming model using Hexaly.
- `README.md`: Documentation of model structure and solver requirements.

### `Test instances/`
Provides benchmark datasets used in the experiments.

- Small and large-sized instances based on Taillard’s testbed.
- Includes job counts, machine counts, family configurations, and transport matrices.
- `README.md`: Description of instance generation and configuration.

### `Results/`
Contains output data from experiments using the models.

- `Results_Exact_Methods_Flow_Shop_transport_times.xlsx`: Spreadsheet with performance metrics (makespan, tardiness, runtime).
- `Comparison.pptx`: Presentation summarizing comparative results across models.
- `README.md`: Summary of result structure and key findings.

---

## 📊 Features

- MILP and CP models for solving DPFSP with transport times
- Support for multiple solvers: Gurobi, IBM CPLEX, Hexaly
- Benchmark datasets for reproducibility
- Detailed results and visual comparisons
- Peer-reviewed conference article

---
