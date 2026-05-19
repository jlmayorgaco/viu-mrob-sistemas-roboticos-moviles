.PHONY: all report slides pptx clean

all: report slides pptx

report:
	pdflatex -interaction=nonstopmode -halt-on-error main.tex
	bibtex main
	pdflatex -interaction=nonstopmode -halt-on-error main.tex
	pdflatex -interaction=nonstopmode -halt-on-error main.tex

slides:
	cd slides && pdflatex -interaction=nonstopmode -halt-on-error slides.tex
	cd slides && pdflatex -interaction=nonstopmode -halt-on-error slides.tex

pptx:
	cd slides && node build_editable_pptx.js

clean:
	-del /Q *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot 2>NUL
	-del /Q slides\*.aux slides\*.log slides\*.out slides\*.nav slides\*.snm slides\*.toc 2>NUL
