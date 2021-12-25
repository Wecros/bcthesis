THESIS_DIR := ./text-latex
PRESENTATION_DIR := ./presentation-latex

.PHONY: latex

all: thesis presentation

thesis:
	$(MAKE) -C $(THESIS_DIR)
	mv $(THESIS_DIR)/projekt.pdf ./thesis.pdf

presentation:
	$(MAKE) -C $(PRESENTATION_DIR)
	mv $(PRESENTATION_DIR)/prezentace.pdf ./thesis-presentation.pdf

clean:
	$(MAKE) clean -C $(THESIS_DIR)
	$(MAKE) clean -C $(PRESENTATION_DIR)
