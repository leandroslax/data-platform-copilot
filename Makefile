run-api:
	uvicorn app.api.main:app --reload

install:
	python3 -m pip install -r requirements.txt
