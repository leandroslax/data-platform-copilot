DATASETS = [
    {
        "dataset_id": "main.sales.orders",
        "name": "main.sales.orders",
        "catalog": "main",
        "schema": "sales",
        "table": "orders",
        "type": "table",
        "description": "Sales orders dataset used for revenue and order tracking.",
        "owner": "sales-platform",
        "columns": [
            {
                "name": "order_id",
                "data_type": "string",
                "nullable": False,
                "description": "Primary order identifier",
            },
            {
                "name": "customer_id",
                "data_type": "string",
                "nullable": False,
                "description": "Customer identifier",
            },
            {
                "name": "order_total",
                "data_type": "decimal(18,2)",
                "nullable": True,
                "description": "Total amount of the order",
            },
        ],
        "documentation": [
            {
                "document_id": "doc-orders-001",
                "title": "Orders domain documentation",
            }
        ],
    },
    {
        "dataset_id": "main.finance.invoices",
        "name": "main.finance.invoices",
        "catalog": "main",
        "schema": "finance",
        "table": "invoices",
        "type": "table",
        "description": "Invoice dataset for finance reconciliation.",
        "owner": "finance-data",
        "columns": [
            {
                "name": "invoice_id",
                "data_type": "string",
                "nullable": False,
                "description": "Invoice identifier",
            },
            {
                "name": "invoice_amount",
                "data_type": "decimal(18,2)",
                "nullable": True,
                "description": "Invoice amount",
            },
        ],
        "documentation": [
            {
                "document_id": "doc-invoices-001",
                "title": "Finance invoices documentation",
            }
        ],
    },
]
