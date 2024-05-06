import tkinter as tk
from tkinter import messagebox, filedialog
import xml.etree.ElementTree as ET

class DrawingEditor:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack()

        self.begin_x = None
        self.begin_y = None
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

        self.move_button = tk.Button(self.toolbar, text="Move", command=lambda: self.switch_mode("move"))
        self.move_button.pack(side=tk.LEFT)
        
        self.group_button = tk.Button(self.toolbar, text="Group", command=self.group_selected)
        self.group_button.pack(side=tk.LEFT)
        
        self.ungroup_button = tk.Button(self.toolbar, text="Ungroup", command=self.ungroup_selected)
        self.ungroup_button.pack(side=tk.LEFT)
        
        self.delete_button = tk.Button(self.toolbar, text="Delete", command=self.delete_selected)
        self.delete_button.pack(side=tk.LEFT)

        self.export_button = tk.Button(self.toolbar, text="Export", command=self.export)
        self.export_button.pack(side=tk.RIGHT)
        
        self.open_button = tk.Button(self.toolbar, text="Open", command=self.open)
        self.open_button.pack(side=tk.RIGHT)
        
        self.save_button = tk.Button(self.toolbar, text="Save", command=self.save)
        self.save_button.pack(side=tk.RIGHT)

        # self.menu = tk.Menu(root)
        # self.menu.add_command(label="Save", command=self.save)
        # self.menu.add_command(label="Export", command=self.export)
        # self.root.config(menu=self.menu)

    def switch_mode(self, mode):
        self.draw_mode = mode
        if mode == "select":
            self.selection_mode = True
            self.canvas.bind("<Button-1>", self.start_selection)
            self.canvas.bind("<B1-Motion>", self.draw_selection)
            self.canvas.bind("<ButtonRelease-1>", self.end_selection)
        elif mode == "move":
            self.selection_mode = True
            self.canvas.bind("<Button-1>", self.start_move)
            self.canvas.bind("<B1-Motion>", self.move)
            self.canvas.bind("<ButtonRelease-1>", self.stop_move)
        else:
            self.selection_mode = False
            self.canvas.bind("<Button-1>", self.start_drawing)
            self.canvas.bind("<B1-Motion>", self.draw)
            self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def start_drawing(self, event):
        self.begin_x = event.x
        self.begin_y = event.y

    def draw(self, event):
        self.canvas.delete("temp_shape")
        if self.draw_mode == "rectangle":
            self.canvas.create_rectangle(self.begin_x, self.begin_y, event.x, event.y, outline="black", tags="temp_shape")
        elif self.draw_mode == "line":
            self.canvas.create_line(self.begin_x, self.begin_y, event.x, event.y, fill="black", tags="temp_shape")

    def stop_drawing(self, event):
        self.canvas.delete("temp_shape")
        shape_details = (
            self.draw_mode,
            {'begin_x': self.begin_x, 'begin_y': self.begin_y, 'end_x': event.x, 'end_y': event.y},
            self.canvas.create_line(self.begin_x, self.begin_y, event.x, event.y, fill="black") if self.draw_mode == "line" else self.canvas.create_rectangle(self.begin_x, self.begin_y, event.x, event.y, outline="black")
        )
        # Add new shape to a new group
        self.shapes.append([shape_details])

    def start_selection(self, event):
        self.begin_x = event.x
        self.begin_y = event.y
        self.canvas.delete("selection")

    def draw_selection(self, event):
        self.canvas.delete("selection")
        self.canvas.create_rectangle(self.begin_x, self.begin_y, event.x, event.y, outline="blue", tags="selection")

    def end_selection(self, event):
        self.canvas.delete("selection")
        selection_rect = (self.begin_x, self.begin_y, event.x, event.y)
        self.select_shapes(selection_rect)

    def select_shapes(self, rect):
        for group in self.shapes:
            for shape in group:
                item_id = shape[2]  # Extract the item ID from the shape details
                if self.canvas.type(item_id) == 'line':
                    self.canvas.itemconfig(item_id, fill="black", width=1)
                else:
                    self.canvas.itemconfig(item_id, outline="black", width=1)
        self.selected_items.clear()

        selected_items = self.canvas.find_overlapping(rect[0], rect[1], rect[2], rect[3])
        for group in self.shapes:
            for shape in group:
                if shape[2] in selected_items:
                    item_id = shape[2]
                    if self.canvas.type(item_id) == 'line':
                        self.canvas.itemconfig(item_id, fill="red", width=2)
                    else:
                        self.canvas.itemconfig(item_id, outline="red", width=2)
                    if group not in self.selected_items:
                        self.selected_items.append(group)
                        # Color all objects within the group when selected
                        for shape_in_group in group:
                            item_id_in_group = shape_in_group[2]
                            if self.canvas.type(item_id_in_group) == 'line':
                                self.canvas.itemconfig(item_id_in_group, fill="red", width=2)
                            else:
                                self.canvas.itemconfig(item_id_in_group, outline="red", width=2)
                    break

    def start_move(self, event):
        self.begin_x = event.x
        self.begin_y = event.y

    def stop_move(self, event):
        # Unbind motion and button release events
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

        # Reset the appearance of all moved items
        for group in self.selected_items:
            for shape in group:
                item_id = shape[2]
                if self.canvas.type(item_id) == 'line':
                    self.canvas.itemconfig(item_id, fill="black", width=1)
                else:
                    self.canvas.itemconfig(item_id, outline="black", width=1)

        # Clear the list of selected items
        self.selected_items.clear()
        
    def move(self, event):
        dx = event.x - self.begin_x
        dy = event.y - self.begin_y
        for group in self.selected_items:
            for shape in group:
                self.canvas.move(shape[2], dx, dy)
        self.begin_x = event.x
        self.begin_y = event.y
        
    def delete_selected(self):
        for group in self.selected_items:
            for shape in group:
                self.canvas.delete(shape[2])
        self.shapes = [group for group in self.shapes if group not in self.selected_items]
        self.selected_items.clear()
        
    def group_selected(self):
        if len(self.selected_items) > 1:
            new_group = []
            for group in self.selected_items:
                for shape in group:
                    new_group.append(shape)
            self.shapes.append(new_group)
            self.selected_items.clear()
        else:
            messagebox.showwarning("Group", "Select multiple items to group!")
            
    def ungroup_selected(self):
        for group in self.selected_items:
            for shape in group:
                self.shapes.append([shape])
        self.shapes.remove(group)
        self.selected_items.clear()

    # def save(self):
    #     filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    #     if filename:
    #         with open(filename, "w") as file:
    #             file.write("Save your drawing data here") # Needs to be updated with ASCII text format of the drawing

    def save(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if filename:
            with open(filename, "w") as file:
                for group in self.shapes:
                    if len(group) > 1:
                        file.write("start\n")
                    for shape in group:
                        print(shape)
                        file.write((" ").join([shape[0], str(shape[1]['begin_x']), str(shape[1]['begin_y']), str(shape[1]['end_x']), str(shape[1]['end_y'])]))
                        file.write("\n")
                    if len(group) > 1:
                        file.write("end\n")
                messagebox.showinfo("Save", "Drawing saved successfully!")

    def open(self, filename=None):
        if not filename:
            filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filename:
            with open(filename, "r") as file:
                self.load_drawing(file)

    def load_drawing(self, file):
        print("Yes")
        # self.clear()  # Clear existing drawing
        current_group = []  # List to hold shapes in the current group
        for line in file:
            line = line.strip()
            if line == "start":
                current_group = []  # Start a new group
            elif line == "end":
                self.shapes.append(current_group)  # Add the current group to the list of shapes
                current_group = []  # Clear the current group
            else:
                shape_data = line.split()
                shape_type = shape_data[0]
                shape_properties = {
                    'begin_x': int(shape_data[1]),
                    'begin_y': int(shape_data[2]),
                    'end_x': int(shape_data[3]),
                    'end_y': int(shape_data[4])
                }
                current_group.append((shape_type, shape_properties))
        # Add the last group if it exists
        # if current_group:
        #     self.shapes.append(current_group)
        print(self.shapes)
        


    def export(self):
        root = ET.Element("Shapes")
        for group in self.shapes:
            if len(group) > 1:
                group_element = ET.SubElement(root, "Group")  # Create a group element for each group
                
            for shape in group:
                shape_type = shape[0]  # 'line' or 'rectangle'
                props = shape[1]
                # Create an XML element for each shape based on its type
                if len(group) == 1:
                    shape_element = ET.SubElement(root, shape_type)  # Add shape element as a child of the root element
                else:
                    shape_element = ET.SubElement(group_element, shape_type)  # Add shape element as a child of the group element
                # Add details as sub-elements or attributes
                ET.SubElement(shape_element, 'StartX').text = str(props['begin_x'])
                ET.SubElement(shape_element, 'StartY').text = str(props['begin_y'])
                ET.SubElement(shape_element, 'EndX').text = str(props['end_x'])
                ET.SubElement(shape_element, 'EndY').text = str(props['end_y'])
                # Assume 'color' is always defined; if not, you'll need to set a default or check if it exists
                ET.SubElement(shape_element, 'Color').text = props.get('color', 'black')  
                if shape_type == 'rectangle':
                    # Only rectangles might have 'corner_style'
                    corner_style = props.get('corner_style', 'square')  # Default to 'square' if not present
                    ET.SubElement(shape_element, 'CornerStyle').text = corner_style
        
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)
        filename = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML Files", "*.xml")])
        if filename:
            try:
                tree.write(filename, encoding="utf-8")
                messagebox.showinfo("Export", "Drawing exported to XML successfully!")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

root = tk.Tk()
app = DrawingEditor(root)
root.mainloop()
