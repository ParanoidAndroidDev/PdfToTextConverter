class TextTemplate:
    def __init__(self, canvas):
        self.canvas = canvas
        self.pos_rects = []
        self.neg_rects = []
    
    def add_pos_rect(self, rect_bounds):
        self.pos_rects.append(rect_bounds)
    
    def add_neg_rect(self, rect_bounds):
        self.neg_rects.append(rect_bounds)

    def check_rect(self, coords, max_width, max_height):
        x1_percent = coords[0] / max_width
        x2_percent = coords[2] / max_width
        y1_percent = coords[1] / max_height
        y2_percent = coords[3] / max_height

        for pos_rect in self.pos_rects:
            rect_x1_percent = pos_rect[0] / self.canvas.width
            rect_x2_percent = pos_rect[2] / self.canvas.width
            rect_y1_percent = pos_rect[1] / self.canvas.height
            rect_y2_percent = pos_rect[3] / self.canvas.height

            if x1_percent < rect_x1_percent or x2_percent > rect_x2_percent or y1_percent < rect_y1_percent or y2_percent > rect_y2_percent:
                return False
        
        for neg_rect in self.neg_rects:
            rect_x1_percent = neg_rect[0] / self.canvas.width
            rect_x2_percent = neg_rect[2] / self.canvas.width
            rect_y1_percent = neg_rect[1] / self.canvas.height
            rect_y2_percent = neg_rect[3] / self.canvas.height

            # check if target is fully contained in neg_rect
            if x1_percent >= rect_x1_percent and x2_percent <= rect_x2_percent and y1_percent >= rect_y1_percent and y2_percent <= rect_y2_percent:
                return False
            
            # otherwise check if at least 50% of target is covered by neg_rect
            intersection_x1 = max(x1_percent, rect_x1_percent)
            intersection_x2 = min(x2_percent, rect_x2_percent)
            intersection_y1 = max(y1_percent, rect_y1_percent)
            intersection_y2 = min(y2_percent, rect_y2_percent)

            if intersection_x2 <= intersection_x1 or intersection_y2 <= intersection_y1:
                continue

            intersection_area = (intersection_x2 - intersection_x1) * (intersection_y2 - intersection_y1)
            target_area = (x2_percent - x1_percent) * (y2_percent - y1_percent)

            if intersection_area >= (0.5 * target_area):
                return False

        
        return True
