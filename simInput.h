#ifndef SIMINPUT_H
#define SIMINPUT_H

#include <iostream>
#include <fstream>
#include <vector>
#include <string>

#include "simClass.h"

using namespace std;

inline vector<Process> readProcessList(const string& inputFileName) {
    vector<Process> processes;
    ifstream file(inputFileName);

    int processId, totalMemory;
    while (file >> processId >> totalMemory) {
        Process process;
        process.processId = processId;
        process.totalMemory = totalMemory;
        processes.push_back(process);
    }

    return processes;
}

inline vector<ProcessTraceEntry> readProcessTrace(const string& inputFileName) {
    vector<ProcessTraceEntry> processTraceList;
    ifstream file(inputFileName);

    int processId, memoryLocation;
    while (file >> processId >> memoryLocation) {
        ProcessTraceEntry entry;
        entry.processId = processId;
        entry.memoryLocation = memoryLocation - 1;  
        processTraceList.push_back(entry);
    }

    return processTraceList;
}

#endif 