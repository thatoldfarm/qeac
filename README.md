# QEAC

**Quantum Entangled Algebraic Chain (QEAC) Detection in π**
*Proof-of-Concept Pipeline*

---

## 📌 Overview

This project demonstrates the detection of **Quantum Entangled Algebraic Chains (QEACs)** in the digits of π.
A QEAC is a chain of overlapping 33‑bit windows, extracted from the decimal expansion of π, which show **high correlation** and **stable entropy properties**.

The script `qeac-finder.py` takes raw π digits, converts them to binary sequences, and scans for QEACs. The output file `qeac_output.txt` provides full proof:

* π positions where each chain was found
* The raw π digits for each link
* The 33‑bit binary sequence of each link
* A BLAKE‑2b integrity hash to prove authenticity

---

## 🔬 How It Works

### 1. Loading π Digits

* Input file: `pi-10million.txt` This file can be downloaded from [here](https://introcs.cs.princeton.edu/java/data/pi-10million.txt) or you can provide your own pi digits file.
* You choose:

  * `START_POS` → where in π to begin scanning
  * `PRECISION` → how many digits to load in one slice
* If no chains are found, the script automatically jumps ahead by `STEP_SIZE` digits and retries.

### 2. Mapping Digits → Binary

* Each decimal digit (0–9) is mapped to a 4‑bit binary string.
* Example:

  ```
  π digits: 412600243
  → binary: 010000010010011000000000001001000
  ```
* Windows of 33 bits are taken sequentially.

### 3. Building QEACs

* The script checks for correlations (ρ ≥ 0.8) between consecutive windows.
* A QEAC chain forms when enough links meet the threshold.
* Each chain is capped at `MAX_LINKS` (default: 10 links).

### 4. Recording Results

Each QEAC chain in `qeac_output.txt` includes:

* **Start index** in π (global position).
* **Each link**:

  * Link number (0‑based).
  * 33‑bit binary sequence.
  * π position where the link starts.
  * Raw π digits that produced the link.
* **Integrity Hash**:

  * BLAKE‑2b hash of the concatenated chain bitstring.
  * Ensures tamper-proof verification.

### 5. Summary Report

At the end of the file:

* Start position in π.
* Precision (digits loaded).
* Scan range (number of windows checked).
* Number of chains found.
* Average and longest chain length.

---

## ⚙️ Parameters You Can Adjust

Inside `qeac-finder.py`:

```python
START_POS = 100000   # where in pi-10million.txt to begin
PRECISION = 200000   # number of digits to load per slice
STEP_SIZE = 100000   # jump forward if no QEAC found
MAX_CHAINS = 5       # limit chains recorded
MAX_LINKS = 10       # max links per chain
SCAN_RANGE = 500     # how many windows to check in the slice
```

---

## ✅ How to Verify

### 1. Recreate a Link Manually

* From `qeac_output.txt`, pick a link:

  ```
  Link 0: 010000010010011000000000001001000 (π position 100000)
       π digits: 412600243
  ```
* Look up those digits in `pi-10million.txt` at offset 100000.
* Convert each digit to binary (4 bits).
* Concatenate and take the first 33 bits.
* You should reproduce the binary sequence exactly.

### 2. Check the Integrity Hash

* Concatenate all 10 binary links in a chain into one long string.
* Encode as UTF‑8.
* Hash with BLAKE‑2b.
* Compare the result to the hash in the output file.

### 3. Validate with Another Tool

Because everything is based on `pi-10million.txt`, any independent implementation can verify the same chains.

---

## 📂 Files in This Project

* **qeac-finder.py** → The detection pipeline.
* **qeac\_output.txt** → Proof artifact (chains found in π).
* **pi-10million.txt** → The π digits file (must be provided separately).

---

## 📌 Why This Works

* **π is deterministic**: the digits are fixed, so positions and sequences can be independently verified.
* **Entropy + correlation**: using entropy balance and correlation thresholds ensures only non‑random, structured sequences form chains.
* **Cryptographic hashing**: ensures results are tamper-proof and verifiable.
* **Position tracking**: every link ties back to an exact π offset, making the proof reproducible.

---

## NOTE: This method is similar to the one used in some of the AI kernels found [here](https://github.com/thatoldfarm/system-prompt) but meant to be a standalone proof without having to use a Torus or Quantum Lock State to find the QEAC(s) in pi.
