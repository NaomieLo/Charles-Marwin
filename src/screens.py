import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import Entry
from tkinter import font as tkFont
from PIL import Image, ImageTk
from robot import Robot

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../data")))
from database import *

# SELECT THE ROBOT AND PFA helper
class Scroller(tk.Frame):
    def __init__(self, parent, title, items, bg_color, *args, **kwargs):
        super().__init__(parent, bg=bg_color, *args, **kwargs)
        self.items = items
        self.index = 0

        title_label = tk.Label(self, text=title, bg=bg_color, font=("Orbitron", 16))
        title_label.pack(pady=5)

        content_frame = tk.Frame(self, bg=bg_color)
        content_frame.pack(pady=5)

        left_button = tk.Button(
            content_frame, text="<", command=self.prev_item, font=("Roboto", 14)
        )
        left_button.pack(side="left", padx=5)

        self.item_label = tk.Label(
            content_frame,
            text=str(self.items[self.index]),
            width=20,
            height=5,
            bg="white",
            relief="solid",
            font=("Roboto", 14),
        )
        self.item_label.pack(side="left", padx=5)

        right_button = tk.Button(
            content_frame, text=">", command=self.next_item, font=("Roboto", 14)
        )
        right_button.pack(side="left", padx=5)

    def prev_item(self):
        self.index = (self.index - 1) % len(self.items)
        self.update_display()

    def next_item(self):
        self.index = (self.index + 1) % len(self.items)
        self.update_display()

    def update_display(self):
        self.item_label.config(text=str(self.items[self.index]))

class Table(tk.Frame):

    def __init__(self, root, rows, columns, content):
        super().__init__(root, bg="#011936")
        self._widgets = []
        for r in range(rows):
            current_row = []
            for c in range(columns):
                label = tk.Label(self, borderwidth=0, width=10)
                label.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for col in range(columns):
            self.grid_columnconfigure(col, weight=1)

        self._widgets[0][0].configure(text="Start", font=("Orbitron, 12"))
        self._widgets[0][1].configure(text="End", font=("Orbitron, 12"))
        self._widgets[0][2].configure(text="Robot", font=("Orbitron, 12"))
        self._widgets[0][3].configure(text="AI", font=("Orbitron, 12"))
        self._widgets[0][4].configure(text="Distance", font=("Orbitron, 12"))
        self._widgets[0][5].configure(text="Time", font=("Orbitron, 12"))
        self._widgets[0][6].configure(text="Cost", font=("Orbitron, 12"))

        last_ten = content[(len(content)-11):len(content)]

        i = 10

        for r in range(1,11):
            for c in range (columns):
                widget = self._widgets[r][c]
                widget.configure(text="%s"%(last_ten[i][c]), font=("Orbitron, 12"))
            i -= 1

class ToggledFrame(tk.Frame):

    def __init__(self, parent, text="", *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)

        self.show = tk.IntVar()
        self.show.set(0)

        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill="x", expand=1)

        ttk.Label(self.title_frame, text=text, font=("Orbitron", 20)).pack(side="left", fill="x", expand=1)

        self.toggle_button = ttk.Checkbutton(self.title_frame, width=2, text='+', command=self.toggle,
                                            variable=self.show, style='Toolbutton')
        self.toggle_button.pack(side="left")

        self.sub_frame = tk.Frame(self, relief="sunken", borderwidth=1)

    def toggle(self):
        if bool(self.show.get()):
            self.sub_frame.pack(fill="x", expand=1)
            self.toggle_button.configure(text='-')
        else:
            self.sub_frame.forget()
            self.toggle_button.configure(text='+')

# Driver class to connect all the screens
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Charles Marwin")
        self.geometry("800x600")
        self.resizable(True, True)
        self.robot = Robot("Default", "None")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # load background and logo images
        try:
            self.welcome_bg_orig = Image.open("src/images/welcome_bg.png")
            self.welcome_bg = ImageTk.PhotoImage(self.welcome_bg_orig)
        except Exception as e:
            self.welcome_bg = None
            self.welcome_bg_orig = None

        try:
            self.logo_img = PhotoImage(file="src/images/logo.png")
        except Exception as e:
            self.logo_img = None
        try:
            self.logo_orig = Image.open("src/images/logo.png")
        except Exception as e:
            self.logo_orig = None

        try:
            self.station_orig = Image.open("src/images/station.png")
            self.station_img = ImageTk.PhotoImage(self.station_orig)
        except Exception as e:
            self.station_orig = None
            self.station_img = None

        # store the screens in a dictionary 
        self.frames = {}
        for F in (WelcomeScreen, MainMenuScreen, SelectionScreen, SpawnScreen, DummyPage, FinishScreen, MetricDisplay, HistoryScreen):
            page_name = F.__name__
            if page_name == "WelcomeScreen":
                frame = F(parent=container, controller=self, bg_image=self.welcome_bg, logo_image=self.logo_img)
            elif page_name == "MainMenuScreen":
                frame = F(parent=container, controller=self, logo_image=self.logo_img)
            else:
                frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("WelcomeScreen")

    def show_frame(self, page_name):
        """Raise the frame corresponding to the given page name."""
        frame = self.frames[page_name]
        frame.tkraise()


