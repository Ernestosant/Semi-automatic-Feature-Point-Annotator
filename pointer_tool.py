import tkinter as tk
from tkinter import ttk
from point_matching_tool import DualImageMatchingApp
from image_matching_tool import ObesityAnalyzerApp

class IntegratedToolApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Semi-automatic Feature Point Annotator")
        self.master.geometry("1200x800")

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.dual_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dual_frame, text="Point Mapping")
        self.dual_app = DualImageMatchingApp(self.dual_frame)

        self.analyzer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analyzer_frame, text="Image Overlay")
        self.analyzer_app = ObesityAnalyzerApp(self.analyzer_frame)

def main():
    root = tk.Tk()
    app = IntegratedToolApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
