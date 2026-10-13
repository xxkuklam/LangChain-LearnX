"""Customer support tools shared by the notebooks.

Same tools as built step by step in 04_tools.py, collected here so that
the following notebooks (agents, middleware, LangGraph) can simply import them.
"""

from langchain.tools import tool
from pydantic import BaseModel, Field

# Fake data (in memory). Invoice number = order ID.
ORDERS = {
    "4821": {"customer": "Anne Hansen", "status": "delivered", "total": 1200.0},
    "4822": {"customer": "Anne Hansen", "status": "shipped", "total": 89.9},
    "4823": {"customer": "Ingrid Solberg", "status": "delivered", "total": 1200.0},
    "5010": {"customer": "Lars Berg", "status": "cancelled", "total": 450.0},
}

# Records from the bank, keyed by invoice number
BANK_PAYMENTS = {
    "4821": [  # paid twice: two records, each equal to the invoice total
        {"date": "2026-10-02", "amount": 1200.0, "reference": "Invoice 4821"},
        {"date": "2026-10-03", "amount": 1200.0, "reference": "Invoice 4821"},
    ],
    "4822": [{"date": "2026-10-05", "amount": 89.9, "reference": "Invoice 4822"}],
    "4823": [  # two instalments of 600: NOT a duplicate (together they equal the total)
        {"date": "2026-10-01", "amount": 600.0, "reference": "Invoice 4823"},
        {"date": "2026-10-08", "amount": 600.0, "reference": "Invoice 4823"},
    ],
    "5010": [{"date": "2026-09-20", "amount": 450.0, "reference": "Invoice 5010"}],
}

SYSTEM_PROMPT = (
    "You are a customer support assistant. Check the facts with the tools before acting. "
    "An invoice was paid twice only if the bank shows two payments and each equals the invoice total. "
    "In that case refund one payment. Otherwise do not refund."
)

USER_MESSAGE = "Anne Hansen reports that her invoice #4821 for 1200 NOK was charged twice. Please sort it out."


@tool
def get_order_status(order_id: str) -> str:
    """Look up an order by its ID and return the customer, status and invoice total in NOK."""
    order = ORDERS.get(order_id)
    if order is None:
        return f"Order {order_id} not found."
    return (
        f"Order {order_id} for {order['customer']}: status={order['status']}, "
        f"invoice total={order['total']} NOK"
    )


@tool
def get_bank_payments(invoice_number: str) -> str:
    """Return the bank records (date, amount in NOK) and the total received for an invoice number.
    Use it to check whether and how many times an invoice was paid, and how much money came in."""
    records = BANK_PAYMENTS.get(invoice_number)
    if not records:
        return f"No bank records for invoice {invoice_number}."
    lines = [f"- {r['date']}: {r['amount']} NOK ({r['reference']})" for r in records]
    total = sum(r["amount"] for r in records)
    return (
        f"{len(records)} bank record(s) for invoice {invoice_number}:\n"
        + "\n".join(lines)
        + f"\nTotal received: {total} NOK"
    )


class RefundInput(BaseModel):
    order_id: str = Field(description="ID of the order to refund, e.g. '4821'")
    amount: float = Field(gt=0, description="Amount to refund in NOK. Must not exceed the order total.")
    reason: str = Field(description="Short reason for the refund, e.g. 'duplicate payment'")


@tool(args_schema=RefundInput)
def issue_refund(order_id: str, amount: float, reason: str) -> str:
    """Refund money to the customer for an order. This moves real money, use it only when the refund is justified."""
    order = ORDERS.get(order_id)
    if order is None:
        return f"Refund failed: order {order_id} not found."
    if amount > order["total"]:
        return f"Refund failed: {amount} NOK is more than the order total ({order['total']} NOK)."
    return f"Refunded {amount} NOK for order {order_id} ({reason})."


TOOLS = [get_order_status, get_bank_payments, issue_refund]
