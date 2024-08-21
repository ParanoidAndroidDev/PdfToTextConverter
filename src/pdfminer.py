from typing import List
import pymupdf
from tkinter import PhotoImage
from src.pdfpagetemplate import PageTemplate
import math

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
    
    def convert_to_text(self, page_templates: List[PageTemplate]):
        result_text = ""

        for page_num in range(self.pdf.page_count):
            page = self.pdf.load_page(page_num)
            extracted_dict = page.get_text("rawdict", sort=True)
            width = extracted_dict["width"]
            height = extracted_dict["height"]

            active_page_templates = []
            order_values = set()
            for page_template in page_templates:
                if page_num in page_template.get_page_range():
                    active_page_templates.append(page_template)
                    order_values.add(page_template.order)
            
            if len(active_page_templates) == 0:
                continue

            active_page_templates.sort(key=lambda x: x.order)
            sorted_order_values = list(order_values)
            sorted_order_values.sort()

            lines = []
            for block in extracted_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        line_chars = []
                        if "spans" in line:
                            for span in line["spans"]:
                                if "chars" in span:
                                    for char in span["chars"]:
                                        print(char["c"], end="")
                                        line_chars.append(char)

                    line_chars.sort(key=lambda c: (c["bbox"][2], c["bbox"][0]))
                    lines.append(line_chars)

            for order in sorted_order_values:
                for line in lines:
                    text_line = ""
                    for char in line:
                        accept = False
                        reject = False
                        for page_template in active_page_templates:
                            if page_template.order == order and page_template.check_rect(char["bbox"], width, height):
                                if page_template.templatetype == "negative":
                                    reject = True
                                    break
                                if page_template.templatetype == "positive":
                                    accept = True

                        if accept and not reject: 
                            text_line += char["c"]

                    print(text_line)
                    result_text += text_line + "\n"
                
        return result_text