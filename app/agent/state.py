from typing import TypedDict, Any

class AfterSaleAgentState(TypedDict, total=False):
    # Basic run context
    run_id: int
    user_id: int
    customer_id: int | None
    message: str

    # Parsed user intent
    intent: str | None
    order_no: str | None

    # Loaded business context
    order: dict[str, Any] | None
    payment: dict[str, Any] | None
    shipment: dict[str, Any] | None

    # Retrieved policy context
    policy_chunks: list[dict[str, Any]]

    # Decision result
    risk_level: str | None
    requires_approval: bool
    action: str | None

    # Final response
    final_answer: str | None
    error: str | None
    

