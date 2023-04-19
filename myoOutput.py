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

#import time
from tkinter.filedialog import askopenfilename

q = multiprocessing.Queue()

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

# ------------ Plot Setup ---------------
QUEUE_SIZE = 100
RECORD_QUEUE_SIZE = 8000
SENSORS = 8
subplots = []
lines = []
# Set the size of the plot
plt.rcParams["figure.figsize"] = (17.5,11)
# using the variable axs for multiple Axes
fig, subplots = plt.subplots(SENSORS, 1, sharex=True)
#fig.canvas.manager.set_window_title("8 Channel EMG plot")
fig.tight_layout()
# Set each line to a different color

name = "tab10"
cmap = get_cmap(name) 
colors = cmap.colors

for i in range(0,SENSORS):
	ch_line,  = subplots[i].plot(range(QUEUE_SIZE),[0]*(QUEUE_SIZE), color=colors[i])
	lines.append(ch_line)

emg_queue = queue.Queue(QUEUE_SIZE)
record_queue = queue.Queue(RECORD_QUEUE_SIZE)

global startRecording
startRecording = False

global playingRecorded
playingRecorded = False

def animate(i):
	# Myo Plot

	if playingRecorded == False:
		while not(q.empty()):
			myox = list(q.get())

			if (emg_queue.full()):
				emg_queue.get()

			emg_queue.put(myox)
			#print(emg_queue.queue)

			if (startRecording == True):
				record_queue.put(myox)
				#print(record_queue.qsize())

		channels = np.array(emg_queue.queue)

		if (emg_queue.full()):

			for i in range(0,SENSORS):
				channel = channels[:,i]
				lines[i].set_ydata(channel)
				#subplots[i].set_ylim(0,max(1024,max(channel)))
				subplots[i].set_ylim(-127, 128)


	else:
		if not (playQueue.empty()):
			
			emg_queue.queue.clear()

			while not (emg_queue.full()):
				emg_queue.put(playQueue.get())

			channels = np.array(emg_queue.queue)

			for i in range(0,SENSORS):
				channel = channels[:,i]
				lines[i].set_ydata(channel)
				#subplots[i].set_ylim(0,max(1024,max(channel)))
				subplots[i].set_ylim(-127, 128)


global seconds
seconds = 0

global timerStarted
timerStarted = False

global startTime

def recordBtnClicked():

	global startRecording
	startRecording = True

	global timerStarted
	#global startTime

	if (timerStarted == False):
		timerStarted = True
		#startTime = time.time()

	global seconds

	#seconds = time.time() - startTime

	timerLbl.config(text = f"Elapsed time: {seconds}")

	seconds += 1

	if (seconds < 36):

		if (seconds == 35):
			startRecording = False

		window.after(980, recordBtnClicked)
		#print(record_queue.qsize())

	else:
		startRecording = False

		print(record_queue.qsize())

		cutSize = int((record_queue.qsize() - 6000) / 2)

		if (cutSize % 2 != 0):
			cutSize += 1

		file = open('test.csv', 'w')

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

playQueue = queue.Queue(6000)
global playArray
playArray = np.array([])

def importBtnClicked():

	#filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
	filename = "C:\\Users\\Viktorija\\Desktop\\NNKR\\N1\\out\\myoOutput\\test.csv"

	f = open(filename, "r")
	
	measurementList = f.read().splitlines()

	#print(measurementList[0])

	f.close()

	#global playArray

	for line in measurementList:
		tempCharLine = line.split(';')

		tempIntLine = [eval(i) for i in tempCharLine]

		playQueue.put(tempIntLine)
		#temp = np.array(tempIntLine)
		#playArray = np.concatenate((playArray, temp))

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
		# Wait until we actually get data
		continue

	anim = animation.FuncAnimation(fig, animate, blit=False, interval=1)

	def on_close(event):
		p.terminate()
		p.close()
		quit()

	fig.canvas.mpl_connect('close_event', on_close)

	window.mainloop()
