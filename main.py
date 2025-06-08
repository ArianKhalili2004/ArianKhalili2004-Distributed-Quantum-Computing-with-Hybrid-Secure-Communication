"""Graphical interface for running quantum communication demos."""

import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import time, itertools

from nodes import QuantumNode
from channels import ClassicalChannel, QuantumChannel
from qkd import bb84_key_exchange
from encryption import encrypt_message_AES, decrypt_message_AES
from grover import distributed_grover_search
from visualize import plot_performance


class App(tk.Tk):
    """Main GUI application for demonstrating the network protocols."""

    def __init__(self):
        """Initialize all widgets and state."""
        super().__init__()
        self.title("Distributed Quantum Demo (Multi-node)")
        self.geometry("1000x860")
        self.pos = {}


        top = ttk.Frame(self); top.pack(fill='x', padx=12, pady=8)

        ttk.Label(top, text="Message:").pack(side='left')
        self.msg_var = tk.StringVar(value="Hello Quantum World!")
        ttk.Entry(top, textvariable=self.msg_var, width=30).pack(side='left', padx=6)

        ttk.Label(top, text="Target (binary):").pack(side='left')
        self.target_var = tk.StringVar(value="101")
        ttk.Entry(top, textvariable=self.target_var, width=15).pack(side='left', padx=6)

        ttk.Label(top, text="Delay (s):").pack(side='left')
        self.delay_var = tk.DoubleVar(value=0.01)
        ttk.Entry(top, textvariable=self.delay_var, width=6).pack(side='left', padx=4)

        ttk.Label(top, text="Eavesdrop rate:").pack(side='left')
        self.eaves_var = tk.DoubleVar(value=0.0)
        ttk.Entry(top, textvariable=self.eaves_var, width=6).pack(side='left', padx=4)

        ttk.Button(top, text="START", command=self.start_thread).pack(side='left', padx=10)
        ttk.Button(top, text="RUN GROVER", command=self.run_grover_thread).pack(side='left')


        self.prog = ttk.Progressbar(self, mode='determinate', length=200, maximum=100)
        self.prog.pack(pady=4)


        self.log = scrolledtext.ScrolledText(self, height=18, font=("Consolas", 10))
        self.log.pack(fill='both', expand=True, padx=12, pady=8)


        fig, (self.ax_hist, self.ax_net) = plt.subplots(1, 2, figsize=(10, 4))
        fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=12, pady=8)

    def log_print(self, txt: str) -> None:
        """Append ``txt`` to the log window."""
        self.log.insert('end', txt + '\n')
        self.log.see('end')

    def draw_hist(self, data) -> None:
        """Draw the Grover outcome histogram."""
        self.ax_hist.clear()
        self.ax_hist.bar(data.keys(), data.values())
        self.ax_hist.set_title("Grover Histogram")
        self.canvas.draw()

    def draw_network(self, nodes, links, highlights=None) -> None:
        """Visualize the quantum network graph."""
        if highlights is None:
            highlights = []
        self.ax_net.clear()
        G = nx.Graph()
        for node in nodes:
            G.add_node(node.name)
        for n1, n2 in links:
            G.add_edge(n1, n2)
        if not self.pos or set(self.pos.keys()) != set(G.nodes):
            self.pos = nx.spring_layout(G, seed=42)
        nx.draw(G, self.pos, ax=self.ax_net, with_labels=True,
                node_color='lightblue', edge_color='gray')
        if highlights:
            nx.draw_networkx_edges(G, self.pos, edgelist=highlights,
                                   ax=self.ax_net, edge_color='red', width=2)
        self.ax_net.set_title("Quantum Network")
        self.canvas.draw()

    def progress_ctl(self, action: str, value: int = 0) -> None:
        """Update the progress bar based on ``action``."""
        if action == 'start':
            self.after(0, lambda: self.prog.config(value=0))
        elif action == 'update':
            self.after(0, lambda: self.prog.config(value=value))
        elif action == 'stop':
            self.after(0, lambda: self.prog.config(value=100))

    def start_thread(self) -> None:
        """Launch the full scenario in a background thread."""
        self.log.delete('1.0', 'end')
        self.ax_hist.clear(); self.ax_net.clear(); self.canvas.draw()
        target = self.target_var.get().strip()
        th = threading.Thread(target=self.run_scenario, args=(target,), daemon=True)
        th.start()

    def run_grover_thread(self) -> None:
        """Run only the Grover search in a background thread."""
        target = self.target_var.get().strip()
        th = threading.Thread(target=self.run_grover_only, args=(target,), daemon=True)
        th.start()

    def run_scenario(self, target_bits: str) -> None:
        """Execute the full QKD and message passing scenario."""

        def log(x):
            self.after(0, self.log_print, x)

        def draw_hist(data):
            self.after(0, self.draw_hist, data)

        def draw_net(nodes, links, highlights=None):
            if highlights is None:
                highlights = []
            self.after(0, self.draw_network, nodes, links, highlights)
        self.progress_ctl('start')
        total_steps = (len(target_bits) + 1) * 2
        step = 0

        try:
            node_names = ["Alice", "Bob", "Charlie", "Dave"][:min(4, len(target_bits)+1)]
            nodes = [QuantumNode(name, len(target_bits)) for name in node_names]
            links = list(itertools.combinations(node_names, 2))
            draw_net(nodes, links)

            delay = self.delay_var.get()
            eaves = self.eaves_var.get()
            q_chan = QuantumChannel(delay=delay, eavesdrop_rate=eaves)
            c_chan = ClassicalChannel(delay=delay)
            log(f"Nodes and channels created. Delay={delay}s, Eaves={eaves}")

            total_qkd_time = 0
            for i in range(len(nodes) - 1):
                n1, n2 = nodes[i], nodes[i+1]
                log(f"QKD: {n1.name} → {n2.name}")
                t0 = time.time()
                key = bb84_key_exchange(n1, n2, 128, q_chan, c_chan)
                t1 = time.time()
                if key is None:
                    log("❌ QKD failed: high eavesdropping or noise.")
                    return
                total_qkd_time += (t1 - t0)
                step += 1
                self.progress_ctl('update', int(100 * step / total_steps))
                draw_net(nodes, links, [(n1.name, n2.name)])

            msg = self.msg_var.get().strip() or "Hello Quantum World!"
            log(f"📨 Original message: {msg}")
            current_msg = msg
            for i in range(len(nodes) - 1):
                sender = nodes[i]
                receiver = nodes[i+1]
                key = sender.get_shared_key(receiver.name)
                log(f"🔒 {sender.name} encrypts: '{current_msg}'")
                ct = encrypt_message_AES(key, current_msg)
                log(f"📡 {sender.name} sends encrypted to {receiver.name}: {ct.hex()[:32]}…")
                pt = decrypt_message_AES(key, ct)
                log(f"🔓 {receiver.name} decrypts: '{pt}'")
                log(f"🔄 {receiver.name} prepares to forward...")
                current_msg = pt
                step += 1
                self.progress_ctl('update', int(100 * step / total_steps))
                draw_net(nodes, links, [(sender.name, receiver.name)])

            log(f"📬 Final message at {nodes[-1].name}: {current_msg}")
        finally:
            self.progress_ctl('stop')

    def run_grover_only(self, target_bits: str) -> None:
        """Execute only the Grover search demonstration."""
        def log(x):
            self.after(0, self.log_print, x)

        def draw_hist(data):
            self.after(0, self.draw_hist, data)

        def draw_net(nodes, links, highlights=None):
            if highlights is None:
                highlights = []
            self.after(0, self.draw_network, nodes, links, highlights)
        log("Running Grover…")
        nodes = [QuantumNode("A", len(target_bits)), QuantumNode("B", len(target_bits))]
        q_chan = QuantumChannel(delay=self.delay_var.get(), eavesdrop_rate=0.0)
        t0 = time.time()
        state, counts = distributed_grover_search(nodes, target_bits, q_chan, log_fn=log)
        t1 = time.time()
        log(f"✅ Result: {state}")
        draw_hist(counts)
        plot_performance(qkd_time=0, grover_delay=t1 - t0,
                         key_bits=0, iters=len(counts))
        draw_net(nodes, [("A", "B")], highlights=[("A", "B")])


if __name__ == "__main__":
    App().mainloop()
