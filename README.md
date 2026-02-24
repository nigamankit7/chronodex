# Chronodex Planner Generator

![Chronodex Preview](preview.png)

A Python-based automation tool that generates a print-ready, A4 PDF of Chronodex daily planners for any given date range. It uses LaTeX and TikZ to dynamically render the vector graphics, applying custom typography, color palettes, and print-ready cutlines.



## Features
* **Dynamic Date Generation:** Automatically loops through a given start and end date.
* **Print-Ready Grid Layout:** Outputs a perfect 2x3 A4 grid optimized for physical trimming.
* **Custom Typography & Palette:** Configured with Helvetica/Arial and a warm gradient color palette.
* **Smart Compilation:** Handles standard `pdflatex` compilation and automatic layout resolution.
* **Environment Agnostic:** Runs locally or seamlessly downloads the output when run in Google Colab.

## Prerequisites
To run this script locally, you must have Python 3 installed, along with a working LaTeX distribution.
* **Ubuntu/Debian:** `sudo apt-get install texlive-latex-extra texlive-fonts-recommended texlive-pictures`
* **MacOS:** Install MacTeX.
* **Windows:** Install MiKTeX or TeX Live.

## Installation
1. Clone the repository:

   git clone [https://github.com/yourusername/chronodex-generator.git](https://github.com/yourusername/chronodex-generator.git) <br>
   cd chronodex-generator
2. (Optional) Install Python requirements:
   ```bash
   pip install -r requirements.txt


## Usage
Open chronodex_generator.py and modify the configuration constants at the top of the file:

START_DATE = "2026-03-01"
END_DATE   = "2026-03-31"
FILE_NAME  = "Chronodex_March_2026"

Run the script:
   ```bash
    python chronodex_generator.py
