from tkinter import *
from pdftexttemplate import TextTemplate

# Canvas Mode
CM_POSRECT = 0
CM_NEGRECT = 1
CM_TEMPLATE_POSRECT = 2
CM_TEMPLATE_NEGRECT = 3

POSRECT_COLOR = "#36a127"
NEGRECT_COLOR = "red"
SELECTION_COLOR = "yellow"

class PDFCanvas(Canvas):
    def __init__(self, master, mt_prect_listbox, mt_nrect_listbox, pt_prect_listbox, pt_nrect_listbox, cnf={}, **kwargs):
        super().__init__(master, cnf, **kwargs)

        self.page_number = 0
        self.mode = CM_POSRECT
        self.main_template = TextTemplate(self)
        self.page_templates = dict()
        self.current_rect_id = None
        self.rect_ids = []

        self.main_template_posrects_listbox = mt_prect_listbox
        self.main_template_negrects_listbox = mt_nrect_listbox
        self.page_template_posrects_listbox = pt_prect_listbox
        self.page_template_negrects_listbox = pt_nrect_listbox

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
                self.current_rect_id = self.create_rectangle(point[0], point[1], point[0], point[1], outline=SELECTION_COLOR, width=3)
                self.drag_startpoint = point

        def on_canvas_buttonrelease(event):
            if event.num == 1:
                coords = self.coords(self.current_rect_id)
                if self.mode == CM_POSRECT:
                    if not self.page_number in self.page_templates:
                        self.page_templates[self.page_number] = TextTemplate(self)
                    template = self.page_templates[self.page_number]
                    template.add_pos_rect(coords)
                    idx = len(template.pos_rects) - 1
                    self.page_template_posrects_listbox.insert(idx, idx)
                    self.delete(self.current_rect_id)
                elif self.mode == CM_NEGRECT:
                    if not self.page_number in self.page_templates:
                        self.page_templates[self.page_number] = TextTemplate(self)
                    template = self.page_templates[self.page_number]
                    template.add_neg_rect(coords)
                    idx = len(template.neg_rects) - 1
                    self.page_template_negrects_listbox.insert(idx, idx)
                    self.delete(self.current_rect_id)
                elif self.mode == CM_TEMPLATE_POSRECT:
                    self.main_template.add_pos_rect(coords)
                    idx = len(self.main_template.pos_rects) - 1
                    self.main_template_posrects_listbox.insert(idx, idx)
                    self.delete(self.current_rect_id)
                elif self.mode == CM_TEMPLATE_NEGRECT:
                    self.main_template.add_neg_rect(coords)
                    idx = len(self.main_template.neg_rects) - 1
                    self.main_template_negrects_listbox.insert(idx, idx)
                    self.delete(self.current_rect_id)
                
                self.update_templates()
        
        self.bind("<B1-Motion>", on_canvas_drag_lmb)
        self.bind("<ButtonPress>", on_canvas_buttonpress)
        self.bind("<ButtonRelease>", on_canvas_buttonrelease)
    
    def set_page_number(self, p):
        self.page_number = p
        for i in range(self.page_template_posrects_listbox.size()):
            self.page_template_posrects_listbox.delete(i)
        for i in range(self.page_template_negrects_listbox.size()):
            self.page_template_negrects_listbox.delete(i)
        
        if p in self.page_templates:
            page_template = self.page_templates[p]
            idx = 0
            for pos_rect in page_template.pos_rects:
                self.page_template_posrects_listbox.insert(idx, idx)
                idx += 1
            
            idx = 0
            for neg_rect in page_template.neg_rects:
                self.page_template_negrects_listbox.insert(idx, idx)
                idx += 1
    
    def update_templates(self, selected_main_posrects=[], selected_main_negrects=[], selected_page_posrects=[], selected_page_negrects=[]):
        for rect_id in self.rect_ids:
            self.delete(rect_id)
        
        if self.page_number in self.page_templates:
            page_template = self.page_templates[self.page_number]
            idx = 0
            for rect in page_template.pos_rects:
                rect_id = self.create_rectangle(rect[0], rect[1], rect[2], rect[3], outline=SELECTION_COLOR if idx in selected_page_posrects else POSRECT_COLOR, width=3)
                self.rect_ids.append(rect_id)
                idx += 1
            idx = 0
            for rect in page_template.neg_rects:
                rect_id = self.create_rectangle(rect[0], rect[1], rect[2], rect[3], outline=SELECTION_COLOR if idx in selected_page_negrects else NEGRECT_COLOR, width=3)
                self.rect_ids.append(rect_id)
                idx += 1

        idx = 0
        for rect in self.main_template.pos_rects:
            rect_id = self.create_rectangle(rect[0], rect[1], rect[2], rect[3], outline=SELECTION_COLOR if idx in selected_main_posrects else POSRECT_COLOR, width=3)
            self.rect_ids.append(rect_id)
            idx += 1
        idx = 0
        for rect in self.main_template.neg_rects:
            rect_id = self.create_rectangle(rect[0], rect[1], rect[2], rect[3], outline=SELECTION_COLOR if idx in selected_main_negrects else NEGRECT_COLOR, width=3)
            self.rect_ids.append(rect_id)
            idx += 1

    def delete_main_template_posrects(self):
        selecteditems = list(self.main_template_posrects_listbox.curselection())
        selecteditems.sort(reverse=True)
        for i in selecteditems:
            del self.main_template.pos_rects[i]
            self.main_template_posrects_listbox.delete(i)
        
        self.update_templates()
    
    def delete_main_template_negrects(self):
        selecteditems = list(self.main_template_negrects_listbox.curselection())
        selecteditems.sort(reverse=True)
        for i in selecteditems:
            del self.main_template.neg_rects[i]
            self.main_template_negrects_listbox.delete(i)
        
        self.update_templates()
    
    def delete_page_template_posrects(self):
        selecteditems = list(self.page_template_posrects_listbox.curselection())
        selecteditems.sort(reverse=True)
        for i in selecteditems:
            del self.page_templates[self.page_number].pos_rects[i]
            self.page_template_posrects_listbox.delete(i)
        
        self.update_templates()

    def delete_page_template_negrects(self):
        selecteditems = list(self.page_template_negrects_listbox.curselection())
        selecteditems.sort(reverse=True)
        for i in selecteditems:
            del self.page_templates[self.page_number].neg_rects[i]
            self.page_template_negrects_listbox.delete(i)
        
        self.update_templates()

    def select_page_template_posrect(self, index):
        self.update_templates(selected_page_posrects=[index])
    
    def select_page_template_negrect(self, index):
        self.update_templates(selected_page_negrects=[index])

    def select_main_template_posrect(self, index):
        self.update_templates(selected_main_posrects=[index])

    def select_main_template_negrect(self, index):
        self.update_templates(selected_main_negrects=[index])