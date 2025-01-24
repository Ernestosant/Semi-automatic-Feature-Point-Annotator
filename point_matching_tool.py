import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import os

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

class DualImageMatchingApp:
    def __init__(self, master):
        try:
            self.master = master

            # Main frame with scroll
            self.main_frame = ScrollableFrame(self.master)
            self.main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

            # Top control panel
            self.control_panel = self.create_control_panel()
            
            # Container for images and point lists
            self.images_container = ttk.Frame(self.main_frame.scrollable_frame)
            self.images_container.pack(fill=tk.BOTH, expand=True, pady=10)

            # Containers for each image and its point list
            self.rgb_container = self.create_image_container("RGB", True)
            self.depth_container = self.create_image_container("Depth", False)

            # Variable initialization
            self.rgb_image_cv = None
            self.depth_image_cv = None
            self.rgb_points = []
            self.depth_points = []
            self.rgb_lines = []
            self.depth_lines = []
            self.current_rgb_image_tk = None
            self.current_depth_image_tk = None
        except Exception as e:
            self.show_error("Error initializing application", str(e))

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def create_control_panel(self):
        control_panel = ttk.Frame(self.main_frame.scrollable_frame)
        control_panel.pack(fill=tk.X, pady=10)

        # Loading buttons
        btn_frame = ttk.Frame(control_panel)
        btn_frame.pack(pady=5)
        
        self.btn_load_rgb = ttk.Button(btn_frame, text="Load RGB Image", 
                                     command=self.load_rgb_image)
        self.btn_load_rgb.pack(side=tk.LEFT, padx=5)
        
        self.btn_load_depth = ttk.Button(btn_frame, text="Load Depth Map", 
                                       command=self.load_depth_image)
        self.btn_load_depth.pack(side=tk.LEFT, padx=5)

        # Add clear points button after other buttons
        self.clear_button = ttk.Button(btn_frame, text="Clear Points", command=self.clear_points)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Offset controls
        offset_frame = ttk.LabelFrame(control_panel, text="Depth Map Offset")
        offset_frame.pack(pady=5, padx=10, fill=tk.X)

        # Control X
        x_frame = ttk.Frame(offset_frame)
        x_frame.pack(fill=tk.X, pady=2)
        ttk.Label(x_frame, text="X Offset:").pack(side=tk.LEFT, padx=5)
        
        self.x_offset_var = tk.StringVar(value="36")
        self.x_offset_entry = ttk.Entry(x_frame, textvariable=self.x_offset_var, width=5)
        self.x_offset_entry.pack(side=tk.LEFT, padx=5)
        
        self.x_offset_slider = ttk.Scale(x_frame, from_=-100, to=100, orient="horizontal")
        self.x_offset_slider.set(36)
        self.x_offset_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Control Y
        y_frame = ttk.Frame(offset_frame)
        y_frame.pack(fill=tk.X, pady=2)
        ttk.Label(y_frame, text="Y Offset:").pack(side=tk.LEFT, padx=5)
        
        self.y_offset_var = tk.StringVar(value="-8")
        self.y_offset_entry = ttk.Entry(y_frame, textvariable=self.y_offset_var, width=5)
        self.y_offset_entry.pack(side=tk.LEFT, padx=5)
        
        self.y_offset_slider = ttk.Scale(y_frame, from_=-100, to=100, orient="horizontal")
        self.y_offset_slider.set(-8)
        self.y_offset_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Bind events
        self.bind_offset_events()
        
        return control_panel

    def create_image_container(self, title, is_rgb):
        container = ttk.Frame(self.images_container)
        container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Title
        ttk.Label(container, text=f"{title} Image", font=("Arial", 12, "bold")).pack(pady=5)

        # Canvas for image
        canvas = tk.Canvas(container, width=400, height=400)
        canvas.pack(pady=5)
        
        if is_rgb:
            self.rgb_canvas = canvas
            canvas.bind("<Button-1>", self.on_rgb_click)
        else:
            self.depth_canvas = canvas

        # Points list
        points_frame = ttk.LabelFrame(container, text=f"Points in {title} Image")
        points_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        points_scroll = ScrollableFrame(points_frame)
        points_scroll.pack(fill=tk.BOTH, expand=True)

        if is_rgb:
            self.rgb_points_frame = points_scroll.scrollable_frame
        else:
            self.depth_points_frame = points_scroll.scrollable_frame

        return container

    def bind_offset_events(self):
        self.x_offset_slider.bind("<Motion>", self.update_offset)
        self.y_offset_slider.bind("<Motion>", self.update_offset)
        self.x_offset_entry.bind("<Return>", self.update_offset_from_entry)
        self.y_offset_entry.bind("<Return>", self.update_offset_from_entry)

    def load_rgb_image(self):
        try:
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if path:
                # Normalize file path
                path = os.path.normpath(path)
                # Read image using cv2.IMREAD_UNCHANGED to preserve alpha channel if exists
                self.rgb_image_cv = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if self.rgb_image_cv is None:
                    raise IOError("Could not load image. The file may be corrupted or in an unsupported format.")
                self.update_canvas()
        except Exception as e:
            self.show_error("Error loading RGB image", str(e))

    def load_depth_image(self):
        try:
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
            if path:
                # Normalize file path
                path = os.path.normpath(path)
                # Read image using cv2.IMREAD_UNCHANGED to preserve alpha channel if exists
                self.depth_image_cv = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if self.depth_image_cv is None:
                    raise IOError("Could not load image. The file may be corrupted or in an unsupported format.")
                self.update_canvas()
        except Exception as e:
            self.show_error("Error loading depth map", str(e))

    def update_canvas(self):
        try:
            if self.rgb_image_cv is not None:
                rgb_display = cv2.cvtColor(self.rgb_image_cv, cv2.COLOR_BGR2RGB)
                rgb_img = Image.fromarray(rgb_display)
                self.current_rgb_image_tk = ImageTk.PhotoImage(rgb_img)
                
                self.rgb_canvas.config(width=rgb_img.width, height=rgb_img.height)
                self.rgb_canvas.delete("all")
                self.rgb_canvas.create_image(0, 0, image=self.current_rgb_image_tk, anchor="nw")
                self.redraw_points()

            if self.depth_image_cv is not None:
                depth_display = cv2.cvtColor(self.depth_image_cv, cv2.COLOR_BGR2RGB)
                depth_img = Image.fromarray(depth_display)
                self.current_depth_image_tk = ImageTk.PhotoImage(depth_img)
                
                self.depth_canvas.config(width=depth_img.width, height=depth_img.height)
                self.depth_canvas.delete("all")
                self.depth_canvas.create_image(0, 0, image=self.current_depth_image_tk, anchor="nw")
                self.redraw_points()
        except Exception as e:
            self.show_error("Error updating display", str(e))

    def on_rgb_click(self, event):
        if self.rgb_image_cv is None or self.depth_image_cv is None:
            return

        x = event.x
        y = event.y
        
        # Add point in RGB image
        self.rgb_points.append((x, y))
        
        # Calculate position in depth image
        x_offset = int(self.x_offset_var.get())
        y_offset = int(self.y_offset_var.get())
        depth_x = x + x_offset
        depth_y = y + y_offset
        self.depth_points.append((depth_x, depth_y))

        # Update visualization
        self.redraw_points()
        self.update_point_lists()

    def redraw_points(self):
        # Clear canvas
        self.rgb_canvas.delete("point", "line", "label")
        self.depth_canvas.delete("point", "line", "label")

        # Draw points and lines in RGB
        for i, (x, y) in enumerate(self.rgb_points, 1):
            self.draw_point(self.rgb_canvas, x, y, f"PO{i}")
            if i > 1:
                prev_x, prev_y = self.rgb_points[i-2]
                self.rgb_canvas.create_line(prev_x, prev_y, x, y, fill="yellow", width=2, tags="line")

        # Draw points and lines in Depth
        for i, (x, y) in enumerate(self.depth_points, 1):
            self.draw_point(self.depth_canvas, x, y, f"PD{i}")
            if i > 1:
                prev_x, prev_y = self.depth_points[i-2]
                self.depth_canvas.create_line(prev_x, prev_y, x, y, fill="yellow", width=2, tags="line")

    def draw_point(self, canvas, x, y, label):
        canvas.create_oval(x-4, y-4, x+4, y+4, fill="white", outline="black", width=2, tags="point")
        # Get only the number from label (removing 'PO' or 'PD')
        number = label[2:]
        canvas.create_text(x, y-15, text=number, fill="white", font=("Arial", 12, "bold"), tags="label")

    def update_point_lists(self):
        # Clear existing lists
        for widget in self.rgb_points_frame.winfo_children():
            widget.destroy()
        for widget in self.depth_points_frame.winfo_children():
            widget.destroy()

        # Update RGB list
        for i, (x, y) in enumerate(self.rgb_points, 1):
            frame = ttk.Frame(self.rgb_points_frame, relief="solid", borderwidth=1)
            frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(frame, text=f"{i}: ({int(x)}, {int(y)})").pack(padx=5, pady=2)

        # Update Depth list
        for i, (x, y) in enumerate(self.depth_points, 1):
            frame = ttk.Frame(self.depth_points_frame, relief="solid", borderwidth=1)
            frame.pack(fill=tk.X, padx=5, pady=2)
            ttk.Label(frame, text=f"{i}: ({int(x)}, {int(y)})").pack(padx=5, pady=2)

    def update_offset(self, event=None):
        x_offset = self.x_offset_slider.get()
        y_offset = self.y_offset_slider.get()
        self.x_offset_var.set(str(int(x_offset)))
        self.y_offset_var.set(str(int(y_offset)))
        self.update_depth_points()

    def update_offset_from_entry(self, event=None):
        try:
            x_offset = int(self.x_offset_var.get())
            y_offset = int(self.y_offset_var.get())
            
            if not (-100 <= x_offset <= 100) or not (-100 <= y_offset <= 100):
                raise ValueError("Offset values must be between -100 and 100")

            self.x_offset_slider.set(x_offset)
            self.y_offset_slider.set(y_offset)
            self.x_offset_var.set(str(x_offset))
            self.y_offset_var.set(str(y_offset))
            
            self.update_depth_points()
        except ValueError as e:
            self.show_error("Invalid offset value", str(e))
            # Restore previous values
            self.x_offset_var.set(str(int(self.x_offset_slider.get())))
            self.y_offset_var.set(str(int(self.y_offset_slider.get())))

    def update_depth_points(self):
        try:
            if not self.rgb_points:
                return

            x_offset = int(self.x_offset_var.get())
            y_offset = int(self.y_offset_var.get())
            
            # Update depth points
            self.depth_points = [(x + x_offset, y + y_offset) for x, y in self.rgb_points]
            
            # Redraw all points
            self.redraw_points()
            self.update_point_lists()
        except Exception as e:
            self.show_error("Error updating depth points", str(e))

    def clear_points(self):
        # Clear left canvas points
        self.rgb_canvas.delete("point", "line", "label")
        self.rgb_points = []
        
        # Clear right canvas points
        self.depth_canvas.delete("point", "line", "label")
        self.depth_points = []
        
        # Update both canvases
        self.redraw_points()
        self.update_point_lists()

def main():
    root = tk.Tk()
    # Create the app without assigning to an unused variable
    DualImageMatchingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
