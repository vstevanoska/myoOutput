from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 

import multiprocessing
from pyomyo import Myo, emg_mode
from matplotlib import animation
import queue
import numpy as np
from matplotlib.cm import get_cmap

from tkinter.filedialog import askopenfilename

import os

q = multiprocessing.Queue()

QUEUE_SIZE = 100
RECORD_QUEUE_SIZE = 8000
SENSORS = 8
subplots = []
lines = []

plt.rcParams["figure.figsize"] = (17.5,11)

#ustvarimo sliko z 8 subploti v istem stolpcu, ki imajo skupno os x.
fig, subplots = plt.subplots(SENSORS, 1, sharex=True)
fig.tight_layout()

#barve
name = "tab10"
cmap = get_cmap(name) 
colors = cmap.colors

#izriše začetno stanje subplotov
for i in range(0,SENSORS):
	ch_line,  = subplots[i].plot(range(QUEUE_SIZE),[0]*(QUEUE_SIZE), color=colors[i])
	lines.append(ch_line)

emg_queue = queue.Queue(QUEUE_SIZE)
record_queue = queue.Queue(RECORD_QUEUE_SIZE)

def worker(q):

	m = Myo(mode=emg_mode.RAW)
	m.connect()
	
	def add_to_queue(emg, movement):
		q.put(emg)

	m.add_emg_handler(add_to_queue)

	while True:
		try:
			m.run()
		except:
			print("Worker Stopped")
			quit()

global startRecording
startRecording = False

global playingRecorded
playingRecorded = False

def animate(i):

	#če ne predvajamo uvožene datoteke
	if playingRecorded == False:
		while not(q.empty()):
			myox = list(q.get())

			if (emg_queue.full()):
				emg_queue.get()

			emg_queue.put(myox)

			#če snemamo gibanje, dodamo meritev tudi v record_queue
			if (startRecording == True):
				record_queue.put(myox)

		channels = np.array(emg_queue.queue)

		if (emg_queue.full()):

			for i in range(0,SENSORS):
				channel = channels[:,i]
				lines[i].set_ydata(channel)
				subplots[i].set_ylim(-127, 128)


	#če predvajamo uvoženo datoteko
	else:
		if not (playQueue.empty()):
			
			while emg_queue.qsize() > (QUEUE_SIZE / 2):
				emg_queue.get()

			while not (emg_queue.full()):
				emg_queue.put(playQueue.get())

			channels = np.array(emg_queue.queue)

			for i in range(0,SENSORS):
				channel = channels[:,i]
				lines[i].set_ydata(channel)
				subplots[i].set_ylim(-127, 128)

global seconds
seconds = 0

global userClicked
userClicked = False

def recordBtnClicked():

	if (len(folderEntry.get()) == 0) or (movementCb.get() == ""):
		print("Please specify the folder name and the movement!")
		return

	global startRecording
	startRecording = True

	global seconds
	global userClicked

	#ponastavitev števca
	if (userClicked):
		seconds = 0
		userClicked = False

	timerLbl.config(text = f"Elapsed time: {seconds}")

	seconds += 1

	if (seconds < 36):

		if (seconds == 35):
			startRecording = False

		#recordBtnClicked se pokliče vsakih 980 milisekund, da se poveča števec
		window.after(980, recordBtnClicked)

	else:
		startRecording = False
		userClicked = True

		print(record_queue.qsize())

		#izrežemo prvih in zadnjih nekaj vzorcev, da bi zaokrožili na 6000
		cutSize = int((record_queue.qsize() - 6000) / 2)

		if (cutSize % 2 != 0):
			cutSize += 1

		foldername = ".\\Posnetki\\" + folderEntry.get() + "\\"

		if not os.path.exists(foldername):
			os.makedirs(foldername)

		filename = foldername + str(movementCb.current()) + ".csv"

		file = open(filename, 'w')

		print("Writing to file...")

		tempQueueSize = record_queue.qsize()
		
		for j in range(0, tempQueueSize):

			if j < cutSize:
				record_queue.get()
			
			elif j < cutSize + 6000:

				popOut = record_queue.get()

				for i in range(0, len(popOut)):

					file.write(str(popOut[i]))

					if (i + 1 != len(popOut)):
						file.write(";")

				file.write('\n')

			else:
				break
			
		file.close()

		record_queue.queue.clear()

playQueue = queue.Queue(6000)

