import pyttsx3
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import os
from pdfminer import PDFMiner
from pdfcanvas import *

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
        self.canvas = PDFCanvas(self.pdf_frame, bg='#ECE8F3')
        self.canvas.configure(yscrollcommand=self.scrolly.set, xscrollcommand=self.scrollx.set)
        self.canvas.grid(row=0, column=0, sticky=N + W + S + E)
        self.scrollx.configure(command=self.canvas.xview)
        self.scrolly.configure(command=self.canvas.yview)


        #
        # CONTROLS FRAME
        #

        self.controls_frame = ttk.Frame(self.main)
        self.controls_frame.grid(row=0, column=1)

        # navigation controls
        self.navigation_controls = ttk.Frame(self.controls_frame)
        self.navigation_controls.pack(side=TOP)
        self.uparrow_icon = PhotoImage(file='uparrow.png')
        self.downarrow_icon = PhotoImage(file='downarrow.png')
        self.uparrow = self.uparrow_icon.subsample(3, 3)
        self.downarrow = self.downarrow_icon.subsample(3, 3)
        self.upbutton = ttk.Button(self.navigation_controls, image=self.uparrow, command=self.previous_page)
        self.upbutton.grid(row=0, column=1, pady=8)
        self.downbutton = ttk.Button(self.navigation_controls, image=self.downarrow, command=self.next_page)
        self.downbutton.grid(row=0, column=3, pady=8)
        self.page_label = ttk.Label(self.navigation_controls, text='page')
        self.page_label.grid(row=0, column=4, padx=5)

        # template controls
        self.template_controls = ttk.Frame(self.controls_frame)
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

        # text conversion controls
        self.conversion_controls = ttk.Frame(self.controls_frame)
        self.conversion_controls.pack(side=TOP)
        self.convert_to_text_button = ttk.Button(self.conversion_controls, text="Convert to text", command=self.convert_to_text)
        self.convert_to_text_button.pack()
        self.speak_text_button = ttk.Button(self.conversion_controls, text="Speak text", command=self.speak_text)
        self.speak_text_button.pack()

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

        engine = pyttsx3.init()
        with open("test3.txt", encoding="utf-8", newline="\n") as file:
            lines = file.readlines()
            text = "".join(lines)    
        engine.say(text)
        engine.runAndWait()
        
    def get_output_filename(self):
        if self.path:
            return os.path.basename(self.path).removesuffix(".pdf") + ".txt"
        else:
            return None
