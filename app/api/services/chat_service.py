import re
import unicodedata
from typing import Iterable, Optional

from app.api.repositories.dataset_repository import list_datasets as list_dataset_records
from app.api.repositories.job_repository import list_jobs as list_job_records
from app.api.schemas.chat import ChatResponse, ChatSource
from app.api.services.dataset_service import get_dataset
from app.api.services.job_service import get_job_incidents
from app.api.services.lineage_service import get_lineage
from app.api.services.llm_service import synthesize_grounded_answer
from app.api.services.novadrive_service import (
    list_faturamento_por_concessionaria,
    list_performance_vendedores,
)
from app.api.services.retrieval_service import search_catalog, summarize_owners

STOPWORDS = {
    "a",
    "ao",
    "as",
    "coluna",
    "colunas",
    "com",
    "concessionaria",
    "concessionarias",
    "da",
    "das",
    "dataset",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "existe",
    "existem",
    "faturamento",
    "job",
    "o",
    "os",
    "owner",
    "owners",
    "pipeline",
    "qual",
    "quais",
    "quem",
    "responsavel",
    "schema",
    "ticket",
    "vendedor",
    "vendedores",
    "vendeu",
    "venderam",
    "vendas",
}

DATASET_ID_PATTERN = re.compile(r"\b[a-z0-9_][a-z0-9_-]*\.[a-z0-9_]+\.[a-z0-9_]+\b")


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9_]+", _normalize_text(text))
        if len(token) > 1 and token not in STOPWORDS
    }


def _pick_best_match(records: Iterable[dict], question: str, id_key: str, name_key: str) -> Optional[dict]:
    normalized_question = _normalize_text(question)
    tokens = _tokenize(question)
    best_match = None
    best_score = 0

    for record in records:
        record_id = str(record.get(id_key, "")).lower()
        record_name = str(record.get(name_key, "")).lower()
        score = 0

        if record_id and record_id in normalized_question:
            score += 100

        if record_name and record_name in normalized_question:
            score += 40

        record_tokens = _tokenize(record_id.replace(".", " ") + " " + record_name.replace("_", " "))
        score += len(tokens.intersection(record_tokens)) * 5

        if score > best_score:
            best_score = score
            best_match = record

    return best_match if best_score > 0 else None


def _resolve_dataset(question: str):
    explicit_match = DATASET_ID_PATTERN.search(_normalize_text(question))
    if explicit_match:
        return get_dataset(explicit_match.group(0))

    dataset_records = list_dataset_records()
    matched_dataset = _pick_best_match(dataset_records, question, "dataset_id", "name")
    if matched_dataset:
        return get_dataset(matched_dataset["dataset_id"])

    return None


def _resolve_job(question: str):
    job_records = list_job_records()
    matched_job = _pick_best_match(job_records, question, "job_id", "job_name")
    if matched_job:
        return get_job_incidents(matched_job["job_id"])

    return None


def _answers_about_columns(question: str) -> bool:
    normalized_question = _normalize_text(question)
    return any(keyword in normalized_question for keyword in {"coluna", "colunas", "columns", "schema"})


def _answers_about_lineage(question: str) -> bool:
    normalized_question = _normalize_text(question)
    return any(
        keyword in normalized_question
        for keyword in {"lineage", "upstream", "upstreams", "downstream", "dependencia", "dependencias"}
    )


def _answers_about_owner(question: str) -> bool:
    normalized_question = _normalize_text(question)
    return any(keyword in normalized_question for keyword in {"owner", "dono", "responsavel"})


def _answers_about_environment(question: str) -> bool:
    normalized_question = _normalize_text(question)
    return any(
        keyword in normalized_question
        for keyword in {
            "ambiente",
            "catalogo",
            "catalog",
            "datasets",
            "metadados",
            "metadata",
            "owner",
            "owners",
        }
    )


def _answers_about_job(question: str) -> bool:
    normalized_question = _normalize_text(question)
    return any(
        keyword in normalized_question
        for keyword in {"job", "pipeline", "erro", "error", "incidente", "incident", "status"}
    )


