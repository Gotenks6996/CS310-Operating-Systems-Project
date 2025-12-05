from tkinter import *
from PIL import Image as PIL_Image
from PIL import ImageTk
import cv2
from tkinter import messagebox
import sys
import os
import glob

# Keep references to Tk images so they don't get garbage-collected
_image_refs = []

# Will be set in main()
NUM_PROCESSES = 0
MEMORY_SIZE = ""
PAGE_SIZE = ""
PAGING = ""
REPLACEMENT = ""
PROCESS_COUNT = ""
MEMORY_REQ_COUNT = ""
PAGE_FAULTS = ""


def build_stats_header():
    """Build the fixed header (title + stats table + section title)."""
    # Frames
    frame1 = Frame(master=master_frame, width=1530, pady=10, bg='black')
    frame2 = Frame(master=master_frame, width=1530, pady=10, bg='black')
    frame3 = Frame(master=master_frame, width=1530, pady=5, bg='black')
    frame4 = Frame(master=master_frame, width=1530, pady=10, bg='black')

    frame1.pack()
    frame2.pack()
    frame3.pack()
    frame4.pack(pady=(20, 0))

    # Fonts
    TITLE_FONT = ("Segoe UI", 26, "bold")
    SUBTITLE_FONT = ("Segoe UI", 18, "bold")
    TABLE_FONT = ("Consolas", 13)

    # Title
    title = Label(
        master=frame1,
        text='Virtual Memory Management Simulator',
        font=TITLE_FONT,
        fg='#23ff0f',
        bg='black'
    )
    title.pack()

    subtitle1 = Label(
        master=frame2,
        text='Results',
        font=SUBTITLE_FONT,
        fg='light green',
        bg='black'
    )
    subtitle1.pack(side=LEFT, padx=10)

    # Stats table
    height = 7
    width = 2
    data = [
        ['Number of processes',        ':  ' + PROCESS_COUNT],
        ['Number of memory requests',  ':  ' + MEMORY_REQ_COUNT],
        ['Fetch policy',               ':  ' + PAGING],
        ['Replacement policy',         ':  ' + REPLACEMENT],
        ['Page size',                  ':  ' + PAGE_SIZE],
        ['Memory size',                ':  ' + MEMORY_SIZE],
        ['Number of page faults',      ':  ' + PAGE_FAULTS],
    ]

    for i in range(height):
        for j in range(width):
            if j == 0:
                fgcolor = 'white'
            elif i == 6:
                fgcolor = '#ff5c5c'  # highlight page faults
            else:
                fgcolor = '#ffb347'

            entry = Entry(
                frame3,
                fg=fgcolor,
                font=TABLE_FONT,
                bg='black',
                highlightthickness=0,
                highlightbackground="black",
                borderwidth=0,
                width=40,
                disabledbackground='black',
                disabledforeground=fgcolor,
                justify=LEFT
            )
            entry.grid(row=i, column=j, sticky="w", padx=(5 if j == 0 else 0, 5))
            entry.insert(END, data[i][j])
            entry['state'] = DISABLED

    subtitle2 = Label(
        master=frame4,
        text='Statistics (select a section below to view plots)',
        font=SUBTITLE_FONT,
        fg='light green',
        bg='black'
    )
    subtitle2.pack(side=LEFT, padx=10)


def clear_plots():
    """Remove all plot widgets from the plots container."""
    global _image_refs
    for widget in plots_container_frame.winfo_children():
        widget.destroy()
    _image_refs = []


def derive_plot_title(plot_path, process_label):
    """Build a human-friendly title from the filename and process/overall info."""
    CAPTION_FONT = ("Segoe UI", 13, "bold")

    plot_filename = os.path.basename(plot_path)

    # Trace info from combo index in filename
    if 'combo1' in plot_filename:
        trace_info = 'Trace 1'
    elif 'combo2' in plot_filename:
        trace_info = 'Trace 1+2'
    elif 'combo3' in plot_filename:
        trace_info = 'Trace 1+2+3'
    else:
        trace_info = ''

    # Plot type from name
    if 'plot1' in plot_filename:
        plot_type = 'Page faults vs page size'
    elif 'plot2' in plot_filename:
        plot_type = 'Page faults for different combinations'
    else:
        plot_type = 'Plot'

    if trace_info:
        title_text = f'{plot_type} ({trace_info} - {process_label})'
    else:
        title_text = f'{plot_type} ({process_label})'

    return title_text, CAPTION_FONT


