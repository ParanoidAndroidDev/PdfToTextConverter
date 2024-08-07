import pyttsx3
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import os
from src.pdfminer import PDFMiner
from src.pdfcanvas import *

class PDFViewer:
    def __init__(self, main):
        self.path = None
        self.fileisopen = None
        self.author = None
        self.name = None
        self.current_page = 0
        self.num_pages = None
        self.miner = None
        self.converted_text = ""

        self.main = main
        self.main.title('PDF Viewer')
        self.main.geometry('800x800+440+100')
        self.main.grid_rowconfigure(0, weight=3)
        self.main.grid_columnconfigure(0, weight=3)
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_columnconfigure(1, weight=1)
        

        # menu
        self.menu = Menu(self.main)
        self.main.config(menu=self.menu)
        self.filemenu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="Open File", command=self.open_file)
        self.filemenu.add_command(label="Exit", command=self.main.destroy)


        #
        # CONTROLS FRAME
        #

        self.controls_frame = ttk.Frame(self.main)
        self.controls_frame.grid(row=0, column=1)

        # navigation controls
        self.navigation_controls = ttk.Frame(self.controls_frame)
        self.navigation_controls.pack(side=TOP)
        self.uparrow_icon = PhotoImage(file='img/uparrow.png')
        self.downarrow_icon = PhotoImage(file='img/downarrow.png')
        self.uparrow = self.uparrow_icon.subsample(3, 3)
        self.downarrow = self.downarrow_icon.subsample(3, 3)
        self.upbutton = Button(self.navigation_controls, bg="darkgrey", image=self.uparrow, command=self.previous_page)
        self.upbutton.grid(row=0, column=1, pady=8)
        self.downbutton = Button(self.navigation_controls, bg="darkgrey", image=self.downarrow, command=self.next_page)
        self.downbutton.grid(row=0, column=3, pady=8)
        self.page_label = ttk.Label(self.navigation_controls, text='page')
        self.page_label.grid(row=0, column=4, padx=5)

        # template controls
        self.template_controls = Frame(self.controls_frame, borderwidth=5)
        self.template_controls.pack(side=TOP)
        self.canvas_mode_var = IntVar(self.main, CM_POSRECT)
        self.canvas_mode_maintemplate_var = BooleanVar(self.main, False)
        self.template_controls_radiogroup = ttk.Frame(self.template_controls)
        self.template_controls_radiogroup.pack()
        self.canvas_mode_button_posrect = ttk.Radiobutton(self.template_controls_radiogroup, text="Positive", variable=self.canvas_mode_var, command=lambda: self.update_canvas_mode(CM_POSRECT, self.canvas_mode_maintemplate_var.get()), value=CM_POSRECT)
        self.canvas_mode_button_posrect.grid(row=0, column=0)
        self.canvas_mode_button_negrect = ttk.Radiobutton(self.template_controls_radiogroup, text="Negative", variable=self.canvas_mode_var, command=lambda: self.update_canvas_mode(CM_NEGRECT, self.canvas_mode_maintemplate_var.get()), value=CM_NEGRECT)
        self.canvas_mode_button_negrect.grid(row=0, column=1)
        self.canvas_mode_button_maintemplate = ttk.Checkbutton(self.template_controls, text="Global Template", variable=self.canvas_mode_maintemplate_var, command=lambda: self.update_canvas_mode(self.canvas_mode_var.get(), self.canvas_mode_maintemplate_var.get()), onvalue=True, offvalue=False)
        self.canvas_mode_button_maintemplate.pack()
        self.rect_listboxes = ttk.Frame(self.template_controls)
        self.rect_listboxes.pack()
        self.main_template_posrects_label = ttk.Label(self.rect_listboxes, text="Global Template", justify="center")
        self.main_template_posrects_label.grid(row=0, column=0, columnspan=2)
        self.main_template_posrects_listbox = Listbox(self.rect_listboxes, )
        self.main_template_posrects_listbox.grid(row=1, column=0)
        self.main_template_posrects_listbox.bind('<<ListboxSelect>>', self.select_main_template_posrect)
        self.main_template_posrects_delete_button = ttk.Button(self.rect_listboxes, text="Delete selected", command=self.delete_main_template_posrects)
        self.main_template_posrects_delete_button.grid(row=2, column=0)
        self.main_template_negrects_listbox = Listbox(self.rect_listboxes)
        self.main_template_negrects_listbox.grid(row=1, column=1)
        self.main_template_negrects_listbox.bind('<<ListboxSelect>>', self.select_main_template_negrect)
        self.main_template_negrects_delete_button = ttk.Button(self.rect_listboxes, text="Delete selected", command=self.delete_main_template_negrects)
        self.main_template_negrects_delete_button.grid(row=2, column=1)
        self.page_template_posrects_label = ttk.Label(self.rect_listboxes, text="Page Template", justify="center")
        self.page_template_posrects_label.grid(row=3, column=0, columnspan=2)
        self.page_template_posrects_listbox = Listbox(self.rect_listboxes)
        self.page_template_posrects_listbox.grid(row=4, column=0)
        self.page_template_posrects_listbox.bind('<<ListboxSelect>>', self.select_page_template_posrect)
        self.page_template_posrects_delete_button = ttk.Button(self.rect_listboxes, text="Delete selected", command=self.delete_page_template_posrects)
        self.page_template_posrects_delete_button.grid(row=5, column=0)
        self.page_template_negrects_listbox = Listbox(self.rect_listboxes)
        self.page_template_negrects_listbox.grid(row=4, column=1)
        self.page_template_negrects_listbox.bind('<<ListboxSelect>>', self.select_page_template_negrect)
        self.page_template_negrects_delete_button = ttk.Button(self.rect_listboxes, text="Delete selected", command=self.delete_page_template_negrects)
        self.page_template_negrects_delete_button.grid(row=5, column=1)


        # text conversion controls
        self.conversion_controls = Frame(self.controls_frame, bg="grey", borderwidth=5)
        self.conversion_controls.pack(side=TOP)
        self.convert_to_text_button = ttk.Button(self.conversion_controls, text="Convert to text", command=self.convert_to_text)
        self.convert_to_text_button.pack()
        self.speak_text_button = ttk.Button(self.conversion_controls, text="Speak text", command=self.speak_text)
        self.speak_text_button.pack()



        #
        # PDF FRAME
        #

        self.pdf_frame = ttk.Frame(self.main)
        self.pdf_frame.grid(row=0, column=0, sticky=(N, E, S, W))
        self.pdf_frame.grid_rowconfigure(0, weight=1)
        self.pdf_frame.grid_columnconfigure(0, weight=1)

        # scroll bars
        self.scrolly = Scrollbar(self.pdf_frame, orient=VERTICAL)
        self.scrolly.grid(row=0, column=1, sticky=(N, E, S))
        self.scrollx = Scrollbar(self.pdf_frame, orient=HORIZONTAL)
        self.scrollx.grid(row=1, column=0, sticky=(W, S, E))

        # PDF canvas
        self.canvas = PDFCanvas(self.pdf_frame, self.main_template_posrects_listbox, self.main_template_negrects_listbox, self.page_template_posrects_listbox, self.page_template_negrects_listbox, bg='#ECE8F3')
        self.canvas.configure(yscrollcommand=self.scrolly.set, xscrollcommand=self.scrollx.set)
        self.canvas.grid(row=0, column=0, sticky=N + W + S + E)
        self.scrollx.configure(command=self.canvas.xview)
        self.scrolly.configure(command=self.canvas.yview)


    def update_canvas_mode(self, mode, maintemplate=False):
        if maintemplate:
            if mode == CM_POSRECT:
                self.canvas.mode = CM_TEMPLATE_POSRECT
            elif mode == CM_NEGRECT:
                self.canvas.mode = CM_TEMPLATE_NEGRECT
            else:
                self.canvas.mode = mode
        else:
            if mode == CM_TEMPLATE_POSRECT:
                self.canvas.main_templatemode = CM_POSRECT
            elif mode == CM_TEMPLATE_NEGRECT:
                self.canvas.mode = CM_NEGRECT
            else:
                self.canvas.mode = mode

    def delete_main_template_posrects(self):
        self.canvas.delete_main_template_posrects()
    
    def delete_main_template_negrects(self):
        self.canvas.delete_main_template_negrects()
    
    def delete_page_template_posrects(self):
        self.canvas.delete_page_template_posrects()

    def delete_page_template_negrects(self):
        self.canvas.delete_page_template_negrects()

    def select_main_template_posrect(self, evt):
        selection = evt.widget.curselection()
        if len(selection) > 0:
            index = int(selection[0])
            self.canvas.select_main_template_posrect(index)

    def select_main_template_negrect(self, evt):
        selection = evt.widget.curselection()
        if len(selection) > 0:
            index = int(selection[0])
            self.canvas.select_main_template_negrect(index)

    def select_page_template_posrect(self, evt):
        selection = evt.widget.curselection()
        if len(selection) > 0:
            index = int(selection[0])
            self.canvas.select_page_template_posrect(index)

    def select_page_template_negrect(self, evt):
        selection = evt.widget.curselection()
        if len(selection) > 0:
            index = int(selection[0])
            self.canvas.select_page_template_negrect(index)

    def open_file(self):
        filepath = fd.askopenfilename(title='Select a PDF file', initialdir=os.getcwd(), filetypes=(('PDF', '*.pdf'), ))
        if filepath:
            self.path = filepath
            filename = os.path.basename(self.path)
            self.miner = PDFMiner(self.path)
            data, num_pages = self.miner.get_metadata()
            self.current_page = 0
            self.canvas.set_page_number(0)
            if num_pages:
                self.name = data.get('title', filename[:-4])
                self.author = data.get('author', None)
                self.num_pages = num_pages
                self.fileisopen = True
                self.display_page()
                self.main.title(self.name)
                self.canvas.width = self.miner.width
                self.canvas.height = self.miner.height
                # self.canvas.config(width=math.ceil(self.miner.width), height=math.ceil(self.miner.height))

    def display_page(self):
        if 0 <= self.current_page < self.num_pages:
            self.img_file = self.miner.get_page(self.current_page)
            self.canvas.create_image(0, 0, anchor='nw', image=self.img_file)
            self.stringified_current_page = self.current_page + 1
            self.page_label['text'] = str(self.stringified_current_page) + ' of ' + str(self.num_pages)
            region = self.canvas.bbox(ALL)
            self.canvas.configure(scrollregion=region)   

    def next_page(self):
        if self.fileisopen:
            if self.current_page <= self.num_pages - 1:
                self.current_page += 1
                self.display_page()
                self.canvas.set_page_number(self.current_page)
                self.canvas.update_templates()

    def previous_page(self):
        if self.fileisopen:
            if self.current_page > 0:
                self.current_page -= 1
                self.display_page()
                self.canvas.set_page_number(self.current_page)
                self.canvas.update_templates()
    
    def convert_to_text(self):
        filename = self.get_output_filename()
        if not filename:
            print("Error: No filename given")
            return

        with open(filename, "w", encoding="utf-8", newline="\n") as file:
            if self.miner:
                self.converted_text = self.miner.convert_to_text(self.canvas.main_template, self.canvas.page_templates)
                file.write(self.converted_text)

    def speak_text(self):
        filename = self.get_output_filename()
        if not filename:
            print("Error: No filename given.")
            return

        engine = pyttsx3.init()
        with open(filename, encoding="utf-8", newline="\n") as file:
            lines = file.readlines()
            text = "".join(lines)    
        engine.say(text)
        engine.runAndWait()
        
    def get_output_filename(self):
        if self.path:
            return os.path.basename(self.path).removesuffix(".pdf") + ".txt"
        else:
            return None
