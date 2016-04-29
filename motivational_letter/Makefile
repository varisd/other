SHELL=bash
.PHONY: all
all: letter.pdf

letter.pdf paper.pdf article.pdf: varis.bib


LATEX=pdflatex

%.pdf: %.tex
	$(LATEX) $<
#	bibtex $* || ( echo "Bibtex failed" && exit 1 )
#	lim=4; \
#    while [ $$lim -ge 0 ] \
        && grep 'Rerun to get cross-references right.\|Citation.*undefined' $*.log >/dev/null 2>/dev/null; do \
      $(LATEX) $< ; \
      lim=$$(($$lim - 1)) ; \
    done
#	$(LATEX) $<

clean:
	rm -f {letter,cv_7,article,abstract,paper}.{log,aux,bbl,blg,pdf}

