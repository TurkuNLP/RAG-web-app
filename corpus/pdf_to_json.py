import json
import os
from pathlib import Path
from docling_core.types.doc import ImageRefMode
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

# Model and database configuration
IMAGE_RESOLUTION_SCALE = 2.0
SOURSE = "data/documents/ship_data"

# Define paths
doc_dirs = ["txts", "jsons", "md-embed", "md-ref"]
output_dir = Path("data/documents/ship_processed")

for index, doc_dir in enumerate(doc_dirs):
    new_dir = output_dir / doc_dir
    new_dir.mkdir(parents=True, exist_ok=True)
    doc_dirs[index] = new_dir

def process_pdf(pdf_file):
    """Converts the PDF to structured text and extracts images."""
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.ocr_options.lang = ["ru"]
    pipeline_options.do_table_structure = True
    #pipeline_options.do_formula_understanding = True
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True
    
    doc_converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )
    conv_result = doc_converter.convert(Path(pdf_file))
    doc_filename = conv_result.input.file.stem

    with (doc_dirs[0] / f"{doc_filename}.txt").open("w", encoding="utf-8") as fp:
        fp.write(conv_result.document.export_to_text())

    with (doc_dirs[1] / f"{doc_filename}.json").open("w", encoding="utf-8") as fp:
        fp.write(json.dumps(conv_result.document.export_to_dict()))

    # Save markdown with embedded pictures
    md_filename = doc_dirs[2] / f"{doc_filename}-with-images.md"
    conv_result.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

    # Save markdown with externally referenced pictures
    md_filename = doc_dirs[3] / f"{doc_filename}-with-image-refs.md"
    conv_result.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)


def main():

    # Process the PDF file and extract text
    for filename in os.listdir(SOURSE):
        if filename.endswith(".pdf"):
            file_path = os.path.join(SOURSE, filename)
            process_pdf(file_path)



main()