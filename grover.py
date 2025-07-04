"""Minimal distributed Grover search utilities."""

import math
import time
from qiskit import QuantumCircuit, transpile

from qiskit_aer import Aer
_backend = Aer.get_backend('qasm_simulator')


# A helper to run circuits regardless of qiskit version
def _run(circuit, shots=1024):
    """Execute ``circuit`` on the simulator and return the result."""
    try:
        from qiskit import execute
        job = execute(circuit, _backend, shots=shots)
    except ImportError:
        job = _backend.run(transpile(circuit, _backend), shots=shots)
    return job.result()

# Oracle and diffuser ---------------------------------------------------------
def apply_oracle(qc: QuantumCircuit, target: str, anc=None):
    """Apply the Grover oracle for ``target`` on ``qc``."""
    n = len(target)
    controls = list(range(n - 1))
    last = n - 1
    needed_ancilla = max(0, len(controls) - 2)

    if needed_ancilla > 0: 
        if anc is None or len(anc) < needed_ancilla:
            raise ValueError("❌ Ancilla qubits are required for this Grover circuit.")

    for i, b in enumerate(target):
        if b == '0':
            qc.x(i)

    qc.h(last)
    if len(controls) == 0:
        qc.z(0)
    elif len(controls) == 1:
        qc.cz(controls[0], last)
    elif len(controls) == 2:
        qc.ccx(controls[0], controls[1], last)
    else:
        qc.mct(controls, last, anc, mode='basic')
    qc.h(last)

    for i, b in enumerate(target):
        if b == '0':
            qc.x(i)
def apply_diffuser(qc: QuantumCircuit, n: int, ancilla_idxs=None):
    """Apply the Grover diffuser on ``n`` qubits."""
    # ➊ H روی همهٔ کیوبیت‌های داده
    for q in range(n):
        qc.h(q)

    # ➋ X روی همه
    for q in range(n):
        qc.x(q)

    # ➌ وارون‌سازی فاز روی |11..1>
    qc.h(n - 1)
    if n == 1:
        qc.z(0)
    elif n == 2:
        qc.cz(0, 1)
    else:
        last = n - 1
        if n - 1 == 2:
            qc.ccx(0, 1, last)
        else:
            controls = list(range(0, n - 1))
            qc.mct(controls, last, ancilla_idxs, mode='basic')
    qc.h(n - 1)

    # ➍ X را برگردان
    for q in range(n):
        qc.x(q)

    # ➎ H پایانی روی همه
    for q in range(n):
        qc.h(q)
    return qc

# تابع اصلی ---------------------------------------------------------------
def distributed_grover_search(nodes, target_state: str, qchannel=None, log_fn=None):
    """Simulate Grover search across ``nodes``.

    Each node sequentially applies the oracle and diffuser while optional
    communication delays are imposed by ``qchannel``.
    """

    def log(msg):
        if log_fn:
            log_fn(msg)

    n = len(target_state)
    anc_cnt = max(0, n-3)
    qc = QuantumCircuit(n+anc_cnt, n)
    anc = list(range(n, n+anc_cnt)) if anc_cnt else None

    for q in range(n):
        qc.h(q)

    iters = max(1, math.floor((math.pi/4)*math.sqrt(2**n)))
    for i in range(iters):
        for node in nodes:
            log(f"🌀 Node {node.name}: oracle step {i+1}/{iters}")
            apply_oracle(qc, target_state[::-1], anc)
            if qchannel and qchannel.delay:
                time.sleep(qchannel.delay)
        for node in nodes:
            log(f"✨ Node {node.name}: diffuser step {i+1}/{iters}")
            apply_diffuser(qc, n, anc)
            if qchannel and qchannel.delay:
                time.sleep(qchannel.delay)

    qc.measure(range(n), range(n))
    res = _run(qc, shots=1024)
    counts = res.get_counts()
    best = max(counts, key=counts.get)
    return best, counts