def _answers_about_novadrive(question: str) -> bool:
    normalized_question = _normalize_text(question)
    return any(
        keyword in normalized_question
        for keyword in {
            "concessionaria",
            "concessionarias",
            "faturamento",
            "vendedor",
            "vendedores",
            "ticket medio",
            "ticket",
            "novadrive",
            "melhor vendedor",
            "mais faturou",
            "performance",
        }
    )


def _answer_novadrive_question(question: str) -> Optional[ChatResponse]:
    normalized_question = _normalize_text(question)

    if "concessionaria" in normalized_question or "concessionarias" in normalized_question:
        ranking = list_faturamento_por_concessionaria(limit=5)
        if not ranking.items:
            return None

        top = ranking.items[0]
        return ChatResponse(
            answer=(
                f"A concessionaria com maior faturamento e {top.concessionaria}, em {top.cidade}-{top.sigla_estado}, "
                f"com faturamento total de {top.faturamento_total:.2f}, {top.total_vendas} vendas e ticket medio de "
                f"{top.ticket_medio:.2f}."
            ),
            sources=[
                ChatSource(
                    type="novadrive_gold",
                    id="faturamento_por_concessionaria",
                    label="Gold Novadrive - faturamento por concessionaria",
                )
            ],
        )

    if "vendedor" in normalized_question or "vendedores" in normalized_question or "performance" in normalized_question:
        ranking = list_performance_vendedores(limit=5)
        if not ranking.items:
            return None

        top = ranking.items[0]
        return ChatResponse(
            answer=(
                f"O vendedor com maior faturamento e {top.vendedor_nome}, da {top.concessionaria}, "
                f"com faturamento total de {top.faturamento_total:.2f}, {top.total_vendas} vendas e ticket medio de "
                f"{top.ticket_medio:.2f}."
            ),
            sources=[
                ChatSource(
                    type="novadrive_gold",
                    id="performance_vendedores",
                    label="Gold Novadrive - performance de vendedores",
                )
            ],
        )

    return None


