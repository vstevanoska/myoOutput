from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
	
#myo includes
import multiprocessing
from pyomyo import Myo, emg_mode
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.cm import get_cmap
import queue
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

q = multiprocessing.Queue()

def worker(q):
	
	m = Myo(mode=emg_mode.PREPROCESSED)
	#m = Myo(mode=emg_mode.RAW)
	m.connect()
	
	def add_to_queue(emg, movement):
		q.put(emg)
		#print(emg)
		
#	def print_battery(bat):
#		print("Battery level:", bat)

	# Orange logo and bar LEDs
#	m.set_leds([128, 0, 0], [128, 0, 0])
	# Vibrate to know we connected okay
#	m.vibrate(1)
#	m.add_battery_handler(print_battery)
	m.add_emg_handler(add_to_queue)
	
#	"""worker function"""
	while True:
		try:
			m.run()
		except:
			#m.stop()
			print("Worker Stopped")
			quit()

def animate():
	# Myo Plot

	#while True: 

	while not(q.empty()):
		myox = list(q.get())
		print("myox: " + myox)
		if (emg_queue.full()):
			emg_queue.get()
		emg_queue.put(myox)

	channels = np.array(emg_queue.queue)

	if (emg_queue.full()):
		for i in range(0,SENSORS):
			channel = channels[:,i]
			print(channel)
			lines[i].set_ydata(channel)
			subplots[i].set_ylim(0,max(1024,max(channel)))
		canvas = FigureCanvasTkAgg(fig, master = window)  
		canvas.draw()
		canvas.get_tk_widget().grid(row=0, column=2, rowspan=7)
		print("Canvas updated!")
  
	# placing the canvas on the Tkinter window
	#canvas.get_tk_widget().pack()

def animationStart():
#	print("Hi")
	animation.FuncAnimation(fig, animate, blit=False, interval=2)

# ------------ Plot Setup ---------------
QUEUE_SIZE = 100
SENSORS = 8
subplots = []
lines = []
# Set the size of the plot
plt.rcParams["figure.figsize"] = (18,11)
# using the variable axs for multiple Axes

#fig.tight_layout()
# Set each line to a different color

name = "tab10" # Change this if you have sensors > 10
cmap = get_cmap(name)  # type: matplotlib.colors.ListedColormap
colors = cmap.colors  # type: list

#main
window = tk.Tk()
window.state('zoomed')
window.title("Myo Output")

fig, subplots = plt.subplots(SENSORS, 1, sharex='all')

global onUpdate
onUpdate = False

global canvas
canvas = FigureCanvasTkAgg(fig, master = window)  
canvas.get_tk_widget().grid(row=0, column=2, rowspan=7)

emg_queue = queue.Queue(QUEUE_SIZE)

def test2(i):

	#global canvas
	if (emg_queue.full()):
		canvas.draw()
		canvas.get_tk_widget().update()

def testThread(q):
	#global canvas

	while True:
		while not(q.empty()):
			emg = list(q.get())
			print(emg)
			if (emg_queue.full()):
				emg_queue.get()
			emg_queue.put(emg)

		channels = np.array(emg_queue.queue)

		if (emg_queue.full()):
			for i in range(0,SENSORS):
				channel = channels[:,i]
				#print(channel)
				lines[i].set_ydata(channel)
				subplots[i].set_ylim(0,max(1024,max(channel)))
			#canvas = FigureCanvasTkAgg(fig, master = window)  
			#canvas.draw()
			#canvas.get_tk_widget().grid(row=0, column=2, rowspan=7)
			#canvas.get_tk_widget().update()
			#print("Canvas updated!")

for i in range(0,SENSORS):
	ch_line,  = subplots[i].plot(range(QUEUE_SIZE),[0]*(QUEUE_SIZE), color=colors[i])
	lines.append(ch_line)

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

#img = tk.PhotoImage(file='flower.png')
#imgLbl = ttk.Label(window, image=img)
#imgLbl = ttk.Label(window)

#add instances to grid
movementTypeLbl.grid(row=0, column=0, sticky="ew")
movementCb.grid(row=0, column=1, sticky="ew")
movementImgLbl.grid(row=1, column=0, columnspan=2)
recordBtn.grid(row=2, column=0, columnspan=2, sticky="ew")
saveBtn.grid(row=3, column=0, columnspan=2, sticky="ew")
playBtn.grid(row=4, column=0, columnspan=2, sticky="ew")
stopBtn.grid(row=5, column=0, columnspan=2, sticky="ew")
importBtn.grid(row=6, column=0, columnspan=2, sticky="ew")
#imgLbl.grid(row=0, column=2, rowspan=7)

#fig = Figure(figsize = (5, 5), dpi = 100)
  
	# list of squares
#y = [i**2 for i in range(101)]
  
	# adding the subplot
#plot1 = fig.add_subplot(111)
  
	# plotting the graph
#plot1.plot(y)
  
	# creating the Tkinter canvas
	# containing the Matplotlib figure
#canvas.draw()
  
	# placing the canvas on the Tkinter window


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

	# Start Myo Process
	p = multiprocessing.Process(target=worker, args=(q,))
	p.start()

	#thread2 = multiprocessing.Process(target=animationStart)
	#thread2 = multiprocessing.Process(target=animate)
	thread2 = multiprocessing.Process(target=testThread, args=(q,))
	thread2.start()

	anim = animation.FuncAnimation(fig, test2, blit=False, interval=2)

	#while(q.empty()):
		# Wait until we actually get data
	#	continue

	def on_close(event):
		p.terminate()
		thread2.terminate()
		p.close()
		thread2.close()
		quit()
#		raise KeyboardInterrupt
	#	print("On close has ran")
#		plt.close()
	fig.canvas.mpl_connect('close_event', on_close)

	#try:
	#	plt.show()
	#except KeyboardInterrupt:
	#	plt.close()
	#	p.close()
	#	quit()

	window.mainloop()
