import io
from pathlib import Path

import pymupdf

from src.utilities.data_utilities import (
    remove_text_after_transaction_end,
    remove_uob_disclaimer,
)


def pdf_to_text(pdf_file: Path):
    doc = pymupdf.open(pdf_file)  # open a document
    all_text = ''

    for page in doc:  # iterate the document pages
        text = page.get_text()  # get plain text encoded as UTF-8
        all_text += '\n\n' + text
    all_text = remove_uob_disclaimer(all_text)
    return remove_text_after_transaction_end(all_text)


def pdf_to_images(pdf_file: Path, output_format: str = 'png'):
    doc = pymupdf.open(pdf_file)  # open document

    image_files = []
    try:
        for i, page in enumerate(doc):
            pix = page.get_pixmap()  # render page to an image
            out = pdf_file.parent / f'{pdf_file.stem}_{i}.{output_format}'
            pix.save(str(out))

            img_buffer = pixmap_to_bytes_io(pix, output_format)
            image_files.append(img_buffer)

        return image_files
    except Exception as e:
        print(f"Error converting PDF to images: {str(e)}")
        return None


def pixmap_to_bytes_io(pixmap: pymupdf.Pixmap, output_format: str = 'PNG') -> io.BytesIO:
    """
    Convert a PyMuPDF Pixmap to a BytesIO object.

    :param pixmap: fitz.Pixmap object to convert
    :param output_format: Output image format (default is PNG)
    :return: BytesIO object containing the image data
    """
    # Ensure the output format is uppercase
    output_format = output_format.upper()

    # Check if the pixmap has an alpha channel
    if pixmap.alpha:
        # If it has an alpha channel, we need to remove it for certain formats
        pix = pymupdf.Pixmap(pixmap, 0) if output_format in [
            'JPEG', 'JPG'] else pixmap
    else:
        pix = pixmap

    # Convert the pixmap to bytes
    img_bytes = pix.tobytes(output_format)

    # Create a BytesIO object from the bytes
    img_buffer = io.BytesIO(img_bytes)
    img_buffer.seek(0)

    # If we created a new pixmap (pix) without alpha, we need to clear it from memory
    if pix != pixmap:
        pix = None

    return img_buffer