def _extract_owner_hint(question: str) -> Optional[str]:
    normalized_question = _normalize_text(question)
    patterns = [
        r"owner\s+([a-z0-9_-]+)",
        r"owners\s+([a-z0-9_-]+)",
        r"responsavel\s+([a-z0-9_-]+)",
        r"dono\s+([a-z0-9_-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized_question)
        if match:
            return match.group(1)

    return None


def _build_dataset_sources(datasets: list[dict], limit: int = 5) -> list[ChatSource]:
    return [
        ChatSource(type="dataset", id=dataset["dataset_id"], label="Metadados do dataset")
        for dataset in datasets[:limit]
    ]


def _answer_owner_environment_question(question: str) -> Optional[ChatResponse]:
    normalized_question = _normalize_text(question)

    if "owners" in normalized_question and "quais" in normalized_question:
        owners = summarize_owners()
        if not owners:
            return None

        rendered = ", ".join(f"{item['owner']} ({item['dataset_count']})" for item in owners[:5])
        return ChatResponse(
            answer=f"Os owners com mais datasets catalogados são: {rendered}.",
            sources=[
                ChatSource(type="catalog", id="metadata_catalog", label="Catalogo persistido de metadados")
            ],
        )

    owner_hint = _extract_owner_hint(question)
    if not owner_hint:
        return None

    matching_datasets = [
        dataset
        for dataset in list_dataset_records()
        if owner_hint in _normalize_text(dataset.get("owner") or "")
    ]

    if not matching_datasets:
        return ChatResponse(
            answer=f"Nao encontrei datasets catalogados para o owner {owner_hint}.",
            sources=[ChatSource(type="catalog", id="metadata_catalog", label="Catalogo persistido de metadados")],
        )

    rendered = ", ".join(dataset["dataset_id"] for dataset in matching_datasets[:5])
    extra_count = len(matching_datasets) - min(len(matching_datasets), 5)
    suffix = f" e mais {extra_count}" if extra_count > 0 else ""
    owner_name = matching_datasets[0].get("owner") or owner_hint

    return ChatResponse(
        answer=(
            f"Encontrei {len(matching_datasets)} datasets do owner {owner_name}: "
            f"{rendered}{suffix}."
        ),
        sources=_build_dataset_sources(matching_datasets),
    )


def _answer_from_semantic_retrieval(question: str) -> Optional[ChatResponse]:
    retrieved = [result for result in search_catalog(question) if result["score"] >= 0.18]
    if not retrieved:
        return None

    contexts = [result["dataset"] for result in retrieved]
    grounded_answer = synthesize_grounded_answer(question, contexts)

    if grounded_answer is None:
        rendered = "; ".join(
            (
                f"{result['dataset_id']} (owner {result['dataset'].get('owner') or 'n/a'}"
                f", source {result['dataset'].get('source_system') or 'n/a'})"
            )
            for result in retrieved[:3]
        )
        grounded_answer = f"Os datasets mais relevantes para essa pergunta são: {rendered}."

    return ChatResponse(
        answer=grounded_answer,
        sources=_build_dataset_sources(contexts),
    )


def answer_question(question: str) -> ChatResponse:
    normalized_question = _normalize_text(question)
    explicit_dataset_match = DATASET_ID_PATTERN.search(normalized_question)
    owner_catalog_query = _answers_about_owner(question) and any(
        keyword in normalized_question for keyword in {"datasets", "owners", "ambiente", "catalogo"}
    )

    if _answers_about_novadrive(question) and explicit_dataset_match is None:
        novadrive_response = _answer_novadrive_question(question)
        if novadrive_response is not None:
            return novadrive_response

    if _answers_about_job(question) and explicit_dataset_match is None:
        incident = _resolve_job(question) or get_job_incidents("12345")

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

    if owner_catalog_query and explicit_dataset_match is None:
        owner_response = _answer_owner_environment_question(question)
        if owner_response is not None:
            return owner_response

    dataset = _resolve_dataset(question)
    if dataset is not None:
        lineage = get_lineage(dataset.dataset_id)

        if _answers_about_columns(question):
            if dataset.columns:
                rendered_columns = ", ".join(column.name for column in dataset.columns[:10])
                extra_columns = len(dataset.columns) - min(len(dataset.columns), 10)
                suffix = f" e mais {extra_columns}" if extra_columns > 0 else ""
                answer = (
                    f"O dataset {dataset.dataset_id} possui {len(dataset.columns)} colunas: "
                    f"{rendered_columns}{suffix}."
                )
            else:
                answer = f"Nao encontrei colunas catalogadas para o dataset {dataset.dataset_id}."
        elif _answers_about_lineage(question):
            answer = (
                f"O dataset {dataset.dataset_id} possui {len(lineage.upstream)} upstreams "
                f"e {len(lineage.downstream)} downstreams."
            )
        elif _answers_about_owner(question):
            answer = f"O dataset {dataset.dataset_id} pertence ao owner {dataset.owner}."
        else:
            answer = (
                f"O dataset {dataset.dataset_id} pertence ao owner {dataset.owner}. "
                f"Ele possui {len(lineage.upstream)} dependencias upstream e "
                f"{len(lineage.downstream)} dependencias downstream."
            )

        sources = [
            ChatSource(
                type="dataset",
                id=dataset.dataset_id,
                label="Metadados do dataset",
            )
        ]

        if _answers_about_lineage(question) or not _answers_about_columns(question):
            sources.append(
                ChatSource(
                    type="lineage",
                    id=dataset.dataset_id,
                    label="Resumo de lineage",
                )
            )

        return ChatResponse(
            answer=answer,
            sources=sources,
        )

    if _answers_about_owner(question) and explicit_dataset_match is None:
        owner_response = _answer_owner_environment_question(question)
        if owner_response is not None:
            return owner_response

    if _answers_about_job(question):
        incident = _resolve_job(question) or get_job_incidents("12345")

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

    if _answers_about_environment(question):
        retrieved_response = _answer_from_semantic_retrieval(question)
        if retrieved_response is not None:
            return retrieved_response

    retrieved_response = _answer_from_semantic_retrieval(question)
    if retrieved_response is not None:
        return retrieved_response

    return ChatResponse(
        answer=(
            "Ainda não encontrei contexto suficiente para responder com confiança. "
            "Tente perguntar sobre datasets, lineage, jobs ou indicadores da Novadrive."
        ),
        sources=[],
    )
