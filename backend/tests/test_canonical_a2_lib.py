import unittest
from backend.canonical_a2_lib import compose_canonical_a2


class TestCanonicalA2Lib(unittest.TestCase):
    def test_refund_exchange(self):
        out = compose_canonical_a2("Refund/Exchange/Cancellation", "policy", "facts", {})
        self.assertIn("refund", out.lower())

    def test_price_match(self):
        out = compose_canonical_a2("Price match/Discount/Coupon stacking", "policy", "facts", {})
        self.assertIn("price match", out.lower())

    def test_adversarial(self):
        out = compose_canonical_a2("Adversarial/trap attempts", "policy", "facts", {})
        self.assertIn("policy", out.lower())


if __name__ == "__main__":
    unittest.main()
