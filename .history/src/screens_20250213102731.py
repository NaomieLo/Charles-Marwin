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
# class App(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("Charles Marwin")
#         self.geometry("800x600")
#         self.resizable(True, True)

#         # A container that will hold all the screens.
#         # container = tk.Frame(self, width=800, height=600)
#         container = tk.Frame(self)
#         container.pack(side="top", fill="both", expand=True)

#         # Dictionary of frames
#         self.frames = {}

#         # Preload images (keep references so they aren’t garbage-collected)
#         # Note: PhotoImage supports PNG in Tk 8.6+.
#         # If JPEG is not supported, consider converting welcome_bg.jpg to PNG.
#         try:

#             self.welcome_bg = PhotoImage(file="images/welcome_bg.png")
#         except Exception as e:
#             print("Error loading welcome_bg.jpg:", e)
#             self.welcome_bg = None
#         try:
#             self.logo_img = PhotoImage(file="images/logo.png")
#         except Exception as e:
#             print("Error loading logo.png:", e)
#             self.logo_img = None

#         # Create each screen and store in the dictionary.
#         for F in (WelcomeScreen, MainMenuScreen, SelectionScreen, HistoryScreen):
#             page_name = F.__name__
#             if page_name == "WelcomeScreen":
#                 frame = F(
#                     parent=container,
#                     controller=self,
#                     bg_image=self.welcome_bg,
#                     logo_image=self.logo_img,
#                 )
#             elif page_name == "MainMenuScreen":
#                 frame = F(parent=container, controller=self, logo_image=self.logo_img)
#             else:
#                 frame = F(parent=container, controller=self)
#             self.frames[page_name] = frame
#             # All frames are placed in the same location.
#             frame.grid(row=0, column=0, sticky="nsew")

#         self.show_frame("WelcomeScreen")

#     def show_frame(self, page_name):
#         """Raise the frame corresponding to the given page name."""
#         frame = self.frames[page_name]
#         frame.tkraise()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Charles Marwin")
        self.geometry("800x600")
        self.resizable(True, True)

        # A container that will hold all the screens.
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        self.frames = {}

        # Load original images
        try:
            self.original_logo_img = Image.open("images/logo.png")
        except Exception as e:
            print("Error loading logo.png:", e)
            self.original_logo_img = None

        try:
            self.original_welcome_bg = Image.open("images/welcome_bg.png")
        except Exception as e:
            print("Error loading welcome_bg.png:", e)
            self.original_welcome_bg = None

        # Ensure logo is initialized before passing it to screens
        self.logo_img = self.get_resized_logo()

        # Create each screen
        for F in (WelcomeScreen, MainMenuScreen, SelectionScreen, HistoryScreen):
            page_name = F.__name__
            if page_name == "WelcomeScreen":
                frame = F(
                    parent=container,
                    controller=self,
                    bg_image=self.original_welcome_bg,  # Pass the background image
                )
            elif page_name == "MainMenuScreen":
                frame = F(parent=container, controller=self, logo_image=self.logo_img)
            else:
                frame = F(parent=container, controller=self)

            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Bind resize event
        self.bind("<Configure>", self.on_resize)

        self.show_frame("WelcomeScreen")

    def get_resized_logo(self):
        """Resize logo to 10% of window width"""
        if self.original_logo_img:
            win_width = self.winfo_width() or 800  # Default width if window isn't ready
            new_width = int(win_width * 0.1)
            new_height = int((new_width / self.original_logo_img.width) * self.original_logo_img.height)

            resized_logo = self.original_logo_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(resized_logo)
        return None

    def show_frame(self, page_name):
        """Raise the frame corresponding to the given page name."""
        frame = self.frames[page_name]
        frame.tkraise()

    def on_resize(self, event=None):
        """Resize logo dynamically based on window size."""
        self.logo_img = self.get_resized_logo()

        # Update logo on MainMenuScreen
        if "MainMenuScreen" in self.frames:
            self.frames["MainMenuScreen"].update_logo(self.logo_img)



# ============================================================================
# Welcome Screen
class WelcomeScreen(tk.Frame):
    def __init__(self, parent, controller, bg_image, logo_image):
        super().__init__(parent)
        self.controller = controller

        # Use a Canvas to display the background image so it fills the entire frame.
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both", expand=True)

        # If background image loaded successfully, set it as background.
        if bg_image:
            self.bg_image = bg_image  # keep a reference
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        else:
            # Otherwise, use a white background.
            self.canvas.config(bg="white")

        # Place the logo at the top middle.
        if logo_image:
            self.logo_image = logo_image  # keep a reference
            self.canvas.create_image(400, 100, image=self.logo_image, anchor="center")
        else:
            self.canvas.create_text(400, 100, text="Logo", font=("Helvetica", 32))

        # Place the Start button in the lower middle.
        start_button = tk.Button(
            self,
            text="Start",
            font=("Helvetica", 20),
            command=lambda: controller.show_frame("MainMenuScreen"),
        )
        # Use the Canvas window method to place the button.
        self.canvas.create_window(400, 500, window=start_button)


# ============================================================================
# Main Menu Screen
# class MainMenuScreen(tk.Frame):
#     def __init__(self, parent, controller, logo_image):
#         super().__init__(parent, bg="#D99F6B")
#         self.controller = controller

#         # Place the logo at the top middle.
#         if logo_image:
#             self.logo_image = logo_image
#             logo_label = tk.Label(self, image=self.logo_image, bg="#D99F6B")
#             logo_label.pack(pady=20)
#         else:
#             logo_label = tk.Label(
#                 self, text="Logo", font=("Helvetica", 28), bg="#D99F6B"
#             )
#             logo_label.pack(pady=20)

#         # Create the three buttons.
#         btn_find_path = tk.Button(
#             self,
#             text="find a path",
#             font=("Helvetica", 20),
#             command=lambda: controller.show_frame("SelectionScreen"),
#         )
#         btn_see_history = tk.Button(
#             self,
#             text="see history",
#             font=("Helvetica", 20),
#             command=lambda: controller.show_frame("HistoryScreen"),
#         )
#         btn_exit = tk.Button(
#             self,
#             text="exit",
#             font=("Helvetica", 20),
#             command=lambda: controller.show_frame("WelcomeScreen"),
#         )

#         # Pack the buttons with spacing.
#         btn_find_path.pack(pady=10)
#         btn_see_history.pack(pady=10)
#         btn_exit.pack(pady=10)

class MainMenuScreen(tk.Frame):
    def __init__(self, parent, controller, logo_image=None):
        super().__init__(parent, bg="#D99F6B")
        self.controller = controller

        # Initialize logo label
        self.logo_label = tk.Label(self, bg="#D99F6B")
        self.logo_label.pack(pady=20)

        # Set initial logo if available
        if logo_image:
            self.update_logo(logo_image)

        # Create buttons
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

        # Pack the buttons
        btn_find_path.pack(pady=10)
        btn_see_history.pack(pady=10)
        btn_exit.pack(pady=10)

    def update_logo(self, new_logo):
        """Update the logo image dynamically."""
        if new_logo:
            self.logo_label.config(image=new_logo)
            self.logo_label.image = new_logo  # Keep reference to prevent garbage collection

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
