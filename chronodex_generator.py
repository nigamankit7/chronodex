"""
Chronodex Planner Generator
---------------------------
Generates a print-ready A4 PDF containing a Chronodex grid for a specified date range.
Uses Python to dynamically build LaTeX/TikZ code and compiles it via pdflatex.
"""

import datetime
import subprocess
import os

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
START_DATE = "2026-03-01"  # Format: YYYY-MM-DD
END_DATE   = "2026-03-31"  # Format: YYYY-MM-DD
FILE_NAME  = "Chronodex_Planner_Final"

# -----------------------------------------------------------------------------
# LaTeX Templates
# -----------------------------------------------------------------------------
LATEX_HEADER = r"""
\documentclass[a4paper]{article}
\usepackage[margin=1cm]{geometry}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{tikz}
\usetikzlibrary{calendar, decorations.text} 

\definecolor{sunLight}{HTML}{FFFCCB}
\definecolor{sunDark}{HTML}{FF6F61}
\definecolor{pal1}{HTML}{FFFCCB}
\definecolor{pal2}{HTML}{FFD59A}
\definecolor{pal3}{HTML}{FF9A7A}
\definecolor{pal4}{HTML}{FF6F61}
\definecolor{pal5}{HTML}{FFA07A}
\definecolor{pal6}{HTML}{A8DDF4}

\newcount\chronodexcurrentdate
\newcount\chronodexcurrentweekday

\tikzset{
    pics/chronodex/.style={
        code={
            \tikzset{chronodex/.cd, #1}
            % Inner segments
            \fill[chronodex/segment 6 to 7 am] (270:3) arc[start angle=270, end angle=240, radius=3] -- (240:2) arc[start angle=240, end angle=270, radius=2] -- cycle;
            \fill[chronodex/segment 7 to 8 am] (240:3) arc[start angle=240, end angle=210, radius=3] -- (210:2) arc[start angle=210, end angle=240, radius=2] -- cycle;
            \fill[chronodex/segment 8 to 9 am] (210:3) arc[start angle=210, end angle=180, radius=3] -- (180:2) arc[start angle=180, end angle=210, radius=2] -- cycle;
            \draw[chronodex/inner ring] (90:2) arc[start angle=90, end angle=-180, radius=2];
            \foreach \i [count=\a from 0] in {90,60,...,-180} {
                \draw[chronodex/inner line] (\i:3) -- (\i:2);
                \pgfmathparse{int(\a > 0 && \a < 7 ? 1 : 0)}
                \ifnum\pgfmathresult=1\relax \node[rotate={\i}, anchor=south east, chronodex/inner label] at (\i:3) {\a\pgfkeysvalueof{/tikz/chronodex/am suffix}}; \fi
                \pgfmathparse{int(\a > 6 && \a < 9 ? 1 : 0)}
                \ifnum\pgfmathresult=1\relax \node[rotate={\i-180}, anchor=south west, chronodex/inner label] at (\i:3) {\a\pgfkeysvalueof{/tikz/chronodex/am suffix}}; \fi
            }
            % Outer segments
            \fill[chronodex/segment 9 to 10 pm] (180:7) arc[start angle=180, end angle=150, radius=7] -- (150:6) arc[start angle=150, end angle=180, radius=6] -- cycle;
            \fill[chronodex/segment 10 to 11 pm] (150:7) arc[start angle=150, end angle=120, radius=7] -- (120:6) arc[start angle=120, end angle=150, radius=6] -- cycle;
            \fill[chronodex/segment 11 pm to 12 am] (120:7) arc[start angle=120, end angle=90, radius=7] -- (90:6) arc[start angle=90, end angle=120, radius=6] -- cycle;
            \draw[chronodex/outer ring] (180:7) arc[start angle=180, end angle=90, radius=7] (90:6) arc[start angle=90, end angle=180, radius=6];
            \foreach \o [count=\p from 0] in {180,150,...,90} {
                \draw[chronodex/outer line] (\o:7) -- (\o:6);
                \ifnum\p<3\relax
                    \pgfmathsetmacro{\h}{int(\p+9+\pgfkeysvalueof{/tikz/chronodex/24 hours conversion})}
                    \node[rotate={\o-180}, anchor=south west, chronodex/outer label] at (\o:7) {\h\pgfkeysvalueof{/tikz/chronodex/pm suffix}};
                \fi
            }
            % Base segments
            \foreach \b [count=\a from 0] in {180,90,...,-90} {
                \draw[chronodex/additional ring] (\b:5) arc[start angle={\b}, end angle={\b-30}, radius=5] (\b:6) arc[start angle={\b}, end angle={\b-60}, radius=6] ({\b-30}:5) -- ({\b-30}:6);
                \fill[chronodex/base segments] (\b:4) arc[start angle={\b}, end angle={\b-30}, radius=4] -- ({\b-30}:5) arc[start angle={\b-30}, end angle={\b-60}, radius=5] -- ({\b-60}:6) arc[start angle={\b-60}, end angle={\b-90}, radius=6] -- ({\b-90}:3) arc[start angle={\b-90}, end angle={\b}, radius=3] -- (\b:3) -- cycle;
                \draw[chronodex/primary ring] (\b:3) -- (\b:4) arc[start angle={\b}, end angle={\b-30}, radius=4] -- ({\b-30}:3);
                \draw[chronodex/primary ring] ({\b-30}:3) -- ({\b-30}:5) arc[start angle={\b-30}, end angle={\b-60}, radius=5] -- ({\b-60}:3);
                \draw[chronodex/secondary ring] ({\b-30}:4) arc[start angle={\b-30}, end angle={\b-60}, radius=4];
                \draw[chronodex/primary ring] ({\b-60}:3) -- ({\b-60}:6) arc[start angle={\b-60}, end angle={\b-90}, radius=6] -- ({\b-90}:3);
                \draw[chronodex/secondary ring] ({\b-60}:4) arc[start angle={\b-60}, end angle={\b-90}, radius=4] ({\b-60}:5) arc[start angle={\b-60}, end angle={\b-90}, radius=5];
                \foreach \n in {7.5,15,22.5} {
                    \foreach \t/\a in {4/0, 5/30, 6/60} {
                        \tikzset{chronodex/tick bottom start={3}}
                        \draw[rotate={\b-\a-\n}, chronodex/primary tick] \pgfkeysvalueof{/tikz/chronodex/tick bottom code};
                        \tikzset{chronodex/tick top start={\t}}
                        \draw[rotate={\b-\a-\n}, chronodex/primary tick] \pgfkeysvalueof{/tikz/chronodex/tick top code};
                    }
                    \tikzset{chronodex/tick middle start={4}}
                    \draw[rotate={\b-30-\n}, chronodex/secondary tick] \pgfkeysvalueof{/tikz/chronodex/tick middle code};
                    \draw[rotate={\b-60-\n}, chronodex/secondary tick] \pgfkeysvalueof{/tikz/chronodex/tick middle code};
                    \tikzset{chronodex/tick middle start={5}}
                    \draw[rotate={\b-60-\n}, chronodex/secondary tick] \pgfkeysvalueof{/tikz/chronodex/tick middle code};
                }
                \ifnum\a=0\relax
                    \node[rotate={\b-180}, anchor=south west, chronodex/base label] at (\b:4) {9\pgfkeysvalueof{/tikz/chronodex/am suffix}};
                    \node[rotate={\b-210}, anchor=south west, chronodex/base label] at ({\b-30}:5) {10\pgfkeysvalueof{/tikz/chronodex/am suffix}};
                    \node[rotate={\b-240}, anchor=south west, chronodex/base label] at ({\b-60}:6) {11\pgfkeysvalueof{/tikz/chronodex/am suffix}};
                    \node[rotate={\b-270}, anchor=south west, chronodex/base label] at ({\b-90}:6) {12\pgfkeysvalueof{/tikz/chronodex/noon suffix}};
                \else
                    \ifnum\a=3\relax
                        \pgfmathsetmacro{\h}{int(\a*3-2+\pgfkeysvalueof{/tikz/chronodex/24 hours conversion})}
                        \node[rotate={\b-210}, anchor=south west, chronodex/base label] at ({\b-30}:5) {\h\pgfkeysvalueof{/tikz/chronodex/pm suffix}};
                        \pgfmathsetmacro{\h}{int(\a*3-1+\pgfkeysvalueof{/tikz/chronodex/24 hours conversion})}
                        \node[rotate={\b-240}, anchor=south west, chronodex/base label] at ({\b-60}:6) {\h\pgfkeysvalueof{/tikz/chronodex/pm suffix}};
                    \else
                        \pgfmathsetmacro{\h}{int(\a*3-2+\pgfkeysvalueof{/tikz/chronodex/24 hours conversion})}
                        \node[rotate={\b-30}, anchor=south east, chronodex/base label] at ({\b-30}:4) {\h\pgfkeysvalueof{/tikz/chronodex/pm suffix}};
                        \pgfmathsetmacro{\h}{int(\a*3-1+\pgfkeysvalueof{/tikz/chronodex/24 hours conversion})}
                        \node[rotate={\b-60}, anchor=south east, chronodex/base label] at ({\b-60}:5) {\h\pgfkeysvalueof{/tikz/chronodex/pm suffix}};
                        \pgfmathsetmacro{\h}{int(\a*3+\pgfkeysvalueof{/tikz/chronodex/24 hours conversion})}
                        \node[rotate={\b-90}, anchor=south east, chronodex/base label] at ({\b-90}:6) {\h\pgfkeysvalueof{/tikz/chronodex/pm suffix}};
                    \fi
                \fi
            }
            \draw[chronodex/base ring] (0:0) circle[radius=3];
            
            \path [decorate, decoration={text along path, text={|\sffamily\bfseries\scriptsize\color{purple}|CHRONODEX}, text align=center}] (180:2.5) arc [start angle=180, end angle=90, radius=2.5];
            
            \ifdefined\chronodexcurrentday
                \pgfmathtruncatemacro{\d}{\chronodexcurrentday.0}
                \node[chronodex/day] at (0,0) {\d};
                \node[chronodex/weekday] at (0,0) {\pgfcalendarweekdayname{\chronodexcurrentweekday}};
            \fi
        }
    },
    chronodex/date/.code={
        \pgfcalendardatetojulian{#1}{\chronodexcurrentdate}
        \pgfcalendarjuliantodate{\chronodexcurrentdate}{\chronodexcurrentyear}{\chronodexcurrentmonth}{\chronodexcurrentday}
        \pgfcalendarjuliantoweekday{\chronodexcurrentdate}{\chronodexcurrentweekday}
    },
    chronodex/date/.initial={},
    chronodex/am suffix/.initial={\,am},
    chronodex/pm suffix/.initial={\,pm},
    chronodex/noon suffix/.initial={\,noon},
    chronodex/24 hours conversion/.initial={0},
    chronodex/24 hours/.style={
        am suffix={:00}, pm suffix={:00}, noon suffix={:00}, 24 hours conversion={12},    
    },
    chronodex/minor tick length/.initial={5},
    chronodex/major tick length/.initial={7},
    chronodex/tick top start/.initial={0},
    chronodex/tick middle start/.initial={0},
    chronodex/tick bottom start/.initial={0},
    chronodex/tick top code/.initial={
        (0:\pgfkeysvalueof{/tikz/chronodex/tick top start}) -- ++(0:{(\n == 15 ? \pgfkeysvalueof{/tikz/chronodex/major tick length} : \pgfkeysvalueof{/tikz/chronodex/minor tick length})*-1pt})
    },
    chronodex/tick middle code/.initial={
        ([shift={(0:{(\n == 15 ? \pgfkeysvalueof{/tikz/chronodex/major tick length} : \pgfkeysvalueof{/tikz/chronodex/minor tick length})*-0.5pt})}]0:\pgfkeysvalueof{/tikz/chronodex/tick middle start}) -- ++(0:{(\n == 15 ? \pgfkeysvalueof{/tikz/chronodex/major tick length} : \pgfkeysvalueof{/tikz/chronodex/minor tick length})*1pt})
    },
    chronodex/tick bottom code/.initial={
        (0:\pgfkeysvalueof{/tikz/chronodex/tick bottom start}) -- ++(0:{(\n == 15 ? \pgfkeysvalueof{/tikz/chronodex/major tick length} : \pgfkeysvalueof{/tikz/chronodex/minor tick length})*1pt})
    },
    chronodex/base ring/.style={thick},
    chronodex/base segments/.style={white!0},
    chronodex/primary ring/.style={thick},
    chronodex/primary tick/.style={},
    chronodex/secondary ring/.style={gray},
    chronodex/secondary tick/.style={},
    chronodex/inner ring/.style={gray, densely dashed},
    chronodex/inner line/.style={gray},
    chronodex/outer ring/.style={gray, densely dashed},
    chronodex/additional ring/.style={gray, densely dotted},
    chronodex/outer line/.style={gray},
    chronodex/label/.style={font=\footnotesize},
    chronodex/base label/.style={chronodex/label},
    chronodex/inner label/.style={chronodex/label, gray},
    chronodex/outer label/.style={chronodex/label, gray},
    chronodex/segment 6 to 7 am/.style={gray!25},
    chronodex/segment 7 to 8 am/.style={gray!15},
    chronodex/segment 8 to 9 am/.style={gray!5},
    chronodex/segment 9 to 10 pm/.style={white!0},
    chronodex/segment 10 to 11 pm/.style={white!0},
    chronodex/segment 11 pm to 12 am/.style={white!0},
    chronodex/day/.style={anchor=south, font=\fontsize{45}{50}\selectfont\bfseries}, 
    chronodex/weekday/.style={anchor=north, font=\fontsize{20}{22}\selectfont}, 
    
    % Core Theme Definition
    chronodex/mytheme/.style={
        24 hours, 
        tick middle code={},
        base ring/.append style={black, thick},
        base segments/.append style={pal6},
        primary ring/.append style={black, thick},
        primary tick/.append style={black, thick},
        secondary tick/.append style={black, thin},
        segment 6 to 7 am/.append style={orange!50},
        segment 7 to 8 am/.append style={orange!30},
        segment 8 to 9 am/.append style={orange!10},
        segment 9 to 10 pm/.append style={teal!50},
        segment 10 to 11 pm/.append style={teal!30},
        segment 11 pm to 12 am/.append style={teal!10},
        label/.append style={text=black, font=\sffamily},
        outer label/.append style={text=black},
        day/.append style={text=purple},
        weekday/.append style={text=teal}
    }
}
"""


