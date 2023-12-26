freeze:
	pip freeze --local > requirements.txt

install:
	pip install -r requirements.txt

type_check:
	mypy src

test:
	python -m unittest discover ./src

run:
	python src/main.py
