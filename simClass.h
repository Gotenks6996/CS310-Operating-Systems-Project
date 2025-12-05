#ifndef SIMCLASS_H
#define SIMCLASS_H

#include <vector>

class Page {
  public:
    int processId;
    int pageNumber;

    long long addedTime;
    long long lastAccessedTime;

    Page() {
      addedTime = -1;
      lastAccessedTime = -1;
    }
};

class PageTableEntry {
  public:
    int frame;
    int valid;
    int pageNumber;

    PageTableEntry() {
      valid = 0;
      frame = -1;
    }
};

class Process {
  public:
    int processId;
    int totalMemory;
    std::vector<Page> pages;
    std::vector<PageTableEntry> pageTable;
};

class MemoryEntry {
  public:
    int occupied;
    int processId;
    int pageNumber;
    int usedBit;

    MemoryEntry() {
      occupied = 0;
      processId = -1;
      pageNumber = -1;
      usedBit = 0;
    }
};

class ProcessTraceEntry {
  public:
    int processId;
    int memoryLocation;
};

#endif