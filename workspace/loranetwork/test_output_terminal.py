from tkinter import *


def str2int(s):
    try:
        k = int(s)
        return k
    except:
        return 0


class ConsoleLogApplication(object):
    def __init__(self, parent):
        self.name = StringVar()
        self.parent = parent
        self.scrollbar = Scrollbar(parent)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.messages = Listbox(parent, bd="7", yscrollcommand=self.scrollbar.set, relief=RIDGE,
                                selectbackground="#56D548", selectmode=BROWSE, font="bold", fg="green")
        self.messages.pack({"side": "top", "expand": "yes", "fill": "both"})
        self.scrollbar.config(command=self.messages.yview)

        self.StatusBar = Label(parent, text="...")
        self.StatusBar['background'] = "#FFFFFF"
        self.StatusBar['foreground'] = "blue"
        self.StatusBar.pack({"side": "bottom", "expand": "no", "fill": "x"})

    def print(self, message):
        m = Label(self.parent, text=message)
        self.messages.insert(END, message)


def main():
    root = Tk()
    root.geometry("600x600")
    myapp = ConsoleLogApplication(root)
    for i in range(100):
        myapp.print("Ciao")
        myapp.print("bella")
        myapp.print("come")
        myapp.print("stai")
        myapp.print("***")

    root2 = Tk()
    root2.geometry("600x600")
    myapp2 = ConsoleLogApplication(root2)
    for i in range(100):
        myapp2.print("Ciao")
        myapp2.print("bella")
        myapp2.print("come")
        myapp2.print("stai")
        myapp2.print("***")
    root.mainloop()
    root2.mainloop()


if __name__ == '__main__':
    main()

