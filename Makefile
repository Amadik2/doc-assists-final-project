.PHONY: setup index serve ui test

setup:
	python3 -m pip install -r requirements.txt
	python -m spacy download en_core_web_sm
	python -c "import nltk; nltk.download('stopwords')"

index:
	python scripts/build_index.py --config configs/build_index.yaml

serve:
	uvicorn src.api.app:app --host 0.0.0.0 --port 8080 --workers 2

ui:
	streamlit run src/ui/app.py

test:
	pytest -q
