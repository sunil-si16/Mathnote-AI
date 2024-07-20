import tkinter as tk
from tkinter import font as tkFont
from openai import OpenAI
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class MathNotes():
    def __init__(self, root):
        self.root = root
        self.root.title("Math Notes - AI")

        self.canvas_width = 1200
        self.canvas_height = 800

        self.canvas = tk.Canvas(root, bg='black', width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)
        self.root.bind("<Control-z>", self.command_undo)
        self.root.bind("<Return>", self.command_calculate)

        self.current_action = []
        self.actions = []
        self.last_x = None
        self.last_y = None

        self.button_clear = tk.Button(root, text="Clear", command=self.clear)
        self.button_clear.pack(side=tk.LEFT)

        self.button_undo = tk.Button(root, text="Undo", command=self.undo)
        self.button_undo.pack(side=tk.LEFT)

        self.button_calculate = tk.Button(root, text="Calculate", command=self.calculate)
        self.button_calculate.pack(side=tk.LEFT)

        self.font = tkFont.Font(family="Noteworthy", size=20)

        self.api_key = 'YOUR API KEY'
        self.client = OpenAI(api_key=self.api_key)

    def start_drawing(self, event):
        self.current_action = []
        self.last_x, self.last_y = event.x, event.y

    def paint(self, event):
        x, y = event.x, event.y
        if self.last_x and self.last_y:
            line_id = self.canvas.create_line((self.last_x, self.last_y, x, y), fill='white', width=5)
            self.draw.line((self.last_x, self.last_y, x, y), fill='white', width=5)
            self.current_action.append((line_id, (self.last_x, self.last_y, x, y)))
        self.last_x, self.last_y = x, y

    def reset(self, event):
        self.last_x, self.last_y = None, None
        if self.current_action:
            self.actions.append(self.current_action)

    def clear(self):
        self.canvas.delete('all')
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.actions = []

    def undo(self):
        if self.actions:
            last_action = self.actions.pop()
            for line_id, coords in last_action:
                self.canvas.delete(line_id)
            self.redraw_all()

    def redraw_all(self):
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.canvas.delete('all')
        for action in self.actions:
            for _, coords in action:
                self.draw.line(coords, fill='white', width=5)
                self.canvas.create_line(coords, fill='white', width=5)

    def draw_answer(self, answer):
        if not self.actions:
            return

        last_action = self.actions[-1]
        last_coords = last_action[-1][-1]

        equals_x = last_coords[2]
        equals_y = last_coords[3]

        x_start = equals_x + 70
        y_start = equals_y - 20

        self.canvas.create_text(x_start, y_start, text=answer, font=self.font, fill='#11ff00')

        font = ImageFont.load_default()
        self.draw.text((x_start, y_start - 50), answer, font=font, fill='#11ff00')

    def calculate(self):
        def encode_image(image):
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

        base64_image = encode_image(self.image)

        response = self.client.completions.create(
            model="gpt-3.5-turbo",
            prompt=f"Give the answer to this math equation. Only respond with the answer. Only respond with numbers. NEVER Words. Only answer unanswered expressions. Look for equal sign with nothing on the right of it. If it has an answer already. DO NOT ANSWER it.\n\n[image_url data:image/png;base64,{base64_image}]",
            max_tokens=300
        )

        answer = response.choices[0].text.strip()
        self.draw_answer(answer)

    def command_undo(self, event):
        self.undo()

    def command_calculate(self, event):
        self.calculate()

if __name__ == "__main__":
    root = tk.Tk()
    app = MathNotes(root)
    root.mainloop()
