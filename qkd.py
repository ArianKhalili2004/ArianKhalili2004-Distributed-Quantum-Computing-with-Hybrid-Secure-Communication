# qkd.py  ─────────────────────────────────────────────────────
import random
from channels import QuantumChannel, ClassicalChannel
from nodes import QuantumNode

def bb84_key_exchange(alice: QuantumNode,
                      bob: QuantumNode,
                      key_length: int,
                      qchannel: QuantumChannel,
                      cchannel: ClassicalChannel):

    initial = key_length * 3
    a_bits   = [random.randint(0, 1) for _ in range(initial)]
    a_bases  = [random.choice(['Z', 'X']) for _ in range(initial)]
    b_bases  = [random.choice(['Z', 'X']) for _ in range(initial)]
    b_bits   = []

    for bit, a_bs, b_bs in zip(a_bits, a_bases, b_bases):
        b_bits.append(qchannel.transmit_qubit(bit, a_bs, b_bs))

    cchannel.send(alice.name, bob.name, a_bases)
    match = [i for i in range(initial) if a_bases[i] == b_bases[i]]

    raw_a = [a_bits[i] for i in match]
    raw_b = [b_bits[i] for i in match]

    sample = max(1, int(len(raw_a) * 0.2))
    test_idx = random.sample(range(len(raw_a)), sample)

    test_bits = {i: raw_a[i] for i in test_idx}
    cchannel.send(alice.name, bob.name, test_bits)

    if any(raw_a[i] != raw_b[i] for i in test_idx):
        return None                       # شنود یا نویز زیاد

    for i in sorted(test_idx, reverse=True):
        raw_a.pop(i)
    key_bits = raw_a[:key_length]
    key_str  = ''.join(map(str, key_bits))

    alice.store_shared_key(bob.name, key_str)
    bob.store_shared_key(alice.name, key_str)
    return key_str
