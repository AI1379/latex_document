#
# Created by Renatus Madrigal on 04/23/2025
#

import os
import subprocess
from pydantic import BaseModel, Field


class BuildFlowConfig(BaseModel):
    """
    Configuration for building LaTeX documents using PyLaTeXFlow.
    """

    max_round: str = Field(default="20", description="Maximum number of build rounds")
    directory: str = Field(default=".", description="Directory containing the TeX file")
    base_name: str = Field(default="main", description="Base name of the LaTeX file")
    output_dir: str = Field(default="output", description="Output directory")
    build_command: str = Field(default="pdflatex", description="LaTeX build command")
    bibtex_command: str = Field(default="bibtex", description="BibTeX build command")
    build_args: list = Field(
        default=["--interaction=nonstopmode", "--shell-escape"],
        description="Additional arguments for the build command",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = os.path.abspath(self.output_dir)
        self.directory = os.path.abspath(self.directory)


class LaTeXBuildError(Exception):
    def __init__(self, return_code: int, *args):
        super().__init__(*args)
        self.return_code = return_code


class LaTeXBuilder:
    def __init__(self, config: BuildFlowConfig):
        self.config = config

    def _check_bib(self, aux_file: str):
        bib_tag = ["\\bibdata", "\\addbibresource", "\\citation"]
        with open(aux_file, "r", encoding="utf-8") as f:
            aux = f.read()
            for tag in bib_tag:
                if tag in aux:
                    return True
            return False

    def build(self):
        if not os.path.isdir(self.config.output_dir):
            os.makedirs(self.config.output_dir, exist_ok=True)
        max_rounds = 20
        tex_name = f"{self.config.base_name}.tex"
        aux_name = f"{self.config.base_name}.aux"
        tex_file = os.path.join(self.config.directory, tex_name)
        aux_file = os.path.join(self.config.output_dir, aux_name)
        prev_aux = ""
        build_bib = False
        for i in range(max_rounds):
            if build_bib:
                build_command = [
                    self.config.bibtex_command,
                    os.path.join(self.config.output_dir, self.config.base_name),
                ]
            else:
                build_command = [
                    self.config.build_command,
                    tex_file,
                    f"-output-directory={self.config.output_dir}",
                ] + self.config.build_args
            print(f"Round {i+1}: Running {build_command} ...")
            if not os.path.isfile(tex_file):
                raise FileNotFoundError(f"TeX file '{tex_file}' not found.")

            result = subprocess.run(
                build_command,
                cwd=self.config.output_dir,
                stdout=subprocess.DEVNULL,
            )
            if result.returncode:
                raise LaTeXBuildError(result.returncode)

            with open(aux_file, "r", encoding="utf-8") as f:
                aux = f.read()
                if aux == prev_aux:
                    break
                prev_aux = aux
            build_bib = self._check_bib(aux_file)
