THESIS_DIR := ./text-latex
THESIS_FILE := xfilip46-thesis
PRESENTATION_DIR := ./presentation-latex
PRESENTATION_FILE := xfilip46-thesis-presentation

.PHONY: latex

all: thesis presentation

thesis:
	$(MAKE) -C $(THESIS_DIR)
	mv $(THESIS_DIR)/$(THESIS_FILE).pdf .

presentation:
	$(MAKE) -C $(PRESENTATION_DIR)
	mv $(PRESENTATION_DIR)/$(PRESENTATION_FILE).pdf .

clean:
	$(MAKE) clean -C $(THESIS_DIR)
	$(MAKE) clean -C $(PRESENTATION_DIR)
