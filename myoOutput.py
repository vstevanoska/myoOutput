from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
    
window = tk.Tk()
window.title("Myo Output")

#configure row and column size

for i in range(7):
    window.rowconfigure(i, weight=1, minsize=1)

#instantiate buttons, labels, combobox, image
recordBtn = ttk.Button(window, text="Record")
playBtn = ttk.Button(window, text="Play")
stopBtn = ttk.Button(window, text="Stop")
importBtn = ttk.Button(window, text="Import")
saveBtn = ttk.Button(window, text="Save")

movementTypeLbl = ttk.Label(window, text="Movement: ")
movementCb = ttk.Combobox(window)
movementCb['values'] = ('Pest', 'Ekstenzija', 'Fleksija', 'Ulnarna deviacija', 'Radialna deviacija', 'Pronacija', 'Supinacija', 'Nevtralen položaj')
movementCb['state'] = 'readonly'

movementImgLbl = ttk.Label(window)

img = tk.PhotoImage(file='flower.png')
imgLbl = ttk.Label(window, image=img)

#add instances to grid
movementTypeLbl.grid(row=0, column=0, sticky="ew")
movementCb.grid(row=0, column=1, sticky="ew")
movementImgLbl.grid(row=1, column=0, columnspan=2)
recordBtn.grid(row=2, column=0, columnspan=2, sticky="ew")
saveBtn.grid(row=3, column=0, columnspan=2, sticky="ew")
playBtn.grid(row=4, column=0, columnspan=2, sticky="ew")
stopBtn.grid(row=5, column=0, columnspan=2, sticky="ew")
importBtn.grid(row=6, column=0, columnspan=2, sticky="ew")
imgLbl.grid(row=0, column=2, rowspan=7)

def showMovementImg(event):

    if movementCb.get() == 'Pest':
        filename = "img/pest.png"
    elif movementCb.get() == 'Ekstenzija':
        filename = "img/ekstenzija.png"
    elif movementCb.get() == 'Fleksija':
        filename = "img/fleksija.png"
    elif movementCb.get() == 'Ulnarna deviacija':
        filename = "img/ulnarnaDeviacija.png"
    elif movementCb.get() == 'Radialna deviacija':
        filename = "img/radialnaDeviacija.png"
    elif movementCb.get() == 'Pronacija':
        filename = "img/pronacija.png"
    elif movementCb.get() == 'Supinacija':
        filename = "img/supinacija.png"
    else:
        filename = "img/nevtralenPolozaj.png"

    movementImg = ImageTk.PhotoImage(Image.open(filename).resize((250, 200)))

    movementImgLbl.configure(image=movementImg)
    movementImgLbl.image = movementImg

movementCb.bind('<<ComboboxSelected>>', showMovementImg)

window.mainloop()