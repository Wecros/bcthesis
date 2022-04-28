THESIS_DIR := ./text
THESIS_FILE := xfilip46-thesis.pdf
PRESENTATION_DIR := ./presentation
PRESENTATION_FILE := xfilip46-thesis-presentation.pdf
CONTAINER_NAME = backtester-dev

.PHONY: clean create-venv docker-build docker-detached-exec docker-detached-up docker-down docker-up format git installdeps latex lint presentation run test text thesis

help:
	@make -pRrq  -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

run:
	python -m backtester -f ./backtester/args.yaml

test:
	python -m pytest tests

create-venv:
	virtualenv -p python3.9 venv

installdeps:
	pip install -r requirements.txt

docker-build:
	docker-compose build

docker-up:
	docker-compose up

docker-detached-up:
	docker-compose up -d

docker-detached-exec:
	docker exec -it $(CONTAINER_NAME) bash

docker-down:
	docker-compose down

git: text presentation clean
	git add $(THESIS_FILE) $(PRESENTATION_FILE)

latex: text presentation

text:
	$(MAKE) -C $(THESIS_DIR)
	mv $(THESIS_DIR)/$(THESIS_FILE) .

presentation:
	$(MAKE) -C $(PRESENTATION_DIR)
	mv $(PRESENTATION_DIR)/$(PRESENTATION_FILE) .

clean:
	$(MAKE) clean -C $(THESIS_DIR)
	$(MAKE) clean -C $(PRESENTATION_DIR)

format:
	fd '^.*\.py$$' | xargs black
	fd '^.*\.py$$' | xargs autoflake --in-place --remove-unused-variables --imports=pandas,numpy,vectorbt,yaml,binance,decouple,plotly,schema,requests,yaml,pytest,kaleido,$(shell fd '^.*\.py' --exec basename {} .py | tr '\n' ',')
	fd '^.*\.py$$' | xargs isort

lint:
	fd '^.*\.py$$' | xargs black --check
	fd '^.*\.py$$' | xargs isort --check
	fd '^.*\.py$$' | xargs flake8
	# fd '^.*\.py$$' | xargs pylint
