import sys
import os
import subprocess
import shutil
import matplotlib.pyplot as plt
from tkinter import *
from tkinter.ttk import Progressbar

plt.rcParams['figure.figsize'] = [16, 9]
plt.rcParams.update({'font.size': 18})
plt.style.use('dark_background')

totalProgress = 0
CONTR_PROCESS = 7
CONTR_PLOT = 3


def mergeTraceFiles(trace_files):
    """Merge multiple trace files into a single list"""
    merged_trace = []
    for trace_file in trace_files:
        if trace_file and os.path.exists(trace_file):
            with open(trace_file, 'r') as f:
                for line in f:
                    merged_trace.append(line.strip())
    return merged_trace


def createMergedTraceFile(trace_files, output_file):
    """Create a merged trace file from multiple trace files"""
    merged_trace = mergeTraceFiles(trace_files)
    with open(output_file, 'w') as f:
        for line in merged_trace:
            f.write(line + '\n')


def generateStatistics_Plot1(trace_file):
    global pageFaults, PATH_TO_PROCESS_LIST, REPLACEMENT, PAGING, MEMORY_SIZE
    global totalProgress

    pageSizeList = ['1', '2', '4', '8', '16', '32']
    pageFaultList = []

    for i, pageSize in enumerate(pageSizeList):
        if pageSize == PAGE_SIZE:
            pageFaultList.append(pageFaults)
            pageIndex = i
        else:
            processInfo = [
                'a.exe',
                PATH_TO_PROCESS_LIST,
                trace_file,
                REPLACEMENT,
                PAGING,
                pageSize,
                '0',
                MEMORY_SIZE
            ]

            process = subprocess.Popen(processInfo, stdout=subprocess.PIPE)
            dataBytes = process.communicate()[0]
            dataStr = dataBytes.decode('utf-8').strip()
            data = list(map(int, dataStr.split(' ')))
            pageFaultList.append(data[2])

        totalProgress += CONTR_PROCESS
        updateProgressBar()

    return pageSizeList, pageFaultList, pageIndex


def generateStatistics_Plot2(trace_file):
    global pageFaults, PATH_TO_PROCESS_LIST, PAGE_SIZE, MEMORY_SIZE
    global totalProgress

    simCombinations = [
        ['DEMAND', 'FIFO'],
        ['DEMAND', 'LRU'],
        ['DEMAND', 'SECOND_CHANCE'],
        ['DEMAND', 'OPTIMAL'],
        ['PRE', 'FIFO'],
        ['PRE', 'LRU'],
        ['PRE', 'SECOND_CHANCE'],
        ['PRE', 'OPTIMAL'],
    ]

    for i, combination in enumerate(simCombinations):
        if combination[0] == PAGING and combination[1] == REPLACEMENT:
            simCombinations[i].append(pageFaults)
            mainIndex = i
        else:
            processInfo = [
                'a.exe',
                PATH_TO_PROCESS_LIST,
                trace_file,
                combination[1],
                combination[0],
                PAGE_SIZE,
                '0',
                MEMORY_SIZE
            ]

            process = subprocess.Popen(processInfo, stdout=subprocess.PIPE)
            dataBytes = process.communicate()[0]
            dataStr = dataBytes.decode('utf-8').strip()
            data = list(map(int, dataStr.split(' ')))
            simCombinations[i].append(data[2])

        totalProgress += CONTR_PROCESS
        updateProgressBar()

    combinationList = [c[0] + ' + ' + c[1] for c in simCombinations]
    pageFaultList = [c[2] for c in simCombinations]

    return combinationList, pageFaultList, mainIndex


def generateStatistics_PerProcess_Plot1(trace_file, process_id):
    """Generate plot 1 data for a specific process"""
    global PATH_TO_PROCESS_LIST, REPLACEMENT, PAGING, PAGE_SIZE, MEMORY_SIZE
    global totalProgress, numProcesses

    pageSizeList = ['1', '2', '4', '8', '16', '32']
    pageFaultList = []

    for i, pageSize in enumerate(pageSizeList):
        processInfo = [
            'a.exe',
            PATH_TO_PROCESS_LIST,
            trace_file,
            REPLACEMENT,
            PAGING,
            pageSize,
            '0',
            MEMORY_SIZE
        ]

        process = subprocess.Popen(processInfo, stdout=subprocess.PIPE)
        dataBytes = process.communicate()[0]
        dataStr = dataBytes.decode('utf-8').strip()
        data = list(map(int, dataStr.split(' ')))
        
        # Extract per-process page faults (after total page faults)
        per_process_faults = data[3:3+numProcesses]
        pageFaultList.append(per_process_faults[process_id])

        totalProgress += CONTR_PROCESS
        updateProgressBar()

    pageIndex = pageSizeList.index(PAGE_SIZE)
    return pageSizeList, pageFaultList, pageIndex


