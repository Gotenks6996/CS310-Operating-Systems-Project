#include <ctime>
#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <string>
#include <chrono>
#include <algorithm>

#include "simInput.h"
#include "simConstants.h"

using namespace std;
using namespace chrono;

int pointer;
int pageSize;
int pageFault;
int pagingType;
int numProcesses;
int replacementType;
int printDetails;
int processTraceListSize;
int counter = 0;
int MEMORY_SIZE; // Now dynamic
auto start = high_resolution_clock::now();

vector<Process> processes;
vector<MemoryEntry> memory;
vector<int> pageFaultTracker;
vector<int> perProcessPageFaults; // Track page faults per process
vector<ProcessTraceEntry> processTraceList;

// ------------ Replacement helpers (FIFO / LRU / SECOND_CHANCE / OPTIMAL) ------------

void fifoReplace() {
    int firstComeFrame = 0;
    long long firstComeTime =
        processes[memory[0].processId].pages[memory[0].pageNumber].addedTime;

    for (int i = pageSize; i < MEMORY_SIZE; i += pageSize) {
        if (processes[memory[i].processId].pages[memory[i].pageNumber].addedTime <
            firstComeTime) {
            firstComeTime =
                processes[memory[i].processId].pages[memory[i].pageNumber].addedTime;
            firstComeFrame = i / pageSize;
        }
    }

    int processId = memory[firstComeFrame * pageSize].processId;
    int pageNumber = memory[firstComeFrame * pageSize].pageNumber;

    for (int i = 0; i < pageSize; i++) {
        memory[firstComeFrame * pageSize + i].occupied = 0;
        memory[firstComeFrame * pageSize + i].processId = -1;
        memory[firstComeFrame * pageSize + i].pageNumber = -1;
    }

    processes[processId].pageTable[pageNumber].valid = 0;
    processes[processId].pageTable[pageNumber].frame = -1;
    processes[processId].pages[pageNumber].addedTime = -1;
    processes[processId].pages[pageNumber].lastAccessedTime = -1;
}

void lruReplace() {
    int firstAccessedFrame = 0;
    long long firstAccessedTime =
        processes[memory[0].processId].pages[memory[0].pageNumber].lastAccessedTime;

    for (int i = pageSize; i < MEMORY_SIZE; i += pageSize) {
        if (processes[memory[i].processId].pages[memory[i].pageNumber].lastAccessedTime <
            firstAccessedTime) {
            firstAccessedTime =
                processes[memory[i].processId].pages[memory[i].pageNumber]
                    .lastAccessedTime;
            firstAccessedFrame = i / pageSize;
        }
    }

    int processId = memory[firstAccessedFrame * pageSize].processId;
    int pageNumber = memory[firstAccessedFrame * pageSize].pageNumber;

    for (int i = 0; i < pageSize; i++) {
        memory[firstAccessedFrame * pageSize + i].occupied = 0;
        memory[firstAccessedFrame * pageSize + i].processId = -1;
        memory[firstAccessedFrame * pageSize + i].pageNumber = -1;
    }

    processes[processId].pageTable[pageNumber].valid = 0;
    processes[processId].pageTable[pageNumber].frame = -1;
    processes[processId].pages[pageNumber].addedTime = -1;
    processes[processId].pages[pageNumber].lastAccessedTime = -1;
}

void secondChanceReplace() {
    while (memory[pointer * pageSize].usedBit != 0) {
        for (int i = 0; i < pageSize; i++) {
            memory[pointer * pageSize + i].usedBit = 0;
        }

        int frame_count = MEMORY_SIZE / pageSize;
        pointer = (pointer + 1) % frame_count;
    }
}

void optimalReplace(size_t currentIndex, const vector<ProcessTraceEntry>& traceList) {
    int frameCount = MEMORY_SIZE / pageSize;
    int victimFrame = 0;
    long long farthestUse = -1;

    for (int frame = 0; frame < frameCount; ++frame) {
        int base = frame * pageSize;

        if (!memory[base].occupied) {
            victimFrame = frame;
            break;
        }

        int procId = memory[base].processId;
        int pageNo = memory[base].pageNumber;

        size_t nextUseIndex = static_cast<size_t>(-1);

        for (size_t idx = currentIndex + 1; idx < traceList.size(); ++idx) {
            if (traceList[idx].processId == procId) {
                int refPage = traceList[idx].memoryLocation / pageSize;
                if (refPage == pageNo) {
                    nextUseIndex = idx;
                    break;
                }
            }
        }

        if (nextUseIndex == static_cast<size_t>(-1)) {
            victimFrame = frame;
            break;
        }

        if (static_cast<long long>(nextUseIndex) > farthestUse) {
            farthestUse = static_cast<long long>(nextUseIndex);
            victimFrame = frame;
        }
    }

    int base = victimFrame * pageSize;
    int processId = memory[base].processId;
    int pageNumber = memory[base].pageNumber;

    for (int i = 0; i < pageSize; i++) {
        memory[base + i].occupied = 0;
        memory[base + i].processId = -1;
        memory[base + i].pageNumber = -1;
        memory[base + i].usedBit = 0;
    }

    processes[processId].pageTable[pageNumber].valid = 0;
    processes[processId].pageTable[pageNumber].frame = -1;
    processes[processId].pages[pageNumber].addedTime = -1;
    processes[processId].pages[pageNumber].lastAccessedTime = -1;
}

