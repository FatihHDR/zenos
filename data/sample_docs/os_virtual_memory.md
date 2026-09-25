# Chapter 9: Virtual Memory and Paging Architectures

## 9.1 Background and Motivation
Virtual memory is a storage allocation scheme in which secondary memory can be addressed as though it were part of main memory. The addresses a program may use to reference memory are distinguished from the addresses the memory system uses to identify physical storage sites, and program-generated addresses are translated automatically to the corresponding machine addresses.

The size of virtual storage is limited by the addressing scheme of the computer system and the amount of secondary storage available, rather than by the actual number of main storage locations.

### Key Benefits of Virtual Memory:
1. **Large Address Space**: Programs can exceed the physical capacity of primary RAM.
2. **Protection and Isolation**: Each process has its own isolated address space, preventing unauthorized modification of other process states.
3. **Memory Sharing**: Multiple processes can share common libraries (e.g., libc, DLLs) as read-only pages.
4. **Demand Paging**: Only pages actively used by the process need to reside in physical RAM, reducing startup latency and memory pressure.

## 9.2 Paging Hardware and Address Translation
In a paging system, the virtual address space is divided into fixed-size units called **pages**. Physical memory is divided into fixed-size blocks called **page frames** (or simply frames), which have the exact same size as pages (typically 4 KB on modern x86_64 architectures).

A virtual address is split into two components:
- **Virtual Page Number (VPN)**: Used as an index into the page table.
- **Offset (VPO)**: Specifies the specific byte within the page.

Address translation is performed by the **Memory Management Unit (MMU)** hardware:
$$\text{Physical Address} = (\text{Physical Frame Number (PFN)} \times \text{Page Size}) + \text{Offset}$$

## 9.3 Translation Lookaside Buffer (TLB)
Because accessing the multi-level page table for every memory reference introduces significant latency (2 to 4 additional memory accesses), modern CPUs utilize a hardware cache known as the **Translation Lookaside Buffer (TLB)**.

- **TLB Hit**: The VPN is found in the TLB cache, and the PFN is retrieved within a single clock cycle.
- **TLB Miss**: The hardware or OS page table walker traverses the hierarchical page table (PML4, PDPT, PD, PT in x86_64) to locate the PTE, loads the entry into the TLB, and resumes memory execution.

## 9.4 Page Fault Handling
When a process references a virtual address whose corresponding Page Table Entry (PTE) has its `Present` bit set to 0, the MMU triggers a hardware interrupt known as a **Page Fault** (`#PF` in x86).

### Sequence of Page Fault Servicing:
1. Trap to the kernel page fault handler with the faulting address stored in CPU register `CR2`.
2. Verify whether the memory address falls within a valid virtual memory area (VMA) of the process. If invalid, terminate the process with a Segmentation Fault (`SIGSEGV`).
3. Allocate an available physical page frame from the buddy allocator free list.
4. Issue an asynchronous disk I/O request to read the page content from the backing swap space or mapped file.
5. Update the PTE with the new PFN and set the `Present` bit to 1.
6. Invalidate or update the TLB, and restart the instruction that caused the fault.
