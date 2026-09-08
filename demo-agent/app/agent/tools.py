AGENT_SLUG = "customer-support-agent"
AGENT_NAME = "Customer Support Agent"

TOOL_NAMES = frozenset(
    {
        "list_orders",
        "get_order",
        "cancel_order",
        "refund_order",
        "cancel_all_orders",
    }
)

OPENAI_TOOLS: list[dict] = [
    {
        "type": "function",
        "name": "list_orders",
        "description": "List all customer orders.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_order",
        "description": "Get details for a specific order by ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "integer",
                    "description": "The numeric order ID.",
                },
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "cancel_order",
        "description": "Cancel a single order by ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "integer",
                    "description": "The numeric order ID to cancel.",
                },
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "refund_order",
        "description": "Refund a specific order by ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "integer",
                    "description": "The numeric order ID to refund.",
                },
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "cancel_all_orders",
        "description": "Cancel all active orders. Use only when the user explicitly requests bulk cancellation.",
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        "strict": True,
    },
]
