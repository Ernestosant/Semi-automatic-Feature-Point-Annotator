import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar_h = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_h.set)

        scrollbar.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

class ObesityAnalyzerApp:
    def __init__(self, master):
        self.master = master
        
        # Main frame with scroll
        self.main_frame = ScrollableFrame(self.master)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Button frame - centered
        self.button_frame = ttk.Frame(self.main_frame.scrollable_frame)
        self.button_frame.pack(fill=tk.X, padx=10, pady=10)

        # Container to center buttons
        self.center_buttons = ttk.Frame(self.button_frame)
        self.center_buttons.pack(expand=True)

        # Buttons to load images
        self.btn_load_rgb = tk.Button(self.center_buttons, text="Load RGB Image", 
                                    command=self.load_rgb_image)
        self.btn_load_rgb.pack(side=tk.LEFT, padx=5)
        
        self.btn_load_depth = tk.Button(self.center_buttons, text="Load Depth Map", 
                                      command=self.load_depth_image)
        self.btn_load_depth.pack(side=tk.LEFT, padx=5)

        # Slider for alpha
        self.alpha_label = ttk.Label(self.center_buttons, text="Transparency:")
        self.alpha_label.pack(side=tk.LEFT, padx=5)
        self.alpha_slider = ttk.Scale(self.center_buttons, from_=0, to=100, orient="horizontal")
        self.alpha_slider.set(40)  # Initial value 0.4
        self.alpha_slider.pack(side=tk.LEFT, padx=5)
        self.alpha_slider.bind("<Motion>", self.update_overlay)

        # After the alpha slider, add sliders for offset
        self.offset_frame = ttk.Frame(self.center_buttons)
        self.offset_frame.pack(side=tk.LEFT, padx=10)
        
        # Frame for X offset
        self.x_offset_frame = ttk.Frame(self.offset_frame)
        self.x_offset_frame.pack(fill=tk.X)
        
        self.x_offset_label = ttk.Label(self.x_offset_frame, text="X Offset:")
        self.x_offset_label.pack(side=tk.LEFT)
        
        self.x_offset_slider = ttk.Scale(self.x_offset_frame, from_=-100, to=100, orient="horizontal")
        self.x_offset_slider.set(-36)  # Initial value X = -36
        self.x_offset_slider.pack(side=tk.LEFT, padx=5)
        
        # Variable to sync entry with slider
        self.x_offset_var = tk.StringVar(value="0")  # Initially 0
        self.x_offset_entry = ttk.Entry(self.x_offset_frame, textvariable=self.x_offset_var, width=5)
        self.x_offset_entry.pack(side=tk.LEFT)
        
        ttk.Label(self.x_offset_frame, text="px").pack(side=tk.LEFT)
        
        # Frame for Y offset
        self.y_offset_frame = ttk.Frame(self.offset_frame)
        self.y_offset_frame.pack(fill=tk.X, pady=5)
        
        self.y_offset_label = ttk.Label(self.y_offset_frame, text="Y Offset:")
        self.y_offset_label.pack(side=tk.LEFT)
        
        self.y_offset_slider = ttk.Scale(self.y_offset_frame, from_=-100, to=100, orient="horizontal")
        self.y_offset_slider.set(0)
        self.y_offset_slider.pack(side=tk.LEFT, padx=5)
        
        # Variable to sync entry with slider
        self.y_offset_var = tk.StringVar(value="0")  # Initially 0
        self.y_offset_entry = ttk.Entry(self.y_offset_frame, textvariable=self.y_offset_var, width=5)
        self.y_offset_entry.pack(side=tk.LEFT)
        
        ttk.Label(self.y_offset_frame, text="px").pack(side=tk.LEFT)
        
        # Bind events
        self.x_offset_slider.bind("<Motion>", self.on_x_slider_change)
        self.y_offset_slider.bind("<Motion>", self.on_y_slider_change)
        self.x_offset_entry.bind("<Return>", self.on_x_entry_change)
        self.y_offset_entry.bind("<Return>", self.on_y_entry_change)

        # Variable initialization
        self.points = []
        self.lines = []  # New list for storing lines
        self.canvas = None
        self.rgb_image_cv = None
        self.depth_image_cv = None
        self.current_image_tk = None

        # Add clear points button after other buttons
        self.clear_button = ttk.Button(self.button_frame, text="Clear Points", command=self.clear_points)
        self.clear_button.pack(side=tk.LEFT, padx=5)

    def load_rgb_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg")])
        if not path:
            return
        
        self.rgb_image_cv = cv2.imread(path)
        self.create_or_update_canvas()
        self.update_overlay()

    def load_depth_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg")])
        if not path:
            return
        
        self.depth_image_cv = cv2.imread(path)
        # Set default values when loading depth image
        self.x_offset_slider.set(-36)
        self.x_offset_var.set("-36")
        self.y_offset_slider.set(8)
        self.y_offset_var.set("8")
        self.create_or_update_canvas()
        self.update_overlay()

    def create_or_update_canvas(self):
        if self.rgb_image_cv is None:
            return

        if self.canvas is None:
            # Horizontal frame for canvas and point list
            self.horizontal_frame = ttk.Frame(self.main_frame.scrollable_frame)
            self.horizontal_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
            
            # Left frame for canvas
            self.canvas_frame = ttk.Frame(self.horizontal_frame)
            self.canvas_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0,10))
            
            self.canvas = tk.Canvas(self.canvas_frame)
            self.canvas.pack(expand=True)
            self.canvas.bind("<Button-1>", self.on_click)

            # Right frame for point list - fixed width
            self.points_container = ttk.Frame(self.horizontal_frame, width=200)
            self.points_container.pack_propagate(False)  # Prevent frame from auto-adjusting
            self.points_container.pack(side=tk.RIGHT, fill=tk.Y, padx=(10,0))
            
            # Title for point list - centered
            self.points_title = ttk.Label(self.points_container, 
                                        text="Points List", 
                                        font=("Arial", 12, "bold"),
                                        anchor="center")
            self.points_title.pack(pady=5, fill=tk.X)

            # Scrollable frame for points - fixed width
            self.points_scroll = ScrollableFrame(self.points_container)
            self.points_scroll.pack(fill=tk.BOTH, expand=True)
            
            self.points_frame = ttk.Frame(self.points_scroll.scrollable_frame)
            self.points_frame.pack(fill=tk.X, expand=True)

            # Button to clear points
            self.clear_points_btn = tk.Button(self.points_container, 
                                            text="Clear Points",
                                            command=self.clear_points)
            self.clear_points_btn.pack(pady=10)

    def clear_points(self):
        # Clear points and lines from canvas
        for _, _, point_id in self.points:
            self.canvas.delete(point_id)
        for line_id in self.lines:
            self.canvas.delete(line_id)
        
        # Clear lists
        self.points = []
        self.lines = []
        
        # Update image
        self.update_overlay()
        
        # Clear point list
        for widget in self.points_frame.winfo_children():
            widget.destroy()

    def update_overlay(self, event=None):
        if self.rgb_image_cv is None:
            return

        # Create base image
        overlay = self.rgb_image_cv.copy()

        if self.depth_image_cv is not None:
            # Get offset values from variables
            try:
                x_offset = int(self.x_offset_var.get())
                y_offset = int(self.y_offset_var.get())
            except ValueError:
                x_offset = int(self.x_offset_slider.get())
                y_offset = int(self.y_offset_slider.get())
            
            # Create transformation matrix for offset
            M = np.float32([[1, 0, x_offset], [0, 1, y_offset]])
            
            # Apply offset to depth map
            depth_resized = cv2.resize(self.depth_image_cv, 
                                     (self.rgb_image_cv.shape[1], self.rgb_image_cv.shape[0]))
            depth_shifted = cv2.warpAffine(depth_resized, M, 
                                         (depth_resized.shape[1], depth_resized.shape[0]))
            
            # Convert to grayscale and apply colormap
            depth_gray = cv2.cvtColor(depth_shifted, cv2.COLOR_BGR2GRAY)
            depth_normalized = cv2.normalize(depth_gray, None, 0, 255, cv2.NORM_MINMAX)
            depth_colormap = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)

            # Apply transparency
            alpha = self.alpha_slider.get() / 100.0
            overlay = cv2.addWeighted(overlay, 1-alpha, depth_colormap, alpha, 0)

        # Convert to PIL format and then to PhotoImage
        overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(overlay_rgb)
        self.current_image_tk = ImageTk.PhotoImage(image)

        # Update canvas
        if self.canvas is not None:
            self.canvas.delete("all")
            self.canvas.config(width=image.width, height=image.height)
            self.canvas.create_image(0, 0, image=self.current_image_tk, anchor="nw")
            
            # Redraw lines
            for i in range(len(self.points)-1):
                x1, y1, _ = self.points[i]
                x2, y2, _ = self.points[i+1]
                self.canvas.create_line(x1, y1, x2, y2, fill="yellow", width=2)
            
            # Redraw points and their labels above the lines
            for i, (x, y, _) in enumerate(self.points, 1):
                self.canvas.create_oval(x-4, y-4, x+4, y+4, 
                                     fill="white", outline="black", width=2)
                self.canvas.create_text(x, y-15, text=f"{i}", 
                                     fill="white", font=("Arial", 12, "bold"))

    def on_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Create the point
        point_id = self.canvas.create_oval(x-4, y-4, x+4, y+4, 
                                         fill="white", outline="black", width=2)
        self.points.append((x, y, point_id))
        
        # Draw line if there is a previous point
        if len(self.points) > 1:
            prev_x, prev_y, _ = self.points[-2]
            line_id = self.canvas.create_line(prev_x, prev_y, x, y, 
                                            fill="yellow", width=2)
            self.lines.append(line_id)
        
        # Add only the number above the point
        self.canvas.create_text(x, y-15, text=str(len(self.points)), 
                              fill="white", font=("Arial", 12, "bold"))
        
        # Create frame for each point with border and fixed width
        point_container = ttk.Frame(self.points_frame, relief="solid", borderwidth=1)
        point_container.pack(fill=tk.X, padx=5, pady=2)
        
        # Centered label with coordinates
        point_label = ttk.Label(point_container, 
                              text=f"Point {len(self.points)} at ({int(x)}, {int(y)})",
                              anchor="center")
        point_label.pack(padx=5, pady=2, fill=tk.X)

    def on_x_slider_change(self, event=None):
        value = int(self.x_offset_slider.get())
        self.x_offset_var.set(str(value))
        self.update_overlay()

    def on_y_slider_change(self, event=None):
        value = int(self.y_offset_slider.get())
        self.y_offset_var.set(str(value))
        self.update_overlay()

    def on_x_entry_change(self, event=None):
        try:
            value = int(self.x_offset_var.get())
            value = max(-100, min(100, value))  # Limit between -100 and 100
            self.x_offset_slider.set(value)
            self.x_offset_var.set(str(value))
            self.update_overlay()
        except ValueError:
            self.x_offset_var.set(str(int(self.x_offset_slider.get())))  # Corrected missing parenthesis

    def on_y_entry_change(self, event=None):
        try:
            value = int(self.y_offset_var.get())
            value = max(-100, min(100, value))  # Limit between -100 and 100
            self.y_offset_slider.set(value)
            self.y_offset_var.set(str(value))
            self.update_overlay()
        except ValueError:
            self.y_offset_var.set(str(int(self.y_offset_slider.get())))

def main():
    root = tk.Tk()
    app = ObesityAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
