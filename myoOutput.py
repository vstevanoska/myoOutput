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

q = multiprocessing.Queue()

def worker(q):
	
	m = Myo(mode=emg_mode.PREPROCESSED)
	#m = Myo(mode=emg_mode.RAW)
	m.connect()
	
	def add_to_queue(emg, movement):
		q.put(emg)
		
	def print_battery(bat):
		print("Battery level:", bat)

	# Orange logo and bar LEDs
	m.set_leds([128, 0, 0], [128, 0, 0])
	# Vibrate to know we connected okay
	m.vibrate(1)
	m.add_battery_handler(print_battery)
	m.add_emg_handler(add_to_queue)
	
	"""worker function"""
	while True:
		try:
			m.run()
		except:
			print("Worker Stopped")
			quit()

def animate(i):
	# Myo Plot
	while not(q.empty()):
		myox = list(q.get())
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
  
	# placing the canvas on the Tkinter window
	#canvas.get_tk_widget().pack()

# ------------ Plot Setup ---------------
QUEUE_SIZE = 100
SENSORS = 8
subplots = []
lines = []
# Set the size of the plot
plt.rcParams["figure.figsize"] = (4,8)
# using the variable axs for multiple Axes
fig, subplots = plt.subplots(SENSORS, 1)
fig.canvas.manager.set_window_title("8 Channel EMG plot")
fig.tight_layout()
# Set each line to a different color

name = "tab10" # Change this if you have sensors > 10
cmap = get_cmap(name)  # type: matplotlib.colors.ListedColormap
colors = cmap.colors  # type: list

for i in range(0,SENSORS):
	ch_line,  = subplots[i].plot(range(QUEUE_SIZE),[0]*(QUEUE_SIZE), color=colors[i])
	lines.append(ch_line)

emg_queue = queue.Queue(QUEUE_SIZE)

#main
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

#img = tk.PhotoImage(file='flower.png')
#imgLbl = ttk.Label(window, image=img)
imgLbl = ttk.Label(window)

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

	while(q.empty()):
		# Wait until we actually get data
		continue

	anim = animation.FuncAnimation(fig, animate, blit=False, interval=2)

	def on_close(event):
		p.terminate()
		#raise KeyboardInterrupt
		#print("On close has ran")
		plt.close()
		p.close()
		quit()
	fig.canvas.mpl_connect('close_event', on_close)

	#try:
#		plt.show()
#	except KeyboardInterrupt:
#		plt.close()
#		p.close()
#		quit()

	window.mainloop()