def importBtnClicked():

	filename = askopenfilename()

	f = open(filename, "r")
	
	measurementList = f.read().splitlines()

	f.close()

	#tip giba dobimo iz imena datoteke
	movementNumber = int(os.path.basename(filename).split('.')[0])

	if movementNumber == 0:
		filename = "img/pest.png"
	elif movementNumber == 1:
		filename = "img/ekstenzija.png"
	elif movementNumber == 2:
		filename = "img/fleksija.png"
	elif movementNumber == 3:
		filename = "img/ulnarnaDeviacija.png"
	elif movementNumber == 4:
		filename = "img/radialnaDeviacija.png"
	elif movementNumber == 5:
		filename = "img/pronacija.png"
	elif movementNumber == 6:
		filename = "img/supinacija.png"
	else:
		filename = "img/nevtralenPolozaj.png"

	movementImg = ImageTk.PhotoImage(Image.open(filename).resize((250, 200)))

	movementImgLbl.configure(image=movementImg)
	movementImgLbl.image = movementImg

	for line in measurementList:
		tempCharLine = line.split(';')

		tempIntLine = [eval(i) for i in tempCharLine]

		playQueue.put(tempIntLine)

	importStatusLbl.config(text = "Successfully imported!")

	recordBtn.configure(state='disabled')
	movementTypeLbl.configure(state='disabled')
	movementCb.configure(state='disabled')
	folderEntryLbl.configure(state='disabled')
	folderEntry.configure(state='disabled')

	playBtn.configure(state='normal')
	stopBtn.configure(state='normal')

	
def playBtnClicked():

	print("Started playing...")

	global playingRecorded
	playingRecorded = True

def stopBtnClicked():
	
	print("Stopping...")

	global playingRecorded
	playingRecorded = False

	recordBtn.configure(state='normal')
	movementTypeLbl.configure(state='normal')
	movementCb.configure(state='normal')
	folderEntryLbl.configure(state='normal')
	folderEntry.configure(state='normal')

	playBtn.configure(state='disabled')
	stopBtn.configure(state='disabled')

	importStatusLbl.config(text = "")


window = tk.Tk()
window.state('zoomed')
window.title("Myo Output")

global canvas
canvas = FigureCanvasTkAgg(fig, master = window)  
canvas.get_tk_widget().grid(row=0, column=2, rowspan=9)

#configure row and column size

for i in range(10):
	window.rowconfigure(i, weight=1, minsize=1)

#instantiate buttons, labels, combobox, image
recordBtn = ttk.Button(window, text="Record", command=recordBtnClicked)
importBtn = ttk.Button(window, text="Import", command=importBtnClicked)
playBtn = ttk.Button(window, text="Play", command=playBtnClicked, state='disabled')
stopBtn = ttk.Button(window, text="Stop", command=stopBtnClicked, state='disabled')

movementTypeLbl = ttk.Label(window, text="Movement: ")
movementCb = ttk.Combobox(window)
movementCb['values'] = ('Pest', 'Ekstenzija', 'Fleksija', 'Ulnarna deviacija', 'Radialna deviacija', 'Pronacija', 'Supinacija', 'Nevtralen položaj')
movementCb['state'] = 'readonly'

movementImgLbl = ttk.Label(window)
timerLbl = ttk.Label(window)
importStatusLbl = ttk.Label(window)
folderEntryLbl = ttk.Label(window, text="Folder Name: ")

folderEntry = ttk.Entry(window)

#add instances to grid
folderEntryLbl.grid(row=0, column=0, sticky="ew")
folderEntry.grid(row=0, column=1, sticky="ew")
movementTypeLbl.grid(row=1, column=0, sticky="ew")
movementCb.grid(row=1, column=1, sticky="ew")
movementImgLbl.grid(row=2, column=0, columnspan=2)
recordBtn.grid(row=3, column=0, columnspan=2, sticky="ew")
timerLbl.grid(row=4, column=0, columnspan=2, sticky="ew")
importBtn.grid(row=5, column=0, columnspan=2, sticky="ew")
importStatusLbl.grid(row=6, column=0, columnspan=2, sticky="ew")
playBtn.grid(row=7, column=0, columnspan=2, sticky="ew")
stopBtn.grid(row=8, column=0, columnspan=2, sticky="ew")

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

	while(q.empty()):
		continue

	anim = animation.FuncAnimation(fig, animate, blit=False, interval=1)

	def on_close(event):
		p.terminate()
		p.close()
		quit()

	fig.canvas.mpl_connect('close_event', on_close)

	window.mainloop()