def generate_date_list(start_str: str, end_str: str) -> list:
    """Parses date strings and generates a contiguous list of datetime.date objects."""
    start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()
    return [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]


def build_latex_document(dates: list, styling_options: str = "mytheme") -> str:
    """Constructs the full LaTeX document string with the specified chronodex instances."""
    tikz_blocks = ""

    for i, current_date in enumerate(dates):
        date_str = current_date.strftime("%Y-%m-%d")
        month_year_str = current_date.strftime("%b '%y")
        
        # Pagination and vertical alignment for a 2x3 Grid
        if i % 6 == 0:
            if i != 0:
                tikz_blocks += "\\clearpage\n"
            tikz_blocks += "\\vspace*{\\fill}\n\\noindent\n"
            
        # Define layout scope
        tikz_blocks += f"\\begin{{minipage}}[c]{{0.48\\textwidth}}\n"
        tikz_blocks += f"  \\centering\n"
        tikz_blocks += f"  \\begin{{tikzpicture}}[scale=0.45, transform shape]\n" 
        tikz_blocks += f"    \\pic {{chronodex={{date={date_str}, {styling_options}}}}};\n"
        
        # Inject custom nodes (Cutlines and Month/Year annotations)
        tikz_blocks += f"    \\draw[dashed, thin, gray] (0:0) circle[radius=7];\n"
        tikz_blocks += f"    \\node[text=teal, font=\\sffamily\\fontsize{{14}}{{16}}\\selectfont, anchor=north] at (0,-0.9) {{{month_year_str}}};\n"
        
        tikz_blocks += f"  \\end{{tikzpicture}}\n"
        tikz_blocks += f"\\end{{minipage}}%" 
        
        # Column management
        if i % 2 == 0:
            if i != len(dates) - 1:
                tikz_blocks += "\\hfill\n"
        else:
            if i % 6 != 5 and i != len(dates) - 1:
                tikz_blocks += "\n\\par\\vspace{\\fill}\n\\noindent\n"
                
        # Closure of page spacing
        if i % 6 == 5 or i == len(dates) - 1:
            tikz_blocks += "\n\\par\\vspace*{\\fill}\n"

    document = LATEX_HEADER + r"""
\begin{document} 
""" + tikz_blocks + r"""
\end{document}
"""
    # Sanitize document to handle non-breaking spaces typically copied from web IDEs
    return document.replace('\xa0', ' ')


def compile_and_download(file_name: str, latex_content: str):
    """Writes the LaTeX code to a file, compiles it via pdflatex, and attempts download."""
    tex_filename = f"{file_name}.tex"
    pdf_filename = f"{file_name}.pdf"

    with open(tex_filename, "w") as f:
        f.write(latex_content)

    print(f"Compiling LaTeX to PDF...")
    process = subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_filename], capture_output=True, text=True)

    if process.returncode != 0:
        print("Compilation Failed. Log output below:")
        print(process.stdout)
        return

    # Secondary compilation ensures references and alignments settle correctly
    subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_filename], capture_output=True)
    print(f"Success! Generated {pdf_filename}")

    # Fallback to allow execution outside of Google Colab environments
    try:
        from google.colab import files
        print("Initiating download in Colab environment...")
        files.download(pdf_filename)
    except ImportError:
        print(f"File saved locally at: {os.path.abspath(pdf_filename)}")


def main():
    print(f"Initializing Chronodex generation for {START_DATE} through {END_DATE}")
    target_dates = generate_date_list(START_DATE, END_DATE)
    latex_source = build_latex_document(target_dates)
    compile_and_download(FILE_NAME, latex_source)


if __name__ == "__main__":
    main()
