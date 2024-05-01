import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

rectangles = []
rect_id = None

def import_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        show_image(file_path)

def show_image(file_path):
    global photo
    image = Image.open(file_path)
    photo = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)

def on_canvas_click(event):
    global start_x, start_y, rect_id
    start_x, start_y = event.x, event.y
    rect_id = canvas.create_rectangle(start_x, start_y, start_x + 1, start_y + 1, outline='red')

def on_canvas_drag(event):
    end_x, end_y = event.x, event.y
    canvas.coords(rect_id, start_x, start_y, end_x, end_y)

def on_canvas_release(event):
    global rect_id
    end_x, end_y = event.x, event.y
    if rect_id:
        coordinates = (start_x, start_y, end_x, end_y)
        rectangles.append([rect_id, coordinates])
        rect_id = None  # Réinitialise rect_id après validation
        print(f"Rectangle added: {coordinates}")  # Debug: print when rectangle is added

def clear_last_rectangle():
    if rectangles:
        rect_to_delete = rectangles.pop()
        canvas.delete(rect_to_delete[0])
        print(f"Rectangle removed: {rect_to_delete[1]}")  # Debug: print when rectangle is removed

def validate_all():
    coords_list = [rect[1] for rect in rectangles]
    coords_str = "\n".join(map(str, coords_list))
    messagebox.showinfo("Coordonnées des Rectangles", f"Les coordonnées des rectangles sont :\n{coords_str}")
    print("Les coordonnées des rectangles sont :")
    for coords in coords_list:
        print(coords)

root = tk.Tk()
root.geometry('1368x768')
root.title("ProjectL2")

canvas = tk.Canvas(root)
canvas.pack(fill='both', expand=True)

btn_import_image = tk.Button(root, text="Importer Image", command=import_image)
btn_import_image.pack(pady=10)

canvas.bind("<ButtonPress-1>", on_canvas_click)
canvas.bind("<B1-Motion>", on_canvas_drag)
canvas.bind("<ButtonRelease-1>", on_canvas_release)  # Bind the release event to finalize the rectangle

btn_validate = tk.Button(root, text="Valider Tout", command=validate_all)
btn_validate.pack(side='left', padx=10)

btn_clear = tk.Button(root, text="Effacer Dernier Rectangle", command=clear_last_rectangle)
btn_clear.pack(side='left', padx=10)

root.mainloop()
