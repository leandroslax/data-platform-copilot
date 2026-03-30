from app.api.schemas.chat import ChatResponse, ChatSource
from app.api.services.dataset_service import get_dataset
from app.api.services.job_service import get_job_incidents
from app.api.services.lineage_service import get_lineage


def answer_question(question: str) -> ChatResponse:
    normalized_question = question.lower()

    if "orders" in normalized_question or "main.sales.orders" in normalized_question:
        dataset = get_dataset("main.sales.orders")
        lineage = get_lineage("main.sales.orders")

        return ChatResponse(
            answer=(
                f"O dataset {dataset.dataset_id} pertence ao owner "
                f"{dataset.owner}. Ele possui {len(lineage.upstream)} dependências "
                f"upstream e {len(lineage.downstream)} dependências downstream."
            ),
            sources=[
                ChatSource(
                    type="dataset",
                    id=dataset.dataset_id,
                    label="Metadados do dataset",
                ),
                ChatSource(
                    type="lineage",
                    id=dataset.dataset_id,
                    label="Resumo de lineage",
                ),
            ],
        )

    if "invoice" in normalized_question or "invoices" in normalized_question:
        dataset = get_dataset("main.finance.invoices")
        lineage = get_lineage("main.finance.invoices")

        return ChatResponse(
            answer=(
                f"O dataset {dataset.dataset_id} pertence ao owner "
                f"{dataset.owner}. Ele possui {len(lineage.upstream)} dependência "
                f"upstream e {len(lineage.downstream)} dependência downstream."
            ),
            sources=[
                ChatSource(
                    type="dataset",
                    id=dataset.dataset_id,
                    label="Metadados do dataset",
                ),
                ChatSource(
                    type="lineage",
                    id=dataset.dataset_id,
                    label="Resumo de lineage",
                ),
            ],
        )

    if "job" in normalized_question or "pipeline" in normalized_question:
        incident = get_job_incidents("12345")

        return ChatResponse(
            answer=(
                f"O job {incident.job_name} está com status mais recente "
                f"'{incident.latest_status}'. O último erro identificado foi: "
                f"{incident.latest_error_summary}."
            ),
            sources=[
                ChatSource(
                    type="job",
                    id=incident.job_id,
                    label="Metadados do job",
                ),
                ChatSource(
                    type="incident",
                    id=incident.job_id,
                    label="Resumo de incidentes",
                ),
            ],
        )

    return ChatResponse(
        answer=(
            "Ainda não encontrei contexto suficiente para responder com confiança. "
            "Tente perguntar sobre datasets, lineage ou jobs específicos do MVP."
        ),
        sources=[],
    )
