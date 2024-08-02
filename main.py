from tkinter import *
from src.pdfviewer import PDFViewer
# import pypdf

# pdffileobj = open('test2.pdf', 'rb')
# file1=open(r"test2.txt","a")

# pdfreader = pypdf.PdfReader(pdffileobj)

# def visitor_body(text, cm, tm, fontDict, fontSize):
#     y = tm[5]
#     if y > 50 and y < 720:
#         file1.writelines(text)


# num_pages = len(pdfreader.pages)

# for i in range(num_pages):
#     pageobj = pdfreader.pages[i]
#     file1.writelines(pageobj.extract_text(0, extraction_mode="layout"))


root = Tk()
app = PDFViewer(root)

root.mainloop()

# import pyttsx3
# engine = pyttsx3.init()
# with open("test3.txt", encoding="utf-8", newline="\n") as file:
#     lines = file.readlines()
#     for line in lines:
#         engine.say(line)
#     # text = "".join(lines)
#     # print(text)

# # engine.say(text)
# engine.runAndWait()

# from gtts import gTTS
# tts = gTTS(text, lang='de')
# tts.save('hello.mp3')

# import os

# def text_to_speech(text):
#     os.system(f"espeak -v mb-de1 '{text}'")

# text_to_speech("Hallo, hier bin ich!")
