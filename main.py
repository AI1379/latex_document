#
# Created by Renatus Madrigal on 04/24/2025
#

from pylatexflow.build_flow import BuildFlowConfig, LaTeXBuilder
from pylatexflow.clean import CleanTempFilesConfig, clean_temp_files
from pylatexflow.create import CreateConfig, create_latex_project
from pylatexflow.argument import ArgumentParser


def main():
    """
    Main function to handle command-line arguments and initiate the LaTeX build process.
    """
    parser = ArgumentParser(
        {
            "build": BuildFlowConfig,
            "clean": CleanTempFilesConfig,
            "create": CreateConfig,
        }
    )
    args = parser.parse_args()
    if isinstance(args, BuildFlowConfig):
        builder = LaTeXBuilder(args)
        builder.build()
    elif isinstance(args, CleanTempFilesConfig):
        clean_temp_files(args)
    elif isinstance(args, CreateConfig):
        create_latex_project(args)


if __name__ == "__main__":
    main()