def generateStatistics_PerProcess_Plot2(trace_file, process_id):
    """Generate plot 2 data for a specific process"""
    global PATH_TO_PROCESS_LIST, PAGE_SIZE, PAGING, REPLACEMENT, MEMORY_SIZE
    global totalProgress, numProcesses

    simCombinations = [
        ['DEMAND', 'FIFO'],
        ['DEMAND', 'LRU'],
        ['DEMAND', 'SECOND_CHANCE'],
        ['DEMAND', 'OPTIMAL'],
        ['PRE', 'FIFO'],
        ['PRE', 'LRU'],
        ['PRE', 'SECOND_CHANCE'],
        ['PRE', 'OPTIMAL'],
    ]

    for i, combination in enumerate(simCombinations):
        processInfo = [
            'a.exe',
            PATH_TO_PROCESS_LIST,
            trace_file,
            combination[1],
            combination[0],
            PAGE_SIZE,
            '0',
            MEMORY_SIZE
        ]

        process = subprocess.Popen(processInfo, stdout=subprocess.PIPE)
        dataBytes = process.communicate()[0]
        dataStr = dataBytes.decode('utf-8').strip()
        data = list(map(int, dataStr.split(' ')))
        
        # Extract per-process page faults
        per_process_faults = data[3:3+numProcesses]
        simCombinations[i].append(per_process_faults[process_id])

        totalProgress += CONTR_PROCESS
        updateProgressBar()

    mainIndex = -1
    for i, combination in enumerate(simCombinations):
        if combination[0] == PAGING and combination[1] == REPLACEMENT:
            mainIndex = i
            break

    combinationList = [c[0] + ' + ' + c[1] for c in simCombinations]
    pageFaultList = [c[2] for c in simCombinations]

    return combinationList, pageFaultList, mainIndex


def createPlot1(trace_file, plot_name, plot_title):
    global totalProgress
    pageSizeList, pageFaultList, pageIndex = generateStatistics_Plot1(trace_file)

    fig, ax = plt.subplots(figsize=(16, 9))

    bars = ax.barh(pageSizeList, pageFaultList)
    bars[pageIndex].set_color('r')
    ax.spines['right'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)
    ax.grid(visible=True, color='grey', linestyle='-.', linewidth=0.5, alpha=0.2)
    ax.invert_yaxis()

    for patch in ax.patches:
        ax.text(
            patch.get_width() + 0.2,
            patch.get_y() + 0.45,
            str(round(patch.get_width(), 2)),
            color='white'
        )

    ax.set_ylabel('Page size')
    ax.set_xlabel('Number of page faults')
    ax.set_title(plot_title, fontsize=20, pad=20)
    fig.tight_layout()

    if not os.path.exists('Plots'):
        os.makedirs('Plots')
    fig.savefig(os.path.join('Plots', plot_name))

    plt.close(fig)

    totalProgress += CONTR_PLOT
    updateProgressBar()


def createPlot2(trace_file, plot_name, plot_title):
    global totalProgress
    combinationList, pageFaultList, mainIndex = generateStatistics_Plot2(trace_file)

    fig, ax = plt.subplots(figsize=(16, 9))

    bars = ax.barh(combinationList, pageFaultList)
    bars[mainIndex].set_color('r')
    ax.spines['right'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)
    ax.grid(visible=True, color='grey', linestyle='-.', linewidth=0.5, alpha=0.2)
    ax.invert_yaxis()

    for patch in ax.patches:
        ax.text(
            patch.get_width() + 0.2,
            patch.get_y() + 0.45,
            str(round(patch.get_width(), 2)),
            color='white'
        )

    ax.set_ylabel('Different combinations of paging and replacement methods')
    ax.set_xlabel('Number of pagefaults')
    ax.set_title(plot_title, fontsize=20, pad=20)
    fig.tight_layout()

    if not os.path.exists('Plots'):
        os.makedirs('Plots')
    fig.savefig(os.path.join('Plots', plot_name))

    plt.close(fig)

    totalProgress += CONTR_PLOT
    updateProgressBar()


