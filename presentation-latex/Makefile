CO=prezentace

all: $(CO).pdf

%.pdf: %.tex
	pdflatex $<
	pdflatex $<

clean:
	rm -f *.dvi *.log $(CO).blg $(CO).bbl $(CO).toc *.aux $(CO).out $(CO).lof $(CO).ptc $(CO).nav $(CO).snm
	rm -f $(CO).pdf
	rm -f *~
