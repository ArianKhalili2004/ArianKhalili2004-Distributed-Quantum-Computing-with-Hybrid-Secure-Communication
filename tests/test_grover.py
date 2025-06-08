import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from channels import QuantumChannel
from nodes import QuantumNode
from grover import distributed_grover_search


def test_distributed_grover():
    nodes = [QuantumNode('A', 2), QuantumNode('B', 2)]
    qch = QuantumChannel()
    target = '11'
    best, counts = distributed_grover_search(nodes, target, qchannel=qch)
    assert best == target
    assert sum(counts.values()) > 0
