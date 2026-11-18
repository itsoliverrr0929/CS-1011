import tkinter

Menu = tkinter.Tk()
Menu.geometry("720x480")
Menu.config(bg="black")
Menu.title("Menu Screen")

#Labels
title_Label = tkinter.Label(Menu, text="Monster Slayers",font=("Arial",40), fg="yellow", bg="green")
title_Label.place(x=360, y=180, anchor= "center")

#Button
Play_Button= tkinter.Button(Menu, text="     Play     ", font=("Arial",30), fg="black",bg="red")
Play_Button.place(x=360,y=250,anchor="center")
Credits_Button= tkinter.Button(Menu, text="Credits", font=("Arial",30), fg="dark gray",bg="gray")
Credits_Button.place(x=360,y=330,anchor="center")

Menu.mainloop()