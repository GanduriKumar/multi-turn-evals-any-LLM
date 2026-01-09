import unittest
from backend.convgen_v2 import build_records
from backend.schemas import SchemaValidator


class TestConvGenV2(unittest.TestCase):
    def test_build_records_schema(self):
        axes = {
            "price_sensitivity": "high",
            "brand_bias": "none",
            "availability": "sold_out",
            "policy_boundary": "near_edge_allowed",
        }
        ds, gd = build_records(domain="Orders & Returns", behavior="Refund/Exchange/Cancellation", axes=axes)
        sv = SchemaValidator()
        self.assertEqual([], sv.validate("dataset", ds))
        self.assertEqual([], sv.validate("golden", gd))
        self.assertEqual(ds["dataset_id"], gd["dataset_id"])
        # expected final assistant turn index stored
        self.assertEqual(gd["entries"][0]["turns"][0]["turn_index"], 3)


if __name__ == "__main__":
    unittest.main()
