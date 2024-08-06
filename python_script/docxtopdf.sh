#!/bin/bash

# Directory containing DOCX files
directory="/home/mtebad/projects/RAG-web-app/data/EN"

# Change to the specified directory
cd "$directory" || exit

# Convert each DOCX file to PDF using pandoc with the specified pdf-engine and YAML settings
for file in *.docx; do
  if [ -f "$file" ]; then
    echo "Converting $file to PDF..."
    pandoc "$file" --pdf-engine=xelatex --metadata-file=pandoc_latex_template.yaml -o "${file%.docx}.pdf"
    echo "Converted $file to PDF."
  fi
done

echo "All DOCX files have been converted to PDF."

