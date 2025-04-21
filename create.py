import os
import sys

#
# Created by Renatus Madrigal on 04/21/2025
#


def main():
    if len(sys.argv) < 3:
        print("Usage: python create.py <directory_name> <template_name>")
        sys.exit(1)

    directory_name = sys.argv[1]
    template_name = sys.argv[2]
    template_path = os.path.join("templates", f"{template_name}.tex")

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
        f"main.tex created in '{directory_name}' using the '{template_name}' template.")


if __name__ == "__main__":
    main()
