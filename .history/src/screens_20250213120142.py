import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk

# ============================================================================
# A helper class for a simple left/right scroller widget.
class Scroller(tk.Frame):
    def __init__(self, parent, title, items, bg_color, *args, **kwargs):
        super().__init__(parent, bg=bg_color, *args, **kwargs)
        self.items = items
        self.index = 0

        # Title label
        title_label = tk.Label(self, text=title, bg=bg_color, font=("Helvetica", 16))
        title_label.pack(pady=5)

        # Container for arrows and display
        content_frame = tk.Frame(self, bg=bg_color)
        content_frame.pack(pady=5)

        left_button = tk.Button(
            content_frame, text="<", command=self.prev_item, font=("Helvetica", 14)
        )
        left_button.pack(side="left", padx=5)

        # The display area (simulate a white rectangle with a border)
        self.item_label = tk.Label(
            content_frame,
            text=str(self.items[self.index]),
            width=20,
            height=5,
            bg="white",
            relief="solid",
            font=("Helvetica", 14),
        )
        self.item_label.pack(side="left", padx=5)

        right_button = tk.Button(
            content_frame, text=">", command=self.next_item, font=("Helvetica", 14)
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

# ============================================================================
# Main application class
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Charles Marwin")
        self.geometry("800x600")
        self.resizable(True, True)

        # A container that will hold all the screens.
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary of frames
        self.frames = {}

        # ----------------------------------------------------------------------
        # Preload images (keep references so they aren’t garbage-collected)
        # For the welcome background image, load using PIL for resizing support.
        try:
            self.welcome_bg_orig = Image.open("images/welcome_bg.png")
            # Create an initial image (will be updated on resize)
            self.welcome_bg = ImageTk.PhotoImage(self.welcome_bg_orig)
        except Exception as e:
            print("Error loading welcome_bg.png:", e)
            self.welcome_bg = None
            self.welcome_bg_orig = None

        # Load the logo image both as a Tk image and as a PIL image.
        try:
            self.logo_img = PhotoImage(file="images/logo.png")
        except Exception as e:
            print("Error loading logo.png as PhotoImage:", e)
            self.logo_img = None
        try:
            self.logo_orig = Image.open("images/logo.png")
        except Exception as e:
            print("Error loading logo.png as PIL image:", e)
            self.logo_orig = None

        # ----------------------------------------------------------------------
        # Create each screen and store in the dictionary.
        for F in (WelcomeScreen, MainMenuScreen, SelectionScreen, HistoryScreen):
            page_name = F.__name__
            if page_name == "WelcomeScreen":
                frame = F(
                    parent=container,
                    controller=self,
                    bg_image=self.welcome_bg,
                    # Pass the Tk logo image (used if no resizing is done)
                    logo_image=self.logo_img,
                )
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

# ============================================================================
# Welcome Screen
class WelcomeScreen(tk.Frame):
    def __init__(self, parent, controller, bg_image, logo_image):
        super().__init__(parent)
        self.controller = controller

        # Create a Canvas that fills the entire frame.
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Set up the background image on the canvas.
        if bg_image:
            self.bg_image = bg_image  # initial image; will be updated on resize
            self.bg_image_id = self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
            # Bind the canvas resize event.
            self.canvas.bind("<Configure>", self._resize_bg)
        else:
            self.canvas.config(bg="white")

        # Create the start button and add it via the canvas.
        start_button = tk.Button(
            self,
            text="Start",
            font=("Helvetica", 20),
            command=lambda: controller.show_frame("MainMenuScreen"),
        )
        self.start_button = start_button
        # Create the button window; initial coords will be updated on resize.
        self.start_button_id = self.canvas.create_window(0, 0, window=start_button, anchor="center")

    def _resize_bg(self, event):
        """Update the background image (using cover strategy), logo, and start button when the canvas resizes."""
        # ---------------------
        # Update the background image
        if self.controller.welcome_bg_orig:
            orig_width, orig_height = self.controller.welcome_bg_orig.size
            # Compute the scale factor that covers the entire canvas.
            scale = max(event.width / orig_width, event.height / orig_height)
            new_size = (int(orig_width * scale), int(orig_height * scale))
            # Use the new resampling filter.
            resized_bg = self.controller.welcome_bg_orig.resize(new_size, Image.Resampling.LANCZOS)
            # Crop to exactly the canvas size.
            left = (new_size[0] - event.width) // 2
            top = (new_size[1] - event.height) // 2
            cropped_bg = resized_bg.crop((left, top, left + event.width, top + event.height))
            self.bg_image = ImageTk.PhotoImage(cropped_bg)
            self.canvas.itemconfig(self.bg_image_id, image=self.bg_image)

        # ---------------------
        # Update the logo image to be 10% of the canvas width.
        if self.controller.logo_orig:
            new_logo_width = int(event.width * 0.40)
            orig_logo_width, orig_logo_height = self.controller.logo_orig.size
            logo_ratio = orig_logo_height / orig_logo_width
            new_logo_height = int(new_logo_width * logo_ratio)
            resized_logo = self.controller.logo_orig.resize((new_logo_width, new_logo_height), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(resized_logo)
            # Place the logo at the top center (vertically at 10% of canvas height).
            logo_x = event.width // 2
            logo_y = int(event.height * 0.50)
            if hasattr(self, 'logo_image_id'):
                self.canvas.coords(self.logo_image_id, logo_x, logo_y)
                self.canvas.itemconfig(self.logo_image_id, image=self.logo_image)
            else:
                self.logo_image_id = self.canvas.create_image(logo_x, logo_y, image=self.logo_image, anchor="center")

        # ---------------------
        # Update the start button position to be centered at 90% of the canvas height.
        start_x = event.width // 2
        start_y = int(event.height * 0.90)
        self.canvas.coords(self.start_button_id, start_x, start_y)

# ============================================================================
# Main Menu Screen
class MainMenuScreen(tk.Frame):
    def __init__(self, parent, controller, logo_image):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        # Create a logo label.
        self.logo_label = tk.Label(self, bg="#D99F6B")
        self.logo_label.pack(pady=20)
        # Bind to update the logo when the frame is resized.
        self.bind("<Configure>", self._resize_logo)

        # Create the three buttons.
        btn_find_path = tk.Button(
            self,
            text="find a path",
            font=("Helvetica", 20),
            command=lambda: controller.show_frame("SelectionScreen"),
        )
        btn_see_history = tk.Button(
            self,
            text="see history",
            font=("Helvetica", 20),
            command=lambda: controller.show_frame("HistoryScreen"),
        )
        btn_exit = tk.Button(
            self,
            text="exit",
            font=("Helvetica", 20),
            command=lambda: controller.show_frame("WelcomeScreen"),
        )

        btn_find_path.pack(pady=10)
        btn_see_history.pack(pady=10)
        btn_exit.pack(pady=10)

    def _resize_logo(self, event):
        """Resize the logo to be 10% of the current frame's width."""
        if self.controller.logo_orig:
            new_logo_width = int(event.width * 0.10)
            orig_logo_width, orig_logo_height = self.controller.logo_orig.size
            logo_ratio = orig_logo_height / orig_logo_width
            new_logo_height = int(new_logo_width * logo_ratio)
            resized_logo = self.controller.logo_orig.resize((new_logo_width, new_logo_height), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(resized_logo)
            self.logo_label.config(image=self.logo_image)

# ============================================================================
# History Screen
class HistoryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        label = tk.Label(
            self, text="History Screen", font=("Helvetica", 24), bg="#D99F6B"
        )
        label.pack(pady=40)

        back_button = tk.Button(
            self,
            text="Back",
            font=("Helvetica", 20),
            command=lambda: controller.show_frame("MainMenuScreen"),
        )
        back_button.pack(pady=20)

# ============================================================================
# Selection Screen
class SelectionScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        # Create a container for the scrollers.
        top_frame = tk.Frame(self, bg="#D99F6B")
        top_frame.pack(pady=10, fill="x")

        # Scroller for "select your robot"
        scroller1 = Scroller(
            top_frame, "select your robot", items=list(range(1, 7)), bg_color="#D99F6B"
        )
        scroller1.pack(pady=10)

        # Scroller for "select you ai"
        scroller2 = Scroller(
            top_frame, "select you ai", items=list(range(1, 7)), bg_color="#D99F6B"
        )
        scroller2.pack(pady=10)

        # Bottom frame for navigation buttons.
        bottom_frame = tk.Frame(self, bg="#D99F6B")
        bottom_frame.pack(side="bottom", pady=20)

        btn_back = tk.Button(
            bottom_frame,
            text="back",
            font=("Helvetica", 20),
            command=lambda: controller.show_frame("MainMenuScreen"),
        )
        btn_dummy = tk.Button(
            bottom_frame,
            text="next",
            font=("Helvetica", 20),
            command=lambda: print("Dummy Next Button Pressed"),
        )
        btn_back.pack(side="left", padx=20)
        btn_dummy.pack(side="right", padx=20)

# ============================================================================
# Run the application.
if __name__ == "__main__":
    app = App()
    app.mainloop()
