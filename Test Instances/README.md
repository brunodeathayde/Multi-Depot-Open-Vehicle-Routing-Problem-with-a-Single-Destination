# Benchmark Instances for the Open Vehicle Routing Problem with a Single Destination (OVRP-SD)

This repository provides benchmark instances for the **Open Vehicle Routing Problem with a Single Destination (OVRP-SD)**. In this variant, vehicles originate from multiple initial depots, visit a subset of customers to satisfy their demand, and finish their routes at a shared single destination (or terminal).

---

## Data Structure & File Format

The benchmark instances consist of two main datasets/tables describing the spatial layout (nodes) and the fleet characteristics (vehicles).

### 1. Nodes Specification 

Contains coordinate, demand, and functional role details for all locations in the network:

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `N_ID` | Integer | Unique identifier for each node. |
| `X` | Float / Int | X-coordinate in a 2D Cartesian plane. |
| `Y` | Float / Int | Y-coordinate in a 2D Cartesian plane. |
| `Demanda` | Integer | Demand quantity requested by the node. (`0` for depots/destinations). |
| `Tipo` | Char | Node type: **`D`** for Depots / Origin-Destination points, **`C`** for Customers. |

#### Sample Node Data
```text
N_ID,X,Y,Demanda,Tipo
1,126,-5,0,D
2,459,-731,0,D
3,-140,886,0,D
4,294,-185,0,D
5,130,294,4,C
6,95,-545,7,C
7,724,485,3,C
8,44,750,6,C
9,638,275,2,C
10,-879,16,10,C
11,-534,725,9,C
12,238,-705,5,C
```
### 2. Fleet & Vehicle Specification 

Defines the available fleet, carrying capacity, and starting location assignment for each vehicle:

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `V_ID` | Integer | Unique identifier for each vehicle. |
| `Capacidade` | Integer | Maximum load capacity of the vehicle. |
| `Deposito_ID` | Integer | Node ID (`N_ID`) representing the starting depot for the vehicle. |

#### Sample Vehicle Data
```text
V_ID,Capacidade,Deposito_ID
1,10,4
2,10,4
3,10,1
4,10,2
5,10,1
6,10,4
7,10,2
8,10,4
9,10,1
```
