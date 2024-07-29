import math
from typing import Dict
import pymupdf
from tkinter import PhotoImage
from pdftexttemplate import TextTemplate

class PDFMiner:
    def __init__(self, filepath):
        self.filepath = filepath
        self.pdf = pymupdf.open(self.filepath)
        self.first_page = self.pdf.load_page(0)
        self.width, self.height = self.first_page.rect.width, self.first_page.rect.height

    def get_metadata(self):
        metadata = self.pdf.metadata
        numPages = self.pdf.page_count
        return metadata, numPages
    
    def get_page(self, page_num):
        page = self.pdf.load_page(page_num)
        pix = page.get_pixmap()
        px1 = pymupdf.Pixmap(pix, 0) if pix.alpha else pix
        imgdata = px1.tobytes("ppm")
        return PhotoImage(data=imgdata)
    
    def convert_to_text(self, main_template: TextTemplate, page_templates: Dict[int, TextTemplate]):
        result_text = ""

        for page_num in range(self.pdf.page_count):
            page = self.pdf.load_page(page_num)
            extracted_dict = page.get_text('dict', sort=True)
            width = extracted_dict["width"]
            height = extracted_dict["height"]

            for block in extracted_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        if "spans" in line:
                            for span in line["spans"]:
                                if "text" in span:
                                    text = span["text"]
                                    
                                    if not main_template.check_rect(span["bbox"], width, height):
                                        continue

                                    if page_num in page_templates:
                                        page_template = page_templates[page_num]
                                        if not page_template.check_rect(span["bbox"], width, height):
                                            print(text)
                                            continue

                                    result_text += text + "\n"
                
        return result_text