def createPerProcessPlot1(trace_file, process_id, plot_name, plot_title):
    """Create plot 1 for a specific process"""
    global totalProgress
    
    pageSizeList, pageFaultList, pageIndex = generateStatistics_PerProcess_Plot1(
        trace_file, process_id
    )

    fig, ax = plt.subplots(figsize=(16, 9))

    bars = ax.barh(pageSizeList, pageFaultList)
    bars[pageIndex].set_color('r')
    ax.spines['right'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)
    ax.grid(visible=True, color='grey', linestyle='-.', linewidth=0.5, alpha=0.2)
    ax.invert_yaxis()

    for patch in ax.patches:
        ax.text(
            patch.get_width() + 0.2,
            patch.get_y() + 0.45,
            str(round(patch.get_width(), 2)),
            color='white'
        )

    ax.set_ylabel('Page size')
    ax.set_xlabel(f'Number of page faults (Process {process_id})')
    ax.set_title(plot_title, fontsize=20, pad=20)
    fig.tight_layout()

    # ----- Save in per-process subfolder -----
    base_dir = 'Plots'
    process_dir = os.path.join(base_dir, f'Process_{process_id}')
    os.makedirs(process_dir, exist_ok=True)

    fig.savefig(os.path.join(process_dir, plot_name))
    # -----------------------------------------

    plt.close(fig)

    totalProgress += CONTR_PLOT
    updateProgressBar()


def createPerProcessPlot2(trace_file, process_id, plot_name, plot_title):
    """Create plot 2 for a specific process"""
    global totalProgress
    
    combinationList, pageFaultList, mainIndex = generateStatistics_PerProcess_Plot2(
        trace_file, process_id
    )

    fig, ax = plt.subplots(figsize=(16, 9))

    bars = ax.barh(combinationList, pageFaultList)
    if mainIndex >= 0:
        bars[mainIndex].set_color('r')
    ax.spines['right'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)
    ax.grid(visible=True, color='grey', linestyle='-.', linewidth=0.5, alpha=0.2)
    ax.invert_yaxis()

    for patch in ax.patches:
        ax.text(
            patch.get_width() + 0.2,
            patch.get_y() + 0.45,
            str(round(patch.get_width(), 2)),
            color='white'
        )

    ax.set_ylabel('Different combinations of paging and replacement methods')
    ax.set_xlabel(f'Number of pagefaults (Process {process_id})')
    ax.set_title(plot_title, fontsize=20, pad=20)
    fig.tight_layout()

    # ----- Save in per-process subfolder -----
    base_dir = 'Plots'
    process_dir = os.path.join(base_dir, f'Process_{process_id}')
    os.makedirs(process_dir, exist_ok=True)

    fig.savefig(os.path.join(process_dir, plot_name))
    # -----------------------------------------

    plt.close(fig)

    totalProgress += CONTR_PLOT
    updateProgressBar()



def executeMainRequest(trace_file):
    global totalProgress, CONTR_PROCESS
    global processCount, memoryRequestCount, pageFaults, pageFaultTracker
    global numProcesses, perProcessPageFaults

    os.system('g++ simulator.cpp -o a.exe')

    processInfo = [
        'a.exe',
        PATH_TO_PROCESS_LIST,
        trace_file,
        REPLACEMENT,
        PAGING,
        PAGE_SIZE,
        '1',
        MEMORY_SIZE
    ]

    backend = subprocess.Popen(processInfo, stdout=subprocess.PIPE)
    dataBytes = backend.communicate()[0]
    dataStr = dataBytes.decode('utf-8').strip()
    data = list(map(int, dataStr.split(' ')))

    processCount = data[0]
    memoryRequestCount = data[1]
    pageFaults = data[2]
    
    numProcesses = processCount
    perProcessPageFaults = data[3:3+processCount]
    pageFaultTracker = data[3+processCount:]

    totalProgress += CONTR_PROCESS
    updateProgressBar()


def printData():
    print(
        processCount,
        memoryRequestCount,
        PAGING,
        REPLACEMENT,
        PAGE_SIZE,
        MEMORY_SIZE,
        pageFaults,
        numProcesses,
        end=''
    )


def updateProgressBar():
    global progress, totalProgress
    progress['value'] = totalProgress
    ProgressWin.update_idletasks()


def destroyProgressBar():
    global ProgressWin
    ProgressWin.destroy()


