from tkinter import *
import tkinter.filedialog as tkFileDialog
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
import os


# ------------- Callbacks -------------

def select_plist():
    global plist_path
    plist_path = tkFileDialog.askopenfilename()
    if len(plist_path) > 0 and plist_path.lower().endswith('.txt'):
        plist_path_entry.delete(0, tk.END)
        plist_path_entry.insert(0, plist_path)
    else:
        messagebox.showinfo("Warning", "Please choose a .txt file!")


def select_ptrace1():
    global ptrace_path1
    ptrace_path1 = tkFileDialog.askopenfilename()
    if len(ptrace_path1) > 0 and ptrace_path1.lower().endswith('.txt'):
        ptrace_path1_entry.delete(0, tk.END)
        ptrace_path1_entry.insert(0, ptrace_path1)
    else:
        messagebox.showinfo("Warning", "Please choose a .txt file!")


def select_ptrace2():
    global ptrace_path2
    ptrace_path2 = tkFileDialog.askopenfilename()
    if len(ptrace_path2) > 0 and ptrace_path2.lower().endswith('.txt'):
        ptrace_path2_entry.delete(0, tk.END)
        ptrace_path2_entry.insert(0, ptrace_path2)
    else:
        messagebox.showinfo("Warning", "Please choose a .txt file!")


def select_ptrace3():
    global ptrace_path3
    ptrace_path3 = tkFileDialog.askopenfilename()
    if len(ptrace_path3) > 0 and ptrace_path3.lower().endswith('.txt'):
        ptrace_path3_entry.delete(0, tk.END)
        ptrace_path3_entry.insert(0, ptrace_path3)
    else:
        messagebox.showinfo("Warning", "Please choose a .txt file!")


def setDefault():
    global fetch_policy
    global replacement_policy
    global page_size
    global memory_size
    global plist_path
    global ptrace_path1
    global ptrace_path2
    global ptrace_path3

    page_size = 2
    memory_size = 512
    fetch_policy = 'DEMAND'
    replacement_policy = 'FIFO'
    plist_path = os.path.join('.', 'Data', 'plist.txt')
    ptrace_path1 = os.path.join('.', 'Data', 'ptrace.txt')
    ptrace_path2 = ''
    ptrace_path3 = ''

    plist_path_entry.delete(0, tk.END)
    plist_path_entry.insert(0, plist_path)

    ptrace_path1_entry.delete(0, tk.END)
    ptrace_path1_entry.insert(0, ptrace_path1)

    ptrace_path2_entry.delete(0, tk.END)
    ptrace_path2_entry.insert(0, ptrace_path2)

    ptrace_path3_entry.delete(0, tk.END)
    ptrace_path3_entry.insert(0, ptrace_path3)

    combobox1.current(0)   # DEMAND
    combobox2.current(0)   # FIFO
    combobox3.current(1)   # page size 2
    combobox4.current(0)   # memory size 512


def submit():
    global fetch_policy
    global replacement_policy
    global page_size
    global memory_size
    global plist_path_var
    global ptrace_path1_var
    global ptrace_path2_var
    global ptrace_path3_var
    global plist_path
    global ptrace_path1
    global ptrace_path2
    global ptrace_path3

    plist_path = str(plist_path_var.get()).strip()
    ptrace_path1 = str(ptrace_path1_var.get()).strip()
    ptrace_path2 = str(ptrace_path2_var.get()).strip()
    ptrace_path3 = str(ptrace_path3_var.get()).strip()

    if len(plist_path) < 1 or not plist_path.lower().endswith('.txt'):
        messagebox.showinfo("Error", "Process List path invalid!")
        return
    if len(ptrace_path1) < 1 or not ptrace_path1.lower().endswith('.txt'):
        messagebox.showinfo("Error", "Process Trace 1 path invalid!")
        return
    if not os.path.isfile(plist_path):
        messagebox.showinfo("Error", "Process List file doesn't exist!")
        return
    if not os.path.isfile(ptrace_path1):
        messagebox.showinfo("Error", "Process Trace 1 file doesn't exist!")
        return
    
    # Check ptrace2 if provided
    if len(ptrace_path2) > 0:
        if not ptrace_path2.lower().endswith('.txt'):
            messagebox.showinfo("Error", "Process Trace 2 path invalid!")
            return
        if not os.path.isfile(ptrace_path2):
            messagebox.showinfo("Error", "Process Trace 2 file doesn't exist!")
            return
    
    # Check ptrace3 if provided
    if len(ptrace_path3) > 0:
        if not ptrace_path3.lower().endswith('.txt'):
            messagebox.showinfo("Error", "Process Trace 3 path invalid!")
            return
        if not os.path.isfile(ptrace_path3):
            messagebox.showinfo("Error", "Process Trace 3 file doesn't exist!")
            return

    fetch_policy = str(c1.get())
    replacement_policy = str(c2.get())
    page_size = int(c3.get())
    memory_size = int(c4.get())

    if fetch_policy == '' or replacement_policy == '' or page_size == '' or memory_size == '':
        messagebox.showinfo("Error", "All required fields not filled!")
        return

    # This is what driver.py reads
    print(fetch_policy, replacement_policy, plist_path, ptrace_path1, ptrace_path2, ptrace_path3, page_size, memory_size, end='')

    messagebox.showinfo("Info", "Successfully submitted for processing!")
    root.destroy()


