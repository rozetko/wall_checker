import Tkinter as Tk

class Gui(object):
	def __init__(self):
		self.result = ()		
		self.main()

	def focusNextWindow(self, event):
	    event.widget.tk_focusNext().focus()
	    return("break")
		
	def main(self):
		self.window = Tk.Tk()
		self.window.title("Login")
		
		self.canvas = Tk.Canvas(self.window, width=240, height=300)
		self.canvas.pack(fill='both', expand='yes')
		
		self.label = Tk.Label(self.window, text = 'Login:').place(x = 50, y = 45)
		
		self.login = Tk.Text(height=1, width=18)
		self.login.place(x = 50, y = 75)

		self.label = Tk.Label(self.window, text = 'Password:').place(x = 50, y = 120)
		
		self.password = Tk.Text(height=1, width=18)
		self.password.place(x = 50, y = 150)
		self.password.bind('<Return>', self.send)

		self.OK = Tk.Button(self.window, text = 'Log in')
		self.OK.place(x = 100, y = 200)
		self.OK.bind('<Button-1>', self.send)
		self.OK.bind('<Return>', self.send)

		self.login.bind('<Tab>', self.focusNextWindow)
		self.password.bind('<Tab>', self.focusNextWindow)
		self.OK.bind('<Tab>', self.focusNextWindow)

		self.center()

		self.window.mainloop()

	def center(self):
		self.window.update_idletasks()

		width = self.window.winfo_width()
		height = self.window.winfo_height()
		x = (self.window.winfo_screenwidth() // 2) - (width // 2)
		y = (self.window.winfo_screenheight() // 2) - (height // 2)

		self.window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
		
	def send(self, event):
		self.result = (self.login.get("1.0", "end-1c"), self.password.get("1.0", "end-1c"))

		self.window.destroy()

if __name__ == '__main__':
	Gui()