import tkinter as tk
from tkinter import messagebox, filedialog
import xml.etree.ElementTree as ET

class DrawingEditor:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack()

        self.start_x = None
        self.start_y = None
        self.draw_mode = "line"
        self.shapes = []
        self.selected_items = []

        self.toolbar = tk.Frame(root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.line_button = tk.Button(self.toolbar, text="Line", command=lambda: self.switch_mode("line"))
        self.line_button.pack(side=tk.LEFT)

        self.rectangle_button = tk.Button(self.toolbar, text="Rectangle", command=lambda: self.switch_mode("rectangle"))
        self.rectangle_button.pack(side=tk.LEFT)

        self.select_button = tk.Button(self.toolbar, text="Select", command=lambda: self.switch_mode("select"))
        self.select_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.toolbar, text="Save", command=self.save)
        self.save_button.pack(side=tk.LEFT)

        self.export_button = tk.Button(self.toolbar, text="Export", command=self.export)
        self.export_button.pack(side=tk.LEFT)

        self.delete_button = tk.Button(self.toolbar, text="Delete", command=self.delete_selected)
        self.delete_button.pack(side=tk.LEFT)

        self.menu = tk.Menu(root)
        self.menu.add_command(label="Save", command=self.save)
        self.menu.add_command(label="Export", command=self.export)
        self.root.config(menu=self.menu)

    def switch_mode(self, mode):
        self.draw_mode = mode
        if mode == "select":
            self.selection_mode = True
            self.canvas.bind("<Button-1>", self.start_selection)
            self.canvas.bind("<B1-Motion>", self.draw_selection)
            self.canvas.bind("<ButtonRelease-1>", self.end_selection)
        else:
            self.selection_mode = False
            self.canvas.bind("<Button-1>", self.start_drawing)
            self.canvas.bind("<B1-Motion>", self.draw)
            self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def start_drawing(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def draw(self, event):
        self.canvas.delete("temp_shape")
        if self.draw_mode == "rectangle":
            self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="black", tags="temp_shape")
        elif self.draw_mode == "line":
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, fill="black", tags="temp_shape")

    def stop_drawing(self, event):
        self.canvas.delete("temp_shape")
        item_id = self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, fill="black") if self.draw_mode == "line" else self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="black")
        shape_details = {
            'type': self.draw_mode,
            'start_x': self.start_x,
            'start_y': self.start_y,
            'end_x': event.x,
            'end_y': event.y,
            'item_id': item_id
        }
        self.shapes.append(shape_details)

    def start_selection(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.canvas.delete("selection")

    def draw_selection(self, event):
        self.canvas.delete("selection")
        self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="blue", tags="selection")

    def end_selection(self, event):
        self.canvas.delete("selection")
        selection_rect = (self.start_x, self.start_y, event.x, event.y)
        self.select_shapes(selection_rect)

    def select_shapes(self, rect):
        for item in self.selected_items:
            item_type = self.canvas.type(item)
            if item_type == 'line':
                self.canvas.itemconfig(item, fill="black", width=1)
            else:
                self.canvas.itemconfig(item, outline="black", width=1)
        self.selected_items.clear()
        selected_items = self.canvas.find_overlapping(rect[0], rect[1], rect[2], rect[3])
        for item in selected_items:
            item_type = self.canvas.type(item)
            if item_type == 'line':
                self.canvas.itemconfig(item, fill="red", width=2)
            else:
                self.canvas.itemconfig(item, outline="red", width=2)
            self.selected_items.append(item)

    def delete_selected(self):
        for item in self.selected_items:
            self.canvas.delete(item)
        self.shapes = [shape for shape in self.shapes if shape['item_id'] not in self.selected_items]
        self.selected_items.clear()

    def save(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if filename:
            with open(filename, "w") as file:
                file.write("Save your drawing data here")

    def export(self):
        root = ET.Element("Shapes")
        for shape in self.shapes:
            shape_element = ET.SubElement(root, shape['type'])
            for key, value in shape.items():
                if key != 'type':
                    shape_element.set(key, str(value))
        tree = ET.ElementTree(root)
        filename = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML Files", "*.xml")])
        if filename:
            tree.write(filename)
        messagebox.showinfo("Export", "Drawing exported to XML successfully!")

root = tk.Tk()
app = DrawingEditor(root)
root.mainloop()