# ------------- UI setup -------------

root = Tk()
root.title('Virtual Memory Management Simulator')
root.resizable(False, False)
root.config(bg='black')

window_height = 650
window_width = 1200

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_cordinate = int((screen_width / 2) - (window_width / 2))
y_cordinate = int((screen_height / 2) - (window_height / 2))

root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

# Common fonts
TITLE_FONT = ("Segoe UI", 26, "bold")
LABEL_FONT = ("Segoe UI", 14)
BUTTON_FONT = ("Segoe UI", 12, "bold")
ENTRY_FONT = ("Segoe UI", 13)
COMBO_FONT = ("Segoe UI", 13)

frame1 = Frame(master=root, height=100, width=1000, pady=10, bg='black')
frame2 = Frame(master=root, height=50, width=1000, pady=15, bg='black')
frame3 = Frame(master=root, height=50, width=1000, pady=15, bg='black')
frame4 = Frame(master=root, height=50, width=1000, pady=15, bg='black')
frame5 = Frame(master=root, height=50, width=1000, pady=15, bg='black')
frame6 = Frame(master=root, height=50, width=1000, pady=15, bg='black')
frame7 = Frame(master=root, height=50, width=1000, pady=15, bg='black')
frame8 = Frame(master=root, height=50, width=1000, pady=15, bg='black')

frame1.pack()
frame2.pack()
frame3.pack()
frame4.pack()
frame5.pack()
frame6.pack()
frame7.pack()
frame8.pack()

title = Label(
    master=frame1,
    text='Virtual Memory Management Simulator',
    font=TITLE_FONT,
    fg='#23ff0f',
    bg='black'
)
title.pack()

plist_path_label = Label(
    master=frame2,
    text='Process list:',
    font=LABEL_FONT,
    fg='white',
    bg='black'
)
plist_path_label.pack(side=tk.LEFT, padx=10)

plist_path_var = StringVar()
plist_path = ''
plist_path_entry = Entry(
    master=frame2,
    textvariable=plist_path_var,
    width=50,
    font=ENTRY_FONT
)
plist_path_entry.pack(side=tk.LEFT, padx=10)

plist_btn = Button(
    master=frame2,
    text='Browse',
    font=BUTTON_FONT,
    command=select_plist
)
plist_btn.pack(side=tk.LEFT, padx=10)

# Process Trace 1
ptrace_path1_label = Label(
    master=frame3,
    text='Process trace 1:',
    font=LABEL_FONT,
    fg='white',
    bg='black'
)
ptrace_path1_label.pack(side=tk.LEFT, padx=10)

ptrace_path1_var = StringVar()
ptrace_path1 = ''
ptrace_path1_entry = Entry(
    master=frame3,
    textvariable=ptrace_path1_var,
    width=50,
    font=ENTRY_FONT
)
ptrace_path1_entry.pack(side=tk.LEFT, padx=10)

ptrace1_btn = Button(
    master=frame3,
    text='Browse',
    font=BUTTON_FONT,
    command=select_ptrace1
)
ptrace1_btn.pack(side=tk.LEFT, padx=10)

