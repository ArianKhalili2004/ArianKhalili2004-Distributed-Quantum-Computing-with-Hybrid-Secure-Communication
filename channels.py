# channels.py  ────────────────────────────────────────────────
import time, random

class ClassicalChannel:
    def __init__(self, delay: float = 0.0):
        self.delay = delay

    def send(self, sender: str, receiver: str, message):
        if self.delay:
            time.sleep(self.delay)
        return message


class QuantumChannel:
    def __init__(self, delay: float = 0.0, eavesdrop_rate: float = 0.0):
        self.delay = delay
        self.eavesdrop_rate = eavesdrop_rate

    def transmit_qubit(self, bit: int, alice_basis: str, bob_basis: str) -> int:
        if self.delay:
            time.sleep(self.delay)

        eavesdropped = (random.random() < self.eavesdrop_rate)
        if eavesdropped:
            eve_basis = random.choice(['Z', 'X'])
            if eve_basis != alice_basis:          # خطای احتمالی ایجاد می‌کند
                bit = random.choice([0, 1])

        if alice_basis == bob_basis:
            return bit
        return random.choice([0, 1])
