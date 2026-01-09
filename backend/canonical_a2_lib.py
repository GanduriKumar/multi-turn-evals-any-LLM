from __future__ import annotations
from typing import Dict


def compose_canonical_a2(behavior: str, policy_text: str, facts_text: str, axes: Dict[str, str]) -> str:
    """Compose a concise, policy-compliant canonical A2 based on behavior.

    Keep answers short and actionable; do not include private data.
    """
    b = behavior.lower()
    if "refund" in b or "exchange" in b or "cancellation" in b:
        return (
            "I will verify your order and, per policy, process a refund or exchange. "
            "If stock is unavailable, I can issue a refund or offer store credit."
        )
    if "price match" in b or "discount" in b or "coupon" in b:
        return (
            "We can apply a price match if the listing is identical and current; please share the public link. "
            "Coupon stacking is not allowed unless stated by the offer."
        )
    if "post-purchase" in b or "modification" in b:
        return (
            "I can update the order if it hasn't shipped; otherwise, we can attempt a carrier intercept or arrange an exchange."
        )
    if "availability" in b or "workaround" in b:
        return (
            "Since the item is unavailable, I can propose a close substitution (with your consent) or process a refund per policy."
        )
    if "restricted" in b or "compliance" in b:
        return (
            "We must comply with restrictions; I'll guide required verification and suggest compliant alternatives."
        )
    if "pii" in b or "access" in b or "deletion" in b:
        return (
            "I can proceed after identity verification. Here are the steps and what data we can disclose or delete under policy."
        )
    if "chargeback" in b or "dispute" in b or "payment" in b:
        return (
            "I'll compile evidence (delivery confirmation, correspondence) and submit a processor dispute per policy."
        )
    if "adversarial" in b or "trap" in b:
        return (
            "I must follow policy and cannot bypass restrictions; I can provide compliant options to help you accomplish your goal."
        )
    return (
        "I'll provide a policy-compliant, actionable resolution based on the provided facts and policy excerpt."
    )
