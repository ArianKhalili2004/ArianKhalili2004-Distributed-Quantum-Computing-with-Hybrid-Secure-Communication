# nodes.py  ───────────────────────────────────────────────────
class QuantumNode:
    """
    نماينده يک گره کوانتومی در شبکه.
    name          : شناسهٔ گره
    num_qubits    : تعداد کیوبیت‌های محلی (فقط برای اطلاعات)
    shared_keys   : دیکشنری «نام گره مقابل → کلید باینری»
    """
    def __init__(self, name: str, num_qubits: int):
        self.name = name
        self.num_qubits = num_qubits
        self.shared_keys = {}

    def store_shared_key(self, other: str, key: str):
        self.shared_keys[other] = key

    def get_shared_key(self, other: str):
        return self.shared_keys.get(other)
