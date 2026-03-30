from app.api.repositories import job_repository


def test_list_jobs_uses_mock_data_when_databricks_is_not_configured(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return False

        def get_jobs(self):
            return [{"job_id": "999", "job_name": "should_not_be_used"}]

        def get_job_runs(self):
            return []

    monkeypatch.setattr(job_repository, "DatabricksClient", StubDatabricksClient)

    jobs = job_repository.list_jobs()

    assert len(jobs) == 2
    assert jobs[0]["job_id"] == "12345"


def test_list_jobs_uses_databricks_when_configured(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return True

        def get_jobs(self):
            return [
                {
                    "id": 321,
                    "name": "customer_gold_refresh",
                    "active": True,
                }
            ]

        def get_job_runs(self):
            return [
                {
                    "run_id": 9001,
                    "job_id": 321,
                    "result_state": "FAILED",
                    "end_time": "2026-03-30T12:00:00Z",
                    "error_message": "Task failed because source table was unavailable",
                },
                {
                    "run_id": 9000,
                    "job_id": 321,
                    "result_state": "SUCCESS",
                    "end_time": "2026-03-29T12:00:00Z",
                    "summary": "Previous run completed successfully",
                },
            ]

    monkeypatch.setattr(job_repository, "DatabricksClient", StubDatabricksClient)

    jobs = job_repository.list_jobs()

    assert jobs == [
        {
            "id": 321,
            "name": "customer_gold_refresh",
            "active": True,
            "job_id": "321",
            "job_name": "customer_gold_refresh",
            "status": "active",
            "latest_status": "failed",
            "latest_error_summary": "Task failed because source table was unavailable",
            "recent_incidents": [
                {
                    "run_id": "9001",
                    "severity": "high",
                    "event_type": "job_failure",
                    "event_timestamp": "2026-03-30T12:00:00Z",
                    "summary": "Task failed because source table was unavailable",
                },
                {
                    "run_id": "9000",
                    "severity": "low",
                    "event_type": "job_success",
                    "event_timestamp": "2026-03-29T12:00:00Z",
                    "summary": "Previous run completed successfully",
                },
            ],
        }
    ]


def test_find_job_by_id_reads_from_databricks_when_configured(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return True

        def get_jobs(self):
            return [
                {
                    "job_id": "777",
                    "job_name": "silver_orders_pipeline",
                    "status": "inactive",
                }
            ]

        def get_job_runs(self):
            return []

    monkeypatch.setattr(job_repository, "DatabricksClient", StubDatabricksClient)

    job = job_repository.find_job_by_id("777")

    assert job is not None
    assert job["job_name"] == "silver_orders_pipeline"
