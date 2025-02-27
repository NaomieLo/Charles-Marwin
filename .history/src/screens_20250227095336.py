
import tkinter as tk
from tkinter import PhotoImage
from tkinter import font as tkFont
from PIL import Image, ImageTk


# SELECT THE ROBOT AND PFA
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

# Main application class
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Charles Marwin")
        self.geometry("800x600")
        self.resizable(True, True)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # load background and logo images
        try:
            self.welcome_bg_orig = Image.open("images/welcome_bg.png")
            self.welcome_bg = ImageTk.PhotoImage(self.welcome_bg_orig)
        except Exception as e:
            self.welcome_bg = None
            self.welcome_bg_orig = None

        try:
            self.logo_img = PhotoImage(file="images/logo.png")
        except Exception as e:
            self.logo_img = None
        try:
            self.logo_orig = Image.open("images/logo.png")
        except Exception as e:
            self.logo_orig = None

        try:
            self.station_orig = Image.open("images/station.png")
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

        # Create the start button.
        start_button = tk.Button(
            self,
            text="Start",
            font=("Roboto", 20),
            command=lambda: self.controller.show_frame("MainMenuScreen"),
        )
        self.start_button_id = self.canvas.create_window(0, 0, window=start_button, anchor="center")

    def _resize_bg(self, event):
        # Update background image using "cover" strategy.
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

        # Update logo to be 10% of canvas width.
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

        # Update start button position to be centered at 90% of canvas height.
        start_x = event.width // 2
        start_y = int(event.height * 0.90)
        self.canvas.coords(self.start_button_id, start_x, start_y)

# ============================================================================
# Main Menu Screen
class MainMenuScreen(tk.Frame):
    def __init__(self, parent, controller, logo_image):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        # Logo label.
        self.logo_label = tk.Label(self, bg="#D99F6B")
        self.logo_label.pack(pady=20)
        self.bind("<Configure>", self._resize_logo)

        # Three main buttons.
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

# ============================================================================
# Selection Screen
class SelectionScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        top_frame = tk.Frame(self, bg="#D99F6B")
        top_frame.pack(pady=10, fill="x")

        # Scroller for "Select Your Robot"
        scroller1 = Scroller(
            top_frame, "Select Your Robot", items=list(range(1, 7)), bg_color="#D99F6B"
        )
        scroller1.pack(pady=10)

        # Scroller for "Select Your AI"
        scroller2 = Scroller(
            top_frame, "Select Your AI", items=list(range(1, 7)), bg_color="#D99F6B"
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
        # Dummy "Next" button now sends us to SpawnScreen.
        btn_next = tk.Button(
            bottom_frame,
            text="Next",
            font=("Roboto", 20),
            command=lambda: controller.show_frame("SpawnScreen"),
        )
        btn_back.pack(side="left", padx=20)
        btn_next.pack(side="right", padx=20)

# ============================================================================
# Spawn Screen (Select Station Location)
class SpawnScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        # Title at the top.
        title_label = tk.Label(self, text="Select Your Station Location", font=("Orbitron", 24), bg="#D99F6B")
        title_label.pack(pady=10)

        # Main content area.
        main_frame = tk.Frame(self, bg="#D99F6B")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left: Station image.
        image_frame = tk.Frame(main_frame, bg="#000000")
        image_frame.pack(side="left", fill="both", expand=True, padx=10)
        if controller.station_orig:
            self.station_canvas = tk.Canvas(image_frame, bg="#000000", highlightthickness=0)
            self.station_canvas.pack(fill="both", expand=True)
            self.station_canvas.bind("<Configure>", self._resize_station)
            self.station_image_id = None
        else:
            tk.Label(image_frame, text="Station Image", font=("Orbitron", 20), bg="#000000", fg="white").pack(expand=True)

        # Right: Table for X and Y coordinates.
        table_frame = tk.Frame(main_frame, bg="#D99F6B")
        table_frame.pack(side="right", fill="y", padx=10)
        header_x = tk.Label(table_frame, text="X", font=("Roboto", 14), bg="#D99F6B")
        header_y = tk.Label(table_frame, text="Y", font=("Roboto", 14), bg="#D99F6B")
        header_x.grid(row=0, column=0, padx=5, pady=5)
        header_y.grid(row=0, column=1, padx=5, pady=5)
        # Dummy coordinate rows.
 
        lbl_x = tk.Label(table_frame, text=str(10), font=("Roboto", 14), bg="#D99F6B")
        lbl_y = tk.Label(table_frame, text=str(20), font=("Roboto", 14), bg="#D99F6B")
        lbl_x.grid(row=0, column=0, padx=5, pady=5)
        lbl_y.grid(row=0, column=1, padx=5, pady=5)

        # "Go" button at the bottom center.
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

# ============================================================================
# Dummy Page (transitional)
class DummyPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        label = tk.Label(self, text="Dummy Page", font=("Orbitron", 24), bg="#D99F6B")
        label.pack(pady=40)

        next_button = tk.Button(self, text="Next", font=("Roboto", 20), command=lambda: controller.show_frame("FinishScreen"))
        next_button.pack(pady=20)

# ============================================================================
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

# ============================================================================
# Metric Display Screen
class MetricDisplay(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#011936")
        self.controller = controller

        label = tk.Label(self, text="Metric Display", font=("Orbitron", 24), bg="#011936", fg="white")
        label.pack(pady=40)

        back_button = tk.Button(self, text="Back", font=("Roboto", 20), command=lambda: controller.show_frame("MainMenuScreen"))
        back_button.pack(pady=20)

# ============================================================================
# History Screen
class HistoryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#011936")
        self.controller = controller

        label = tk.Label(self, text="History", font=("Orbitron", 24), bg="#011936", fg="white")
        label.pack(pady=20)

        back_button = tk.Button(self, text="Back", font=("Roboto", 20), command=lambda: controller.show_frame("MainMenuScreen"))
        back_button.pack(side="bottom", pady=20)

# ============================================================================
# Run the application.

# root = tk.Tk()

# # Register local fonts from a folder
# tkextrafont.load_font("fonts/Orbitron-Regular.ttf")
# tkextrafont.load_font("fonts/Roboto_Condensed-BlackItalic.ttf")

# # Now you can create widgets with these font names
# label = tk.Label(root, text="Hello", font=("Orbitron", 24))
# label.pack()

# root.mainloop()


if __name__ == "__main__":
    app = App()
    #load_fonts()
    app.mainloop()
