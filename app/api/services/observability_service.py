import logging
import threading
import time
from typing import Any, Dict

from prometheus_client import Gauge

from app.api.clients.bigquery_client import BigQueryClient
from app.api.core.config import settings

logger = logging.getLogger(__name__)

_LOCK = threading.Lock()
_LAST_REFRESH = 0.0

_silver_row_count = Gauge(
    "novadrive_silver_vendas_row_count",
    "Row count for silver_novadrive.vendas",
)
_silver_latest_ingested_at = Gauge(
    "novadrive_silver_vendas_latest_ingested_at_seconds",
    "Latest ingested_at timestamp in silver_novadrive.vendas as Unix seconds",
)
_silver_latest_sale_at = Gauge(
    "novadrive_silver_vendas_latest_sale_at_seconds",
    "Latest data_venda timestamp in silver_novadrive.vendas as Unix seconds",
)
_silver_distinct_sales_count = Gauge(
    "novadrive_silver_vendas_distinct_sales_count",
    "Distinct sales count in silver_novadrive.vendas",
)
_silver_duplicate_rows_count = Gauge(
    "novadrive_silver_vendas_duplicate_rows_count",
    "Duplicate row count in silver_novadrive.vendas",
)
_silver_duplicate_rate = Gauge(
    "novadrive_silver_vendas_duplicate_rate",
    "Duplicate row rate in silver_novadrive.vendas",
)
_silver_daily_sales_count = Gauge(
    "novadrive_silver_daily_sales_count",
    "Daily sales count for silver_novadrive.vendas",
    labelnames=("sale_date",),
)
_silver_daily_revenue = Gauge(
    "novadrive_silver_daily_revenue",
    "Daily revenue for silver_novadrive.vendas",
    labelnames=("sale_date",),
)
_silver_daily_ticket_medio = Gauge(
    "novadrive_silver_daily_ticket_medio",
    "Daily average ticket for silver_novadrive.vendas",
    labelnames=("sale_date",),
)

_gold_concessionarias_row_count = Gauge(
    "novadrive_gold_concessionarias_row_count",
    "Row count for gold_novadrive.faturamento_por_concessionaria",
)
_gold_concessionarias_total_revenue = Gauge(
    "novadrive_gold_concessionarias_total_revenue",
    "Total revenue summed from gold_novadrive.faturamento_por_concessionaria",
)
_gold_concessionarias_latest_sale_at = Gauge(
    "novadrive_gold_concessionarias_latest_sale_at_seconds",
    "Latest ultima_venda timestamp in gold_novadrive.faturamento_por_concessionaria as Unix seconds",
)

_gold_vendedores_row_count = Gauge(
    "novadrive_gold_vendedores_row_count",
    "Row count for gold_novadrive.performance_vendedores",
)
_gold_vendedores_total_revenue = Gauge(
    "novadrive_gold_vendedores_total_revenue",
    "Total revenue summed from gold_novadrive.performance_vendedores",
)
_gold_vendedores_latest_sale_at = Gauge(
    "novadrive_gold_vendedores_latest_sale_at_seconds",
    "Latest ultima_venda timestamp in gold_novadrive.performance_vendedores as Unix seconds",
)
_gold_top_concessionarias_revenue = Gauge(
    "novadrive_gold_top_concessionarias_revenue",
    "Top dealership revenue values from gold_novadrive.faturamento_por_concessionaria",
    labelnames=("rank", "concessionaria", "cidade", "sigla_estado"),
)
_gold_top_vendedores_revenue = Gauge(
    "novadrive_gold_top_vendedores_revenue",
    "Top seller revenue values from gold_novadrive.performance_vendedores",
    labelnames=("rank", "vendedor_nome", "concessionaria", "sigla_estado"),
)
_gold_state_revenue = Gauge(
    "novadrive_gold_state_revenue",
    "Revenue by state from gold_novadrive marts",
    labelnames=("sigla_estado", "estado"),
)
_gold_top_cities_revenue = Gauge(
    "novadrive_gold_top_cities_revenue",
    "Top city revenue values from gold_novadrive.faturamento_por_concessionaria",
    labelnames=("rank", "cidade", "sigla_estado"),
)
_gold_top_concessionarias_ticket_medio = Gauge(
    "novadrive_gold_top_concessionarias_ticket_medio",
    "Ticket medio values for top dealerships from gold_novadrive.faturamento_por_concessionaria",
    labelnames=("rank", "concessionaria", "sigla_estado"),
)

