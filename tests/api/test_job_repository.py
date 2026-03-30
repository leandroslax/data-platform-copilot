from app.api.repositories import job_repository


def test_list_jobs_uses_mock_data_when_databricks_is_not_configured(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return False

        def get_jobs(self):
            return [
                {
                    "job_id": "should-not-appear",
                    "job_name": "unexpected",
                }
            ]

        def get_job_runs(self):
            return []

    monkeypatch.setattr(job_repository, "DatabricksClient", StubDatabricksClient)

    jobs = job_repository.list_jobs()

    assert len(jobs) == 2
    assert jobs[0]["job_id"] == "12345"


def test_list_jobs_falls_back_to_mock_when_databricks_has_no_jobs(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return True

        def get_jobs(self):
            return []

        def get_job_runs(self):
            return []

    monkeypatch.setattr(job_repository, "DatabricksClient", StubDatabricksClient)

    jobs = job_repository.list_jobs()

    assert len(jobs) == 2
    assert jobs[0]["job_id"] == "12345"


def test_list_jobs_uses_databricks_when_jobs_exist(monkeypatch) -> None:
    class StubDatabricksClient:
        def is_configured(self) -> bool:
            return True

        def get_jobs(self):
            return [
                {
                    "job_id": "999",
                    "job_name": "daily_ingestion",
                    "status": "active",
                }
            ]

        def get_job_runs(self):
            return [
                {
                    "run_id": "run-1",
                    "job_id": "999",
                    "result_state": "FAILED",
                    "state_message": "Task failed",
                    "end_time": "1711793100000",
                }
            ]

    monkeypatch.setattr(job_repository, "DatabricksClient", StubDatabricksClient)

    jobs = job_repository.list_jobs()

    assert jobs == [
        {
            "job_id": "999",
            "job_name": "daily_ingestion",
            "status": "active",
            "latest_status": "failed",
            "latest_error_summary": "Task failed",
            "recent_incidents": [
                {
                    "run_id": "run-1",
                    "severity": "high",
                    "event_type": "job_failure",
                    "event_timestamp": "1711793100000",
                    "summary": "Task failed",
                }
            ],
        }
    ]
