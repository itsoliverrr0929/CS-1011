#Joshua Chan
import tkinter
#Functions
def Try_Again():
    print("Restart")
    
def Menu():
    print("Adler Is poo.py")
#Gui Creation
lose = tkinter.Tk()
lose.geometry("720x480")

lose.config(bg="black")
lose.title("Lose Screen")

#Labels
lose_Label = tkinter.Label(lose, text= "You Lose"
, font=("Arial",50)
, fg="yellow"
, bg="black"
)
lose_Label.place(x=360, y=180, anchor= "center")

Tip_Label = tkinter.Label(lose, text= "Tip: You can shoot to move"
, font=("Arial",20)
, fg="black"
, bg="gray"
)
Tip_Label.place(x=360, y=425, anchor= "center")

highscore_Label = tkinter.Label(lose,text= "Highscore: 67"
,font= ("Arial",30)
,fg = "red"
,bg = "black"
)
highscore_Label.place(x=360,y=240, anchor= "center")

#Buttons
Play_Again= tkinter.Button(lose, text="Try Again?"
, font=("Arial",25)
, fg="yellow"
, bg = "red"
,command=Try_Again
)
Play_Again.place(x=360, y=300, anchor= "center")

Menu_Btn= tkinter.Button(lose, text="Menu"
, font=("Arial",25)
, fg="dark gray"
, bg = "gray"
,command= Menu
)
Menu_Btn.place(x=360, y=360, anchor= "center")

lose.mainloop()