_metrics_refresh_timestamp = Gauge(
    "novadrive_metrics_refresh_timestamp_seconds",
    "Timestamp of the latest successful Novadrive metrics refresh",
)


def _set_if_present(gauge: Gauge, payload: Dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if value is None:
        return
    gauge.set(float(value))


def _short_dealership_name(name: str | None) -> str:
    if not name:
        return "Unknown"
    shortened = name.replace("Concessionária NovaDrive Motors ", "").strip()
    return shortened or name


def _refresh_novadrive_metrics() -> None:
    client = BigQueryClient()

    silver = client.query(
        f"""
        SELECT
          COUNT(*) AS row_count,
          COUNT(DISTINCT id_vendas) AS distinct_sales_count,
          COUNT(*) - COUNT(DISTINCT id_vendas) AS duplicate_rows_count,
          SAFE_DIVIDE(COUNT(*) - COUNT(DISTINCT id_vendas), COUNT(*)) AS duplicate_rate,
          UNIX_SECONDS(MAX(TIMESTAMP(ingested_at))) AS latest_ingested_at_seconds,
          UNIX_SECONDS(MAX(TIMESTAMP(data_venda))) AS latest_sale_at_seconds
        FROM `{settings.bigquery_project_id}.{settings.novadrive_silver_dataset}.vendas`
        """
    )[0]
    silver_daily = client.query(
        f"""
        SELECT
          CAST(DATE(data_venda) AS STRING) AS sale_date,
          COUNT(*) AS sales_count,
          SUM(valor_pago) AS revenue,
          AVG(valor_pago) AS ticket_medio
        FROM `{settings.bigquery_project_id}.{settings.novadrive_silver_dataset}.vendas`
        GROUP BY sale_date
        ORDER BY sale_date DESC
        LIMIT 14
        """
    )

    gold_concessionarias = client.query(
        f"""
        SELECT
          COUNT(*) AS row_count,
          SUM(faturamento_total) AS total_revenue,
          UNIX_SECONDS(MAX(TIMESTAMP(ultima_venda))) AS latest_sale_at_seconds
        FROM `{settings.bigquery_project_id}.{settings.novadrive_gold_dataset}.faturamento_por_concessionaria`
        """
    )[0]

    gold_vendedores = client.query(
        f"""
        SELECT
          COUNT(*) AS row_count,
          SUM(faturamento_total) AS total_revenue,
          UNIX_SECONDS(MAX(TIMESTAMP(ultima_venda))) AS latest_sale_at_seconds
        FROM `{settings.bigquery_project_id}.{settings.novadrive_gold_dataset}.performance_vendedores`
        """
    )[0]
    top_concessionarias = client.query(
        f"""
        SELECT
          concessionaria,
          cidade,
          sigla_estado,
          faturamento_total
        FROM `{settings.bigquery_project_id}.{settings.novadrive_gold_dataset}.faturamento_por_concessionaria`
        ORDER BY faturamento_total DESC
        LIMIT 5
        """
    )
    state_revenue = client.query(
        f"""
        SELECT
          sigla_estado,
          estado,
          SUM(faturamento_total) AS total_revenue
        FROM `{settings.bigquery_project_id}.{settings.novadrive_gold_dataset}.faturamento_por_concessionaria`
        GROUP BY sigla_estado, estado
        ORDER BY total_revenue DESC
        """
    )
    top_cities = client.query(
        f"""
        SELECT
          cidade,
          sigla_estado,
          SUM(faturamento_total) AS total_revenue
        FROM `{settings.bigquery_project_id}.{settings.novadrive_gold_dataset}.faturamento_por_concessionaria`
        GROUP BY cidade, sigla_estado
        ORDER BY total_revenue DESC
        LIMIT 10
        """
    )
    top_concessionarias_ticket = client.query(
        f"""
        SELECT
          concessionaria,
          sigla_estado,
          ticket_medio
        FROM `{settings.bigquery_project_id}.{settings.novadrive_gold_dataset}.faturamento_por_concessionaria`
        ORDER BY faturamento_total DESC
        LIMIT 5
        """
    )
    top_vendedores = client.query(
        f"""
        SELECT
          vendedor_nome,
          concessionaria,
          sigla_estado,
          faturamento_total
        FROM `{settings.bigquery_project_id}.{settings.novadrive_gold_dataset}.performance_vendedores`
        ORDER BY faturamento_total DESC
        LIMIT 5
        """
    )

    _set_if_present(_silver_row_count, silver, "row_count")
    _set_if_present(_silver_distinct_sales_count, silver, "distinct_sales_count")
    _set_if_present(_silver_duplicate_rows_count, silver, "duplicate_rows_count")
    _set_if_present(_silver_duplicate_rate, silver, "duplicate_rate")
    _set_if_present(_silver_latest_ingested_at, silver, "latest_ingested_at_seconds")
    _set_if_present(_silver_latest_sale_at, silver, "latest_sale_at_seconds")

    _silver_daily_sales_count.clear()
    _silver_daily_revenue.clear()
    _silver_daily_ticket_medio.clear()
    for item in silver_daily:
        sale_date = str(item.get("sale_date") or "unknown")
        if item.get("sales_count") is not None:
            _silver_daily_sales_count.labels(sale_date=sale_date).set(float(item["sales_count"]))
        if item.get("revenue") is not None:
            _silver_daily_revenue.labels(sale_date=sale_date).set(float(item["revenue"]))
        if item.get("ticket_medio") is not None:
            _silver_daily_ticket_medio.labels(sale_date=sale_date).set(float(item["ticket_medio"]))

    _set_if_present(_gold_concessionarias_row_count, gold_concessionarias, "row_count")
    _set_if_present(_gold_concessionarias_total_revenue, gold_concessionarias, "total_revenue")
    _set_if_present(
        _gold_concessionarias_latest_sale_at,
        gold_concessionarias,
        "latest_sale_at_seconds",
    )

    _set_if_present(_gold_vendedores_row_count, gold_vendedores, "row_count")
    _set_if_present(_gold_vendedores_total_revenue, gold_vendedores, "total_revenue")
    _set_if_present(_gold_vendedores_latest_sale_at, gold_vendedores, "latest_sale_at_seconds")

    _gold_top_concessionarias_revenue.clear()
    for index, item in enumerate(top_concessionarias, start=1):
        revenue = item.get("faturamento_total")
        if revenue is None:
            continue
        _gold_top_concessionarias_revenue.labels(
            rank=str(index),
            concessionaria=_short_dealership_name(item.get("concessionaria")),
            cidade=str(item.get("cidade") or "Unknown"),
            sigla_estado=str(item.get("sigla_estado") or "NA"),
        ).set(float(revenue))

    _gold_state_revenue.clear()
    for item in state_revenue:
        revenue = item.get("total_revenue")
        if revenue is None:
            continue
        _gold_state_revenue.labels(
            sigla_estado=str(item.get("sigla_estado") or "NA"),
            estado=str(item.get("estado") or "Unknown"),
        ).set(float(revenue))

    _gold_top_cities_revenue.clear()
    for index, item in enumerate(top_cities, start=1):
        revenue = item.get("total_revenue")
        if revenue is None:
            continue
        _gold_top_cities_revenue.labels(
            rank=str(index),
            cidade=str(item.get("cidade") or "Unknown"),
            sigla_estado=str(item.get("sigla_estado") or "NA"),
        ).set(float(revenue))

    _gold_top_concessionarias_ticket_medio.clear()
    for index, item in enumerate(top_concessionarias_ticket, start=1):
        ticket_medio = item.get("ticket_medio")
        if ticket_medio is None:
            continue
        _gold_top_concessionarias_ticket_medio.labels(
            rank=str(index),
            concessionaria=_short_dealership_name(item.get("concessionaria")),
            sigla_estado=str(item.get("sigla_estado") or "NA"),
        ).set(float(ticket_medio))

    _gold_top_vendedores_revenue.clear()
    for index, item in enumerate(top_vendedores, start=1):
        revenue = item.get("faturamento_total")
        if revenue is None:
            continue
        _gold_top_vendedores_revenue.labels(
            rank=str(index),
            vendedor_nome=str(item.get("vendedor_nome") or "Unknown"),
            concessionaria=str(item.get("concessionaria") or "Unknown"),
            sigla_estado=str(item.get("sigla_estado") or "NA"),
        ).set(float(revenue))

    _metrics_refresh_timestamp.set(time.time())


def refresh_observability_metrics_if_needed() -> None:
    global _LAST_REFRESH

    if time.time() - _LAST_REFRESH < settings.novadrive_metrics_ttl_seconds:
        return

    with _LOCK:
        if time.time() - _LAST_REFRESH < settings.novadrive_metrics_ttl_seconds:
            return

        try:
            _refresh_novadrive_metrics()
            _LAST_REFRESH = time.time()
        except Exception as exc:  # pragma: no cover - defensive metrics path
            logger.warning("Failed to refresh Novadrive observability metrics: %s", exc)
