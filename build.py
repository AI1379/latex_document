import subprocess
import sys
import os
import argparse

LATEX_COMPILER = "pdflatex"
BIBTEX_COMPILER = "bibtex"


def build_latex_article(directory, tex_file='main.tex', passes=2):
    if not os.path.isdir(directory):
        print(f"Error: The directory '{directory}' does not exist.")
        sys.exit(1)

    tex_path = os.path.join(directory, tex_file)
    if not os.path.isfile(tex_path):
        print(f"Error: The TeX file '{tex_path}' does not exist.")
        sys.exit(1)

    for i in range(passes):
        print(f"Running pdflatex pass {i+1} on '{tex_file}'...")
        result = subprocess.run(
            [LATEX_COMPILER, "-interaction=nonstopmode", tex_file],
            cwd=directory
        )
        if result.returncode != 0:
            print("Error: pdflatex encountered an issue.")
            sys.exit(result.returncode)

    print("Compilation successful!")


def main():
    parser = argparse.ArgumentParser(
        description="Build a LaTeX article in a specified directory."
    )
    parser.add_argument(
        "directory", help="Directory containing the LaTeX article (with main.tex file)"
    )
    parser.add_argument(
        "--file", default="main.tex", help="Name of the TeX file to build (default: main.tex)"
    )
    parser.add_argument(
        "--passes", type=int, default=2, help="Number of pdflatex runs (default: 2)"
    )
    parser.add_argument(
        "--bibtex", action="store_true", help="Run bibtex after pdflatex passes"
    )
    args = parser.parse_args()

    build_latex_article(args.directory, args.file, args.passes)


if __name__ == "__main__":
    main()
