#
# Created by Renatus Madrigal on 04/29/2025
#

import re
import os
from pydantic import BaseModel, Field
from pylatexflow.argument import PositionalArg


class WordCountConfig(BaseModel):
    """
    Configuration for counting words in LaTeX documents using PyLaTeXFlow.
    """

    root_dir: str = Field(
        description="Root directory to count words",
        position=PositionalArg(0, metavar="ROOT_DIR"),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_dir = os.path.abspath(self.root_dir)


def count_words_in_tex_file(file_path: str) -> int:
    """
    Count the number of words in a LaTeX file.

    Args:
        file_path (str): Path to the LaTeX file.

    Returns:
        int: Number of words in the file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove LaTeX commands and comments and preamble
    begin_match = re.search(r"\\begin\{document\}", content)
    if begin_match:
        content = content[begin_match.end():]
    content = re.sub(r"\\[a-zA-Z]+(\{[^}]*\})*", r" \1 ", content)  # Remove LaTeX commands
    content = re.sub(r"(?<!\\)%.*", "", content)  # Remove comments, but keep escaped \%
    content = re.sub(r"([\u4e00-\u9fff])", r" \1 ", content) # Add spaces around CJK characters
    content = re.sub(r"[\u3000-\u303F\uFF00-\uFFEF]", r" ", content) # Remove punctuation

    # Split the content into words and count them
    words = re.findall(r"\b\w+\b", content)
    
    return len(words)


def count_all_tex_files(config: WordCountConfig):
    """
    Count the total number of words in all LaTeX files in the specified directory.

    Args:
        config (WordCountConfig): Configuration object containing the root directory.

    Returns:
        int: Total number of words in all LaTeX files.
    """
    words_table = {}
    total_words = 0
    for root, _, files in os.walk(config.root_dir):
        for file in files:
            if file.endswith(".tex"):
                file_path = os.path.join(root, file)
                word_count = count_words_in_tex_file(file_path)
                relative_path = os.path.relpath(
                    file_path,
                    os.path.dirname(config.root_dir),
                )
                words_table[relative_path] = word_count
                total_words += word_count

    print("Word count for each file:")
    for file_path, count in words_table.items():
        print(f"{file_path}: {count} words")

    print(f"\nTotal word count: {total_words} words")
