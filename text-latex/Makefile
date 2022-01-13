# makefile pro preklad LaTeX verze Bc. prace
# makefile for compilation of the thesis
# (c) 2008 Michal Bidlo
# E-mail: bidlom AT fit vutbr cz
# Edited by: dytrych AT fit vutbr cz
#===========================================
# asi budete chtit prejmenovat / xfilip46-thesisu will probably rename:
CO=xfilip46-thesis

all: $(CO).pdf

pdf: $(CO).pdf

$(CO).ps: $(CO).dvi
	dvips $(CO)

#$(CO).pdf: clean
	#pdflatex $(CO)
	#-bibtex $(CO)
	#pdflatex $(CO)
	#pdflatex $(CO)

$(CO).pdf: clean
	pdflatex -halt-on-error $(CO)
	-bibtex $(CO)
	pdflatex -halt-on-error $(CO)
	pdflatex -halt-on-error $(CO)

$(CO).dvi: $(CO).tex $(CO).bib
	latex $(CO)
	-bibtex $(CO)
	latex $(CO)
	latex $(CO)

clean:
	rm -f *.dvi *.log $(CO).blg $(CO).bbl $(CO).toc *.aux $(CO).out $(CO).lof $(CO).ptc
	rm -f $(CO).pdf
	rm -f *~

pack:
	tar czvf $(CO).tar.gz *.tex *.bib *.bst ./template-fig/* ./bib-styles/* ./cls/* zadani.pdf $(CO).pdf Makefile Changelog

rename:
	mv $(CO).tex $(NAME).tex
	mv $(CO)-01-chapters.tex $(NAME)-01-chapters.tex
	mv $(CO)-20-bibliography.bib $(NAME)-20-bibliography.bib
	mv $(CO)-30-appendices.tex $(NAME)-30-appendices.tex
	sed -i "s/$(CO)-01-chapters/$(NAME)-01-chapters/g" $(NAME).tex
	sed -i "s/$(CO)-20-bibliography/$(NAME)-20-bibliography/g" $(NAME).tex
	sed -i "s/$(CO)-30-appendices/$(NAME)-30-appendices/g" $(NAME).tex
	sed -i "s/$(CO)/$(NAME)/g" Makefile
	
# Pozor, vlna neresi vse (viz popis.txt) / Warning - vlna is not solving all problems (see description.txt)
vlna:
	vlna -l $(CO)-*.tex

# Spocita normostrany / Count of standard pages
normostrany:
	echo "scale=2; `detex -n $(CO)-[01]*.tex | sed s/"^ *"/""/ | sed s/"^	*"/""/ | wc -c`/1800;" | bc
