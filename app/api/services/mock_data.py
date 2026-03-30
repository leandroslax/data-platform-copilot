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

LINEAGE = {
    "main.sales.orders": {
        "dataset_id": "main.sales.orders",
        "upstream": [
            "main.raw.orders_source",
            "main.raw.customers_source"
        ],
        "downstream": [
            "main.gold.sales_kpis",
            "main.analytics.orders_dashboard"
        ],
        "related_jobs": [
            "sales_orders_pipeline"
        ],
    },
    "main.finance.invoices": {
        "dataset_id": "main.finance.invoices",
        "upstream": [
            "main.raw.invoices_source"
        ],
        "downstream": [
            "main.gold.finance_reconciliation"
        ],
        "related_jobs": [
            "finance_invoices_pipeline"
        ],
    },
}

JOBS = [
    {
        "job_id": "12345",
        "job_name": "sales_orders_pipeline",
        "status": "active",
        "latest_status": "failed",
        "latest_error_summary": "Cluster terminated before task completion",
        "recent_incidents": [
            {
                "run_id": "98765",
                "severity": "high",
                "event_type": "job_failure",
                "event_timestamp": "2026-03-30T10:15:00Z",
                "summary": "Cluster terminated before task completion",
            },
            {
                "run_id": "98760",
                "severity": "medium",
                "event_type": "retry_succeeded",
                "event_timestamp": "2026-03-29T08:00:00Z",
                "summary": "Pipeline recovered after retry",
            },
        ],
    },
    {
        "job_id": "67890",
        "job_name": "finance_invoices_pipeline",
        "status": "active",
        "latest_status": "success",
        "latest_error_summary": None,
        "recent_incidents": [],
    },
]
