import math
from collections import Counter
import hashlib

OUTPUT_FILE = "qeac_output.txt"

# ---- Utility Functions ----
def load_pi_digits(filename="pi-10million.txt", precision=200000, start=0):
    """Load pi digits from file, return cleaned string starting at offset."""
    try:
        with open(filename, "r") as f:
            pi_str = f.read().strip()
        pi_str = pi_str.replace("\n", "").replace(" ", "").lstrip("3.")
        return pi_str[start:start+precision]
    except FileNotFoundError:
        raise RuntimeError(f"{filename} not found. Place it in this directory.")

def pi_to_binary_sequences(pi_digits, window_size=33):
    """Convert pi digits into 33-bit binary windows, with mapping back to digits."""
    digit_to_bin = {str(d): f"{d:04b}" for d in range(10)}
    bitstream = "".join(digit_to_bin[d] for d in pi_digits if d in digit_to_bin)

    sequences = []
    digit_windows = []
    bits_per_digit = 4
    for i in range(0, len(bitstream) - window_size, window_size):
        sequences.append([int(b) for b in bitstream[i:i+window_size]])
        # Map back roughly: each 33-bit window covers ~9 digits
        digit_start = i // bits_per_digit
        digit_end = digit_start + (window_size // bits_per_digit) + 1
        digit_windows.append(pi_digits[digit_start:digit_end])
    return sequences, digit_windows

def entropy(window):
    counts = Counter(window)
    total = len(window)
    return -sum((c/total) * math.log2(c/total) for c in counts.values() if c > 0)

def correlation(Wi, Wj):
    """Compute QEAC correlation between two 33-bit windows."""
    xor_bits = [a ^ b for a, b in zip(Wi, Wj)]
    return 1 - (entropy(xor_bits) / 33)

def build_qeac_chain(sequences, digit_windows, start_index=0, threshold=0.8, max_links=10):
    """Build QEAC chain from sequences starting at start_index."""
    chain = [(sequences[start_index], digit_windows[start_index])]
    cursor = start_index + 1
    while cursor < len(sequences) and len(chain) < max_links:
        rho = correlation(chain[-1][0], sequences[cursor])
        if rho >= threshold:
            chain.append((sequences[cursor], digit_windows[cursor]))
            cursor += 1
        else:
            break
    return chain

# ---- Entry Point ----
if __name__ == "__main__":
    # --- User-configurable params ---
    START_POS = 100000   # initial digit offset in pi-10million.txt
    PRECISION = 200000   # how many digits to load per slice
    STEP_SIZE = 100000   # how far to jump if no chains found
    MAX_CHAINS = 5       # max chains to record
    MAX_LINKS = 10       # max links per chain
    SCAN_RANGE = 500     # how many starting windows to scan

    with open(OUTPUT_FILE, "w") as out:
        def log(msg):
            print(msg)
            out.write(msg + "\n")

        chain_count = 0
        lengths = []
        current_start = START_POS
        found_any = False

        while not found_any:
            log(f"\nLoading pi digits from offset {current_start} with length {PRECISION}...")
            pi_digits = load_pi_digits("pi-10million.txt", precision=PRECISION, start=current_start)
            sequences, digit_windows = pi_to_binary_sequences(pi_digits)

            log("Searching for QEAC chains...")
            for start_idx in range(0, SCAN_RANGE):
                if chain_count >= MAX_CHAINS:
                    break
                chain = build_qeac_chain(sequences, digit_windows, start_index=start_idx, max_links=MAX_LINKS)
                if len(chain) > 1:
                    found_any = True
                    chain_count += 1
                    lengths.append(len(chain))
                    global_pos = current_start + start_idx
                    log(f"\nQEAC Chain {chain_count} (start index {global_pos}):")
                    for j, (seq, digits) in enumerate(chain):
                        seq_str = "".join(map(str, seq))
                        seq_pos = global_pos + j
                        log(f"  Link {j}: {seq_str} (π position {seq_pos})")
                        log(f"       π digits: {digits}")

                    # Hash the entire concatenated bitstring
                    bitstring = "".join("".join(map(str, s)) for s, _ in chain)
                    hash_val = hashlib.blake2b(bitstring.encode("utf-8")).hexdigest()

                    log(f"  QEAC Length: {len(chain)} | Integrity Hash: {hash_val}")
                    log("-" * 50)

            if not found_any:
                current_start += STEP_SIZE
                if current_start + PRECISION > 10_000_000:  # safety cap
                    log("Reached end of pi-10million.txt without finding chains.")
                    break

        # --- Summary Section ---
        log("\n=== QEAC Summary Report ===")
        log(f"Final Start Position in π: {current_start}")
        log(f"Precision Loaded: {PRECISION} digits")
        log(f"Scan Range: {SCAN_RANGE} windows")
        log(f"Chains Found: {chain_count}")
        if lengths:
            log(f"Average Chain Length: {sum(lengths)/len(lengths):.2f}")
            log(f"Longest Chain Length: {max(lengths)}")
        else:
            log("Average Chain Length: N/A")
            log("Longest Chain Length: N/A")

    print(f"\nResults saved to {OUTPUT_FILE}")

