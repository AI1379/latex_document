#
# Created by Renatus Madrigal on 04/24/2025
#

import os
from pylatexflow.build_flow import BuildFlowConfig, LaTeXBuilder, build_all
from pylatexflow.clean import CleanTempFilesConfig, clean_temp_files
from pylatexflow.create import CreateConfig, create_latex_project
from pylatexflow.argument import ArgumentParser
from pylatexflow.word_count import WordCountConfig, count_all_tex_files


def main():
    """
    Main function to handle command-line arguments and initiate the LaTeX build process.
    """
    parser = ArgumentParser(
        {
            "build": BuildFlowConfig,
            "clean": CleanTempFilesConfig,
            "create": CreateConfig,
            "build-all": BuildFlowConfig,
            "word-count": WordCountConfig,
        }
    )
    args, cmd = parser.parse_args()
    if cmd == "build":
        builder = LaTeXBuilder(args)
        builder.build()
    elif cmd == "build-all":
        build_all(os.getcwd(), args)
    elif cmd == "clean":
        clean_temp_files(args)
    elif cmd == "create":
        create_latex_project(args)
    elif cmd == "word-count":
        count_all_tex_files(args)


if __name__ == "__main__":
    main()
