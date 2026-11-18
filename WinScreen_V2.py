# Oliver Ho

import tkinter


# Button functions
def try_again():
    print("Restart")


def open_menu():
    print("Menu")


# Window setup
win = tkinter.Tk()
win.geometry("720x480")
win.config(bg="#74b560")
win.title("Win Screen")


# Decorative background panel
victory_panel = tkinter.Frame(
    win,
    width=600,
    height=410,
    bg="#fff3c4",
    highlightbackground="#9c7734",
    highlightthickness=6
)
victory_panel.place(x=360, y=240, anchor="center")
victory_panel.pack_propagate(False)


# Victory title
win_label = tkinter.Label(
    victory_panel,
    text="YOU WIN!",
    font=("Arial", 50, "bold"),
    fg="#db7f1d",
    bg="#fff3c4"
)
win_label.place(x=300, y=65, anchor="center")


# Victory message
message_label = tkinter.Label(
    victory_panel,
    text="Congratulations!",
    font=("Arial", 22, "bold"),
    fg="#2c6e49",
    bg="#fff3c4"
)
message_label.place(x=300, y=125, anchor="center")


# Score
score_label = tkinter.Label(
    victory_panel,
    text="Score: 127",
    font=("Arial", 30, "bold"),
    fg="#352461",
    bg="#fff3c4"
)
score_label.place(x=300, y=175, anchor="center")


# Time survived
time_label = tkinter.Label(
    victory_panel,
    text="Time Survived: 5:00",
    font=("Arial", 20),
    fg="#352461",
    bg="#fff3c4"
)
time_label.place(x=300, y=220, anchor="center")


# Play again button
play_again_button = tkinter.Button(
    victory_panel,
    text="Play Again?",
    font=("Arial", 22, "bold"),
    fg="white",
    bg="#db7f1d",
    activeforeground="white",
    activebackground="#b96512",
    width=14,
    command=try_again
)
play_again_button.place(x=300, y=285, anchor="center")


# Menu button
menu_button = tkinter.Button(
    victory_panel,
    text="Menu",
    font=("Arial", 20),
    fg="white",
    bg="#2c6e49",
    activeforeground="white",
    activebackground="#1b4d33",
    width=10,
    command=open_menu
)
menu_button.place(x=300, y=345, anchor="center")


win.mainloop()