// ------------ Load helpers ------------

bool fifoLoad(int processId, int pageNumber) {
    for (int i = 0; i < MEMORY_SIZE; i += pageSize) {
        if (!memory[i].occupied) {
            processes[processId].pageTable[pageNumber].valid = 1;
            processes[processId].pageTable[pageNumber].frame = i / pageSize;

            auto elapsed = high_resolution_clock::now() - start;

            processes[processId].pages[pageNumber].addedTime =
                duration_cast<nanoseconds>(elapsed).count();
            processes[processId].pages[pageNumber].lastAccessedTime =
                duration_cast<nanoseconds>(elapsed).count();

            for (int j = 0; j < pageSize; j++) {
                memory[i + j].occupied = 1;
                memory[i + j].processId = processId;
                memory[i + j].pageNumber = pageNumber;
                memory[i + j].usedBit = 1;
            }

            return true;
        }
    }

    return false;
}

bool lruLoad(int processId, int pageNumber) {
    return fifoLoad(processId, pageNumber);
}

bool secondChanceLoad(int processId, int pageNumber) {
    if (memory[pointer * pageSize].usedBit == 0) {
        if (memory[pointer * pageSize].occupied) {
            int frame_processId = memory[pointer * pageSize].processId;
            int frame_pageNumber = memory[pointer * pageSize].pageNumber;

            for (int i = 0; i < pageSize; i++) {
                memory[pointer * pageSize + i].occupied = 0;
                memory[pointer * pageSize + i].processId = -1;
                memory[pointer * pageSize + i].pageNumber = -1;
                memory[pointer * pageSize + i].usedBit = 0;
            }

            processes[frame_processId].pageTable[frame_pageNumber].valid = 0;
            processes[frame_processId].pageTable[frame_pageNumber].frame = -1;
        }

        processes[processId].pageTable[pageNumber].valid = 1;
        processes[processId].pageTable[pageNumber].frame = pointer;

        for (int i = 0; i < pageSize; i++) {
            memory[pointer * pageSize + i].occupied = 1;
            memory[pointer * pageSize + i].processId = processId;
            memory[pointer * pageSize + i].pageNumber = pageNumber;
            memory[pointer * pageSize + i].usedBit = 1;
        }

        int frame_count = MEMORY_SIZE / pageSize;
        pointer = (pointer + 1) % frame_count;

        return true;
    }
    return false;
}

bool optimalLoad(int processId, int pageNumber) {
    for (int i = 0; i < MEMORY_SIZE; i += pageSize) {
        if (!memory[i].occupied) {
            processes[processId].pageTable[pageNumber].valid = 1;
            processes[processId].pageTable[pageNumber].frame = i / pageSize;

            auto elapsed = high_resolution_clock::now() - start;

            processes[processId].pages[pageNumber].addedTime =
                duration_cast<nanoseconds>(elapsed).count();
            processes[processId].pages[pageNumber].lastAccessedTime =
                duration_cast<nanoseconds>(elapsed).count();

            for (int j = 0; j < pageSize; j++) {
                memory[i + j].occupied = 1;
                memory[i + j].processId = processId;
                memory[i + j].pageNumber = pageNumber;
                memory[i + j].usedBit = 1;
            }

            return true;
        }
    }

    return false;
}

// ------------ Load / Paging orchestration ------------

void replacement(size_t currentIndex, const vector<ProcessTraceEntry>& traceList) {
    if (replacementType == FIFO) {
        fifoReplace();
    } else if (replacementType == LRU) {
        lruReplace();
    } else if (replacementType == SECOND_CHANCE) {
        secondChanceReplace();
    } else if (replacementType == OPTIMAL) {
        optimalReplace(currentIndex, traceList);
    }
}

void load(int processId, int pageNumber, size_t currentIndex,
          const vector<ProcessTraceEntry>& traceList) {
    bool loaded = false;

    if (replacementType == FIFO) {
        loaded = fifoLoad(processId, pageNumber);
    } else if (replacementType == LRU) {
        loaded = lruLoad(processId, pageNumber);
    } else if (replacementType == SECOND_CHANCE) {
        loaded = secondChanceLoad(processId, pageNumber);
    } else if (replacementType == OPTIMAL) {
        loaded = optimalLoad(processId, pageNumber);
    }

    if (!loaded) {
        replacement(currentIndex, traceList);
        load(processId, pageNumber, currentIndex, traceList);
    }
}

int findNext(int processId, int pageNumber) {
    int nextPageNumber = -1;
    int pageCount = static_cast<int>(
        ceil(static_cast<double>(processes[processId].totalMemory) / pageSize));

    for (int i = pageNumber + 1; i < pageCount; i++) {
        if (!processes[processId].pageTable[i].valid) {
            nextPageNumber = i;
            return nextPageNumber;
        }
    }
    for (int i = 0; i < pageNumber; i++) {
        if (!processes[processId].pageTable[i].valid) {
            nextPageNumber = i;
            return nextPageNumber;
        }
    }

    return nextPageNumber;
}

