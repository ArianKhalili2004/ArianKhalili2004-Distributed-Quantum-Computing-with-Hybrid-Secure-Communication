import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from channels import QuantumChannel, ClassicalChannel
from nodes import QuantumNode
from qkd import bb84_key_exchange


def test_bb84_key_exchange():
    alice = QuantumNode('Alice', 1)
    bob = QuantumNode('Bob', 1)
    qch = QuantumChannel()
    cch = ClassicalChannel()
    key = bb84_key_exchange(alice, bob, 16, qch, cch)
    assert key is not None
    assert len(key) == 16
