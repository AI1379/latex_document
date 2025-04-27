#
# Created by Renatus Madrigal on 04/23/2025
#

import os
import subprocess
import json
from typing import Dict
from pydantic import BaseModel, Field


class BuildFlowConfig(BaseModel):
    """
    Configuration for building LaTeX documents using PyLaTeXFlow.
    """

    max_round: str = Field(default="20", description="Maximum number of build rounds")
    directory: str = Field(default=".", description="Directory containing the TeX file")
    base_name: str = Field(default="main", description="Base name of the LaTeX file")
    output_dir: str = Field(default="output", description="Output directory")
    output: str = Field(
        default="main", description="LaTeX output file name without extension"
    )
    build_command: str = Field(default="pdflatex", description="LaTeX build command")
    bibtex_command: str = Field(default="bibtex", description="BibTeX build command")
    build_args: list = Field(
        default=["--interaction=nonstopmode", "--shell-escape"],
        description="Additional arguments for the build command",
    )
    environments: dict = Field(
        default={},
        description="A dictionary of environment variables to be passed to LaTeX",
    )
    env_file: str = Field(
        default="env.json",
        description="A json file that contains environment variables",
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
        self.flow = []

    def _check_bib(self, aux_file: str):
        bib_tag = ["\\bibdata", "\\addbibresource", "\\citation"]
        with open(aux_file, "r", encoding="utf-8") as f:
            aux = f.read()
            for tag in bib_tag:
                if tag in aux:
                    return True
            return False

    def generate_environment(self, env: Dict[str, str]):
        """
        Generate the TeX file to push variables into LaTeX environment.
        """
        env_file = os.path.join(self.config.directory, "env.tex")
        with open(env_file, "w", encoding="utf-8") as f:
            for key, value in env.items():
                f.write(f"\\newcommand{{\\{key}}}{{{value}}}\n")

    def build(self):
        self.flow = []
        if not os.path.isdir(self.config.output_dir):
            os.makedirs(self.config.output_dir, exist_ok=True)
        max_rounds = 20
        tex_name = f"{self.config.base_name}.tex"
        aux_name = f"{self.config.output}.aux"
        tex_file = os.path.join(self.config.directory, tex_name)
        aux_file = os.path.join(self.config.output_dir, aux_name)
        prev_aux = ""
        build_bib = False
        env = {}
        if os.path.isfile(self.config.env_file):
            with open(self.config.env_file) as env_json:
                env = json.load(env_json)
        for key, item in self.config.environments.items():
            env[key] = item
        print(
            f"Environments: {', '.join([f"{key} = {item}" for key, item in env.items()])}"
        )
        if env:
            self.generate_environment(env)

        for i in range(max_rounds):
            if build_bib:
                build_command = [
                    self.config.bibtex_command,
                    os.path.join(self.config.output_dir, self.config.base_name),
                ]
            else:
                build_command = [
                    self.config.build_command,
                    f"-output-directory={self.config.output_dir}",
                    f"-jobname={self.config.output}",
                    tex_file,
                ] + self.config.build_args
            print(f"Round {i+1}: Running {build_command} ...")
            self.flow.append(build_command)
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

    def get_flow(self):
        """
        Returns the build flow as a list of commands.
        """
        return self.flow


def build_all(directory: str, config: BuildFlowConfig):
    """
    Build all LaTeX project in the specified directory.
    """
    ignore = [".venv", ".git", ".vscode", config.output_dir, "pylatexflow"]
    main_file_name = f"{config.base_name}.tex"
    for subdir in os.listdir(directory):
        if not os.path.isdir(subdir) or subdir in ignore:
            continue
        full_subdir = os.path.join(directory, subdir)
        print(f"Running in subdirectory: {subdir}")
        if not main_file_name in os.listdir(subdir):
            print(f"Cannot find main file: {main_file_name}. Skipped")
            continue

        config.directory = os.path.abspath(full_subdir)
        config.output = subdir
        builder = LaTeXBuilder(config)
        builder.build()