void prePaging(int processId, int pageNumber, size_t currentIndex,
               const vector<ProcessTraceEntry>& traceList) {
    load(processId, pageNumber, currentIndex, traceList);

    int nextPageNumber = findNext(processId, pageNumber);
    if (nextPageNumber != -1) {
        load(processId, nextPageNumber, currentIndex, traceList);
    }
}

void demandPaging(int processId, int pageNumber, size_t currentIndex,
                  const vector<ProcessTraceEntry>& traceList) {
    load(processId, pageNumber, currentIndex, traceList);
}

void paging(int processId, int pageNumber, size_t currentIndex,
            const vector<ProcessTraceEntry>& traceList) {
    if (pagingType == PRE) {
        prePaging(processId, pageNumber, currentIndex, traceList);
    } else if (pagingType == DEMAND) {
        demandPaging(processId, pageNumber, currentIndex, traceList);
    }
}

void check(int processNumber, int pageNumber, size_t currentIndex,
           const vector<ProcessTraceEntry>& traceList) {
    if (!processes[processNumber].pageTable[pageNumber].valid) {
        pageFault++;
        perProcessPageFaults[processNumber]++;
        paging(processNumber, pageNumber, currentIndex, traceList);
    } else {
        auto elapsed = high_resolution_clock::now() - start;
        processes[processNumber].pages[pageNumber].lastAccessedTime =
            duration_cast<nanoseconds>(elapsed).count();

        int frame = processes[processNumber].pageTable[pageNumber].frame;

        for (int i = 0; i < pageSize; i++) {
            memory[frame * pageSize + i].usedBit = 1;
        }
    }
}

void printData() {
    cout << numProcesses << ' ' << processTraceListSize << ' ' << pageFault;

    // Print per-process page faults
    for (int i = 0; i < numProcesses; i++) {
        cout << ' ' << perProcessPageFaults[i];
    }

    if (printDetails) {
        for (size_t i = 0; i < pageFaultTracker.size(); i++) {
            cout << ' ' << pageFaultTracker[i];
        }
    }
}

int main(int argc, char* argv[]) {
    string processListFilename = argv[1];
    string processTraceFilename = argv[2];
    string replacementParam = argv[3];
    string pagingParam = argv[4];
    string pageSizeParam = argv[5];
    string printDetailsParam = argv[6];
    string memorySizeParam = argv[7]; // New parameter

    if (pagingParam == "DEMAND") {
        pagingType = DEMAND;
    } else if (pagingParam == "PRE") {
        pagingType = PRE;
    } else {
        pagingType = DEMAND;
    }

    if (replacementParam == "FIFO") {
        replacementType = FIFO;
    } else if (replacementParam == "LRU") {
        replacementType = LRU;
    } else if (replacementParam == "SECOND_CHANCE") {
        replacementType = SECOND_CHANCE;
    } else if (replacementParam == "OPTIMAL") {
        replacementType = OPTIMAL;
    } else {
        replacementType = FIFO;
    }

    if (printDetailsParam == "1") {
        printDetails = 1;
    } else {
        printDetails = 0;
    }

    MEMORY_SIZE = stoi(memorySizeParam);

    {
        pointer = 0;
        pageFault = 0;
        pageSize = stoi(pageSizeParam);
        processes = readProcessList(processListFilename);
        processTraceList = readProcessTrace(processTraceFilename);
        numProcesses = static_cast<int>(processes.size());
        processTraceListSize = static_cast<int>(processTraceList.size());
        memory = vector<MemoryEntry>(MEMORY_SIZE);
        perProcessPageFaults = vector<int>(numProcesses, 0);

        for (int i = 0; i < numProcesses; i++) {
            int pageCount = static_cast<int>(
                ceil(static_cast<double>(processes[i].totalMemory) / pageSize));

            processes[i].pages = vector<Page>(pageCount);

            for (int j = 0; j < pageCount; j++) {
                processes[i].pages[j].pageNumber = j;
                processes[i].pages[j].processId = i;
            }

            processes[i].pageTable = vector<PageTableEntry>(pageCount);
            for (int j = 0; j < pageCount; j++) {
                processes[i].pageTable[j].pageNumber = j;
            }
        }
    }

    pageFaultTracker.push_back(0);

    for (size_t idx = 0; idx < processTraceList.size(); ++idx) {
        const ProcessTraceEntry& ptrace = processTraceList[idx];

        int processNumber = ptrace.processId;
        int pageNumber = ptrace.memoryLocation / pageSize;

        check(processNumber, pageNumber, idx, processTraceList);

        counter++;

        if (counter % 1000 == 0) {
            pageFaultTracker.push_back(pageFault);
        }
    }

    if (counter % 1000 != 0) {
        pageFaultTracker.push_back(pageFault);
    }

    printData();

    return 0;
}