#
# Created by Renatus Madrigal on 04/24/2025
#


import os
import sys
from pydantic import BaseModel, Field
from pylatexflow.argument import PositionalArg


class CreateConfig(BaseModel):
    """
    Configuration for creating a LaTeX project directory with a template.
    """

    dirname: str = Field(
        description="Name of the directory to create",
        position=PositionalArg(0, metavar="DIRNAME"),
    )
    template: str = Field(
        description="Name of the template to use",
        position=PositionalArg(1, metavar="TEMPLATE"),
    )
    template_dir: str = Field(
        default="templates",
        description="Directory containing the LaTeX templates",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dirname = os.path.abspath(self.dirname)


def create_latex_project(config: CreateConfig):
    """
    Create a LaTeX project directory with a specified template.

    Args:
        config (CreateConfig): Configuration object containing the directory name and template name.
    """
    directory_name = config.dirname
    template_name = config.template
    template_path = os.path.join(config.template_dir, f"{template_name}.tex")

    # Create the directory if it does not exist.
    os.makedirs(directory_name, exist_ok=True)

    # Read the template content.
    if not os.path.exists(template_path):
        print(f"Template '{template_path}' not found.")
        sys.exit(1)

    with open(template_path, "r", encoding="utf-8") as template_file:
        content = template_file.read()

    # Create main.tex in the new directory.
    output_path = os.path.join(directory_name, "main.tex")
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(content)

    print(
        f"main.tex created in '{directory_name}' using the '{template_name}' template."
    )
