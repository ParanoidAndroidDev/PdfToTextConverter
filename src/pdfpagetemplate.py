import uuid
import math

class TemplateRect:
    def __init__(self, bounds, canvas):
        self.x1 = bounds[0] / canvas.width
        self.y1 = bounds[1] / canvas.height
        self.x2 = bounds[2] / canvas.width
        self.y2 = bounds[3] / canvas.height

class PageTemplate:
    def __init__(self, canvas, templatetype, frompage, topage, eachpage, order):
        if not templatetype in ["positive", "negative"]:
            raise "Template type not recognized: " + templatetype
        self.templatetype = templatetype
        self.canvas = canvas
        self.id = uuid.uuid4()
        self.rects = {}

        if frompage > topage:
            raise "'FromPage' must be at most 'ToPage'"

        if frompage < 0 or topage < 0:
            raise "'FromPage' and 'ToPage' must be non-negative"

        if eachpage <= 0:
            raise "'EachPage' must be positive"

        self.frompage = frompage
        self.topage = topage
        self.eachpage = eachpage
        self.order = order
    
    def add_rect(self, rect_bounds):
        id = uuid.uuid4()
        self.rects[id] = TemplateRect(rect_bounds, self.canvas)

    def get_page_range(self):
        return range(self.frompage, self.topage + 1, self.eachpage)

    def check_rect(self, coords, max_width, max_height):
        x1_percent = coords[0] / max_width
        x2_percent = coords[2] / max_width
        y1_percent = coords[1] / max_height
        y2_percent = coords[3] / max_height
        
        for id in self.rects:
            rect = self.rects[id]

            # check if target is fully contained in rect
            if x1_percent >= rect.x1 and x2_percent <= rect.x2 and y1_percent >= rect.y1 and y2_percent <= rect.y2:
                return True
            
            # otherwise check if at least 50% of target is covered by rect
            intersection_x1 = max(x1_percent, rect.x1)
            intersection_x2 = min(x2_percent, rect.x2)
            intersection_y1 = max(y1_percent, rect.y1)
            intersection_y2 = min(y2_percent, rect.y2)

            if intersection_x2 <= intersection_x1 or intersection_y2 <= intersection_y1:
                continue

            intersection_area = (intersection_x2 - intersection_x1) * (intersection_y2 - intersection_y1)
            target_area = (x2_percent - x1_percent) * (y2_percent - y1_percent)

            if intersection_area >= (0.5 * target_area):
                return True
        
        return False
