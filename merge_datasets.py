import json
from pathlib import Path

datasets_dir = Path(r'c:\Users\kumar.gn\PycharmProjects\Testproject\datasets\commerce')
individual_files = sorted(datasets_dir.glob('promotions-pricing-price-match-discount-coupon-stacking-v1.0.0-*.dataset.json'))

combined = {
    'dataset_id': 'coverage-promotions-pricing-combined-1.0.0',
    'version': '1.0.0',
    'metadata': {
        'domain': 'commerce',
        'difficulty': 'mixed',
        'tags': ['combined', 'promotions', 'pricing', 'price-match'],
        'task_type': 'policy_decision',
        'short_description': 'Combined coverage dataset for Promotions & Pricing domain with Price match/Discount/Coupon stacking behavior scenarios'
    },
    'conversations': []
}

for f in individual_files:
    with f.open('r', encoding='utf-8') as fp:
        data = json.load(fp)
        combined['conversations'].extend(data['conversations'])

output_path = datasets_dir / 'coverage-promotions-pricing-combined-1.0.0.dataset.json'
with output_path.open('w', encoding='utf-8') as fp:
    json.dump(combined, fp, indent=2, ensure_ascii=False)

print(f"Created combined dataset with {len(combined['conversations'])} conversations")
