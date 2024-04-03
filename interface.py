from tkinter import *
from tkinter import ttk
from tesseract_ocr import tesseractOCR
from customtkinter import CTk, CTkButton
from tkinter import filedialog
from pdf2image import convert_from_path

class UserInterface:
    def __init__(self):
        # self.root = Tk()
        self.root = CTk()
        self.root.title("Barrett")
        self.root.geometry("450x350")

        self.user = (0, 1, 2, 3, 4, 5)
        self.doctor = ('Médico 1', 'Médico 2', 'Médico 3', 'Médico 4', 'Médico 5')
        self.cnames = StringVar(value=self.doctor)
        self.lens = ('Personal Constant', 'Alcon SN60WF', 'Alcon SN6AD', 'Alcon SN6ATx', 'Alcon SND1Tx', 'Alcon SV25Tx', 'Alcon TFNTx', 'Alcon DFTx', 'Alcon SA60AT', 'Alcon MN60MA', 'J&J ZCB00', 'J&J ZCT', 'J&J ZCT(USA)', \
                     'J&J ZCU', 'J&J DIU', 'J&J ZKU', 'J&J ZLU', 'J&J AR40e', 'J&J AR40M', 'J&J ZXR00', 'J&J ZXT', 'J&J ZHR00V', 'J&J ZHW', 'Zeiss 409M', 'Zeiss 709M', 'Hoya iSert 251', 'Hoya iSert 351', 'Bausch & Lomb MX60', \
                        'Bausch & Lomb MX60T', 'Bausch & Lomb MX60ET', 'Bausch & Lomb MX60ET(USA)', 'Bausch & Lomb BL1UT', 'Bausch & Lomb LI60AO', 'MBI T302A', 'Lenstec SBL-3', 'SIFI Mini WELL', 'Ophtec 565')
        self.clens = StringVar(value=self.lens)
        self.incisionSia = {0:0.1, 1:0.2, 2:0.3, 3:0.4, 4:0.5, 5:0.6}
        self.incisionLoc = {0:100, 1:105, 2:110, 3:115, 4:120, 5:125}
        self.incisionSiaOE = {0:0.1, 1:0.2, 2:0.3, 3:0.4, 4:0.5, 5:0.6}
        self.incisionLocOE = {0:100, 1:105, 2:110, 3:115, 4:120, 5:125}
        self.eye = StringVar()
        self.statusmsg = StringVar()

        # Create and grid the outer content frame
        self.c = ttk.Frame(self.root, padding=(5, 5, 12, 0))
        self.c.grid(column=0, row=0, sticky=(N,W,E,S))
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.lbox = Listbox(self.c, listvariable=self.cnames, height=5, exportselection=0)
        self.lbox2 = Listbox(self.c, listvariable=self.clens, height=5, exportselection=0)
        lbl = ttk.Label(self.c, text="Médico:")
        lbl2 = ttk.Label(self.c, text="Olho:")
        lbl3 = ttk.Label(self.c, text="Lente:")
        g1 = ttk.Radiobutton(self.c, text='Direito', variable=self.eye, value='1')
        g2 = ttk.Radiobutton(self.c, text='Esquerdo', variable=self.eye, value='2')
        g3 = ttk.Radiobutton(self.c, text='Direito + Esquerdo', variable=self.eye, value='3')
        send = CTkButton(self.c, text='Calcular', command = self.send_data)
        # send = ttk.Button(self.c, text='Calcular', command=self.send_data, default='active')
        # status = ttk.Label(self.c, textvariable=self.statusmsg, anchor=W)
        btn = CTkButton(self.c, text ='Selecionar arquivo', command = lambda:self.open_file())
        # btn2 = ttk.Button(self.c, text='PENTACAM', command = lambda:self.open_file(), state=DISABLED)
        self.btn2 = CTkButton(self.c, text ='PENTACAM', command = lambda:self.open_file(), state=DISABLED)

        # Grid all the widgets
        self.lbox.grid(column=0, row=1, rowspan=6, sticky=(N,S,E,W))
        self.lbox2.grid(column=2, row=1, rowspan=6, sticky=(N,S,E,W))
        lbl.grid(column=0, row=0, sticky=W, padx=0, pady=5)
        lbl2.grid(column=1, row=0, sticky=W, padx=10, pady=5)
        lbl3.grid(column=2, row=0, sticky=W, padx=0, pady=5)
        g1.grid(column=1, row=1, sticky=W, padx=20)
        g2.grid(column=1, row=2, sticky=W, padx=20)
        g3.grid(column=1, row=3, sticky=W, padx=20)
        send.grid(column=2, row=7, sticky=E)
        btn.grid(column=1, row=7, sticky=E, padx = 10, pady= 10)
        self.btn2.grid(column=0, row=7, sticky=E, padx = 10, pady= 10)
        # status.grid(column=0, row=6, columnspan=2, sticky=(W,E))
        self.c.grid_columnconfigure(0, weight=1)
        self.c.grid_rowconfigure(5, weight=1)

        # Set event bindings for when the selection in the listbox changes,
        # when the user double clicks the list, and when they hit the Return key
        self.lbox.bind('<<ListboxSelect>>', self.surgeryData)
        self.root.bind('<Return>', self.send_data)

        # Colorize alternating lines of the listbox
        for i in range(0,len(self.doctor),2):
            self.lbox.itemconfigure(i, background='#f0f0ff')

        for i in range(0,len(self.lens),2):
            self.lbox2.itemconfigure(i, background='#f0f0ff')

        self.surgeryData()
        self.root.mainloop()

    def surgeryData(self, *args):
        idxs = self.lbox.curselection()
        if len(idxs) == 1:
            idx = int(idxs[0])
            name = self.doctor[idx]
            if name == 'Médico 1' or name == 'Médico 2':
                self.btn2.configure(state=NORMAL)
            else:
                self.btn2.configure(state=DISABLED)

    def send_data(self, *args):
        idxs = self.lbox.curselection()
        idxs2 = self.lbox2.curselection()
        if len(idxs)==1:
            idx = int(idxs[0])
            self.lbox.see(idx)
            name = self.doctor[idx]
            sia = self.incisionSia[idx]
            loc = self.incisionLoc[idx]
            siaOE = self.incisionSiaOE[idx]
            locOE = self.incisionLocOE[idx]

        if len(idxs2)==1:
            idx2 = int(idxs2[0])
            self.lbox.see(idx2)
            lente = self.lens[idx2]
            olho = self.eye.get()
            if olho == '1':
                tesseractOCR(name, lente, sia, loc, olho)
            elif olho == '2':
                tesseractOCR(name, lente, siaOE, locOE, olho)
            elif olho == '3':
                tesseractOCR(name, lente, sia, loc, '1')
                tesseractOCR(name, lente, siaOE, locOE, '2')

    def open_file(self):
        file = filedialog.askopenfilename(filetypes =[('PDF Files', '*.pdf')])
        if file is not None:
            print(file)
            images = convert_from_path(file, 300)
            images[0].save(r'C:\Scripts\assets\images\img.jpg', 'JPEG')        

    def create_ui(self):
        self.root.mainloop()

if __name__ == '__main__':
    UI = UserInterface()
    UI.create_ui()
