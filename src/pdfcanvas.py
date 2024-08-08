from tkinter import *
from src.pdfpagetemplate import PageTemplate

# Canvas Mode
CM_POSITIVE = 0
CM_NEGATIVE = 1

POSRECT_COLOR = "#36a127"
NEGRECT_COLOR = "red"
SELECTION_COLOR = "yellow"

class PDFCanvas(Canvas):
    def __init__(self, master, template_listbox, from_entry, to_entry, each_entry, cnf={}, **kwargs):
        super().__init__(master, cnf, **kwargs)

        self.page_number = 0
        self.mode = CM_POSITIVE
        self.page_templates = {}
        self.current_rect_id = None
        self.rect_ids = []

        self.pagetemplate_listbox = template_listbox
        self.from_entry = from_entry
        self.to_entry = to_entry
        self.each_entry = each_entry

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
                self.delete(self.current_rect_id)

                from_value = int(self.from_entry.get()) - 1
                to_value = int(self.to_entry.get()) - 1 
                each_value = int(self.each_entry.get())

                templatetype = "undefined"
                if self.mode == CM_POSITIVE:
                    templatetype = "positive"
                elif self.mode == CM_NEGATIVE:
                    templatetype = "negative"

                key = (templatetype, from_value, to_value, each_value)                
                if key in self.page_templates:
                    template = self.page_templates[key]
                else:
                    template = PageTemplate(self, templatetype, from_value, to_value, each_value)
                    self.page_templates[key] = template

                    listbox_entry = self.get_listbox_entry(template)
                    self.pagetemplate_listbox.insert(self.pagetemplate_listbox.size(), listbox_entry)
                
                template.add_rect(coords)
                self.update_templates()
        
        self.bind("<B1-Motion>", on_canvas_drag_lmb)
        self.bind("<ButtonPress>", on_canvas_buttonpress)
        self.bind("<ButtonRelease>", on_canvas_buttonrelease)
    
    def get_listbox_entry(self, pagetemplate):
        return "type " + pagetemplate.templatetype + ", from " + str(pagetemplate.frompage + 1) + ", to " + str(pagetemplate.topage + 1) + ", each " + str(pagetemplate.eachpage)


    def set_page_number(self, p):
        self.page_number = p
        self.pagetemplate_listbox.delete(0, END)
        
        for d in self.page_templates:
            page_template = self.page_templates[d]
            if p in page_template.get_page_range():
                listbox_entry = self.get_listbox_entry(page_template)
                self.pagetemplate_listbox.insert(self.pagetemplate_listbox.size(), listbox_entry)
    
    def update_templates(self, selected_templates=[]):
        for rect_id in self.rect_ids:
            self.delete(rect_id)
        
        for d in self.page_templates:
            page_template = self.page_templates[d]
            if self.page_number in page_template.get_page_range():
                for id in page_template.rects:
                    rect = page_template.rects[id]
                    color = POSRECT_COLOR if page_template.templatetype == "positive" else NEGRECT_COLOR
                    rect_id = self.create_rectangle(rect.x1 * self.width, rect.y1 * self.height, rect.x2 * self.width, rect.y2 * self.height, outline=SELECTION_COLOR if id in selected_templates else color, width=3)
                    self.rect_ids.append(rect_id)

    def delete_pagetemplate(self):
        selecteditems = list(self.pagetemplate_listbox.curselection())
        selecteditems.sort(reverse=True)
        for i in selecteditems:
            del self.page_templates[self.page_number].pos_rects[i]
            self.pagetemplate_listbox.delete(i)
        
        self.update_templates()

    def select_pagetemplate(self, template_string: str):
        parts = template_string.lower().split(',')
        id = int(parts[0].strip().removeprefix("id").strip())
        self.update_templates(selected_templates=[id])
