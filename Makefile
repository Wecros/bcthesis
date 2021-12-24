LATEX_DIR := ./latex

.PHONY: latex

latex:
	$(MAKE) -C $(LATEX_DIR)
	mv $(LATEX_DIR)/projekt.pdf .

clean:
	$(MAKE) clean -C $(LATEX_DIR)
