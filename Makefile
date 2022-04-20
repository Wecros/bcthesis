THESIS_DIR := ./text-latex
THESIS_FILE := xfilip46-thesis
PRESENTATION_DIR := ./presentation-latex
PRESENTATION_FILE := xfilip46-thesis-presentation
SRC_DIR := src/

.PHONY: latex

git: thesis presentation clean

latex: thesis presentation

thesis:
	$(MAKE) -C $(THESIS_DIR)
	mv $(THESIS_DIR)/$(THESIS_FILE).pdf .

presentation:
	$(MAKE) -C $(PRESENTATION_DIR)
	mv $(PRESENTATION_DIR)/$(PRESENTATION_FILE).pdf .

clean:
	$(MAKE) clean -C $(THESIS_DIR)
	$(MAKE) clean -C $(PRESENTATION_DIR)

format:
	fd '^.*\.py$$' | xargs black
	fd '^.*\.py$$' | xargs autoflake --in-place --remove-unused-variables --imports=pandas,numpy,vectorbt,yaml,binance,decouple,plotly,$(shell fd '^.*\.py' --exec basename {} .py | tr '\n' ',')
	fd '^.*\.py$$' | xargs isort

lint:
	fd '^.*\.py$$' | xargs black --check
	fd '^.*\.py$$' | xargs isort --check
	fd '^.*\.py$$' | xargs flake8
	# fd '^.*\.py$$' | xargs pylint
