.PHONY: setup test run-signal run-live backtest clean monitor install

setup:
	python3.10 -m venv venv
	source venv/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	@echo "✅ Setup complete! Edit .env with API keys"

test:
	source venv/bin/activate && python -m pytest tests/ -v

run-signal:
	source venv/bin/activate && python src/main.py --mode signalonly

run-live:
	source venv/bin/activate && python src/main.py --mode livetrade

backtest:
	source venv/bin/activate && ./scripts/backtest.sh 2024-11-01 2024-12-01

clean:
	rm -rf venv/ __pycache__/ .pytest_cache/ logs/* data/* reports/*

monitor:
	tail -f logs/app.log

install:
	source venv/bin/activate && pip install -e .
