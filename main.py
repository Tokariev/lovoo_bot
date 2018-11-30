from tkinter import *

root = Tk()

root.title("Lovo master")
root.minsize(500,300)
root.geometry("520x300")

Label(root, text="Profil", ).grid(row=0, column=1)
Label(root, text="Password").grid(row=0, column=2)
Label(root, text="Likes").grid(row=0, column=3)

Entry(root, width=40).grid(row=1, column=1)
Entry(root).grid(row=1, column=2)
Entry(root, width=15).grid(row=1, column=3)

def callback():
    print ("click!")

Button(root, text="OK", command=callback).grid(row=1, column=4)



root.mainloop()

