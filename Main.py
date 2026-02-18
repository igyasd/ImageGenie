from tkinter.ttk import *
import openai
from numpy.ma.core import append
from ttkthemes import ThemedTk
import tkinter.ttk as ttk
import tkinter as tk
import requests
import base64
import os
from PIL import Image, ImageTk

client = openai.OpenAI(api_key = "ADD YOUR OWN API KEY")


window = ThemedTk(theme="equilux")
image_label = tk.Label(window, bg="#1e1e1e")
image_label.place(x=25, y=300)
window.title("Theme")
window.configure(bg="#1e1e1e")
window.geometry("450x650")
window.resizable(False, False)

OUTPUT_DIR = "outputs"
image_paths = []
cIndex=0

def download_image(url,filepath):
    img_data= requests.get(url).content
    with open(filepath,"wb") as f:
        f.write(img_data)


def process(event=None):
    global image_paths
    user = promptentry.get().strip()
    if rb.get() == "Choice1":
        n=1
    else:
        n=2

    ideas=generate_ideas(user,n)
    image_paths = generate_images_from_ideas2(ideas)
    cIndex=0
    showImage(0)




def generate_images_from_ideas2(ideas):
    paths=[]

    for i in range(len(ideas)):
        img = client.images.generate(
            model="gpt-image-1.5",  # newest quality
            prompt=ideas[i],
            size="1024x1024",
            n=1,
            output_format="jpeg"  # png / webp / jpeg
        )

        filepath=os.path.join(OUTPUT_DIR,f"request_{i+1}.jpg")

        b64 = img.data[0].b64_json
        print(b64)


        with open(filepath,"wb") as f:
            f.write(base64.b64decode(b64))
        paths.append(filepath)

    return paths



def nextImg(event=None):
    global cIndex
    if not image_paths:
        return
    cIndex = (cIndex + 1) % len(image_paths)
    showImage(cIndex)

def prevImg(event=None):
    global cIndex
    if not image_paths:
        return
    cIndex = (cIndex - 1) % len(image_paths)
    showImage(cIndex)


def generate_ideas(user_text, n):
    prompt = (
        f"Give me {n} creative wallpaper ideas about: {user_text}\n"
        f"Return ONLY {n} lines. No numbering, no bullets."
    )

    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.9,
    )

    ideas = []

    for line in resp.choices[0].message.content.splitlines():
        line = line.strip()
        print(line)
        if line != "":
            ideas.append(line)

    return ideas[:n]

def showImage(ind):
    global imagePreview, image_paths

    if not image_paths:
        return

    img = Image.open(image_paths[ind])
    img = img.resize((400, 400), Image.Resampling.LANCZOS)

    imagePreview = ImageTk.PhotoImage(img)
    image_label = tk.Label(window, bg="#1e1e1e")
    image_label.place(x=25, y=300)

    image_label.config(image=imagePreview)





def generate_images_from_ideas(ideas):
    paths = []

    for i in range(len(ideas)):
        idea = ideas[i]

        img = client.images.generate(
            model="dall-e-3",
            prompt=idea,
            size="1024x1024",
            n=1
        )
        url=img.data[0].url
        print(url)

        filepath = OUTPUT_DIR + "/request-" + str(i + 1) + ".jpg"

        download_image(url, filepath)

        paths.append(filepath)


lbl1 = Label(window, text="PolyGenix", font=("edited", 28, "bold"),background="#1e1e1e")
lbl1.pack(pady=10)

lbl2 = Label(window, text="Idea generation for 3D printable designs", font=("Hamston", 14, "bold"),background="#1e1e1e")
lbl2.pack(pady=5)

rb = tk.StringVar(value="Choice1")

rad1 = Radiobutton(window, text="Short [1 variants]", value="Choice1", variable=rb)
rad1.place(x=85, y=100)

rad2 = Radiobutton(window, text="Extended [2 Variants]", value="Choice3", variable=rb)
rad2.place(x=235, y=100)

promptentry = Entry(window,font=("Arial", 15), background="#1e1e1e",foreground="white",width=30)
promptentry.place(x=60,y=200)

preview = ttk.Button(window, text="Preview")
preview.place(x=60, y=230)


enter = ttk.Button(window, text="Enter",command=process)
enter.place(x=318, y=230)

window.bind("<Left>",prevImg())
window.bind("<Right>",nextImg())

window.mainloop()