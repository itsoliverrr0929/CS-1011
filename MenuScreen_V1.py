import tkinter

Menu = tkinter.Tk()
Menu.geometry("1280x720")
Menu.config(bg="black")
Menu.title("Menu Screen")

#Labels
title_Label = tkinter.Label(Menu, text="Monster Slayers",font=("Impact",60), fg="yellow", bg="green")
title_Label.place(x=640, y=300, anchor="center")

def doPlay():
    Menu.destroy()
    import main

#Button
Play_Button= tkinter.Button(Menu, text="     Play     ", font=("Arial",30), fg="black",bg="red", command=doPlay)
Play_Button.place(x=640,y=500,anchor="center")
Credits_Button= tkinter.Button(Menu, text="Credits", font=("Arial",30), fg="dark gray",bg="gray")
Credits_Button.place(x=640,y=660,anchor="center")

Menu.mainloop()