# Welcome Screen
class WelcomeScreen(tk.Frame):
    def __init__(self, parent, controller, bg_image, logo_image):
        super().__init__(parent)
        self.controller = controller

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # backgroun image
        if bg_image:
            self.bg_image = bg_image  
            self.bg_image_id = self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
            self.canvas.bind("<Configure>", self._resize_bg)
        else:
            self.canvas.config(bg="white")

        # start button
        start_button = tk.Button(
            self,
            text="Start",
            font=("Roboto", 20),
            command=lambda: self.controller.show_frame("MainMenuScreen"),
        )
        self.start_button_id = self.canvas.create_window(0, 0, window=start_button, anchor="center")

    def _resize_bg(self, event):
        # backgound should cover the entire screen, and screen should be able to change sizes
        if self.controller.welcome_bg_orig:
            orig_width, orig_height = self.controller.welcome_bg_orig.size
            scale = max(event.width / orig_width, event.height / orig_height)
            new_size = (int(orig_width * scale), int(orig_height * scale))
            resized_bg = self.controller.welcome_bg_orig.resize(new_size, Image.Resampling.LANCZOS)
            left = (new_size[0] - event.width) // 2
            top = (new_size[1] - event.height) // 2
            cropped_bg = resized_bg.crop((left, top, left + event.width, top + event.height))
            self.bg_image = ImageTk.PhotoImage(cropped_bg)
            self.canvas.itemconfig(self.bg_image_id, image=self.bg_image)

        # logo should modify size as the screen size changes
        if self.controller.logo_orig:
            new_logo_width = int(event.width * 0.40)
            orig_logo_width, orig_logo_height = self.controller.logo_orig.size
            logo_ratio = orig_logo_height / orig_logo_width
            new_logo_height = int(new_logo_width * logo_ratio)
            resized_logo = self.controller.logo_orig.resize((new_logo_width, new_logo_height), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(resized_logo)
            logo_x = event.width // 2
            logo_y = int(event.height * 0.30)
            if hasattr(self, 'logo_image_id'):
                self.canvas.coords(self.logo_image_id, logo_x, logo_y)
                self.canvas.itemconfig(self.logo_image_id, image=self.logo_image)
            else:
                self.logo_image_id = self.canvas.create_image(logo_x, logo_y, image=self.logo_image, anchor="center")

        # button moves as screen size adjusted
        start_x = event.width // 2
        start_y = int(event.height * 0.90)
        self.canvas.coords(self.start_button_id, start_x, start_y)

# main menu
class MainMenuScreen(tk.Frame):
    def __init__(self, parent, controller, logo_image):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        # logo
        self.logo_label = tk.Label(self, bg="#D99F6B")
        self.logo_label.pack(pady=20)
        self.bind("<Configure>", self._resize_logo)

        # buttons
        btn_find_path = tk.Button(
            self,
            text="Find a Path",
            font=("Roboto", 20),
            command=lambda: controller.show_frame("SelectionScreen"),
        )
        btn_see_history = tk.Button(
            self,
            text="See History",
            font=("Roboto", 20),
            command=lambda: controller.show_frame("HistoryScreen"),
        )
        btn_exit = tk.Button(
            self,
            text="Exit",
            font=("Roboto", 20),
            command=lambda: controller.show_frame("WelcomeScreen"),
        )

        btn_find_path.pack(pady=10)
        btn_see_history.pack(pady=10)
        btn_exit.pack(pady=10)

    def _resize_logo(self, event):
        if self.controller.logo_orig:
            new_logo_width = int(event.width * 0.40)
            orig_logo_width, orig_logo_height = self.controller.logo_orig.size
            logo_ratio = orig_logo_height / orig_logo_width
            new_logo_height = int(new_logo_width * logo_ratio)
            resized_logo = self.controller.logo_orig.resize((new_logo_width, new_logo_height), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(resized_logo)
            self.logo_label.config(image=self.logo_image)

# Selection Screen
class SelectionScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        top_frame = tk.Frame(self, bg="#D99F6B")
        top_frame.pack(pady=10, fill="x")

        # robot scroller
        scroller1 = Scroller(
            top_frame, "Select Your Robot", items=["Robot 1", "Robot 2", "Robot 3", 
                                                   "Robot 4", "Robot 5", "Robot 6", "Robot 7"], bg_color="#D99F6B"
        )
        scroller1.pack(pady=10)

        # pfa scroller
        scroller2 = Scroller(
            top_frame, "Select Your AI", items=["A*", "Bidirectional A*",
                                                "Multiresolution Pathfinder"], bg_color="#D99F6B"
        )
        scroller2.pack(pady=10)

        bottom_frame = tk.Frame(self, bg="#D99F6B")
        bottom_frame.pack(side="bottom", pady=20)

        btn_back = tk.Button(
            bottom_frame,
            text="Back",
            font=("Roboto", 20),
            command=lambda: controller.show_frame("MainMenuScreen"),
        )

        def make_robot():
            controller.robot = Robot(scroller1.items[scroller1.index], scroller2.items[scroller2.index])
            controller.show_frame("SpawnScreen")

        btn_next = tk.Button(
            bottom_frame,
            text="Next",
            font=("Roboto", 20),
            command=make_robot,
        )

        btn_back.pack(side="left", padx=20)
        btn_next.pack(side="right", padx=20)

# Spawn Screen
class SpawnScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        title_label = tk.Label(self, text="Select Your Station Location", font=("Orbitron", 24), bg="#D99F6B")
        title_label.pack(pady=10)

        main_frame = tk.Frame(self, bg="#D99F6B")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # image of the map
        image_frame = tk.Frame(main_frame, bg="#000000")
        image_frame.pack(side="left", fill="both", expand=True, padx=10)
        if controller.station_orig:
            self.station_canvas = tk.Canvas(image_frame, bg="#000000", highlightthickness=0)
            self.station_canvas.pack(fill="both", expand=True)
            self.station_canvas.bind("<Configure>", self._resize_station)
            self.station_image_id = None
        else:
            tk.Label(image_frame, text="Station Image", font=("Orbitron", 20), bg="#000000", fg="white").pack(expand=True)

        # coordinates
        table_frame = tk.Frame(main_frame, bg="#D99F6B")
        table_frame.pack(side="right", fill="y", padx=10)
        header_x = tk.Label(table_frame, text="X", font=("Roboto", 14), bg="#D99F6B")
        header_y = tk.Label(table_frame, text="Y", font=("Roboto", 14), bg="#D99F6B")
        header_x.grid(row=0, column=0, padx=5, pady=5)
        header_y.grid(row=0, column=1, padx=5, pady=5)

 
        lbl_x = tk.Label(table_frame, text=str(10), font=("Roboto", 14), bg="#D99F6B")
        lbl_y = tk.Label(table_frame, text=str(20), font=("Roboto", 14), bg="#D99F6B")
        lbl_x.grid(row=0, column=0, padx=5, pady=5)
        lbl_y.grid(row=0, column=1, padx=5, pady=5)

        # go button
        go_button = tk.Button(self, text="Go", font=("Roboto", 20), command=lambda: controller.show_frame("DummyPage"))
        go_button.pack(pady=20)

    def _resize_station(self, event):
        if self.controller.station_orig:
            orig_width, orig_height = self.controller.station_orig.size
            scale = max(event.width / orig_width, event.height / orig_height)
            new_size = (int(orig_width * scale), int(orig_height * scale))
            resized = self.controller.station_orig.resize(new_size, Image.Resampling.LANCZOS)
            left = (new_size[0] - event.width) // 2
            top = (new_size[1] - event.height) // 2
            cropped = resized.crop((left, top, left + event.width, top + event.height))
            self.station_image = ImageTk.PhotoImage(cropped)
            if self.station_image_id:
                self.station_canvas.itemconfig(self.station_image_id, image=self.station_image)
            else:
                self.station_image_id = self.station_canvas.create_image(0, 0, image=self.station_image, anchor="nw")


# Dummy Page FOR TERRAIN AND ROBOT
class DummyPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        label = tk.Label(self, text="Dummy Page", font=("Orbitron", 24), bg="#D99F6B")
        label.pack(pady=40)

        next_button = tk.Button(self, text="Next", font=("Roboto", 20), command=lambda: controller.show_frame("FinishScreen"))
        next_button.pack(pady=20)

# Finish Screen
class FinishScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        label = tk.Label(self, text="You've reached your destination!", font=("Orbitron", 24), bg="#D99F6B")
        label.pack(pady=40)

        button_frame = tk.Frame(self, bg="#D99F6B")
        button_frame.pack(pady=20)

        new_robot_button = tk.Button(
            button_frame,
            text="Select New Robot and AI",
            font=("Roboto", 20),
            command=lambda: controller.show_frame("SelectionScreen")
        )
        view_stats_button = tk.Button(
            button_frame,
            text="View Stats",
            font=("Roboto", 20),
            command=lambda: controller.show_frame("MetricDisplay")
        )
        new_robot_button.grid(row=0, column=0, padx=10, pady=10)
        view_stats_button.grid(row=0, column=1, padx=10, pady=10)


# Post run metric Display Screen
class MetricDisplay(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#011936")
        self.controller = controller

        label = tk.Label(self, text="Metric Display", font=("Orbitron", 24), bg="#011936", fg="white")
        label.pack(pady=40)

        back_button = tk.Button(self, text="Back", font=("Roboto", 20), command=lambda: controller.show_frame("MainMenuScreen"))
        back_button.pack(pady=20)


# History Screen from csv
class HistoryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#011936")
        self.controller = controller

        label = tk.Label(self, text="History", font=("Orbitron", 24), bg="#011936", fg="white")
        label.pack(pady=20)

        back_button = tk.Button(self, text="Back", font=("Roboto", 20), command=lambda: controller.show_frame("MainMenuScreen"))
        back_button.pack(side="bottom", pady=20)

        history_ls = read_history()
        last_ten = []

        if (len(history_ls) <= 10):
            last_ten = history_ls
        else:
            last_ten = history_ls[(len(history_ls)-11):len(history_ls)]

        #j = 10
        for i in range(1,len(last_ten)):
        
            t = ToggledFrame(self, text="%s - %s"%(last_ten[len(last_ten)-i][2], last_ten[len(last_ten)-i][3]), relief="raised", borderwidth=1)
            t.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

            label = ttk.Label(t.sub_frame, text="Start", font=("Orbitron", 15), borderwidth=0, width=20)
            label.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
            cont = ttk.Label(t.sub_frame, text="%s"%(last_ten[len(last_ten)-i][0]), font=("Orbitron", 15), borderwidth=0, width=20)
            cont.grid(row=1, column=0, sticky="nsew", padx=1, pady=1)

            label = ttk.Label(t.sub_frame, text="End", font=("Orbitron", 15), borderwidth=0, width=20)
            label.grid(row=0, column=1, sticky="nsew", padx=1, pady=1)
            cont = ttk.Label(t.sub_frame, text="%s"%(last_ten[len(last_ten)-i][1]), font=("Orbitron", 15), borderwidth=0, width=20)
            cont.grid(row=1, column=1, sticky="nsew", padx=1, pady=1)

            label = ttk.Label(t.sub_frame, text="Distance", font=("Orbitron", 15), borderwidth=0, width=20)
            label.grid(row=0, column=2, sticky="nsew", padx=1, pady=1)
            cont = ttk.Label(t.sub_frame, text="%s"%(last_ten[len(last_ten)-i][4]), font=("Orbitron", 15), borderwidth=0, width=20)
            cont.grid(row=1, column=2, sticky="nsew", padx=1, pady=1)

            label = ttk.Label(t.sub_frame, text="Time", font=("Orbitron", 15), borderwidth=0, width=20)
            label.grid(row=0, column=3, sticky="nsew", padx=1, pady=1)
            cont = ttk.Label(t.sub_frame, text="%s"%(last_ten[len(last_ten)-i][5]), font=("Orbitron", 15), borderwidth=0, width=20)
            cont.grid(row=1, column=3, sticky="nsew", padx=1, pady=1)

            label = ttk.Label(t.sub_frame, text="Cost", font=("Orbitron", 15), borderwidth=0, width=20)
            label.grid(row=0, column=4, sticky="nsew", padx=1, pady=1)
            cont = ttk.Label(t.sub_frame, text="%s"%(last_ten[len(last_ten)-i][6]), font=("Orbitron", 15), borderwidth=0, width=20)
            cont.grid(row=1, column=4, sticky="nsew", padx=1, pady=1)

            

        
        

if __name__ == "__main__":
    app = App()
    #load_fonts()
    app.mainloop()
