#  Virtual Memory Management Simulator (Windows Version)

A complete **Virtual Memory Management Simulator** built using:

- **Python (Tkinter GUI + Matplotlib)**
- **C++ (core memory simulator)**
- **Image rendering using OpenCV + PIL**

This tool allows students and OS enthusiasts to **simulate real virtual memory behavior** under different paging & replacement policies and generate **visual per-process analysis**.

---

# ⭐ Key Features

### 🖥 Graphical Interface (Tkinter)
- Choose **process list**
- Choose **one or more ptrace files**
- Set **memory size** (512 / 1024 / 2048 / 4096)
- Choose **page size**
- Select:
  - **Fetch policy** → *Demand / Pre-Paging*
  - **Replacement policy** → *FIFO / LRU / Second Chance / Optimal*

### ⚙️ C++ Backend Simulator
Implements:
- **Demand Paging**
- **Pre-Paging**
- **FIFO**
- **LRU**
- **Second Chance (Clock)**
- **Optimal Replacement (Belady’s algorithm)**

### 📊 Visualization (auto-generated)

For each cumulative trace set (Trace1 → Trace1+Trace2 → Trace1+Trace2+Trace3):

#### **Aggregate Plots**
1. **Page Size vs Page Faults**
2. **Policy Combination vs Page Faults**

#### **Per-Process Plots**
For each process:
- Page Size vs Page Faults  
- Policy Combination vs Page Faults  

#### 🔘 Results GUI provides Section Buttons:
- **Overall**
- **Process 0**
- **Process 1**
- …

---

# 📂 Project Structure

```
Virtual Memory Management Simulator
│
├── Data/
│   ├── plist.txt
│   ├── ptrace1.txt
│   ├── ptrace2.txt
│   └── ptrace3.txt
│
├── Plots/
│   ├── plot1_combo1.png
│   ├── plot2_combo1.png
│   ├── ...
│   ├── Process_0/
│   │     ├── plot1_combo1_process0.png
│   │     ├── plot2_combo1_process0.png
│   ├── Process_1/
│   ├── ...
│
├── simulator.cpp
├── simClass.h
├── simInput.h
├── simConstants.h
│
├── driver.py
├── menuGUI.py
├── generateResults.py
├── resultsGUI.py
│
├── requirements.txt
└── README.md
```

---

# 🧰 Requirements (Windows)

### 1. Python 3.9+

### 2. MinGW-w64 (g++ compiler)
Required for compiling `simulator.cpp`.

### 3. Install Dependencies

```
pip install -r requirements.txt
```

Installs:
- matplotlib  
- numpy  
- pillow  
- opencv-python  
- pandas  

---

# ▶️ How to Run

### **1 — Open CMD inside the project folder**
```
cd "C:\path\to\Virtual-Memory-Management-Simulator"
```

### **2 — Start the application**
```
python driver.py
```

---

# 🧩 Application Flow

```
menuGUI.py  
    ↓
generateResults.py  
    ↓ (runs simulator.cpp → computes totals + per‑process faults)
resultsGUI.py
```

---

# 🔍 Algorithms Implemented

## Fetch Policies
| Policy | Description |
|--------|-------------|
| **DEMAND** | Load page only when referenced |
| **PRE** | Prefetch next page |

## Replacement Policies
| Policy | Description |
|--------|-------------|
| **FIFO** | Replace oldest loaded frame |
| **LRU** | Replace least recently used |
| **SECOND_CHANCE** | FIFO + use-bit (Clock Algorithm) |
| **OPTIMAL** | Belady’s optimal replacement with future knowledge |

---

# 📊 Plots Generated

### **Aggregate Plots**
- Page Size vs Page Faults  
- Paging + Replacement Combination vs Page Faults  

### **Per-Process Plots**
Stored in:
```
Plots/Process_<id>/
```

Each process folder contains:
- Page Size vs Page Faults  
- Combination vs Page Faults  

---

# ✔ Input File Formats

### **plist.txt**
```
processId   Page Number
0           124
1           342
```

### **ptrace.txt**
```
processId   Page Number
0           324
1           466
```

---

# 📝 Notes
- Application is optimized for **Windows**.
- Supports up to **three ptrace files**, building cumulative trace plots.

