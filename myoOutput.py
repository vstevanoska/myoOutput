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

import time


#Retrieving a recording and showing it


q = multiprocessing.Queue()

def worker(q):
	m = Myo(mode=emg_mode.RAW)
	m.connect()
	
	def add_to_queue(emg, movement):
		q.put(emg)

	m.add_emg_handler(add_to_queue)

	"""worker function"""
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

def animate(i):
	# Myo Plot
	while not(q.empty()):
		myox = list(q.get())

		if (emg_queue.full()):
			emg_queue.get()

		emg_queue.put(myox)

		if (startRecording == True):
			#print(startRecording)
			record_queue.put(myox)
			#print(record_queue.qsize())

	channels = np.array(emg_queue.queue)

	if (emg_queue.full()):
		for i in range(0,SENSORS):
			channel = channels[:,i]
			lines[i].set_ydata(channel)
			#subplots[i].set_ylim(0,max(1024,max(channel)))
			subplots[i].set_ylim(-127, 128)

def timerFunction(): 
	#start = time.time()

	#elapsedTime = time.time() - start
	#while (elapsedTime < 35):
	#	temp = "Elapsed time: " + str(elapsedTime)

	#	print(temp)

	#	timerLbl.config(text=temp)
	#	timerLbl.update()

	#	elapsedTime = time.time() - start

	if seconds < 35:
		timerLbl.config(text = "Elapsed time: {}".format(seconds))
		timerLbl.after(1000, timerFunction) # call this method again in 1,000 milliseconds
		seconds += 1

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
			cutSize -= 1

		file = open('test.txt', 'w')

		print("Writing to file...")

		for j in range(0, record_queue.qsize()):

			if j < cutSize:
				record_queue.get()
			
			elif j < cutSize + 6000:

				popOut = record_queue.get()

				for i in range(0, len(popOut)):

					file.write(str(popOut[i]))

					if (i + 1 != len(popOut)):
						file.write(";")

				if ((j + 1) != record_queue.qsize()):
					file.write('\n')

			else:
				break
			
		file.close()

		print("Done")


window = tk.Tk()
window.state('zoomed')
window.title("Myo Output")

global canvas
canvas = FigureCanvasTkAgg(fig, master = window)  
canvas.get_tk_widget().grid(row=0, column=2, rowspan=8)

#configure row and column size

for i in range(8):
	window.rowconfigure(i, weight=1, minsize=1)

#instantiate buttons, labels, combobox, image
recordBtn = ttk.Button(window, text="Record", command=recordBtnClicked)
playBtn = ttk.Button(window, text="Play")
stopBtn = ttk.Button(window, text="Stop")
importBtn = ttk.Button(window, text="Import")
saveBtn = ttk.Button(window, text="Save")

movementTypeLbl = ttk.Label(window, text="Movement: ")
movementCb = ttk.Combobox(window)
movementCb['values'] = ('Pest', 'Ekstenzija', 'Fleksija', 'Ulnarna deviacija', 'Radialna deviacija', 'Pronacija', 'Supinacija', 'Nevtralen položaj')
movementCb['state'] = 'readonly'

movementImgLbl = ttk.Label(window)
timerLbl = ttk.Label(window)

#add instances to grid
movementTypeLbl.grid(row=0, column=0, sticky="ew")
movementCb.grid(row=0, column=1, sticky="ew")
movementImgLbl.grid(row=1, column=0, columnspan=2)
recordBtn.grid(row=2, column=0, columnspan=2, sticky="ew")
timerLbl.grid(row=3, column=0, columnspan=2, sticky="ew")
saveBtn.grid(row=4, column=0, columnspan=2, sticky="ew")
importBtn.grid(row=5, column=0, columnspan=2, sticky="ew")
playBtn.grid(row=6, column=0, columnspan=2, sticky="ew")
stopBtn.grid(row=7, column=0, columnspan=2, sticky="ew")


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