def main():
    global PAGING, REPLACEMENT, PATH_TO_PROCESS_LIST, MEMORY_SIZE
    global PAGE_SIZE, progress, totalProgress
    global PATH_TO_PROCESS_TRACE1, PATH_TO_PROCESS_TRACE2, PATH_TO_PROCESS_TRACE3
    global numProcesses

    updateProgressBar()

    argData = sys.argv

    PAGING = argData[1]
    REPLACEMENT = argData[2]
    PATH_TO_PROCESS_LIST = argData[3]
    PATH_TO_PROCESS_TRACE1 = argData[4]
    PATH_TO_PROCESS_TRACE2 = argData[5]
    PATH_TO_PROCESS_TRACE3 = argData[6]
    PAGE_SIZE = argData[7]
    MEMORY_SIZE = argData[8]

    dir_name = 'Plots'
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
    os.makedirs(dir_name)

    # Prepare trace file combinations
    trace_files = []
    trace_combinations = []
    
    # First: only trace1
    if PATH_TO_PROCESS_TRACE1:
        trace_combinations.append([PATH_TO_PROCESS_TRACE1])
        
    # Second: trace1 + trace2
    if PATH_TO_PROCESS_TRACE2:
        trace_combinations.append([PATH_TO_PROCESS_TRACE1, PATH_TO_PROCESS_TRACE2])
        
    # Third: trace1 + trace2 + trace3
    if PATH_TO_PROCESS_TRACE3:
        trace_combinations.append([PATH_TO_PROCESS_TRACE1, PATH_TO_PROCESS_TRACE2, PATH_TO_PROCESS_TRACE3])

    # Process each trace combination
    for combo_idx, trace_combo in enumerate(trace_combinations):
        # Create merged trace file
        merged_trace_file = f'temp_merged_trace_{combo_idx+1}.txt'
        createMergedTraceFile(trace_combo, merged_trace_file)
        
        # Execute main request to get process count
        executeMainRequest(merged_trace_file)
        
        # Create cumulative plots
        combo_name = f"Trace {'_'.join([str(i+1) for i in range(len(trace_combo))])}"
        createPlot1(merged_trace_file, f'plot1_combo{combo_idx+1}.png', 
                   f'Plot 1: Page faults vs page size ({combo_name})')
        createPlot2(merged_trace_file, f'plot2_combo{combo_idx+1}.png', 
                   f'Plot 2: Page faults for different combinations ({combo_name})')
        
        # Create per-process plots
        for process_id in range(numProcesses):
            createPerProcessPlot1(merged_trace_file, process_id, 
                                 f'plot1_combo{combo_idx+1}_process{process_id}.png',
                                 f'Plot 1: Page faults vs page size (Process {process_id}, {combo_name})')
            createPerProcessPlot2(merged_trace_file, process_id, 
                                 f'plot2_combo{combo_idx+1}_process{process_id}.png',
                                 f'Plot 2: Page faults combinations (Process {process_id}, {combo_name})')
        
        # Clean up merged trace file
        if os.path.exists(merged_trace_file):
            os.remove(merged_trace_file)

    totalProgress += 3
    updateProgressBar()

    printData()
    ProgressWin.destroy()


if __name__ == '__main__':
    ProgressWin = Tk()
    ProgressWin.title('Virtual memory management simulator - Processing')
    ProgressWin.config(bg='black')

    ProgressWin.resizable(False, False)

    window_height = 150
    window_width = 500

    screen_width = ProgressWin.winfo_screenwidth()
    screen_height = ProgressWin.winfo_screenheight()

    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))

    ProgressWin.geometry(
        f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}"
    )

    main_frame = Frame(ProgressWin, relief=GROOVE, bg='black')
    main_frame.place(x=10, y=10)

    frame1 = Frame(main_frame, padx=3, pady=3, bg='black')
    frame2 = Frame(main_frame, bg='white', pady=5, padx=5)

    frame1.grid(row=1, column=1, padx=5, pady=5)
    frame2.grid(row=2, column=1, padx=5, pady=(30, 10))

    label = Label(
        master=frame1,
        text="Running simulations! Please wait...",
        fg='#23ff0f',
        font="Verdana 15 bold",
        bg='black'
    )
    label.pack()

    progress = Progressbar(
        frame2,
        orient=HORIZONTAL,
        length=450,
        mode='determinate'
    )
    progress.pack()

    main()
    ProgressWin.mainloop()