def render_plots_for_files(plot_files, process_label):
    """Render a list of plot image files as titled sections."""
    global _image_refs

    clear_plots()

    if not plot_files:
        no_plots_label = Label(
            master=plots_container_frame,
            text=f"No plots found for {process_label}.",
            font=("Segoe UI", 12, "italic"),
            fg='white',
            bg='black'
        )
        no_plots_label.pack(pady=20)
        return

    for plot_idx, plot_path in enumerate(sorted(plot_files)):
        # Title frame
        title_frame = Frame(master=plots_container_frame, width=1530, pady=5, bg='black')
        title_frame.pack(pady=(25 if plot_idx > 0 else 10, 0))

        plot_title_text, CAPTION_FONT = derive_plot_title(plot_path, process_label)

        plottitle = Label(
            master=title_frame,
            text=plot_title_text,
            font=CAPTION_FONT,
            fg='white',
            bg='black'
        )
        plottitle.pack(side=LEFT, padx=10)

        # Plot frame
        plot_frame = Frame(master=plots_container_frame, width=1530, pady=10, bg='black')
        plot_frame.pack()

        canvas_plot = Canvas(
            master=plot_frame,
            width=1100,
            height=619,
            bg='black',
            highlightthickness=0
        )
        canvas_plot.pack()

        image = cv2.imread(plot_path)
        if image is None:
            messagebox.showerror("Error", f"Could not load image: {plot_path}")
            continue

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (1100, 619))
        image = PIL_Image.fromarray(image)
        image_tk = ImageTk.PhotoImage(image)

        # Store reference to prevent garbage collection
        canvas_plot.image = image_tk
        _image_refs.append(image_tk)

        canvas_plot.create_image(0, 0, anchor=NW, image=image_tk)


def show_overall_plots():
    """Show all aggregate (overall) plots from Plots/ root."""
    # Only look at pngs directly under Plots/, ignore per-process subdirs
    plot_files = sorted(
        f for f in glob.glob(os.path.join('Plots', '*.png'))
        if os.path.isfile(f)
    )
    render_plots_for_files(plot_files, process_label="All Processes")


def show_process_plots(process_id):
    """Show all plots for a specific process (from Plots/Process_<id>/)."""
    process_dir = os.path.join('Plots', f'Process_{process_id}')
    plot_files = sorted(
        f for f in glob.glob(os.path.join(process_dir, '*.png'))
        if os.path.isfile(f)
    )
    render_plots_for_files(plot_files, process_label=f'Process {process_id}')


def build_section_buttons():
    """Create buttons for Overall + each process, wired to show_* callbacks."""
    buttons_frame = Frame(master=master_frame, width=1530, pady=15, bg='black')
    buttons_frame.pack()

    BUTTON_FONT = ("Segoe UI", 11, "bold")

    # Overall button
    overall_btn = Button(
        master=buttons_frame,
        text="Overall",
        font=BUTTON_FONT,
        command=show_overall_plots
    )
    overall_btn.pack(side=LEFT, padx=10, pady=5)

    # Buttons for each process
    try:
        n_proc = int(NUM_PROCESSES)
    except ValueError:
        n_proc = 0

    for pid in range(n_proc):
        btn = Button(
            master=buttons_frame,
            text=f"Process {pid}",
            font=BUTTON_FONT,
            command=lambda p=pid: show_process_plots(p)
        )
        btn.pack(side=LEFT, padx=5, pady=5)


def displayOutputInCanvas():
    global plots_container_frame

    # Header & stats
    build_stats_header()

    # Section buttons
    build_section_buttons()

    # Container where plots will appear
    plots_container_frame = Frame(master=master_frame, bg='black')
    plots_container_frame.pack(fill="both", expand=True)

    # Initial view: Overall
    show_overall_plots()



def main():
    global PROCESS_COUNT, MEMORY_REQ_COUNT, PAGING, REPLACEMENT
    global PAGE_SIZE, MEMORY_SIZE, PAGE_FAULTS, NUM_PROCESSES

    argData = sys.argv
    # Expected: script, processCount, memoryReqCount, PAGING, REPLACEMENT,
    #           PAGE_SIZE, MEMORY_SIZE, PAGE_FAULTS, NUM_PROCESSES
    if len(argData) < 9:
        messagebox.showerror("Error", "Insufficient data passed to results GUI.")
        return

    PROCESS_COUNT = argData[1]
    MEMORY_REQ_COUNT = argData[2]
    PAGING = argData[3]
    REPLACEMENT = argData[4]
    PAGE_SIZE = argData[5]
    MEMORY_SIZE = argData[6]
    PAGE_FAULTS = argData[7]
    NUM_PROCESSES = argData[8]

    displayOutputInCanvas()


def scrollbar_function(event):
    canvas.configure(
        scrollregion=canvas.bbox("all"),
        width=1530,
        height=795
    )


if __name__ == '__main__':
    root = Tk()
    root.title('Virtual Memory Management - Results')
    root.resizable(False, False)
    root.config(bg='black')

    window_height = 800
    window_width = 1550

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))

    root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    main_frame = Frame(root, relief=GROOVE, bd=1, bg='black')
    main_frame.place(x=0, y=0)

    canvas = Canvas(main_frame, bg='black', highlightthickness=0)
    master_frame = Frame(canvas, bg='black', padx=10, pady=10)

    myscrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=myscrollbar.set)

    myscrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=master_frame, anchor='nw')
    master_frame.bind("<Configure>", scrollbar_function)

    main()
    root.mainloop()