# Process Trace 2
ptrace_path2_label = Label(
    master=frame4,
    text='Process trace 2:',
    font=LABEL_FONT,
    fg='white',
    bg='black'
)
ptrace_path2_label.pack(side=tk.LEFT, padx=10)

ptrace_path2_var = StringVar()
ptrace_path2 = ''
ptrace_path2_entry = Entry(
    master=frame4,
    textvariable=ptrace_path2_var,
    width=50,
    font=ENTRY_FONT
)
ptrace_path2_entry.pack(side=tk.LEFT, padx=10)

ptrace2_btn = Button(
    master=frame4,
    text='Browse',
    font=BUTTON_FONT,
    command=select_ptrace2
)
ptrace2_btn.pack(side=tk.LEFT, padx=10)

# Process Trace 3
ptrace_path3_label = Label(
    master=frame5,
    text='Process trace 3:',
    font=LABEL_FONT,
    fg='white',
    bg='black'
)
ptrace_path3_label.pack(side=tk.LEFT, padx=10)

ptrace_path3_var = StringVar()
ptrace_path3 = ''
ptrace_path3_entry = Entry(
    master=frame5,
    textvariable=ptrace_path3_var,
    width=50,
    font=ENTRY_FONT
)
ptrace_path3_entry.pack(side=tk.LEFT, padx=10)

ptrace3_btn = Button(
    master=frame5,
    text='Browse',
    font=BUTTON_FONT,
    command=select_ptrace3
)
ptrace3_btn.pack(side=tk.LEFT, padx=10)

# Policies and settings
label = Label(
    master=frame6,
    text='Fetch policy:',
    font=LABEL_FONT,
    fg='white',
    bg='black'
)
label.pack(side=tk.LEFT, padx=5)

c1 = StringVar()
combobox1 = ttk.Combobox(
    master=frame6,
    textvariable=c1,
    font=COMBO_FONT,
    width=12,
    state='readonly'
)
combobox1['values'] = ('DEMAND', 'PRE')
combobox1.current(0)
combobox1.pack(side=tk.LEFT, padx=10)

label = Label(
    master=frame6,
    text='Replacement policy:',
    font=LABEL_FONT,
    fg='white',
    bg='black'
)
label.pack(side=tk.LEFT, padx=10)

c2 = StringVar()
combobox2 = ttk.Combobox(
    master=frame6,
    textvariable=c2,
    font=COMBO_FONT,
    width=16,
    state='readonly'
)
combobox2['values'] = ('FIFO', 'LRU', 'SECOND_CHANCE', 'OPTIMAL')
combobox2.current(0)
combobox2.pack(side=tk.LEFT, padx=10)

label = Label(
    master=frame7,
    text='Page size:',
    font=LABEL_FONT,
    fg='white',
    bg='black'
)
label.pack(side=tk.LEFT, padx=10)

c3 = IntVar()
combobox3 = ttk.Combobox(
    master=frame7,
    textvariable=c3,
    font=COMBO_FONT,
    width=10,
    state='readonly'
)
combobox3['values'] = (1, 2, 4, 8, 16, 32)
combobox3.current(0)
combobox3.pack(side=tk.LEFT, padx=10)

label = Label(
    master=frame7,
    text='Memory size:',
    font=LABEL_FONT,
    fg='white',
    bg='black'
)
label.pack(side=tk.LEFT, padx=10)

c4 = IntVar()
combobox4 = ttk.Combobox(
    master=frame7,
    textvariable=c4,
    font=COMBO_FONT,
    width=10,
    state='readonly'
)
combobox4['values'] = (512, 1024, 2048, 4096, 8192)
combobox4.current(0)
combobox4.pack(side=tk.LEFT, padx=10)

fetch_policy = ''
replacement_policy = ''
page_size = -1
memory_size = -1

btn_default = Button(
    master=frame8,
    text='Set default',
    font=BUTTON_FONT,
    command=setDefault
)
btn_default.pack(side=tk.LEFT, padx=10)

btn_submit = Button(
    master=frame8,
    text='Submit',
    font=BUTTON_FONT,
    command=submit
)
btn_submit.pack(side=tk.LEFT, padx=10)

root.mainloop()