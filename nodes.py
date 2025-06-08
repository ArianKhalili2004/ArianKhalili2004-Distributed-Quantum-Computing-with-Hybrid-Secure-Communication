# nodes.py  ───────────────────────────────────────────────────
"""Data structure representing nodes in the quantum network."""

class QuantumNode:
    """Representation of a quantum node in the network."""
    def __init__(self, name: str, num_qubits: int):
        """Create a node with ``name`` and ``num_qubits`` available."""
        self.name = name
        self.num_qubits = num_qubits
        self.shared_keys = {}

    def store_shared_key(self, other: str, key: str):
        """Store a key shared with another node."""
        self.shared_keys[other] = key

    def get_shared_key(self, other: str):
        """Retrieve the key shared with ``other`` if present."""
        return self.shared_keys.get(other)
