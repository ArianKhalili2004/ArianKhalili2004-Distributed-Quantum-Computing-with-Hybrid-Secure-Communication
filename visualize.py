"""Visualization helpers for plots used in the demo."""

import matplotlib.pyplot as plt
import pandas as pd

def plot_grover_hist(counts):
    """Display a histogram of measurement ``counts`` from Grover search."""
    plt.figure(figsize=(8, 4))
    plt.bar(counts.keys(), counts.values())
    plt.title("Grover Search – Outcome Histogram ({} shots)".format(sum(counts.values())))
    plt.xlabel("Measured state")
    plt.ylabel("Counts")
    plt.tight_layout()
    plt.show()

def plot_performance(qkd_time, grover_delay, key_bits, iters):
    """Plot timing contributions of QKD and Grover search."""
    data = [
        {"Task": f"QKD ({key_bits} bits)",       "Time [s]": qkd_time},
        {"Task": f"Grover delay ({iters} iters)","Time [s]": grover_delay},
    ]
    df = pd.DataFrame(data)
    plt.figure(figsize=(6, 4))
    plt.bar(df["Task"], df["Time [s]"])
    plt.title("Approximate Runtime Contributions")
    plt.ylabel("Time [s]")
    plt.tight_layout()
    plt.show()
