from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 

import multiprocessing
from pyomyo import Myo, emg_mode

q = multiprocessing.Queue()

def worker(q):
	m = Myo(mode=emg_mode.PREPROCESSED)
	m.connect()
	
	def add_to_queue(emg, movement):
		q.put(emg)
		print(emg)

	m.add_emg_handler(add_to_queue)

	"""worker function"""
	while True:
		try:
			m.run()
		except:
			print("Worker Stopped")
			quit()

window = tk.Tk()
window.state('zoomed')
window.title("Myo Output")

plt.rcParams["figure.figsize"] = (17.5,11)

SENSORS = 8
fig, subplots = plt.subplots(SENSORS, 1, sharex=True)

global canvas
canvas = FigureCanvasTkAgg(fig, master = window)  
canvas.get_tk_widget().grid(row=0, column=2, rowspan=7)

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


#add instances to grid
movementTypeLbl.grid(row=0, column=0, sticky="ew")
movementCb.grid(row=0, column=1, sticky="ew")
movementImgLbl.grid(row=1, column=0, columnspan=2)
recordBtn.grid(row=2, column=0, columnspan=2, sticky="ew")
saveBtn.grid(row=3, column=0, columnspan=2, sticky="ew")
playBtn.grid(row=4, column=0, columnspan=2, sticky="ew")
stopBtn.grid(row=5, column=0, columnspan=2, sticky="ew")
importBtn.grid(row=6, column=0, columnspan=2, sticky="ew")


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

if __name__ == '__main__':

	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()

	def on_close(event):
		p.terminate()
		p.close()
		quit()

	fig.canvas.mpl_connect('close_event', on_close)

	window.mainloop()
