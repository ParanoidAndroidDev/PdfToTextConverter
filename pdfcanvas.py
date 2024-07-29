from tkinter import *
from pdftexttemplate import TextTemplate

# Canvas Mode
CM_POSRECT = 0
CM_NEGRECT = 1
CM_TEMPLATE_POSRECT = 2
CM_TEMPLATE_NEGRECT = 3

POSRECT_COLOR = "#36a127"
NEGRECT_COLOR = "red"

class PDFCanvas(Canvas):
    def __init__(self, master=None, cnf={}, **kwargs):
        super().__init__(master, cnf, **kwargs)

        self.page_number = 0
        self.mode = CM_POSRECT
        self.main_template = TextTemplate(self)
        self.page_templates = dict()
        self.current_rect_id = None
        self.rect_ids = []

        def on_canvas_drag_lmb(event):
            if (self.current_rect_id):
                coords = self.coords(self.current_rect_id)
                if (event.x < self.drag_startpoint[0]):
                    coords[0] = event.x
                    coords[2] = self.drag_startpoint[0]
                else:
                    coords[2] = event.x
                    coords[0] = self.drag_startpoint[0]
                if (event.y < self.drag_startpoint[1]):
                    coords[1] = event.y
                    coords[3] = self.drag_startpoint[1]
                else:
                    coords[3] = event.y
                    coords[1] = self.drag_startpoint[1]
                self.coords(self.current_rect_id, coords)

        def on_canvas_buttonpress(event):
            if event.num == 1:
                point = (event.x, event.y)
                self.current_rect_id = self.create_rectangle(point[0], point[1], point[0], point[1], outline=(POSRECT_COLOR if self.mode == CM_POSRECT else 'red'), width=3)
                self.drag_startpoint = point

        def on_canvas_buttonrelease(event):
            if event.num == 1:
                coords = self.coords(self.current_rect_id)
                if self.mode == CM_POSRECT:
                    if not self.page_number in self.page_templates:
                        self.page_templates[self.page_number] = TextTemplate(self)
                    template = self.page_templates[self.page_number]
                    template.add_pos_rect(coords)
                    self.delete(self.current_rect_id)
                elif self.mode == CM_NEGRECT:
                    if not self.page_number in self.page_templates:
                        self.page_templates[self.page_number] = TextTemplate(self)
                    template = self.page_templates[self.page_number]
                    template.add_neg_rect(coords)
                    self.delete(self.current_rect_id)
                elif self.mode == CM_TEMPLATE_POSRECT:
                    self.main_template.add_pos_rect(coords)
                    self.delete(self.current_rect_id)
                elif self.mode == CM_TEMPLATE_NEGRECT:
                    self.main_template.add_neg_rect(coords)
                    self.delete(self.current_rect_id)
                
                self.update_templates()
        
        self.bind("<B1-Motion>", on_canvas_drag_lmb)
        self.bind("<ButtonPress>", on_canvas_buttonpress)
        self.bind("<ButtonRelease>", on_canvas_buttonrelease)
    
    def set_page_number(self, p):
        self.page_number = p
    
    def update_templates(self):
        for rect_id in self.rect_ids:
            self.delete(rect_id)
        
        if self.page_number in self.page_templates:
            page_template = self.page_templates[self.page_number]
            for rect in page_template.pos_rects:
                rect_id = self.create_rectangle(rect[0], rect[1], rect[2], rect[3], outline=POSRECT_COLOR, width=3)
            for rect in page_template.neg_rects:
                rect_id = self.create_rectangle(rect[0], rect[1], rect[2], rect[3], outline=NEGRECT_COLOR, width=3)

        for rect in self.main_template.pos_rects:
            rect_id = self.create_rectangle(rect[0], rect[1], rect[2], rect[3], outline=POSRECT_COLOR, width=3)
        for rect in self.main_template.neg_rects:
            rect_id = self.create_rectangle(rect[0], rect[1], rect[2], rect[3], outline=NEGRECT_COLOR, width=3)