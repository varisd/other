all: thesis.pdf

#thesis.pdf: thesis.ps
#	ps2pdf $< $@

#thesis.ps: thesis.dvi
#	dvips -o $@ -D600 -t a4 $<

LATEX=pdflatex

#thesis.pdf: thesis.tex $(wildcard *.tex)
#%.pdf: %.tex
%.pdf: %.tex $(wildcard *.tex)
	$(LATEX) $<
	bibtex $* || ( echo "Bibtex failed" && exit 1 )
	lim=4; \
        while [ $$lim -ge 0 ] \
        && grep 'Rerun to get cross-references right.\|Citation.*undefined' $*.log >/dev/null 2>/dev/null; do \
      $(LATEX) $< ; \
      lim=$$(($$lim - 1)) ; \
	done
	$(LATEX) $<


# LaTeX must be run multiple times to get references right
#thesis.pdf: thesis.tex $(wildcard *.tex)
#	pdflatex $<
#	bibtex thesis
#	pdflatex $<
#	pdflatex $<

clean:
	rm -f *.log *.dvi *.aux *.toc *.lof *.lot *.out *.bbl *.blg
	rm -f thesis.pdf
