# Virtual Memory: Paging, Address Translation and Related Mechanisms

Sumber: artikel Wikipedia berbahasa Inggris, dilisensikan CC BY-SA 4.0.
- Virtual memory — https://en.wikipedia.org/wiki/Virtual_memory
- Memory paging — https://en.wikipedia.org/wiki/Memory_paging
- Page fault — https://en.wikipedia.org/wiki/Page_fault
- Translation lookaside buffer — https://en.wikipedia.org/wiki/Translation_lookaside_buffer
- Memory management unit — https://en.wikipedia.org/wiki/Memory_management_unit
- Page replacement algorithm — https://en.wikipedia.org/wiki/Page_replacement_algorithm
- Demand paging — https://en.wikipedia.org/wiki/Demand_paging
- Memory protection — https://en.wikipedia.org/wiki/Memory_protection
- Thrashing (computer science) — https://en.wikipedia.org/wiki/Thrashing_%28computer_science%29
- Swap (computer programming) — https://en.wikipedia.org/wiki/Swap_%28computer_programming%29
- Memory segmentation — https://en.wikipedia.org/wiki/Memory_segmentation
- Page (computer memory) — https://en.wikipedia.org/wiki/Page_%28computer_memory%29
- Working set — https://en.wikipedia.org/wiki/Working_set
- Fragmentation (computing) — https://en.wikipedia.org/wiki/Fragmentation_%28computing%29
- CPU cache — https://en.wikipedia.org/wiki/CPU_cache
- Virtual address space — https://en.wikipedia.org/wiki/Virtual_address_space
- X86 memory segmentation — https://en.wikipedia.org/wiki/X86_memory_segmentation


---page---

# Virtual memory

In computing, virtual memory, or virtual storage, is enabled by a memory management technique that provides an "idealized abstraction of the storage resources that are actually available on a given machine" which "creates the illusion to users of a very large (main) memory".
The computer's operating system, using a combination of hardware and software, maps memory addresses used by a program, called virtual addresses, into physical addresses in computer memory. Main storage, as seen by a process or task, appears as a contiguous address space or collection of contiguous segments. The operating system manages virtual address spaces and the assignment of real memory to virtual memory. Address translation hardware in the CPU, often referred to as a memory management unit (MMU), automatically translates virtual addresses to physical addresses. Software within the operating system may extend these capabilities, utilizing, e.g., disk storage, to provide a virtual address space that can exceed the capacity of real memory and thus reference more memory than is physically present in the computer.
The primary benefits of virtual memory include freeing applications from having to manage a shared memory space, ability to share memory used by libraries between processes, increased security due to memory isolation, and being able to conceptually use more memory than might be physically available, using the technique of paging or segmentation.


== Properties ==
Virtual memory makes application programming easier by hiding fragmentation of physical memory; by delegating to the kernel the burden of managing the memory hierarchy (eliminating the need for the program to handle overlays explicitly); and, when each process is run in its own dedicated address space, by obviating the need to relocate program code or to access memory with relative addressing.
Memory virtualization can be considered a generalization of the concept of virtual memory.


== Usage ==

Virtual memory is an integral part of a modern computer architecture; implementations usually require hardware support, typically in the form of a memory management unit built into the CPU. While not necessary, emulators and virtual machines can employ hardware support to increase performance of their virtual memory implementations.
Most modern operating systems that support virtual memory also run each process in its own dedicated address space. Each program thus appears to have sole access to the virtual memory. Some older operating systems (such as OS/VS1 and OS/VS2 SVS) and even later ones (such as IBM i) are single address space operating systems that run all processes in a single address space composed of virtualized memory.
Embedded systems and other special-purpose computer systems that require very fast and/or very consistent response times may opt not to use virtual memory due to decreased determinism; virtual memory systems trigger unpredictable traps that may produce unwanted and unpredictable delays in response to input, especially if the trap requires that data be read into main memory from secondary memory.  The hardware to translate virtual addresses to physical addresses typically requires a significant chip area to implement, and not all chips used in embedded systems include that hardware, which is another reason some of those systems do not use virtual memory.


== History ==

During the 1950s, 1960s, and early 1970s, computer memory was very expensive. Larger programs for which the available memory was not large enough to hold all the code and data had to contain logic for managing primary and secondary storage, such as overlaying. Virtual memory was therefore introduced not only to extend primary memory, but to make such an extension as easy as possible for programmers to use.

The first true virtual memory system was that implemented at the University of Manchester to create a one-level storage system as part of the Atlas Computer. It used a paging mechanism to map the virtual addresses available to the programmer onto the real memory that consisted of 16,384 words of primary core memory with an additional 98,304 words of secondary drum memory. The addition of virtual memory into the Atlas also eliminated a looming programming problem: planning and scheduling data transfers between main and secondary memory and recompiling programs for each change of size of main memory. The first Atlas was commissioned in 1962 but working prototypes of paging had been developed by 1959.
To allow for multiprogramming and multitasking, some systems in the 1960s divided memory between multiple programs without virtual memory, such as the UNIVAC 1107, PDP-6 and early models of the PDP-10, via base and bounds registers.
A claim that the concept of virtual memory was first developed by German physicist Fritz-Rudolf Güntsch at the Technische Universität Berlin in 1956 in his doctoral thesis, Logical Design of a Digital Computer with Multiple Asynchronous Rotating Drums and Automatic High Speed Memory Operation, does not stand up to careful scrutiny. The computer proposed by Güntsch (but never built) had an address space of 105  words which mapped exactly onto the 105 words of the drums, i.e. the addresses were real addresses and there was no form of indirect mapping, a key feature of virtual memory. What Güntsch did invent was a form of cache memory, since his high-speed memory was intended to contain a copy of some blocks of code or data taken from the drums. Indeed, he wrote (as quoted in translation): "The programmer need not respect the existence of the primary memory (he need not even know that it exists), for there is only one sort of addresses  [sic] by which one can program as if there were only one storage." This is exactly the situation in computers with cache memory, one of the earliest commercial examples of which was the IBM System/360 Model 85. In the Model 85 all addresses were real addresses referring to the main core store. A semiconductor cache store, invisible to the user, held the contents of parts of the main store in use by the currently executing program. This is exactly analogous to Güntsch's system, designed as a means to improve performance, rather than to solve the problems involved in multi-programming.
As early as 1958, Robert S. Barton, working at Shell Research, suggested that main storage should be allocated automatically rather than have the programmer being concerned with overlays from secondary memory, in effect virtual memory. By 1960 Barton was lead architect on the Burroughs B5000 project. From 1959 to 1961, W. R. Lonergan was manager of the Burroughs Product Planning Group which included Barton, Donald Knuth as consultant, and Paul King. In May 1960, UCLA ran a two-week seminar "Using and Exploiting Giant Computers" to which Paul King and two others were sent. Stan Gill gave a presentation on virtual memory in the Atlas I computer. Paul King took the ideas back to Burroughs and it was determined that virtual memory should be designed into the core of the B5000.. Burroughs Corporation released the B5000 in 1964 as the first commercial computer with virtual memory.
IBM developed the concept of hypervisors in their CP-40 and CP-67, and in 1972 provided it for the S/370 as Virtual Machine Facility/370. IBM introduced the Start Interpretive Execution (SIE) instruction as part of 370-XA on the 3081, and VM/XA versions of VM to exploit it.
Before virtual memory could be implemented in mainstream operating systems, many problems had to be addressed. Dynamic address translation required expensive and difficult-to-build specialized hardware; initial implementations slowed down access to memory slightly. There were worries that new system-wide algorithms utilizing secondary storage would be less effective than previously used application-specific algorithms. By 1969, the debate over virtual memory for commercial computers was over; an IBM research team led by David Sayre showed that their virtual memory overlay system consistently worked better than the best manually controlled systems.
Operating systems supporting virtual memory on mainframes of the 1960s include:

Atlas Supervisor for the Atlas
THE multiprogramming system for the Electrologica X8 (software based virtual memory without hardware support)
MCP for the Burroughs B5000
MTS, TSS/360 and CP/CMS for the IBM System/360 Model 67
Multics for the GE 645
Time Sharing Operating System for the RCA Spectra 70/46
The introduction of virtual memory provided an ability for software systems with large memory demands to run on computers with less real memory.  The savings from this provided a strong incentive to switch to virtual memory for all systems.  The additional capability of providing virtual address spaces added another level of security and reliability, thus making virtual memory even more attractive to the marketplace.
Throughout the 1970s, the IBM System/370 series running their virtual-storage based operating systems provided a means for business users to migrate multiple older systems into fewer, more powerful, mainframes that had improved price/performance. The first minicomputer to introduce virtual memory was the Norwegian NORD-1; during the 1970s, other minicomputers implemented virtual memory, notably VAX models running VMS.
Virtual memory was introduced to the x86 architecture with the protected mode of the Intel 80286 processor, but its segment swapping technique scaled poorly to larger segment sizes. The Intel 80386 introduced paging support underneath the existing segmentation layer, enabling the page fault exception to chain with other exceptions without double fault. However, loading segment descriptors was an expensive operation, causing operating system designers to rely strictly on paging rather than a combination of paging and segmentation.


== Paged virtual memory ==

Nearly all current implementations of virtual memory divide a virtual address space into pages, blocks of contiguous virtual memory addresses. Pages on contemporary systems are usually at least 4 kilobytes in size; systems with large virtual address ranges or amounts of real memory generally use larger page sizes.


=== Page tables ===
Page tables are used to translate the virtual addresses seen by the application into physical addresses used by the hardware to process instructions; such hardware that handles this specific translation is often known as the memory management unit. Each entry in the page table holds a flag indicating whether the corresponding page is in real memory or not.  If it is in real memory, the page table entry will contain the real memory address at which the page is stored.  When a reference is made to a page by the hardware, if the page table entry for the page indicates that it is not currently in real memory, the hardware raises a page fault exception, invoking the paging supervisor component of the operating system.
Systems can have, e.g., one page table for the whole system, separate page tables for each address space or process, separate page tables for each segment; similarly, systems can have, e.g., no segment table, one segment table for the whole system, separate segment tables for each address space or process, separate segment tables for each region in a tree of region tables for each address space or process. If there is only one page table, different applications running at the same time use different parts of a single range of virtual addresses. If there are multiple page or segment tables, there are multiple virtual address spaces and concurrent applications with separate page tables redirect to different real addresses.
Some earlier systems with smaller real memory sizes, such as the SDS 940, used page registers instead of page tables in memory for address translation.


=== Paging supervisor ===
This part of the operating system creates and manages page tables and lists of free page frames. In order to ensure that there will be enough free page frames to quickly resolve page faults, the system may periodically steal allocated page frames, using a page replacement algorithm, e.g., a least recently used (LRU) algorithm. Stolen page frames that have been modified are written back to auxiliary storage before they are added to the free queue. On some systems the paging supervisor is also responsible for managing translation registers that are not automatically loaded from page tables.
Typically, a page fault that cannot be resolved results in an abnormal termination of the application. However, some systems allow the application to have exception handlers for such errors. The paging supervisor may handle a page fault exception in several different ways, depending on the details:

If the virtual address is invalid, the paging supervisor treats it as an error.
If the page is valid and the page information is not loaded into the MMU, the page information will be stored into one of the page registers.
If the page is uninitialized, a new page frame may be assigned and cleared.
If there is a stolen page frame containing the desired page, that page frame will be reused.
For a fault due to a write attempt into a read-protected page, if it is a copy-on-write page then a free page frame will be assigned and the contents of the old page copied; otherwise it is treated as an error.
If the virtual address is a valid page in a memory-mapped file or a paging file, a free page frame will be assigned and the page read in.
In most cases, there will be an update to the page table, possibly followed by purging the Translation Lookaside Buffer (TLB), and the system restarts the instruction that causes the exception.
If the free page frame queue is empty then the paging supervisor must free a page frame using the same page replacement algorithm for page stealing.


=== Pinned pages ===
Operating systems have memory areas that are pinned (never swapped to secondary storage). Other terms used are locked, fixed, or wired pages.  For example, interrupt mechanisms rely on an array of pointers to their handlers, such as I/O completion and page fault. If the pages containing these pointers or the code that they invoke were pageable, interrupt-handling would become far more complex and time-consuming, particularly in the case of page fault interruptions. Hence, some part of the page table structures is not pageable.
Some pages may be pinned for short periods of time, others may be pinned for long periods of time, and still others may need to be permanently pinned. For example:

The paging supervisor code and drivers for secondary storage devices on which pages reside must be permanently pinned, as otherwise paging would not even work because the necessary code would not be available.
Timing-dependent components may be pinned to avoid variable paging delays.
Data buffers that are accessed directly by peripheral devices that use direct memory access or I/O channels must reside in pinned pages while the I/O operation is in progress because such devices and the buses to which they are attached expect to find data buffers located at physical memory addresses; regardless of whether the bus has a memory management unit for I/O, transfers cannot be stopped if a page fault occurs and then restarted when the page fault has been processed. For example, the data could come from a measurement sensor unit and lost real time data that got lost because of a page fault can not be recovered.
In IBM's operating systems for System/370 and successor systems, the term is "fixed", and such pages may be long-term fixed, or may be short-term fixed, or may be unfixed (i.e., pageable). System control structures are often long-term fixed (measured in wall-clock time, i.e., time measured in seconds, rather than time measured in fractions of one second) whereas I/O buffers are usually short-term fixed (usually measured in significantly less than wall-clock time, possibly for tens of milliseconds). Indeed, the OS has a special facility for "fast fixing" these short-term fixed data buffers (fixing which is performed without resorting to a time-consuming Supervisor Call instruction).
Multics used the term "wired". OpenVMS and Windows refer to pages temporarily made nonpageable (as for I/O buffers) as "locked", and simply "nonpageable" for those that are never pageable.  The Single UNIX Specification also uses the term "locked" in the specification for  mlock(), as do the mlock() man pages on many Unix-like systems.


==== Virtual-real operation ====
In OS/VS1 and similar OSes, some parts of systems memory are managed in "virtual-real" mode, called "V=R". In this mode every virtual address corresponds to the same real address. This mode is used for interrupt mechanisms, for the paging supervisor and page tables in older systems, and for application programs using non-standard I/O management. For example, IBM's z/OS has 3 modes (virtual-virtual, virtual-real and virtual-fixed).


=== Thrashing ===
When paging and page stealing are used, a problem called "thrashing" can occur, in which the computer spends an unsuitably large amount of time transferring pages to and from a backing store, hence slowing down useful work. A task's working set is the minimum set of pages that should be in memory in order for it to make useful progress. Thrashing occurs when there is insufficient memory available to store the working sets of all active programs. Adding real memory is the simplest response, but improving application design, scheduling, and memory usage can help. Another solution is to reduce the number of active tasks on the system. This reduces demand on real memory by swapping out the entire working set of one or more processes.
A system thrashing is often a result of a sudden spike in page demand from a small number of running programs. Swap-token is a lightweight and dynamic thrashing protection mechanism. The basic idea is to set a token in the system, which is randomly given to a process that has page faults when thrashing happens. The process that has the token is given a privilege to allocate more physical memory pages to build its working set, which is expected to quickly finish its execution and to release the memory pages to other processes. A time stamp is used to handover the token one by one. The first version of swap-token was implemented in Linux 2.6. The second version is called preempt swap-token and is also in Linux 2.6. In this updated swap-token implementation, a priority counter is set for each process to track the number of swap-out pages. The token is always given to the process with a high priority, which has a high number of swap-out pages. The length of the time stamp is not a constant but is determined by the priority: the higher the number of swap-out pages of a process, the longer the time stamp for it will be.


== Segmented virtual memory ==
Some systems, such as the Burroughs B5500, and the current Unisys MCP systems use segmentation instead of paging, dividing virtual address spaces into variable-length segments. Using segmentation matches the allocated memory blocks to the logical needs and requests of the programs, rather than the physical view of a computer, although pages themselves are an artificial division in memory. The designers of the B5000 would have found the artificial size of pages to be Procrustean in nature, a story they would later use for the exact data sizes in the B1700.
In the Burroughs and Unisys systems, each memory segment is described by a master descriptor which is a single absolute descriptor which may be referenced by other relative (copy) descriptors, effecting sharing either within a process or between processes. Descriptors are central to the working of virtual memory in MCP systems. Descriptors contain not only the address of a segment, but the segment length and status in virtual memory indicated by the 'p-bit' or 'presence bit' which indicates if the address is to a segment in main memory or to a secondary-storage block. When a non-resident segment (p-bit is off) is accessed, an interrupt occurs to load the segment from secondary storage at the given address, or if the address itself is 0 then allocate a new block. In the latter case, the length field in the descriptor is used to allocate a segment of that length.
A further problem to thrashing in using a segmented scheme is checkerboarding, where all free segments become too small to satisfy requests for new segments. The solution is to perform memory compaction to pack all used segments together and create a large free block from which further segments may be allocated. Since there is a single master descriptor for each segment the new block address only needs to be updated in a single descriptor, since all copies refer to the master descriptor.
Paging is not free from fragmentation – the fragmentation is internal to pages (internal fragmentation). If a requested block is smaller than a page, then some space in the page will be wasted. If a block requires larger than a page, a small area in another page is required resulting in large wasted space. The fragmentation thus becomes a problem passed to programmers who may well distort their program to match certain page sizes. With segmentation, the fragmentation is external to segments (external fragmentation) and thus a system problem, which was the aim of virtual memory in the first place, to relieve programmers of such memory considerations. In multi-processing systems, optimal operation of the system depends on the mix of independent processes at any time. Hybrid schemes of segmentation and paging may be used.
The Intel 80286 supports a similar segmentation scheme as an option, but it is rarely used.
Segmentation and paging can be used together by dividing each segment into pages; systems with this memory structure, such as Multics and IBM System/38, are usually paging-predominant, segmentation providing memory protection.
In the Intel 80386 and later IA-32 processors, the segments reside in a 32-bit linear, paged address space. Segments can be moved in and out of that space; pages there can "page" in and out of main memory, providing two levels of virtual memory; few if any operating systems do so, instead using only paging. Early non-hardware-assisted x86 virtualization solutions combined paging and segmentation because x86 paging offers only two protection domains whereas a VMM, guest OS or guest application stack needs three. The difference between paging and segmentation systems is not only about memory division; segmentation is visible to user processes, as part of memory model semantics. Hence, instead of memory that looks like a single large space, it is structured into multiple spaces.
This difference has important consequences; a segment is not a page with variable length or a simple way to lengthen the address space. Segmentation that can provide a single-level memory model in which there is no differentiation between process memory and file system consists of only a list of segments (files) mapped into the process's potential address space.
This is not the same as the mechanisms provided by calls such as mmap and Win32's MapViewOfFile, because inter-file pointers do not work when mapping files into semi-arbitrary places. In Multics, a file (or a segment from a multi-segment file) is mapped into a segment in the address space, so files are always mapped at a segment boundary. A file's linkage section can contain pointers for which an attempt to load the pointer into a register or make an indirect reference through it causes a trap. The unresolved pointer contains an indication of the name of the segment to which the pointer refers and an offset within the segment; the handler for the trap maps the segment into the address space, puts the segment number into the pointer, changes the tag field in the pointer so that it no longer causes a trap, and returns to the code where the trap occurred, re-executing the instruction that caused the trap. This eliminates the need for a linker completely and works when different processes map the same file into different places in their private address spaces.


== Address space swapping ==
Some operating systems provide for swapping entire address spaces, in addition to whatever facilities they have for paging and segmentation. When this occurs, the OS writes those pages and segments currently in real memory to swap files. In a swap-in, the OS reads back the data from the swap files but does not automatically read back pages that had been paged out at the time of the swap out operation.
IBM's MVS, from OS/VS2 Release 2 through z/OS, provides for marking an address space as unswappable; doing so does not pin any pages in the address space. This can be done for the duration of a job by entering the name of an eligible main program in the Program Properties Table with an unswappable flag. In addition, privileged code can temporarily make an address space unswappable using a SYSEVENT Supervisor Call instruction (SVC); certain changes in the address space properties require that the OS swap it out and then swap it back in, using SYSEVENT TRANSWAP.
Swapping does not necessarily require memory management hardware, if, for example, multiple jobs are swapped in and out of the same area of storage.


== See also ==


== Notes ==


== References ==


== Further reading ==
Hennessy, John L.; and Patterson, David A.; Computer Architecture, A Quantitative Approach (ISBN 1-55860-724-2)


== External links ==

Operating Systems: Three Easy Pieces, by Remzi H. Arpaci-Dusseau and Andrea C. Arpaci-Dusseau. Arpaci-Dusseau Books, 2014. Relevant chapters: Address Spaces Address Translation Segmentation Introduction to Paging TLBs Advanced Page Tables Swapping: Mechanisms Swapping: Policies
"Time-Sharing Supervisor Programs" (PDF). Archived from the original (PDF) on 1 November 2012. by Michael T. Alexander in Advanced Topics in Systems Programming, University of Michigan Engineering Summer Conference 1970 (revised May 1971), compares the scheduling and resource allocation approaches, including virtual memory and paging, used in four mainframe operating systems: CP-67, TSS/360, MTS, and Multics.
LinuxMM: Linux Memory Management.
Birth of Linux Kernel, mailing list discussion.
The Virtual-Memory Manager in Windows NT, Randy Kath, Microsoft Developer Network Technology Group, 12 December 1992 at the Wayback Machine (archived 22 June 2010)

---page---

# Memory paging

In computer operating systems, memory paging is a memory management scheme that introduces a level of indirection between physical and logical addresses and allows the physical memory used by a program to be non-contiguous. This also helps avoid the problem of memory fragmentation. 
Paging is often combined with the related technique of allocating and freeing page frames and storing pages on and retrieving them from secondary storage in order to allow the aggregate size of the address spaces to exceed the physical memory of the system. For historical reasons, this technique is sometimes referred to as swapping.
When combined with virtual memory, it is known as paged virtual memory.
In this scheme, the operating system retrieves data from secondary storage in blocks of the same size (pages).
Paging is an important part of virtual memory implementations in modern operating systems, using secondary storage to let programs exceed the size of available physical memory.
Hardware support is necessary for efficient translation of logical addresses to physical addresses. As such, paged memory functionality is usually hardwired into a CPU through its Memory Management Unit (MMU) or Memory Protection Unit (MPU), and separately enabled by privileged system code in the operating system's kernel. In CPUs implementing the x86 instruction set architecture (ISA) for instance, the memory paging is enabled via the CR0 control register.


== History ==
In the 1960s, swapping was an early memory management technique. An entire program or entire segment would be "swapped out" (or "rolled out") from Random-access memory (RAM) to disk or drum, and another one would be swapped in (or rolled in). A swapped-out program would be current but its execution would be suspended while the RAM was in use by another program; a program with a swapped-out segment could continue running until it needed that segment, at which point it would be suspended until the segment was swapped in.
A program might include multiple overlays that occupy the same memory at different times. Overlays are not a method of paging RAM to secondary storage but merely of minimizing the program's RAM use. Subsequent architectures used memory segmentation, and individual program segments became the units exchanged between secondary storage and RAM. A segment was the program's entire code segment or data segment, or sometimes other large data structures. These segments had to be contiguous when resident in RAM, requiring additional computation and movement to remedy fragmentation.
Ferranti's Atlas, and the Atlas Supervisor developed at the University of Manchester (1962), was the first system to implement memory paging. Subsequent early machines, and their operating systems, supporting paging include the IBM M44/44X and its MOS operating system (1964), the SDS 940 and the Berkeley Timesharing System (1966), a modified IBM System/360 Model 40 and the CP-40 operating system (1967), the IBM System/360 Model 67 and operating systems such as TSS/360, CP/CMS and the Michigan Terminal System (MTS) (1967), the RCA 70/46 and the Time Sharing Operating System (TSOS) (1967), the GE 645 and Multics (1969), and the DEC PDP-10 with added BBN-designed paging hardware and the TENEX operating system (1969).
Those machines, and subsequent machines supporting memory paging, use either a set of page address registers or in-memory page tables to allow the processor to operate on arbitrary pages anywhere in RAM as a seemingly contiguous logical address space. These pages became the units exchanged between secondary storage and RAM.


== Page faults ==

When a process tries to reference a page not currently mapped to a page frame in RAM, the processor treats this invalid memory reference as a page fault and transfers control from the program to the operating system. The operating system must:

Determine whether a stolen page frame still contains an unmodified copy of the page; if so, use that page frame.
Otherwise, obtain an empty page frame in RAM to use as a container for the data, and:
Determine whether the page was ever initialized
If so determine the location of the data on secondary storage.
Load the required data into the available page frame.
Update the page table to refer to the new page frame.
Return control to the program, transparently retrying the instruction that caused the page fault.
When all page frames are in use, the operating system must select a page frame to reuse for the page the program now needs. If the evicted page frame was dynamically allocated by a program to hold data, or if a program modified it since it was read into RAM (in other words, if it has become "dirty"), it must be written out to secondary storage before being freed. If a program later references the evicted page, another page fault occurs and the page must be read back into RAM.
The method the operating system uses to select the page frame to reuse, which is its page replacement algorithm, affects efficiency.
The operating system predicts the page frame least likely to be needed soon, often through the least recently used (LRU) algorithm or an algorithm based on the program's working set. To further increase responsiveness, paging systems may predict which pages will be needed soon, preemptively loading them into RAM before a program references them, and may steal page frames from pages that have been unreferenced for a long time, making them available. Some systems clear new pages to avoid data leaks that compromise security; some set them to installation defined or random values to aid debugging.


== Page fetching techniques ==


=== Demand paging ===

When pure demand paging is used, pages are loaded only when they are referenced. A program from a memory mapped file begins execution with none of its pages in RAM. As the program commits page faults, the operating system copies the needed pages from a file, e.g., memory-mapped file, paging file, or a swap partition containing the page data into RAM.


=== Anticipatory paging ===
Some systems use only demand paging—waiting until a page is actually requested before loading it into RAM.
Other systems attempt to reduce latency by guessing which pages not in RAM are likely to be needed soon, and pre-loading such pages into RAM, before that page is requested. (This is often in combination with pre-cleaning, which guesses which pages currently in RAM are not likely to be needed soon, and pre-writing them out to storage).
When a page fault occurs, anticipatory paging systems will not only bring in the referenced page, but also other pages that are likely to be referenced soon.  A simple anticipatory paging algorithm will bring in the next few consecutive pages even though they are not yet needed (a prediction using locality of reference); this is analogous to a prefetch input queue in a CPU.  Swap prefetching will prefetch recently swapped-out pages if there are enough free pages for them.
If a program ends, the operating system may delay freeing its pages, in case the user runs the same program again.
Some systems allow application hints; the application may request that a page be made available and continue without delay.


== Page replacement techniques ==


=== Free page queue, stealing, and reclamation ===
The free page queue is a list of page frames that are available for assignment. Preventing this queue from being empty minimizes the computing necessary to service a page fault. Some operating systems periodically look for pages that have not been recently referenced and then free the page frame and add it to the free page queue, a process known as "page stealing". Some operating systems support page reclamation; if a program commits a page fault by referencing a page that was stolen, the operating system detects this and restores the page frame without having to read the contents back into RAM.


=== Pre-cleaning ===
The operating system may periodically pre-clean dirty pages: write modified pages back to secondary storage even though they might be further modified. This minimizes the amount of cleaning needed to obtain new page frames at the moment a new program starts or a new data file is opened, and improves responsiveness. (Unix operating systems periodically use sync to pre-clean all dirty pages; Windows operating systems use "modified page writer" threads.)
Some systems allow application hints; the application may request that a page be cleared or paged out and continue without delay.


== Thrashing ==

After completing initialization, most programs operate on a small number of code and data pages compared to the total memory the program requires.  The pages most frequently accessed are called the working set.
When the working set is a small percentage of the system's total number of pages, virtual memory systems work most efficiently and an insignificant amount of computing is spent resolving page faults. As the working set grows, resolving page faults remains manageable until the growth reaches a critical point. Then faults go up dramatically and the time spent resolving them overwhelms time spent on the computing the program was written to do. This condition is referred to as thrashing. Thrashing occurs on a program that works with huge data structures, as its large working set causes continual page faults that drastically slow down the system. Satisfying page faults may require freeing pages that will soon have to be re-read from secondary storage. "Thrashing" is also used in contexts other than virtual memory systems; for example, to describe cache issues in computing or silly window syndrome in networking.
A worst case might occur on VAX processors. A single MOVL crossing a page boundary could have a source operand using a displacement deferred addressing mode, where the longword containing the operand address crosses a page boundary, and a destination operand using a displacement deferred addressing mode, where the longword containing the operand address crosses a page boundary, and the source and destination could both cross page boundaries. This single instruction references ten pages; if not all are in RAM, each will cause a page fault. As each fault occurs the operating system needs to go through the extensive memory management routines perhaps causing multiple I/Os which might include writing other process pages to disk and reading pages of the active process from disk.  If the operating system could not allocate ten pages to this program, then remedying the page fault would discard another page the instruction needs, and any restart of the instruction would fault again.
To decrease excessive paging and resolve thrashing problems, a user can increase the number of pages available per program, either by running fewer programs concurrently or increasing the amount of RAM in the computer.


== Sharing ==
In multi-programming or in a multi-user environment, many users may execute the same program, written so that its code and data are in separate pages. To minimize RAM use, all users share a single copy of the program. Each process's page table is set up so that the pages that address code point to the single shared copy, while the pages that address data point to different physical pages for each process.
Different programs might also use the same libraries. To save space, only one copy of the shared library is loaded into physical memory. Programs which use the same library have virtual addresses that map to the same pages (which contain the library's code and data). When programs want to modify the library's code, they use copy-on-write, so memory is only allocated when needed.
Shared memory is an efficient means of communication between programs. Programs can share pages in memory, and then write and read to exchange data.


== Implementations ==


=== Ferranti Atlas ===
The first computer to support paging was the supercomputer Atlas, jointly developed by Ferranti, the University of Manchester and Plessey in 1963. The machine had an associative (content-addressable) memory with one entry for each 512 word page. The Supervisor handled non-equivalence interruptions and managed the transfer of pages between core and drum in order to provide a one-level store to programs.


=== Microsoft Windows ===


==== Windows 3.x and Windows 9x ====
Paging has been a feature of Microsoft Windows since Windows 3.0 in 1990.  Windows 3.x creates a hidden file named 386SPART.PAR or WIN386.SWP for use as a swap file. It is generally found in the root directory, but it may appear elsewhere (typically in the WINDOWS directory). Its size depends on how much swap space the system has (a setting selected by the user under Control Panel → Enhanced under "Virtual Memory"). If the user moves or deletes this file, a blue screen will appear the next time Windows is started, with the error message "The permanent swap file is corrupt". The user will be prompted to choose whether or not to delete the file (even if it does not exist).
Windows 95, Windows 98 and Windows Me use a similar file, and the settings for it are located under Control Panel → System → Performance tab → Virtual Memory. Windows automatically sets the size of the page file to start at 1.5× the size of physical memory, and expand up to 3× physical memory if necessary. If a user runs memory-intensive applications on a system with low physical memory, it is preferable to manually set these sizes to a value higher than default.


==== Windows NT ====
The file used for paging in the Windows NT family is pagefile.sys. The default location of the page file is in the root directory of the partition where Windows is installed. Windows can be configured to use free space on any available drives for page files.  It is required, however, prior to Windows Vista and Windows Server 2008 for the boot partition (i.e., the drive containing the Windows directory) to have a page file on it if the system is configured to write either kernel or full memory dumps after a Blue Screen of Death. Windows uses the paging file as temporary storage for the memory dump. When the system is rebooted, Windows copies the memory dump from the page file to a separate file and frees the space that was used in the page file.


==== Fragmentation ====

In the default configuration of Windows, the page file is allowed to expand beyond its initial allocation when necessary. If this happens gradually, it can become heavily fragmented which can potentially cause performance problems. The common advice given to avoid this is to set a single "locked" page file size so that Windows will not expand it.  However, the page file only expands when it has been filled, which, in its default configuration, is 150% of the total amount of physical memory. Thus the total demand for page file-backed virtual memory must exceed 250% of the computer's physical memory before the page file will expand.
The fragmentation of the page file that occurs when it expands is temporary. As soon as the expanded regions are no longer in use (at the next reboot, if not sooner) the additional disk space allocations are freed and the page file is back to its original state.
Locking a page file size can be problematic if a Windows application requests more memory than the total size of physical memory and the page file, leading to failed requests to allocate memory that may cause applications and system processes to fail. Also, the page file is rarely read or written in sequential order, so the performance advantage of having a completely sequential page file is minimal. However, a large page file generally allows the use of memory-heavy applications, with no penalties besides using more disk space. While a fragmented page file may not be an issue by itself, fragmentation of a variable size page file will over time create several fragmented blocks on the drive, causing other files to become fragmented. For this reason, a fixed-size contiguous page file is better, providing that the size allocated is large enough to accommodate the needs of all applications.
The required disk space may be easily allocated on systems with more recent specifications (i.e. a system with 3 GB of memory having a 6 GB fixed-size page file on a 750 GB disk drive, or a system with 6 GB of memory and a 16 GB fixed-size page file and 2 TB of disk space). In both examples, the system uses about 0.8% of the disk space with the page file pre-extended to its maximum.
Defragmenting the page file is also occasionally recommended to improve performance when a Windows system is chronically using much more memory than its total physical memory. This view ignores the fact that, aside from the temporary results of expansion, the page file does not become fragmented over time. In general, performance concerns related to page file access are much more effectively dealt with by adding more physical memory.


=== Unix and Unix-like systems ===
Unix systems, and other Unix-like operating systems, use the term "swap" to describe the act of substituting disk space for RAM when physical RAM is full. In some of those systems, it is common to dedicate an entire partition of a hard disk to swapping. These partitions are called swap partitions. Many systems have an entire hard drive dedicated to swapping, separate from the data drive(s), containing only a swap partition. A hard drive dedicated to swapping is called a "swap drive" or a "scratch drive" or a "scratch disk".  Some of those systems only support swapping to a swap partition; others also support swapping to files.


==== Linux ====

The Linux kernel supports a virtually unlimited number of swap backends (devices or files), and also supports assignment of backend priorities. When the kernel swaps pages out of physical memory, it uses the highest-priority backend with available free space. If multiple swap backends are assigned the same priority, they are used in a round-robin fashion (which is somewhat similar to RAID 0 storage layouts), providing improved performance as long as the underlying devices can be efficiently accessed in parallel.


===== Swap files and partitions =====
From the end-user perspective, swap files in versions 2.6.x and later of the Linux kernel are virtually as fast as swap partitions; the limitation is that swap files should be contiguously allocated on their underlying file systems.  To increase performance of swap files, the kernel keeps a map of where they are placed on underlying devices and accesses them directly, thus bypassing the cache and avoiding filesystem overhead. When residing on HDDs, which are rotational magnetic media devices, one benefit of using swap partitions is the ability to place them on contiguous HDD areas that provide higher data throughput or faster seek time. However, the administrative flexibility of swap files can outweigh certain advantages of swap partitions. For example, a swap file can be placed on any mounted file system, can be set to any desired size, and can be added or changed as needed. Swap partitions are not as flexible; they cannot be enlarged without using partitioning or volume management tools, which introduce various complexities and potential downtimes.


===== Swappiness =====
Swappiness is a Linux kernel parameter that controls the relative weight given to swapping out of runtime memory, as opposed to dropping pages from the system page cache, whenever a memory allocation request cannot be met from free memory. Swappiness can be set to a value from 0 to 200. A low value causes the kernel to prefer to evict pages from the page cache while a higher value causes the kernel to prefer to swap out "cold" memory pages. The default value is 60; setting it higher can cause high latency if cold pages need to be swapped back in (when interacting with a program that had been idle for example), while setting it lower (even 0) may cause high latency when files that had been evicted from the cache need to be read again, but will make interactive programs more responsive as they will be less likely to need to swap back cold pages. Swapping can also slow down HDDs further because it involves a lot of random writes, while SSDs do not have this problem. Certainly the default values work well in most workloads, but desktops and interactive systems for any expected task may want to lower the setting while batch processing and less interactive systems may want to increase it.


===== Swap death =====
When the system memory is highly insufficient for the current tasks and a large portion of memory activity goes through a slow swap, the system can become practically unable to execute any task, even if the CPU is idle. When every process is waiting on the swap, the system is considered to be in swap death.
Swap death can happen due to incorrectly configured memory overcommitment.
The original description of the "swapping to death" problem relates to the X server. If code or data used by the X server to respond to a keystroke is not in main memory, then if the user enters a keystroke, the server will take one or more page faults, requiring those pages to read from swap before the keystroke can be processed, slowing the response to it.  If those pages do not remain in memory, they will have to be faulted in again to handle the next keystroke, making the system practically unresponsive even if it's actually executing other tasks normally.


==== macOS ====
macOS uses multiple swap files. The default (and Apple-recommended) installation places them on the root partition, though it is possible to place them instead on a separate partition or device.


=== AmigaOS 4 ===
AmigaOS 4.0 introduced a new system for allocating RAM and defragmenting physical memory. It still uses flat shared address space that cannot be defragmented.
It is based on slab allocation and paging memory that allows swapping.
Paging was implemented in AmigaOS 4.1.
It can lock up the system if all physical memory is used up.
Swap memory could be activated and deactivated, allowing the user to choose to use only physical RAM.


== Performance ==
The backing store for a virtual memory operating system is typically many orders of magnitude slower than RAM. Hard disks, for instance, introduce several milliseconds delay before the reading or writing begins. Therefore, it is desirable to reduce or eliminate swapping, where practical. Some operating systems offer settings to influence the kernel's decisions.

Linux offers the /proc/sys/vm/swappiness parameter, which changes the balance between swapping out runtime memory, as opposed to dropping pages from the system page cache.
Windows 2000, XP, and Vista offer the DisablePagingExecutive registry setting, which controls whether kernel-mode code and data can be eligible for paging out.
Mainframe computers frequently used head-per-track disk drives or drums for page and swap storage to eliminate seek time, and several technologies to have multiple concurrent requests to the same device in order to reduce rotational latency.
Flash memory has a finite number of erase-write cycles (see limitations of flash memory), and the smallest amount of data that can be erased at once might be very large, seldom coinciding with pagesize. Therefore, flash memory may wear out quickly if used as swap space under tight memory conditions. For this reason, mobile and embedded operating systems (such as Android) may not use swap space. On the attractive side, flash memory is practically delayless compared to hard disks, and not volatile as RAM chips. Schemes like ReadyBoost and Intel Turbo Memory are made to exploit these characteristics.
Many Unix-like operating systems (for example AIX, Linux, and Solaris) allow using multiple storage devices for swap space in parallel, to increase performance.


=== Swap space size ===
In some older virtual memory operating systems, space in swap backing store is reserved when programs allocate memory for runtime data.  Operating system vendors typically issue guidelines about how much swap space should be allocated.


== Physical and virtual address space sizes ==
Paging is one way of allowing the size of the addresses used by a process, which is the process's "virtual address space" or "logical address space", to be different from the amount of main memory actually installed on a particular computer, which is the physical address space.


=== Main memory smaller than virtual memory ===
In most systems, the size of a process's virtual address space is much larger than the available main memory. For example:

The address bus that connects the CPU to main memory may be limited. The i386SX CPU's 32-bit internal addresses can address 4 GB, but it has only 24 pins connected to the address bus, limiting installed physical memory to 16 MB. There may be other hardware restrictions on the maximum amount of RAM that can be installed.
The maximum memory might not be installed because of cost, because the model's standard configuration omits it, or because the buyer did not believe it would be advantageous.
Sometimes not all internal addresses can be used for memory anyway, because the hardware architecture may reserve large regions for I/O or other features.


=== Main memory the same size as virtual memory ===
A computer with true n-bit addressing may have 2n addressable units of RAM installed. An example is a 32-bit x86 processor with 4 GB and without Physical Address Extension (PAE). In this case, the processor is able to address all the RAM installed and no more.
However, even in this case, paging can be used to support more virtual memory than physical memory. For instance, many programs may be running concurrently. Together, they may require more physical memory than can be installed on the system, but not all of it will have to be in RAM at once. A paging system makes efficient decisions on which memory to relegate to secondary storage, leading to the best use of the installed RAM.
In addition the operating system may provide services to programs that envision a larger memory, such as files that can grow beyond the limit of installed RAM.
Not all of the file can be concurrently mapped into the address space of a process, but the operating system might allow regions of the file to be mapped into the address space, and unmapped if another region needs to be mapped in.


=== Main memory larger than virtual address space ===
A few computers have a main memory larger than the virtual address space of a process, such as the Magic-1, some PDP-11 machines, and some systems using 32-bit x86 processors with Physical Address Extension. This nullifies a significant advantage of paging, since a single process cannot use more main memory than the amount of its virtual address space. Such systems often use paging techniques to obtain secondary benefits:

The "extra memory" can be used in the page cache to cache frequently used files and metadata, such as directory information, from secondary storage.
If the processor and operating system support multiple virtual address spaces, the "extra memory" can be used to run more processes. Paging allows the cumulative total of virtual address spaces to exceed physical main memory.
A process can store data in memory-mapped files on memory-backed file systems, such as the tmpfs file system or file systems on a RAM drive, and map files into and out of the address space as needed.
A set of processes may still depend upon the enhanced security features page-based isolation may bring to a multitasking environment.
The size of the cumulative total of virtual address spaces is still limited by the amount of secondary storage available.


== See also ==


== Notes ==


== References ==


== External links ==
"Time-Sharing Supervisor Programs" (PDF). Archived from the original (PDF) on 2012-11-01. by Michael T. Alexander in Advanced Topics in Systems Programming, University of Michigan Engineering Summer Conference 1970 (revised May 1971), compares the scheduling and resource allocation approaches, including virtual memory and paging, used in four mainframe operating systems: CP-67, TSS/360, MTS, and Multics.
Swap Facts and questions in the Ubuntu documentation
Windows Server - Moving Pagefile to another partition or disk by David Nudelman
How Virtual Memory Works from HowStuffWorks.com (in fact explains only swapping concept, and not virtual memory concept)
Linux swap space management (outdated, as the author admits)
Guide On Optimizing Virtual Memory Speed (outdated)
Virtual Memory Page Replacement Algorithms
Windows XP: How to manually change the size of the virtual memory paging file
Windows XP: Factors that may deplete the supply of paged pool memory
SwapFs driver that can be used to save the paging file of Windows on a swap partition of Linux

---page---

# Page fault

In computing, a page fault is an exception that the memory management unit (MMU) raises when a process accesses a memory page without proper preparations. Accessing the page requires a mapping to be added to the process's virtual address space. Furthermore, the actual page contents may need to be loaded from a back-up, e.g. a disk. The MMU detects the page fault, but the operating system's kernel handles the exception by making the required page accessible in the physical memory or denying an illegal memory access.
Valid page faults are common and necessary to increase the amount of memory available to programs in any operating system that uses virtual memory, such as Windows and macOS.


== Types ==


=== Minor page fault ===
If the page is loaded in  memory at the time the fault is generated, but is not marked in the memory management unit as being loaded in memory, then it is called a minor, or soft, page fault. The page fault handler in the operating system merely needs to make the entry for that page in the memory management unit point to the page in memory and indicate that the page is loaded in memory; it does not need to read the page into memory. This could happen if the memory is shared by different programs and the page has already been brought into memory for another program.


=== Major page fault ===
This is the mechanism used by an operating system to increase the amount of program memory available on demand. The operating system delays loading parts of the program from disk until the program attempts to use them, at which time page faults are generated. If the page is not loaded in memory at the time of the fault, then the fault is major, or hard. The page fault handler in the OS needs to load the page into working memory, and to do so it must choose a location: either a free page or, when free space is scarce, a page in use by another process. In the latter case the OS needs to write the data in that page out to mass storage (if it has not been written out since it was last modified) and mark that page as not being in memory in its process page table. Once the space has thus been made available, the OS reads the data for the new page into memory, adds an entry for its location in the memory management unit, and indicates that the page is loaded. Thus, major faults are more expensive than minor faults and add storage access latency to the interrupted program's execution.


=== Invalid page fault ===
If a page fault occurs for a reference to an address that is not part of the virtual address space, meaning there cannot be a page in memory corresponding to it, then it is called an invalid page fault.  The page fault handler in the operating system will then generally pass a segmentation fault to the offending process, indicating that the access was invalid; this usually results in abnormal termination of the code that made the invalid reference. A null pointer is usually represented as a pointer to address 0 in the address space; many operating systems set up the MMU to indicate that the page that contains that address is not in memory, and do not include that page in the virtual address space, so that attempts to read or write the memory referenced by a null pointer get an invalid page fault.


== Invalid conditions ==
Illegal accesses and invalid page faults can result in a segmentation fault or bus error, resulting in an app or OS crash. Software bugs are often the causes of these problems, but hardware memory errors, such as those caused by overclocking, may corrupt pointers and cause valid code to fail.
Operating systems provide differing mechanisms for reporting page fault errors. Microsoft Windows uses structured exception handling to report invalid page faults as access violation exceptions. UNIX-like systems typically use signals, such as SIGSEGV, to report these error conditions to programs. If the program receiving the error does not handle it, the operating system performs a default action, typically involving the termination of the running process that caused the error condition, and notifying the user that the program has malfunctioned. Windows often reports such crashes without going to any details. An experienced user can retrieve detailed information using WinDbg and the minidump that Windows creates during the crash. UNIX-like operating systems report these conditions with such error messages as "segmentation violation" or "bus error", and may produce a core dump.


== Performance impact ==
Page faults degrade system performance and can cause thrashing. Major page faults on a conventional computer using hard disk drives can have a significant impact on performance, as a typical hard disk drive had an average rotational latency of 3 ms, a seek time of 5 ms and a transfer time of 0.05 ms/page. Therefore, the total time for paging is near 8 ms (8,000 μs). If the memory access time is 0.2 μs, then the page fault would make the operation take about 40,000 times as long. With a more modern system using a fast solid-state drive with a page read latency of 0.030 ms (30 μs) and a memory access latency of 70 ns (0.070 μs), a hard page fault is still takes over 400 times as long.
Performance optimization of programs or operating systems often involves efforts to reduce the number of page faults, by reducing overall memory usage or by improving memory locality. To minimize page faults, OS developers use an appropriate page replacement algorithm that maximizes page hits. Many have been proposed, such as implementing heuristic algorithms to reduce the incidence of page faults.
Having more physical memory also reduces the likelihood of page faults. Chunks of memory-mapped files can remain in memory longer and avoid slow re-reads from storage. Similarly, having more memory lessens the need for frequent swapping out of memory pages to a backing storage device.


== See also ==
Bélády's anomaly
Memory hierarchy


== References ==


== Bibliography ==


== External links ==
"So What Is A Page Fault?"(subscription required) from OSR Online (a Windows-specific explanation)
"Virtual Memory Details" from the Red Hat website.
"UnhandledExceptionFilter (Windows)" from MSDN Online.
"Page fault overhead" for information about how page faults can crucially affect processing time.

---page---

# Translation lookaside buffer

In computing and processor design, a translation lookaside buffer (TLB) is a memory cache that stores the recent translations of virtual memory addresses to physical memory addresses. It is used to reduce the time taken to access a user memory location. It can be called an address-translation cache.  It is a part of the chip's memory-management unit (MMU). A TLB may reside between the CPU and the CPU cache, between CPU cache and the main memory or between the different levels of the multi-level cache. The majority of desktop, laptop, and server processors include one or more TLBs in the memory-management hardware, and it is nearly always present in any processor that uses paged or segmented virtual memory.
The TLB is sometimes implemented as content-addressable memory (CAM). The CAM search key is the virtual address, and the search result is a physical address. If the requested address is present in the TLB, the CAM search yields a match quickly and the retrieved physical address can be used to access memory. This is called a TLB hit. If the requested address is not in the TLB, it is a miss, and the translation proceeds by looking up the page table in a process called a page walk. The page walk is time-consuming when compared to the processor speed, as it involves reading the contents of multiple memory locations and using them to compute the physical address. After the physical address is determined by the page walk, the virtual address to physical address mapping is entered into the TLB.  The PowerPC 604, for example, has a two-way set-associative TLB for data loads and stores. Some processors have different instruction and data address TLBs.


== Overview ==

A TLB has a fixed number of slots containing page-table entries and segment-table entries; page-table entries map virtual addresses to physical addresses and intermediate-table addresses, while segment-table entries map virtual addresses to segment addresses, intermediate-table addresses and page-table addresses.  The virtual memory is the memory space as seen from a process; this space is often split into pages of a fixed size (in paged memory), or less commonly into segments of variable sizes (in segmented memory). The page table, generally stored in main memory, keeps track of where the virtual pages are stored in the physical memory. This method uses two memory accesses (one for the page-table entry, one for the byte) to access a byte. First, the page table is looked up for the frame number. Second, the frame number with the page offset gives the actual address. Thus, any straightforward virtual memory scheme would have the effect of doubling the memory access time. Hence, the TLB is used to reduce the time taken to access the memory locations in the page-table method. The TLB is a cache of the page table, representing only a subset of the page-table contents.
Referencing the physical memory addresses, a TLB may reside between the CPU and the CPU cache, between the CPU cache and primary storage memory, or between levels of a multi-level cache.  The placement determines whether the cache uses physical or virtual addressing.  If the cache is virtually addressed, requests are sent directly from the CPU to the cache, and the TLB is accessed only on a cache miss.  If the cache is physically addressed, the CPU does a TLB lookup on every memory operation, and the resulting physical address is sent to the cache.
In a Harvard architecture or modified Harvard architecture, a separate virtual address space or memory-access hardware may exist for instructions and data.  This can lead to distinct TLBs for each access type, an instruction translation lookaside buffer (ITLB) and a data translation lookaside buffer (DTLB).  Various benefits have been demonstrated with separate data and instruction TLBs.
The TLB can be used as a fast lookup hardware cache. The figure shows the working of a TLB. Each entry in the TLB consists of two parts: a tag and a value. If the tag of the incoming virtual address matches the tag in the TLB, the corresponding value is returned. Since the TLB lookup is usually a part of the instruction pipeline, searches are fast and cause essentially no performance penalty.  However, to be able to search within the instruction pipeline, the TLB has to be small.
A common optimization for physically addressed caches is to perform the TLB lookup in parallel with the cache access. Upon each virtual memory reference, the hardware checks the TLB to see whether the page number is held therein. If yes, it is a TLB hit, and the translation is made. The frame number is returned and is used to access the memory. If the page number is not in the TLB, the page table must be checked. Depending on the CPU, this can be done automatically in hardware or using an interrupt to the operating system. When the frame number is obtained, it can be used to access the memory. In addition, we add the page number and frame number to the TLB, so that they will be found quickly on the next reference. If the TLB is already full, a suitable block must be selected for replacement. There are different replacement methods like least recently used (LRU), first in, first out (FIFO) etc.; see the address translation section in the cache article for more details about virtual addressing as it pertains to caches and TLBs.


== Performance implications ==

The CPU has to access main memory for an instruction-cache miss, data-cache miss, or TLB miss.  The third case (the simplest one) is where the desired information itself actually is in a cache, but the information for virtual-to-physical translation is not in a TLB. These are all slow, due to the need to access a slower level of the memory hierarchy, so a well-functioning TLB is important. Indeed, a TLB miss can be more expensive than an instruction or data cache miss, due to the need for not just a load from main memory, but a page walk, requiring several memory accesses.
The flowchart provided explains the working of a TLB. If it is a TLB miss, then the CPU checks the page table for the page table entry. If the present bit is set, then the page is in main memory, and the processor can retrieve the frame number from the page-table entry to form the physical address. The processor also updates the TLB to include the new page-table entry. Finally, if the present bit is not set, then the desired page is not in the main memory, and a page fault is issued. Then a page-fault interrupt is called, which executes the page-fault handling routine.
If the page working set does not fit into the TLB, then TLB thrashing occurs, where frequent TLB misses occur, with each newly cached page displacing one that will soon be used again, degrading performance in exactly the same way as thrashing of the instruction or data cache does. TLB thrashing can occur even if instruction-cache or data-cache thrashing are not occurring, because these are cached in different-size units. Instructions and data are cached in small blocks (cache lines), not entire pages, but address lookup is done at the page level. Thus, even if the code and data working sets fit into cache, if the working sets are fragmented across many pages, the virtual-address working set may not fit into TLB, causing TLB thrashing. Appropriate sizing of the TLB thus requires considering not only the size of the corresponding instruction and data caches, but also how these are fragmented across multiple pages.


== Multiple TLBs ==
Similar to caches, TLBs may have multiple levels. CPUs can be (and nowadays usually are) built with multiple TLBs, for example a small L1 TLB (potentially fully associative) that is extremely fast, and a larger L2 TLB that is somewhat slower. When instruction-TLB (ITLB) and data-TLB (DTLB) are used, a CPU can have three (ITLB1, DTLB1, TLB2) or four TLBs.
For instance, Intel's Nehalem microarchitecture has a four-way set associative L1 DTLB with 64 entries for 4 KiB pages and 32 entries for 2/4 MiB pages, an L1 ITLB with 128 entries for 4 KiB pages using four-way associativity and 14 fully associative entries for 2/4 MiB pages (both parts of the ITLB divided statically between two threads) and a unified 512-entry L2 TLB for 4 KiB pages, both 4-way associative.
Some TLBs may have separate sections for small pages and huge pages. For example, Intel Skylake microarchitecture separates the TLB entries for 1 GiB pages from those for 4 KiB/2 MiB pages.


== TLB-miss handling ==
Three schemes for handling TLB misses are found in modern architectures:

With hardware TLB management, the CPU automatically walks the page tables (using the CR3 register on x86, for instance) to see whether there is a valid page-table entry for the specified virtual address.  If an entry exists, it is brought into the TLB, and the TLB access is retried: this time the access will hit, and the program can proceed normally.  If the CPU finds no valid entry for the virtual address in the page tables, it raises a page fault exception, which the operating system must handle.  Handling page faults usually involves bringing the requested data into physical memory, setting up a page table entry to map the faulting virtual address to the correct physical address, and resuming the program.  With a hardware-managed TLB, the format of the TLB entries is not visible to software and can change from CPU to CPU without causing loss of compatibility for the operating system.
With software-managed TLBs, a TLB miss generates a TLB miss exception, and operating system code is responsible for walking the page tables and finding the appropriate page table entry.  The operating system then loads the information from that page table entry into the TLB and restarts the program from the instruction that caused the TLB miss.  As with hardware TLB management, if the OS finds no valid translation in the page tables, a page fault has occurred, and the OS must handle it accordingly.  Instruction sets of CPUs that have software-managed TLBs have instructions that allow loading entries into any slot in the TLB. The format of the TLB entry is defined as a part of the instruction set architecture (ISA).
With firmware-managed TLBs, a TLB miss causes a trap to system firmware, which is responsible for walking the page tables and finding the appropriate page table entry, similarly to what a TLB miss handler does for a software-managed TLB.  With a firmware-managed TLB, the format of the TLB entries is not visible to system software and can change from CPU to CPU without causing loss of compatibility for the operating system.
The MIPS architecture specifies a software-managed TLB.
The SPARC V9 architecture allows an implementation of SPARC V9 to have no MMU, an MMU with a software-managed TLB, or an MMU with a hardware-managed TLB, and the UltraSPARC Architecture 2005 specifies a software-managed TLB.
The Itanium architecture provides an option of using either software- or hardware-managed TLBs.
The Alpha architecture has a firmware-managed TLB, with the TLB miss handling code being in PALcode, rather than in the operating system.  As the PALcode for a processor can be processor-specific and operating-system-specific, this allows different versions of PALcode to implement different page-table formats for different operating systems, without requiring that the TLB format, and the instructions to control the TLB, to be specified by the architecture.


== Typical TLB ==
These are typical performance levels of a TLB:

Size: 12 bits – 4,096 entries
Hit time: 0.5 – 1 clock cycle
Miss penalty: 10 – 100 clock cycles
Miss rate: 0.01 – 1% (20–40% for sparse/graph applications)
The average effective memory cycle rate is defined as m+(1−p)h+pm cycles, where m is the number of cycles required for a memory read, p is the miss rate, and h is the hit time in cycles.
If a TLB hit takes 1 clock cycle, a miss takes 30 clock cycles, a memory read takes 30 clock cycles, and the miss rate is 1%, the effective memory cycle rate is an average of 30+0.99×1+0.01×30 (31.29 clock cycles per memory access).


== Address-space switch ==
On an address-space switch, as occurs when context switching between processes (but not between threads), some TLB entries can become invalid, since the virtual-to-physical mapping is different. The simplest strategy to deal with this is to completely flush the TLB. This means that after a switch, the TLB is empty, and any memory reference will be a miss, so it will be some time before things are running back at full speed. Newer CPUs use more effective strategies marking which process an entry is for. This means that if a second process runs for only a short time and jumps back to a first process, the TLB may still have valid entries, saving the time to reload them.
Other strategies avoid flushing the TLB on a context switch:
(a) A single address space operating system uses the same virtual-to-physical mapping for all processes.
(b) Some CPUs have a process ID register, and the hardware uses TLB entries only if they match the current process ID.
For example, in the Alpha 21264, each TLB entry is tagged with an address space number (ASN), and only TLB entries with an ASN matching the current task are considered valid. For another example, in the Intel Pentium Pro, the page global enable (PGE) flag in the register CR4 and the global (G) flag of a page-directory or page-table entry can be used to prevent frequently used pages from being automatically invalidated in the TLBs on a task switch or a load of register CR3. Since the 2010 Westmere microarchitecture Intel 64 processors also support 12-bit process-context identifiers (PCIDs), which allow retaining TLB entries for multiple linear-address spaces, with only those that match the current PCID being used for address translation.
While selective flushing of the TLB is an option in software-managed TLBs, the only option in some hardware TLBs (for example, the TLB in the Intel 80386) is the complete flushing of the TLB on an address-space switch. Other hardware TLBs (for example, the TLB in the Intel 80486 and later x86 processors, and the TLB in ARM processors) allow the flushing of individual entries from the TLB indexed by virtual address.
Flushing of the TLB can be an important security mechanism for memory isolation between processes to ensure a process can't access data stored in memory pages of another process. Memory isolation is especially critical during switches between the privileged operating system kernel process and the user processes – as was highlighted by the Meltdown security vulnerability. Mitigation strategies such as kernel page-table isolation (KPTI) rely heavily on performance-impacting TLB flushes and benefit greatly from hardware-enabled selective TLB entry management such as PCID.


== Virtualization and x86 TLB ==
With the advent of virtualization for server consolidation, a lot of effort has gone into making the x86 architecture easier to virtualize and to ensure better performance of virtual machines on x86 hardware.
Normally, entries in the x86 TLBs are not associated with a particular address space; they implicitly refer to the current address space. Hence, every time there is a change in address space, such as a context switch, the entire TLB has to be flushed. Maintaining a tag that associates each TLB entry with an address space in software and comparing this tag during TLB lookup and TLB flush is very expensive, especially since the x86 TLB is designed to operate with very low latency and completely in hardware. In 2008, both Intel (Nehalem) and AMD (SVM) have introduced tags as part of the TLB entry and dedicated hardware that checks the tag during lookup. Not all operating systems made full use of these tags immediately, but Linux 4.14 started using them to identify recently used address spaces, since the 12-bits PCIDs (4095 different values) are insufficient for all tasks running on a given CPU.


== See also ==
Memory management
Paging
Page Size Extension (PSE)
Virtual address space


== References ==


== External links ==
Virtual Translation Lookaside Buffer on Patentscope.

---page---

# Memory management unit

A memory management unit (MMU), sometimes called paged memory management unit (PMMU), is a computer hardware unit that examines all references to memory, and translates the memory addresses being referenced, known as virtual memory addresses, into physical addresses in main memory.
In modern systems, programs generally have addresses that access the theoretical maximum memory of the computer architecture, 32 or 64 bits. The MMU maps the addresses from each program into separate areas in physical memory, which is generally much smaller than the theoretical maximum. This is possible because programs rarely use large amounts of memory at any one time.
Most modern operating systems (OS) use an MMU to provide virtual memory (VM) support.
The MMU tracks memory use in fixed-size blocks known as pages.
If a program refers to a location in a page that is not in physical memory, the MMU sends an interrupt to the operating system.
The OS selects a lesser-used block in memory, writes it to backing storage such as a hard drive if it has been modified since it was read in, reads the page from backing storage into that block, and sets up the MMU to map the block to the originally requested page so the program can use it.
This is known as demand paging.
Some simpler real-time operating systems do not support virtual memory and do not need an MMU, but still need a hardware memory protection unit.
MMUs generally provide memory protection to block attempts by a program to access memory it has not previously requested, which prevents a misbehaving or malicious program from modifying or reading data belonging to another program.
In some early microprocessor designs, memory management was performed by a separate integrated circuit such as the VLSI Technology VI475 (1986), the Motorola 68851 (1984) used with the Motorola 68020 CPU in the Macintosh II, or the Z8010 and Z8015 (1985) used with the Zilog Z8000 family of processors.  Later microprocessors (such as the Motorola 68030 and the Zilog Z280) placed the MMU together with the CPU on the same integrated circuit, as did the Intel 80286 and later x86 microprocessors.
Some early systems, especially 8-bit systems, used very simple MMUs to perform bank switching.


== Types of address translation ==
Early systems used base and bounds addressing that further developed into segmentation, or paging; paged systems break up main memory into a series of equal-sized blocks, while segmented systems generally allow for variable sizes.


=== Segmented translation ===
In segmented translation, a memory address contains a segment number and an offset within the segment. Segments are variable-length and may have permissions, such as read, write, and execute, associated with them. A segment is loaded into a contiguous area of physical memory. Typically, the segment number is used as an index into a segment table; each entry in the segment table holds the address of the area of physical memory, the length of the segment, and other information such as permission flags.
This style has the advantage of simplicity; the memory blocks are continuous, and thus only the two values, base and limit, need to be stored for mapping purposes.
The disadvantage of this approach is that it leads to an effect known as external fragmentation. This occurs when memory allocations are released but are non-contiguous. In this case, enough memory may be available to handle a request, but this is spread out and cannot be allocated to a single segment. On systems where programs start and stop over time, this can eventually lead to memory being highly fragmented and no large blocks remaining; in this case, segments would need to be moved in memory, and their segment table entries modified to reflect the new physical address, to make a contiguous space large enough for a segment available.
Some models of the PDP-11 16-bit minicomputer have a segmented memory management unit with a set of page address registers (PARs) and page description registers (PDRs); this maps a 16-bit virtual address to an 18-bit physical address. The PDP-11/70 expands that to produce a 22-bit physical address.
Segmenting was widely used on microcomputer platforms of the 1980s. Among the MMUs that used this concept were the Motorola 68451 and the Zilog Z8010, but many other examples exist.
The Intel 8086, Intel 8088, Intel 80186, and Intel 80188 provide crude memory segmentation and no memory protection. (Every byte of every segment is always available to any program.) The 16-bit segment registers allow for 65,536 segments; each segment begins at a fixed offset equal to 16 times the segment number; the segment starting address granularity is 16 bytes. Each segment grants read-write access to 64 KiB (65,536 bytes) of address space (this limit is set by the 16-bit PC and SP registers; the processor does no bounds checking). Offset+address exceeding 0xFFFFF wraps around to 0x00000. Each 64 KiB segment overlaps the next 4,095 segments; each physical address can be denoted by 4,096 segment–offset pairs. This scheme can address only 1 MiB (1024 KiB) of physical memory (and memory-mapped i/o). (Optional expanded memory hardware can add bank-switched memory under software control.) Later x86 processors, starting with the Intel 80286, supported real segmented mapping, with a segment table.


=== Paged translation ===

In paged translation, the address space (the range of addresses used by the processor) is divided into pages, each having a size which is a power of 2, usually a few kilobytes, but they may be much larger. Programs reference memory using the natural address size of the machine, typically 32 or 64 bits in modern systems. The bottom bits of the address (the offset within a page) are left unchanged. The upper address bits are the virtual page numbers.
Most MMUs use an in-memory table of items called a page table, containing one page table entry (PTE) per virtual page, to map virtual page numbers to physical page numbers in main memory. Multi-level page tables are often used to reduce the size of the page table. An associative cache of PTEs is called a translation lookaside buffer (TLB) and is used to avoid the necessity of accessing the main memory every time a virtual address is mapped.
Other MMUs may have a private array of memory, a set of registers, or a one-or-more-level array of static RAM to store a set of mapping information.
The MMU splits the virtual address into a virtual page number and an offset within the page. The virtual page number is used to select a page table entry; if the page table entry is found and the page is marked as being in memory, the physical page number in the page table entry is combined with the offset to construct the physical address corresponding to the virtual address.
The virtual page number may be directly used as an index into the page table or other mapping information, or it may be further divided, with bits at a given level used as an index into a table of lower-level tables into which bits at the next level down are used as an index, with two or more levels of indexing.
One issue with paged translation is that as the virtual address space expands, the amount of memory needed to hold the mapping increases as well.
For instance, in the 68020 the addresses are 32 bits wide, meaning the virtual page number for an 8 kB page size is the upper 19 bits of the address, and a single-level page table would be 512 kB in size. In the 1980s, for an in-memory page table, this might be a significant fraction of the main memory of the machine, and, for an MMU that holds the page map in static RAM, might require a costly amount of static RAM.
This problem can be reduced by making the pages larger, say 64 kB instead of 8.
Now the page index uses 16 bits and the resulting page table is 64 kB, which is more tractable.
Moving to a larger page size leads to the second problem: increased internal fragmentation.
A program that generates a series of requests for small blocks will be assigned large blocks and thereby waste large amounts of memory.
If the address space is sparse, so that not all regions of it are allocated, the problem can be reduced by using a multi-level page table or static RAM map, and not allocating all the page table entries that would be needed for an empty region.
The paged translation approach was widely used by microprocessor MMUs in the 1970s and 1980s, including the 68020's 68851 and the on-chip MMU of the 68030, the Zilog Z8000's Z8015, and the NS32000 series's NS16082.
A page table entry or other per-page information may also include information about whether the page has been written to (the dirty bit), when it was last used (the accessed bit, for a least recently used (LRU) page replacement algorithm), what kind of processes (user mode or supervisor mode) may read and write it, and whether it should be cached.
Sometimes, a page table entry or other per-page information prohibits access to a particular virtual page, perhaps because no physical random-access memory (RAM) has been allocated to that virtual page.  In this case, the MMU signals a page fault to the CPU. The operating system (OS) then handles the situation, perhaps by trying to find a spare frame of RAM and set up the page map to map it to the requested virtual address.  If no RAM is free, it may be necessary to choose an existing page (known as a victim), using some replacement algorithm, and save it to disk (a process called paging). With some MMUs, there can also be a shortage of PTEs, in which case the OS will have to free one for the new mapping.
The MMU may also generate illegal access error conditions or invalid page faults upon illegal or non-existing memory accesses, respectively, leading to segmentation fault or bus error conditions when handled by the operating system.
Paged translation mitigates the problem of external fragmentation of memory.  After blocks of memory have been allocated and freed, the free memory may become fragmented (discontinuous) so that the largest contiguous block of free memory may be much smaller than the total amount.  With virtual memory, a contiguous range of virtual addresses can be mapped to several non-contiguous blocks of physical memory; this non-contiguous allocation is one of the benefits of paging.
However, paged translation causes another problem, internal fragmentation. This occurs when a program requests a block of memory that does not cleanly map into a page, for instance, if a program requests a 1 KB buffer to perform file work. In this case, the request results in an entire page being set aside even though only 1 KB of the page will ever be used; if pages are larger than 1 KB, the remainder of the page is wasted. If many small allocations of this sort are made, memory can be used up even though much of it remains empty.


=== Segmentation plus paging ===
Some systems, such as the GE 645 and its successors, used both segmentation and paging.  The table of segments, instead of containing per-segment entries giving the physical base address and length of the segment, contains entries giving the physical base address of a page table for the segment, in addition to the length of the segment.  Physical memory is divided into fixed-size pages, and the same techniques used for purely page-based demand paging are used for segment-and-page-based demand paging.
The Signetics 68905 MMU, designed for the Motorola 68000, 68010, and 68012 microprocessors, supported segmentation and paging. Both Signetics and Philips produced a version of the 68000 that combined the 68905 on the same physical chip as the processor, the 68070.


== Benefits ==
An MMU can provide memory protection, so that attempts by code to access or modify data to which it does not have access result in a failure; this catches both software bugs and deliberate attempts to access or modify that data. Typically, an operating system assigns each program its own virtual address space.
An MMU can also be used to expand the size of the physical address when the virtual address is too small. For instance, the PDP-11 originally had a 16-bit address that made it too small as memory sizes increased in the 1970s. This was addressed by expanding the physical memory bus to 18 bits, and using an MMU to add two more bits based on other pins on the processor bus to indicate which program was accessing memory.


== Other memory-related MMU functions ==
Some MMUs, such as the Signetics 68905, also included a controller to manage a processor cache, which stores recently accessed data in a very fast memory and thus reduces the need to talk to the slower main memory. In some implementations, MMUs are also responsible for bus arbitration, controlling access to the memory bus among the many parts of the computer that desire access.


== IOMMUs ==
Hardware that performs direct memory access completely bypasses the CPU's MMU.
Some I/O systems allow DMA hardware to use physical addresses to read or write directly anywhere in physical RAM without any restrictions.
Other I/O systems have a separate MMU called an input-output memory management unit (IOMMU) that can be programmed by the OS to translate device addresses from the DMA hardware to specific, limited physical pages chosen by the OS.
The IOMMU can be used to block DMA attacks.


== Examples ==
Most modern systems divide memory into pages that are 4–64 KB in size, often with the capability to use so-called huge pages of 2 MB or 1 GB in size (often both variants are possible).  Page translations are cached in a translation lookaside buffer (TLB).  Some systems, mainly older RISC designs, trap into the OS when a page translation is not found in the TLB.  Most systems use a hardware-based tree walker.  Most systems allow the MMU to be disabled, but some disable the MMU when trapping into OS code.


=== IBM System/360 Model 67, IBM System/370, and successors ===
The IBM System/360 Model 67, which was introduced August, 1965, included an MMU called a dynamic address translation (DAT) box.  It has the unusual feature of storing accessed and dirty bits outside of the page table (along with the four bit protection key for all S/360 processors).  They refer to physical memory rather than virtual memory, and are accessed by special-purpose instructions.  This reduces overhead for the OS, which would otherwise need to propagate accessed and dirty bits from the page tables to a more physically oriented data structure.  This makes OS-level virtualization, later called paravirtualization, easier.
Starting in August, 1972, the IBM System/370 has a similar MMU, although it initially supported only a 24-bit virtual address space rather than the 32-bit virtual address space of the System/360 Model 67.  It also stores the accessed and dirty bits outside the page table.  In early 1983, the System/370-XA architecture expanded the virtual address space to 31 bits, and in 2000, the 64-bit z/Architecture was introduced, with the address space expanded to 64 bits; those continue to store the accessed and dirty bits outside the page table.


=== VAX ===
VAX pages are 512 bytes, which is very small. An OS may treat multiple pages as if they were a single larger page. For example, Linux on VAX groups eight pages together. Thus, the system is viewed as having 4 KB pages. The VAX divides memory into four fixed-purpose regions, each 1 GB in size. They are:

P0 space
Used for general-purpose per-process memory such as heaps.
P1 space
(Or control space) which is also per-process and is typically used for supervisor, executive, kernel, user stacks and other per-process control structures managed by the operating system.
S0 space
(Or system space) which is global to all processes and stores operating system code and data, whether paged or not, including pagetables.
S1 space
Which is unused and "Reserved to Digital".
Page tables are big linear arrays. Normally, this would be very wasteful when addresses are used at both ends of the possible range, but the page tables for P0 and P1 space are stored in the paged S0 space. Thus, there is effectively a two-level tree, allowing applications to have a sparse memory layout without wasting a lot of space on unused page table entries. Unlike page table entries in most MMUs, page table entries in the VAX MMU lack an accessed bit. OSes which implement paging must find some way to emulate the accessed bit if they are to operate efficiently. Typically, the OS will periodically unmap pages so that page-not-present faults can be used to let the OS set an accessed bit.


=== ARM ===
ARM architecture-based application processors implement an MMU defined by ARM's virtual memory system architecture (VMSA).  The current architecture defines PTEs for describing 4 KB and 64 KB pages, 1 MB sections and 16 MB super-sections; legacy versions also defined a 1 KB tiny page.  ARM uses a two-level page table if using 4 KB and 64 KB pages, or just a one-level page table for 1 MB sections and 16 MB sections.
TLB updates are performed automatically by page table walking hardware.  PTEs include read/write access permission based on privilege, cacheability information, an NX bit, and a non-secure bit.


=== DEC Alpha ===
DEC Alpha processors divide memory into 8 KB, 16 KB, 32 KB, or 64 KB; the page size is dependent on the processor. pages.  After a TLB miss, low-level firmware machine code (here called PALcode) walks a page table.
The OpenVMS AXP PALcode and DEC OSF/1 PALcode walk a three-level tree-structured page table.  Addresses are broken down into an unused set of bits (containing the same value as the uppermost bit of the index into the root level of the tree), a set of bits to index the root level of the tree, a set of bits to index the middle level of the tree, a set of bits to index the leaf level of the tree, and remaining bits that pass through to the physical address without modification, indexing a byte within the page.  The sizes of the fields are dependent on the page size; all three tree index fields are the same size. The OpenVMS AXP PALcode supports full read and write permission bits for user, supervisor, executive, and kernel modes, and also supports fault on read/write/execute bits are also supported. The DEC OSF/1 PALcode supports full read and write permission bits for user and kernel modes, and also supports fault on read/write/execute bits.
The Windows NT AXP PALcode can either walk a single-level page table in a virtual address space or a two-level page table in physical address space.  The upper 32 bits of an address are ignored.
For a single-level page table, addresses are broken down into a set of bits to index the page table and remaining bits that pass through to the physical address without modification, indexing a byte within the page.
For a two-level page table, addresses are broken down into a set of bits to index the root level of the tree, a set of bits to index the top level of the tree, a set of bits to index the leaf level of the tree, and remaining bits that pass through to the physical address without modification, indexing a byte within the page.  The sizes of the fields are dependent on the page size. The Windows NT AXP PALcode supports a page being accessible only from kernel mode or being accessible from user and kernel mode, and also supports a fault on write bit.


=== MIPS ===

The MIPS architecture supports one to 64 entries in the TLB.  The number of TLB entries is configurable at CPU configuration before synthesis.  TLB entries are dual.  Each TLB entry maps a virtual page number (VPN2) to either one of two page frame numbers (PFN0 or PFN1), depending on the least significant bit of the virtual address that is not part of the page mask.  This bit and the page mask bits are not stored in the VPN2.  Each TLB entry has its own page size, which can be any value from 1 KB to 256 MB in multiples of four.  Each PFN in a TLB entry has a caching attribute, a dirty and a valid status bit.  A VPN2 has a global status bit and an OS assigned ID, which participates in the virtual address TLB entry match if the global status bit is set to zero.  A PFN stores the physical address without the page mask bits.
A TLB refill exception is generated when there are no entries in the TLB that match the mapped virtual address.  A TLB invalid exception is generated when there is a match, but the entry is marked invalid.  A TLB modified exception is generated when a store instruction references a mapped address and the matching entry's dirty status is not set.  If a TLB exception occurs when processing a TLB exception, a double-fault TLB exception, it is dispatched to its own exception handler.
MIPS32 and MIPS32r2 support 32 bits of virtual address space and up to 36 bits of physical address space.  MIPS64 supports up to 64 bits of virtual address space and up to 59 bits of physical address space.


=== Sun MMU ===
The original Sun-1 is a single-board computer built around the Motorola 68000 microprocessor and introduced in 1982. It includes the original Sun 1 memory management unit that provides address translation, memory protection, memory sharing and memory allocation for multiple processes running on the CPU.  All access of the CPU to private on-board RAM, external Multibus memory, on-board I/O and the Multibus I/O runs through the MMU, where address translation and protection are done in a uniform fashion. The MMU is implemented in hardware on the CPU board.
The MMU consists of a context register, a segment map and a page map.  Virtual addresses from the CPU are translated into intermediate addresses by the segment map, which in turn are translated into physical addresses by the page map.  The page size is 2 KB and the segment size is 32 KB which gives 16 pages per segment.  Up to 16 contexts can be mapped concurrently.  The maximum logical address space for a context is 1024 pages or 2 MB.  The maximum physical address that can be mapped simultaneously is also 2 MB.
The context register is important in a multitasking operating system because it allows the CPU to switch between processes without reloading all the translation state information.  The 4-bit context register can switch between 16 sections of the segment map under supervisor control, which allows 16 contexts to be mapped concurrently.  Each context has its own virtual address space.  Sharing of virtual address space and inter-context communications can be provided by writing the same values into the segment or page maps of different contexts.  Additional contexts can be handled by treating the segment map as a context cache and replacing out-of-date contexts on a least-recently used basis.
The context register makes no distinction between user and supervisor states.  Interrupts and traps do not switch contexts, which requires that all valid interrupt vectors always be mapped in page 0 of context, as well as the valid supervisor stack.
The Sun-2 workstations are similar; they are built around the Motorola 68010 microprocessor and have a similar memory management unit, with 2 KB pages and 32 KB segments.  The context register has a 3-bit system context used in supervisor state and a 3-bit user context used in user state.
The Sun-3 workstations, except for the Sun-3/80, Sun-3/460, Sun-3/470, and Sun-3/480, are built around the Motorola 68020, and have a similar memory management unit.  The page size is increased to 8 KB.  (The later models are built around the Motorola 68030 and use the 68030's on-chip MMU.)
The Sun-4 workstations are built around various SPARC microprocessors, and have a memory management unit similar to that of the Sun-3 workstations.


=== PowerPC ===

In PowerPC G1, G2, G3, and G4 pages are normally 4 KB.  After a TLB miss, the standard PowerPC MMU begins two simultaneous lookups.  One lookup attempts to match the address with one of four or eight data block address translation (DBAT) registers, or four or eight instruction block address translation registers (IBAT), as appropriate.  The BAT registers can map linear chunks of memory as large as 256 MB, and are normally used by an OS to map large portions of the address space for the OS kernel's own use.  If the BAT lookup succeeds, the other lookup is halted and ignored.
The other lookup, not directly supported by all processors in this family, is via a so-called inverted page table, which acts as a hashed off-chip extension of the TLB. First, the top four bits of the address are used to select one of 16 segment registers. Then 24 bits from the segment register replace those four bits, producing a 52-bit address.  The use of segment registers allows multiple processes to share the same hash table.
The 52-bit address is hashed, then used as an index into the off-chip table. There, a group of eight-page table entries is scanned for one that matches. If none match due to excessive hash collisions, the processor tries again with a slightly different hash function. If this, too, fails, the CPU traps into OS (with MMU disabled) so that the problem may be resolved. The OS needs to discard an entry from the hash table to make space for a new entry.  The OS may generate the new entry from a more normal tree-like page table or from per-mapping data structures, which are likely to be slower and more space-efficient.  Support for no-execute control is in the segment registers, leading to 256 MB granularity.
A major problem with this design is poor cache locality caused by the hash function.  Tree-based designs avoid this by placing the page table entries for adjacent pages in adjacent locations.  An operating system running on the PowerPC may minimize the size of the hash table to reduce this problem.
It is also somewhat slow to remove the page table entries of a process.  The OS may avoid reusing segment values to delay facing this, or it may elect to suffer the waste of memory associated with per-process hash tables.  G1 chips do not search for page table entries, but they do generate the hash, with the expectation that an OS will search the standard hash table via software.  The OS can write to the TLB.  G2, G3, and early G4 chips use hardware to search the hash table.  The latest chips allow the OS to choose either method.  On chips that make this optional or do not support it at all, the OS may choose to use a tree-based page table exclusively.


=== x86 ===
The x86 architecture has evolved over a very long time while maintaining full software compatibility, even for OS code. Thus, the MMU is extremely complex, with many different possible operating modes.
The 8086/8088 and 80186/80188 have no memory management unit; they support segmentation, but only to support more physical memory than a 16-bit address can support, as the segment number, in a segment register, is multiplied by 16 and added to the segment offset to generate a physical address.
The 80286 added an MMU that supports segmentation, but not paging. When segmentation is enabled by turning on protected mode, the segment number acts as an index into a table of segment descriptors; a segment descriptor contains a base physical address, a segment length, a presence bit to indicate whether the segment is currently in memory, permission bits, and control bits, If the offset in the segment is within the bounds specified by the segment descriptor, that offset is added to the base physical address to generate a physical address.
The 80386, which introduced the 32-bit IA-32 version of x86, and subsequent x86 CPUs, support segmentation and paging. If paging is enabled, the base address in a segment descriptor is an address in a linear paged address space divided into 4 KB pages, so when that is added to the offset in the segment, the resulting address is a linear address in that address space; in IA-32, that address is then masked to be no larger than 32 bits.  The result may be looked up via a tree-structured page table, with the bits of the address being split as follows: 10 bits for the branch of the tree, 10 bits for the leaves of the branch, and the 12 lowest bits being directly copied to the result.
Segment registers, used in pre-80386 CPUs to extend the address space, are not used in modern OSes, with one major exception: access to thread-specific data for applications or CPU-specific data for OS kernels, which is done with explicit use of the FS and GS segment registers. All memory access involves a segment register, chosen according to the code being executed. Except when using FS or GS, the OS ensures that the offset will be zero. Some operating systems, such as OpenBSD with its W^X feature, and Linux with the Exec Shield or PaX patches, may also limit the length of the code segment, as specified by the CS register, to disallow execution of code in modifiable regions of the address space.
Minor revisions of the MMU introduced with the Pentium have allowed very large 4 MB pages by skipping the bottom level of the tree (this leaves 10 bits for indexing the first level of page hierarchy with the remaining 10+12 bits being directly copied to the result).  Minor revisions of the MMU introduced with the Pentium Pro introduced the physical address extension (PAE) feature, enabling 36-bit physical addresses with 2+9+9 bits for three-level page tables and 12 lowest bits being directly copied to the result.  Large pages (2 MB) are also available by skipping the bottom level of the tree (resulting in 2+9 bits for a two-level table hierarchy and the remaining 9+12 lowest bits copied directly). In addition, the page attribute table allowed specification of cacheability by looking up a few high bits in a small on-CPU table.
No-execute support was originally only provided on a per-segment basis, making it very awkward to use.
More recent x86 chips provide a per-page NX bit (no-execute bit) in the PAE mode.
The W^X, Exec Shield, and PaX mechanisms described above emulate per-page non-execute support on machines with x86 processors that lack the NX bit by setting the length of the code segment, with a performance loss and a reduction in the available address space.

x86-64, the 64-bit version of the x86 architecture, almost entirely removes segmentation in favor of the flat memory model used by almost all operating systems for the 386 or newer processors.  In long mode, all segment offsets are ignored, except for the FS and GS segments; linear addresses are 64-bit rather than 32-bit, with the lowest 48 bits of the address being significant.  When used with 4 KB pages, the page table tree has four levels instead of three, to handle the larger linear addresses; in some newer x86-64 processors, a fifth page table level can be enabled, to support 57-bit linear addresses.  In all levels of the page table, the page table entry includes an NX bit.
48-bit linear addresses are divided as follows: 16 bits unused, nine bits each for four tree levels (for a total of 36 bits), and the 12 lowest bits directly copied to the result.  With 2 MB pages, there are only three levels of page table, for a total of 27 bits used in paging and 21 bits of offset.  Some newer CPUs also support a 1 GB page with two levels of paging and 30 bits of offset. CPUID can be used to determine if 1 GB pages are supported.
In all three cases, the 16 highest bits are required to be equal to the 48th bit, or in other words, the low 48 bits are sign extended to the higher bits. This is done to allow further expansion of the addressable range, without compromising backwards compatibility.
57-bit linear addresses are divided as follows: 7 bits unused, nine bits each for five tree levels (for a total of 45 bits), and the 12 lowest bits directly copied to the result. The low 57 bits are sign extended.


== Alternatives ==


=== Burroughs B5000 series, B6x00/B7x00/B5900/A-series/Unisys MCP systems ===
The Burroughs B5000 from 1961 was the first commercial system to support virtual memory (after the Atlas), has no need for an external MMU. The B5000 and its successors up to current Unisys ClearPath MCP (Libra) systems provide the two functions of an MMU — virtual memory addresses and memory protection — with a different architectural approach. Rather than add virtual memory onto a processor not designed for virtual memory, it is integrated in the core design of the processor/system so there is no requirement for an external unit to add functionality of address translation or bounds checking, resulting in unprecedented memory safety and security.
First, in the mapping of virtual memory addresses, instead of needing an MMU, the machines are descriptor-based. The uppermost bit of a 48-bit memory word in the Burroughs B5000 series systems indicate whether the word is a user data or a descriptor/control word; descriptors were read-only to user processes and could only be updated by the system (hardware or operating system). Memory words in the B6x00/B7x00/B5900/A-series/Unisys MCP systems have 48 data bits and 3 tag bits (and later systems to current have 4 tag bits). Words whose tag is an odd number are read-only to user processes – descriptors have a tag of 5 and code words have a tag of 3.
Each allocated memory block is given a master descriptor with the properties of the block — physical address, size, and whether it is present in main memory or not; in which case, on first access, the block must be allocated, or if there is an address, it is an address on secondary storage and must be loaded to main memory.  All references to code and data are made using a descriptor. When a request is made to access the block for reading or writing, the hardware checks its presence via the presence bit (pbit) in the descriptor.
A pbit of 1 indicates the presence of the block.  In this case, the block can be accessed via the physical main-memory address in the descriptor.  If the pbit is zero, a pbit interrupt is generated for the MCP (operating system) to make the block present.  If the address field is zero, this is the first access to this block, and it is allocated (an init (initial) pbit).  If the address field is non-zero, it is a disk address of the block, which has previously been rolled out — the block is fetched from disk, the pbit is set to one, and the physical memory address is updated to point to the block in memory.  This makes descriptors equivalent to a page-table entry in an MMU system, but descriptors are free of a table.
All memory allocation is therefore completely automatic (one of the features of modern systems) and there is no way to allocate blocks other than this mechanism.  There are no such calls as malloc or dealloc, since memory blocks are also automatically allocated on pbit interrupt or discarded.  The scheme is also lazy, since a block will not be allocated until it is actually referenced.  When memory is nearly full, the MCP examines the working set, trying compaction (since the system is segmented, not paged), deallocating read-only segments (such as code segments which can be restored from their original copy) and, as a last resort, rolling dirty (that is, updated) data segments out to disk.
Another way these systems provide a function of an MMU is in protection.  Since all accesses are via the descriptor, the hardware can check that all accesses are within bounds and, in the case of a write, that the process has write permission.  The MCP system is inherently secure and thus has no need of an MMU to provide this level of memory protection.
Blocks can be shared between processes via copy descriptors in process stacks (a stack is a special system structure representing the execution state of a process).
Thus, some processes may have write permission, whereas others do not.
Code segments are read-only, thus reentrant and shared between processes.
Copy descriptors contain a 20-bit address field giving the index of the master descriptor in the master descriptor array.
This also implements a very efficient and secure Interprocess Communication (IPC) mechanism.
Blocks can easily be relocated, since only the master descriptor needs to be updated when a block's status changes.
Another aspect is performance –  do MMU-based or non-MMU-based systems provide better performance?  MCP systems may be implemented on top of standard hardware that has an MMU (for example, a standard PC).  Even if the system implementation uses the MMU in some way, this will not be at all visible at the MCP level.


== Bank switching ==
A simple technique called bank switching was widely used by early 8-bit microprocessors like the MOS 6502. For instance, the Atari MMU would express additional bits on the address bus to select among several banks of DRAM memory based on which of the chips was currently active, normally the CPU or ANTIC. This was used to expand the available memory on the Atari 130XE to 128 kB. The Commodore 128 used a similar approach.


== See also ==
Burroughs large systems descriptors
Memory controller
Memory protection unit


== References ==

---page---

# Page replacement algorithm

In a computer operating system that uses paging for virtual memory management, page replacement algorithms decide which memory pages to page out, sometimes called swap out, or write to disk, when a page of memory needs to be allocated. Page replacement happens when a requested page is not in memory (page fault) and a free page cannot be used to satisfy the allocation, either because there are none, or because the number of free pages is lower than some threshold.
When the page that was selected for replacement and paged out is referenced again it has to be paged in (read in from disk), and this involves waiting for I/O completion. This determines the quality of the page replacement algorithm: the less time waiting for page-ins, the better the algorithm. A page replacement algorithm looks at the limited information about accesses to the pages provided by hardware, and tries to guess which pages should be replaced to minimize the total number of page misses, while balancing this with the costs (primary storage and processor time) of the algorithm itself.
The page replacing problem is a typical online problem from the competitive analysis perspective in the sense that the optimal deterministic algorithm is known.


== History ==
Page replacement algorithms were a hot topic of research and debate in the 1960s and 1970s.
That mostly ended with the development of sophisticated LRU (least recently used) approximations and working set algorithms. Since then, some basic assumptions made by the traditional page replacement algorithms were invalidated, resulting in a revival of research. In particular, the following trends in the behavior of underlying hardware and user-level software have affected the performance of page replacement algorithms:

Size of primary storage has increased by multiple orders of magnitude. With several gigabytes of primary memory, algorithms that require a periodic check of each and every memory frame are becoming less and less practical.
Memory hierarchies have grown taller. The cost of a CPU cache miss is far more expensive. This exacerbates the previous problem.
Locality of reference of user software has weakened. This is mostly attributed to the spread of object-oriented programming techniques that favor large numbers of small functions, use of sophisticated data structures like trees and hash tables that tend to result in chaotic memory reference patterns, and the advent of garbage collection that drastically changed memory access behavior of applications.
Requirements for page replacement algorithms have changed due to differences in operating system kernel architectures. In particular, most modern OS kernels have unified virtual memory and file system caches, requiring the page replacement algorithm to select a page from among the pages of both user program virtual address spaces and cached files. The latter pages have specific properties. For example, they can be locked, or can have write ordering requirements imposed by journaling. Moreover, as the goal of page replacement is to minimize total time waiting for memory, it has to take into account memory requirements imposed by other kernel sub-systems that allocate memory. As a result, page replacement in modern kernels (Linux, FreeBSD, and Solaris) tends to work at the level of a general purpose kernel memory allocator, rather than at the higher level of a virtual memory subsystem.


== Local vs. global replacement ==
Replacement algorithms can be local or global.
When a process incurs a page fault, a local page replacement algorithm selects for replacement some page that belongs to that same process (or a group of processes sharing a memory partition).
A global replacement algorithm is free to select any page in memory.
Local page replacement assumes some form of memory partitioning that determines how many pages are to be assigned to a given process or a group of processes. Most popular forms of partitioning are fixed partitioning and balanced set algorithms based on the working set model. The advantage of local page replacement is its scalability: each process can handle its page faults independently, leading to more consistent performance for that process. However global page replacement is more efficient on an overall system basis.


== Detecting which pages are referenced and modified ==

Modern general purpose computers and some embedded processors have support for virtual memory. In most of them, each process has its own virtual address space. A page table maps a subset of the process virtual addresses to physical addresses. In addition, in most architectures the page table holds an "access" bit and a "dirty" bit for each page in the page table. The CPU sets the access bit when the process reads or writes memory in that page. The CPU sets the dirty bit when the process writes memory in that page. The operating system can modify the access and dirty bits. The operating system can detect accesses to memory and files through the following means:

By clearing the access bit in pages present in the process' page table. After some time, the OS scans the page table looking for pages that had the access bit set by the CPU. This is fast because the access bit is set automatically by the CPU and inaccurate because the OS does not immediately receive notice of the access nor does it have information about the order in which the process accessed these pages.
By removing pages from the process' page table without necessarily removing them from physical memory. The next access to that page is detected immediately because it causes a page fault. This is slow because a page fault involves a context switch to the OS, software lookup for the corresponding physical address, modification of the page table and a context switch back to the process and accurate because the access is detected immediately after it occurs.
Directly when the process makes system calls that potentially access the page cache like read and write in POSIX.


== Precleaning ==
Most replacement algorithms simply return the target page as their result. This means that if target page is dirty (that is, contains data that have to be written to the stable storage before page can be reclaimed), I/O has to be initiated to send that page to the stable storage (to clean the page). In the early days of virtual memory, time spent on cleaning was not of much concern, because virtual memory was first implemented on systems with full duplex channels to the stable storage, and cleaning was customarily overlapped with paging. Contemporary commodity hardware, on the other hand, does not support full duplex transfers, and cleaning of target pages becomes an issue.
To deal with this situation, various precleaning policies are implemented. Precleaning is the mechanism that starts I/O on dirty pages that are (likely) to be replaced soon. The idea is that by the time the precleaned page is actually selected for the replacement, the I/O will complete and the page will be clean. Precleaning assumes that it is possible to identify pages that will be replaced next. Precleaning that is too eager can waste I/O bandwidth by writing pages that manage to get re-dirtied before being selected for replacement.


== The (h,k)-paging problem ==
The (h,k)-paging problem is a generalization of the model of paging problem: Let h,k be positive integers such that h≤k. We measure the performance of an algorithm with cache of size h≤k relative to the theoretically optimal page replacement algorithm. If h<k, we provide the optimal page replacement algorithm with strictly less resource.
The (h,k)-paging problem is a way to measure how an online algorithm performs by comparing it with the performance of the optimal algorithm, specifically, separately parameterizing the cache size of the online algorithm and optimal algorithm.


== Marking algorithms ==

Marking algorithms is a general class of paging algorithms. For each page, we associate it with a bit called its mark. Initially, we set all pages as unmarked. During a stage (a period of operation or a sequence of requests) of page requests, we mark a page when it is first requested in this stage. A marking algorithm is such an algorithm that never pages out a marked page.
If ALG is a marking algorithm with a cache of size k, and OPT is the optimal algorithm with a cache of size h, where h≤k, then ALG is kk−h+1-competitive. So every marking algorithm attains the kk−h+1-competitive ratio.
LRU is a marking algorithm while FIFO is not a marking algorithm.


== Conservative algorithms ==
An algorithm is conservative, if on any consecutive request sequence containing k or fewer distinct page references, the algorithm will incur k or fewer page faults.
If ALG is a conservative algorithm with a cache of size k, and OPT is the optimal algorithm with a cache of h≤k, then ALG is kk−h+1-competitive. So every conservative algorithm attains the kk−h+1-competitive ratio.
LRU, FIFO and CLOCK are conservative algorithms.


== Page replacement algorithms ==
There are a variety of page replacement algorithms:


=== The theoretically optimal page replacement algorithm ===
The theoretically optimal page replacement algorithm (also known as OPT, clairvoyant replacement algorithm, or Bélády's optimal page replacement policy) is an algorithm that works as follows: when a page needs to be swapped in, the operating system swaps out the page whose next use will occur farthest in the future. For example, a page that is not going to be used for the next 6 seconds will be swapped out over a page that is going to be used within the next 0.4 seconds.
This algorithm cannot be implemented in a general purpose operating system because it is impossible to compute reliably how long it will be before a page is going to be used, except when all software that will run on a system is either known beforehand and is amenable to static analysis of its memory reference patterns, or only a class of applications allowing run-time analysis. Despite this limitation, algorithms exist that can offer near-optimal performance — the operating system keeps track of all pages referenced by the program, and it uses those data to decide which pages to swap in and out on subsequent runs. This algorithm can offer near-optimal performance, but not on the first run of a program, and only if the program's memory reference pattern is relatively consistent each time it runs.
Analysis of the paging problem has also been done in the field of online algorithms. Efficiency of randomized online algorithms for the paging problem is measured using amortized analysis.


=== Not recently used ===
The not recently used (NRU) page replacement algorithm is an algorithm that favours keeping pages in memory that have been recently used. This algorithm works on the following principle: when a page is referenced, a referenced bit is set for that page, marking it as referenced. Similarly, when a page is modified (written to), a modified bit is set. The setting of the bits is usually done by the hardware, although it is possible to do so on the software level as well.
At a certain fixed time interval, a timer interrupt triggers and clears the referenced bit of all the pages, so only pages referenced within the current timer interval are marked with a referenced bit. When a page needs to be replaced, the operating system divides the pages into four classes:

3. referenced, modified
2. referenced, not modified
1. not referenced, modified
0. not referenced, not modified
Although it does not seem possible for a page to be modified yet not referenced, this happens when a class 3 page has its referenced bit cleared by the timer interrupt. The NRU algorithm picks a random page from the lowest category for removal. So out of the above four page categories, the NRU algorithm will replace a not-referenced, not-modified page if such a page exists. Note that this algorithm implies that a modified but not-referenced (within the last timer interval) page is less important than a not-modified page that is intensely referenced.
NRU is a marking algorithm, so it is kk−h+1-competitive.


=== First-in, first-out ===
The simplest page-replacement algorithm is a FIFO algorithm. The first-in, first-out (FIFO) page replacement algorithm is a low-overhead algorithm that requires little bookkeeping on the part of the operating system. The idea is obvious from the name – the operating system keeps track of all the pages in memory in a queue, with the most recent arrival at the back, and the oldest arrival in front. When a page needs to be replaced, the page at the front of the queue (the oldest page) is selected. While FIFO is cheap and intuitive, it performs poorly in practical application. Thus, it is rarely used in its unmodified form. This algorithm experiences Bélády's anomaly.
In simple words, on a page fault, the frame that has been in memory the longest is replaced.
FIFO page replacement algorithm is used by the OpenVMS operating system, with some modifications. Partial second chance is provided by skipping a limited number of entries with valid translation table references, and additionally, pages are displaced from process working set to a systemwide pool from which they can be recovered if not already re-used.
FIFO is a conservative algorithm, so it is kk−h+1-competitive.


=== Second-chance ===
A modified form of the FIFO page replacement algorithm, known as the Second-chance page replacement algorithm, fares relatively better than FIFO at little cost for the improvement. It works by looking at the front of the queue as FIFO does, but instead of immediately paging out that page, it checks to see if its referenced bit is set. If it is not set, the page is swapped out. Otherwise, the referenced bit is cleared, the page is inserted at the back of the queue (as if it were a new page) and this process is repeated. This can also be thought of as a circular queue. If all the pages have their referenced bit set, on the second encounter of the first page in the list, that page will be swapped out, as it now has its referenced bit cleared. If all the pages have their reference bit cleared, then second chance algorithm degenerates into pure FIFO.
As its name suggests, Second-chance gives every page a "second-chance" – an old page that has been referenced is probably in use, and should not be swapped out over a new page that has not been referenced.


=== Clock ===
Clock is a more efficient version of FIFO than Second-chance because pages don't have to be constantly pushed to the back of the list, but it performs the same general function as Second-Chance. The clock algorithm keeps a circular list of pages in memory, with the "hand" (iterator) pointing to the last examined page frame in the list. When a page fault occurs and no empty frames exist, then the R (referenced) bit is inspected at the hand's location. If R is 0, the new page is put in place of the page the "hand" points to, and the hand is advanced one position. Otherwise, the R bit is cleared, then the clock hand is incremented and the process is repeated until a page is replaced. This algorithm was first described in 1969 by Fernando J. Corbató.


==== Variants of clock ====
GCLOCK: Generalized clock page replacement algorithm.
Clock-Pro keeps a circular list of information about recently referenced pages, including all M pages in memory as well as the most recent M pages that have been paged out. This extra information on paged-out pages, like the similar information maintained by ARC, helps it work better than LRU on large loops and one-time scans.
WSclock. By combining the Clock algorithm with the concept of a working set (i.e., the set of pages expected to be used by that process during some time interval), the performance of the algorithm can be improved. In practice, the "aging" algorithm and the "WSClock" algorithm are probably the most important page replacement algorithms.
Clock with Adaptive Replacement (CAR) is a page replacement algorithm that has performance comparable to ARC, and substantially outperforms both LRU and CLOCK. The algorithm CAR is self-tuning and requires no user-specified magic parameters.
CLOCK is a conservative algorithm, so it is kk−h+1-competitive.


=== Least recently used ===
The least recently used (LRU) page replacement algorithm, though similar in name to NRU, differs in the fact that LRU keeps track of page usage over a short period of time, while NRU just looks at the usage in the last clock interval. LRU works on the idea that pages that have been most heavily used in the past few instructions are most likely to be used heavily in the next few instructions too. While LRU can provide near-optimal performance in theory (almost as good as adaptive replacement cache), it is rather expensive to implement in practice. There are a few implementation methods for this algorithm that try to reduce the cost yet keep as much of the performance as possible.
The most expensive method is the linked list method, which uses a linked list containing all the pages in memory. At the back of this list is the least recently used page, and at the front is the most recently used page. The cost of this implementation lies in the fact that items in the list will have to be moved about every memory reference, which is a very time-consuming process.
Another method that requires hardware support is as follows: suppose the hardware has a 64-bit counter that is incremented at every instruction. Whenever a page is accessed, it acquires the value equal to the counter at the time of page access. Whenever a page needs to be replaced, the operating system selects the page with the lowest counter and swaps it out.
Because of implementation costs, one may consider algorithms (like those that follow) that are similar to LRU, but which offer cheaper implementations.
One important advantage of the LRU algorithm is that it is amenable to full statistical analysis. It has been proven, for example, that LRU can never result in more than N-times more page faults than OPT algorithm, where N is proportional to the number of pages in the managed pool.
On the other hand, LRU's weakness is that its performance tends to degenerate under many quite common reference patterns. For example, if there are N pages in the LRU pool, an application executing a loop over array of N + 1 pages will cause a page fault on each and every access. As loops over large arrays are common, much effort has been put into modifying LRU to work better in such situations. Many of the proposed LRU modifications try to detect looping reference patterns and to switch into suitable replacement algorithm, like Most Recently Used (MRU).


==== Variants on LRU ====
LRU-K evicts the page whose K-th most recent access is furthest in the past. For example, LRU-1 is simply LRU whereas LRU-2 evicts pages according to the time of their penultimate access. LRU-K improves greatly on LRU with regards to locality in time.
The ARC algorithm extends LRU by maintaining a history of recently evicted pages and uses this to change preference to recent or frequent access. It is particularly resistant to sequential scans.
The 2Q algorithm improves upon the LRU and LRU/2 algorithm. By having two queues, one for hot-path items and the other for slow-path items, items are first placed in the slow-path queue and after a second access of the items placed in the hot-path items. Because references to added items are longer hold than in the LRU and LRU/2 algorithm, it has a better hot-path queue which improves the hit rate of the cache.
A comparison of ARC with other algorithms (LRU, MQ, 2Q, LRU-2, LRFU, LIRS) can be found in Megiddo & Modha 2004.
LRU is a marking algorithm, so it is kk−h+1-competitive.


=== Random ===
The random replacement algorithm replaces a random page in memory. This eliminates the overhead cost of tracking page references. Usually it fares better than FIFO, and for looping memory references it is better than LRU, although generally LRU performs better in practice. OS/390 uses global LRU approximation and falls back to random replacement when LRU performance degenerates, and the Intel i860 processor used a random replacement policy (Rhodehamel 1989).


=== Not frequently used (NFU) ===
The not frequently used (NFU) page replacement algorithm requires a counter, and every page has one counter of its own which is initially set to 0. At each clock interval, all pages that have been referenced within that interval will have their counter incremented by 1. In effect, the counters keep track of how frequently a page has been used. Thus, the page with the lowest counter can be swapped out when necessary.
The main problem with NFU is that it keeps track of the frequency of use without regard to the time span of use. Thus, in a multi-pass compiler, pages which were heavily used during the first pass, but are not needed in the second pass will be favoured over pages which are comparably lightly used in the second pass, as they have higher frequency counters. This results in poor performance. Other common scenarios exist where NFU will perform similarly, such as an OS boot-up. Thankfully, a similar and better algorithm exists, and its description follows.
The not frequently used page-replacement algorithm generates fewer page faults than the least recently used page replacement algorithm when the page table contains null pointer values.


=== Aging ===
The aging algorithm is a descendant of the NFU algorithm, with modifications to make it aware of the time span of use. Instead of just incrementing the counters of pages referenced, putting equal emphasis on page references regardless of the time, the reference counter on a page is first shifted right (divided by 2), before adding the referenced bit to the left of that binary number. For instance, if a page has referenced bits 1,0,0,1,1,0 in the past 6 clock ticks, its referenced counter will look like this in chronological order: 10000000, 01000000, 00100000, 10010000, 11001000, 01100100. Page references closer to the present time have more impact than page references long ago. This ensures that pages referenced more recently, though less frequently referenced, will have higher priority over pages more frequently referenced in the past. Thus, when a page needs to be swapped out, the page with the lowest counter will be chosen.
The following Python code simulates the aging algorithm.
Counters Vi are initialized with 0 and updated as described above via Vi←(Ri≪(k−1))|(Vi≫1), using arithmetic shift operators.

In the given example of R-bits for 6 pages over 5 clock ticks, the function prints the following output, which lists the R-bits for each clock tick t and the individual counter values Vi for each page in binary representation.

Note that aging differs from LRU in the sense that aging can only keep track of the references in the latest 16/32 (depending on the bit size of the processor's integers) time intervals. Consequently, two pages may have referenced counters of 00000000, even though one page was referenced 9 intervals ago and the other 1000 intervals ago. Generally speaking, knowing the usage within the past 16 intervals is sufficient for making a good decision as to which page to swap out. Thus, aging can offer near-optimal performance for a moderate price.


=== Longest distance first (LDF) page replacement algorithm ===
The basic idea behind this algorithm is Locality of Reference as used in LRU but the difference is that in LDF, locality is based on distance not on the used references. In the LDF, replace the page which is on longest distance from the current page. If two pages are on same distance then the page which is next to current page in anti-clock rotation will get replaced.


== Implementation details ==


=== Techniques for hardware with no reference bit ===
Many of the techniques discussed above assume the presence of a reference bit associated with each page.  Some hardware has no such bit, so its efficient use requires techniques that operate well without one.
One notable example is VAX hardware running OpenVMS. This system knows if a page has been modified, but not necessarily if a page has been read. Its approach is known as Secondary Page Caching. Pages removed from working sets (process-private memory, generally) are placed on special-purpose lists while remaining in physical memory for some time. Removing a page from a working set is not technically a page-replacement operation, but effectively identifies that page as a candidate. A page whose backing store is still valid (whose contents are not dirty, or otherwise do not need to be preserved) is placed on the tail of the Free Page List. A page that requires writing to backing store will be placed on the Modified Page List. These actions are typically triggered when the size of the Free Page List falls below an adjustable threshold.
Pages may be selected for working set removal in an essentially random fashion, with the expectation that if a poor choice is made, a future reference may retrieve that page from the Free or Modified list before it is removed from physical memory. A page referenced this way will be removed from the Free or Modified list and placed back into a process working set. The Modified Page List additionally provides an opportunity to write pages out to backing store in groups of more than one page, increasing efficiency. These pages can then be placed on the Free Page List. The sequence of pages that works its way to the head of the Free Page List resembles the results of a LRU or NRU mechanism and the overall effect has similarities to the Second-Chance algorithm described earlier.
Another example is used by the Linux kernel on ARM. The lack of hardware functionality is made up for by providing two page tables – the processor-native page tables, with neither referenced bits nor dirty bits, and software-maintained page tables with the required bits present. The emulated bits in the software-maintained table are set by page faults. In order to get the page faults, clearing emulated bits in the second table revokes some of the access rights to the corresponding page, which is implemented by altering the native table.


=== Page cache in Linux ===
Linux uses a unified page cache for

brk and anonymous mmaped-regions. This includes the heap and stack of user-space programs. It is written to swap when paged out.
Non-anonymous (file-backed) mmaped regions. If present in memory and not privately modified the physical page is shared with file cache or buffer.
Shared memory acquired through shm_open.
The tmpfs in-memory filesystem; written to swap when paged out.
The file cache including; written to the underlying block storage (possibly going through the buffer, see below) when paged out.
The cache of block devices, called the "buffer" by Linux (not to be confused with other structures also called buffers like those use for pipes and buffers used internally in Linux); written to the underlying storage when paged out.
The unified page cache operates on units of the smallest page size supported by the CPU (4 KiB in ARMv8, x86 and x86-64) with some pages of the next larger size (2 MiB in x86-64) called "huge pages" by Linux. The pages in the page cache are divided in an "active" set and an "inactive" set. Both sets keep a LRU list of pages. In the basic case, when a page is accessed by a user-space program it is put in the head of the inactive set. When it is accessed repeatedly, it is moved to the active list. Linux moves the pages from the active set to the inactive set as needed so that the active set is smaller than the inactive set. When a page is moved to the inactive set it is removed from the page table of any process address space, without being paged out of physical memory. When a page is removed from the inactive set, it is paged out of physical memory. The size of the "active" and "inactive" list can be queried from /proc/meminfo in the fields "Active", "Inactive", "Active(anon)", "Inactive(anon)", "Active(file)" and "Inactive(file)".


== Working set ==

The working set of a process is the set of pages expected to be used by that process during some time interval.
The "working set model" isn't a page replacement algorithm in the strict sense (it's actually a kind of medium-term scheduler)


== References ==


== Further reading ==

---page---

# Demand paging

In computer operating systems, demand paging (as opposed to anticipatory paging) is a method of virtual memory management. In a system that uses demand paging, the operating system copies a disk page into physical memory only when an attempt is made to access it and that page is not already in memory (i.e., if a page fault occurs). It follows that a process begins execution with none of its pages in physical memory, and triggers many page faults until most of its working set of pages are present in physical memory. This is an example of a lazy loading technique.


== Basic concept ==
Demand paging only brings pages into memory when an executing process demands them. This is often referred to as lazy loading, as only those pages demanded by the process are swapped from secondary storage to main memory. Contrast this to pure swapping, where all memory for a process is swapped from secondary storage to main memory when the process starts up or resumes execution.
Commonly, to achieve this process a memory management unit is used. The memory management unit maps logical memory to physical memory. Entries in the memory management unit include a bit that indicates whether a page is valid or invalid. A valid page is one that currently resides in main memory. An invalid page is one that currently resides in secondary memory. When a process tries to access a page, the following steps are generally followed:

Attempt to access page.
If page is valid (in memory) then continue processing instruction as normal.
If page is invalid then a page-fault trap occurs.
Check if the memory reference is a valid reference to a location on secondary memory. If so, we have to page in the required page. Otherwise, the process is terminated (illegal memory access).
Schedule disk operation to read the desired page into main memory.
Restart the instruction that was interrupted by the operating system trap.


== Advantages ==
Demand paging, as opposed to loading all pages immediately:

Only loads pages that are demanded by the executing process.
As there is more space in main memory, more processes can be loaded, reducing the context switching time, which utilizes large amounts of resources.
Less loading latency occurs at program startup, as less information is accessed from secondary storage and less information is brought into main memory.
As main memory is expensive compared to secondary memory, this technique helps significantly reduce the bill of material (BOM) cost in smart phones for example. Symbian OS had this feature.


== Disadvantages ==
Individual programs face extra latency when they access a page for the first time.
Low-cost, low-power embedded systems may not have a memory management unit that supports page replacement.
Memory management with page replacement algorithms becomes slightly more complex.
Possible security risks, including vulnerability to timing attacks; see Percival, Colin (2005-05-13). Cache missing for fun and profit (PDF). BSDCan 2005. (specifically the virtual memory attack in section 2).
Thrashing which may occur due to repeated page faults.


== See also ==

Lazy evaluation
Page cache
Memory management
Virtual memory


== References ==
Tanenbaum, Andrew S. Operating Systems: Design and Implementation (Second Edition). New Jersey: Prentice-Hall 1997.

---page---

# Memory protection

Memory protection is a way to control memory access rights on a computer, and is a part of most modern instruction set architectures and operating systems.  The main purpose of memory protection is to prevent a process from accessing memory that has not been allocated to it.  This prevents a bug or malware within a process from affecting other processes, or the operating system itself.  Protection may encompass all accesses to a specified area of memory, write accesses, or attempts to execute the contents of the area. An attempt to access unauthorized memory results in a hardware fault, e.g., a segmentation fault, storage violation exception, generally causing abnormal termination of the offending process. Memory protection for computer security includes additional techniques such as address space layout randomization and executable-space protection.


== Methods ==


=== Segmentation ===

Segmentation refers to dividing a computer's memory into segments.  A reference to a memory location includes a value that identifies a segment and an offset within that segment. A segment descriptor may limit access rights, e.g., read only, only from certain rings.
The x86 architecture has multiple segmentation features, which are helpful for using protected memory on this architecture. On the x86 architecture, the Global Descriptor Table and Local Descriptor Tables can be used to reference segments in the computer's memory. Pointers to memory segments on x86 processors can also be stored in the processor's segment registers. Initially x86 processors had 4 segment registers, CS (code segment), SS (stack segment), DS (data segment) and ES (extra segment); later another two segment registers were added – FS and GS.


=== Paged virtual memory ===
 
In paging the memory address space or segment is divided into equal-sized blocks called pages.  Using virtual memory hardware, each page can reside in any location at a suitable boundary of the computer's physical memory, or be flagged as being protected.  Virtual memory makes it possible to have a linear virtual memory address space and to use it to access blocks fragmented over physical memory address space.
Most computer architectures which support paging also use pages as the basis for memory protection.
A page table maps virtual memory to physical memory. There may be a single page table, a page table for each process, a page table for each segment, or a hierarchy of page tables, depending on the architecture and the OS. The page tables are usually invisible to the process.  Page tables make it easier to allocate additional memory, as each new page can be allocated from anywhere in physical memory. On some systems a page table entry can also designate a page as read-only.
Some operating systems set up a different address space for each process, which provides hard memory protection boundaries.
It is impossible for an unprivileged application to access a page that has not been explicitly allocated to it, because every memory address either points to a page allocated to that application, or generates an interrupt called a page fault. Unallocated pages, and pages allocated to any other application, do not have any addresses from the application point of view.
A page fault may not necessarily indicate an error.  Page faults are not only used for memory protection. The operating system may manage the page table in such a way that a reference to a page that has been previously paged out to secondary storage causes a page fault. The operating system intercepts the page fault, loads the required memory page, and the application continues as if no fault had occurred. This scheme, a type of virtual memory, allows in-memory data not currently in use to be moved to secondary storage and back in a way which is transparent to applications, to increase overall memory capacity.
On some systems, a request for virtual storage may allocate a block of virtual addresses for which no page frames have been assigned, and the system will only assign and initialize page frames when page faults occur. On some systems a guard page may be used, either for error detection or to automatically grow data structures.
On some systems, the page fault mechanism is also used for executable-space protection such as W^X.


=== Protection keys ===
A memory protection key (MPK) mechanism divides physical memory into blocks of a particular size (e.g., 4 KiB), each of which has an associated numerical value called a protection key.  Each process also has a protection key value associated with it.  On a memory access the hardware checks that the current process's protection key matches the value associated with the memory block being accessed; if not, an exception occurs.  This mechanism was introduced in the System/360 architecture. It is available on today's System z mainframes and heavily used by System z operating systems and their subsystems.
The System/360 protection keys described above are associated with physical addresses.  This is different from the protection key mechanism used by architectures such as the Hewlett-Packard/Intel IA-64 and Hewlett-Packard PA-RISC, which are associated with virtual addresses, and which allow multiple keys per process.
In the Itanium and PA-RISC architectures, translations (TLB entries) have keys (Itanium) or access ids (PA-RISC) associated with them.  A running process has several protection key registers (16 for Itanium, 4 for PA-RISC). A translation selected by the virtual address has its key compared to each of the protection key registers.  If any of them match (plus other possible checks), the access is permitted.  If none match, a fault or exception is generated.  The software fault handler can, if desired, check the missing key against a larger list of keys maintained by software; thus, the protection key registers inside the processor may be treated as a software-managed cache of a larger list of keys associated with a process.
PA-RISC has 15–18 bits of key; Itanium mandates at least 18.  Keys are usually associated with protection domains, such as libraries, modules, etc.
In the x86, the protection keys architecture allows tagging virtual addresses for user pages with any of 16 protection keys. All the pages tagged with the same protection key constitute a protection domain.  A new register contains the permissions associated with each of the protection domain. Load and store operations are checked against both the page table permissions and the protection key permissions associated with the protection domain of the virtual address, and only allowed if both permissions allow the access. The protection key permissions can be set from user space, allowing applications to directly restrict access to the application data without OS intervention. Since the protection keys are associated with a virtual address, the protection domains are per address space, so processes running in different address spaces can each use all 16 domains.


=== Protection rings ===
In Multics and systems derived from it, each segment has a protection ring for reading, writing and execution; an attempt by a process with a higher ring number than the ring number for the segment causes a fault. There is a mechanism for safely calling procedures that run in a lower ring and returning to the higher ring. There are mechanisms for a routine running with a low ring number to access a parameter with the larger of its own ring and the caller's ring.


=== Simulated segmentation ===
Simulation is the use of a monitoring program to interpret the machine code instructions of some computer architectures.  Such an instruction set simulator can provide memory protection by using a segmentation-like scheme and validating the target address and length of each instruction in real time before actually executing them. The simulator must calculate the target address and length and compare this against a list of valid address ranges that it holds concerning the thread's environment, such as any dynamic memory blocks acquired since the thread's inception, plus any valid shared static memory slots. The meaning of "valid" may change throughout the thread's life depending upon context. It may sometimes be allowed to alter a static block of storage, and sometimes not, depending upon the current mode of execution, which may or may not depend on a storage key or supervisor state.
It is generally not advisable to use this method of memory protection where adequate facilities exist on a CPU, as this takes valuable processing power from the computer. However, it is generally used for debugging and testing purposes to provide an extra fine level of granularity to otherwise generic storage violations and can indicate precisely which instruction is attempting to overwrite the particular section of storage which may have the same storage key as unprotected storage.


=== Capability-based addressing ===

Capability-based addressing is a method of memory protection that is unused in modern commercial computers. In this method, pointers are replaced by protected objects (called capabilities) that can only be created using privileged instructions which may only be executed by the kernel, or some other process authorized to do so. This effectively lets the kernel control which processes may access which objects in memory, with no need to use separate address spaces or context switches. Only a few commercial products used capability based security: Plessey System 250, IBM System/38, Intel iAPX 432 architecture and KeyKOS. Capability approaches are widely used in research systems such as EROS and Combex DARPA browser. They are used conceptually as the basis for some virtual machines, most notably Smalltalk and Java. Currently, the DARPA-funded CHERI project at University of Cambridge is working to create a modern capability machine that also supports legacy software.


=== Dynamic tainting ===
Dynamic tainting is a technique for protecting programs from illegal memory accesses. When memory is allocated, at runtime, this technique taints both the memory and the corresponding pointer using the same taint mark. Taint marks are then suitably propagated while the program executes and are checked every time a memory address m is accessed through a pointer p; if the taint marks associated with m and p differ, the execution is stopped and the illegal access is reported.
SPARC M7 processors (and higher) implement dynamic tainting in hardware. Oracle markets this feature as Silicon Secured Memory (SSM) (previously branded as Application Data Integrity (ADI)).
The lowRISC CPU design includes dynamic tainting under the name Tagged Memory.


== Measures ==
The protection level of a particular implementation may be measured by how closely it adheres to the principle of minimum privilege.


== Memory protection in different operating systems ==
Different operating systems use different forms of memory protection or separation. Although memory protection was common on most mainframes and many minicomputer systems from the 1960s, true memory separation was not used in home computer operating systems until OS/2 (and in  RISC OS) was released in 1987. On prior systems, such lack of protection was even used as a form of interprocess communication, by sending a pointer between processes. It is possible for processes to access System Memory in the Windows 9x family of operating systems.
Some operating systems that do implement memory protection include:

Atari MultiTOS (since 1991)
Microsoft Windows family from Windows NT 3.1 (1993)
Microware OS-9, as an optional module (since 1992)
OS/2 (1987)
Pharos (since 2017)
Plan9 and Inferno, created at Bell Labs as Unix successors (1992, 1995)
RISC OS (1987) (The OS memory protection is not comprehensive.)
Unix-like systems (since the late 1970s), including Solaris, Linux, BSD, Mac OS X (from 2001; now named macOS), iOS, and GNU Hurd
On Unix-like systems, the mprotect system call is used to control memory protection.


== See also ==
Memory management (operating systems)
Storage violation, for violation of memory protection


== References ==


== Notes ==


== External links ==
Intel Developer Manuals –  in-depth information on memory protection for Intel-based architectures

---page---

# Thrashing (computer science)

In computer science, thrashing occurs in a system with memory paging when a computer's real memory (RAM) resources are overcommitted, leading to a constant state of paging (swapping, i.e. moving a page to disk) and page faults, slowing most application-level processing. This causes the performance of the computer to degrade or even collapse. The situation can continue indefinitely until the user closes some running applications or the active processes free up additional virtual memory resources.
After initialization, most programs operate on a small number of code and data pages compared to the total memory the program requires. The pages most frequently accessed at any point are called the working set, which may change over time. 
When the working set is not significantly greater than the system's total number of real storage page frames, virtual memory systems work most efficiently, and an insignificant amount of computing is spent resolving page faults. As the total of the working sets grows, resolving page faults remains manageable until the growth reaches a critical point at which the number of faults increases dramatically and the time spent resolving them overwhelms the time spent on computing what the program was written to do. This condition is referred to as thrashing. Thrashing may occur on a program that randomly accesses huge data structures, as its large working set causes continual page faults that drastically slow down the system. Satisfying page faults may require freeing pages that will soon have to be re-read from disk. 
The term is also used for various similar phenomena, particularly movement between other levels of the memory hierarchy, wherein a process progresses slowly because significant time is being spent acquiring resources.
"Thrashing" is also used in contexts other than virtual memory systems –for example, to describe cache issues in computing, or silly window syndrome in networking.


== Overview ==
Memory paging and swapping works by treating a portion of secondary storage such as a computer hard disk as an additional layer of the cache hierarchy.  Paging and swapping allows processes to use more memory than is physically present in main memory. Operating systems supporting paged virtual memory assign processes a virtual address space and each process refers to addresses in its execution context by a so-called virtual address. To access data such as code or variables at that address, the process must translate the address to a physical address in a process known as virtual address translation. In effect, physical main memory becomes a cache for virtual memory, which is in general stored on disk in memory pages.
Programs are allocated a certain number of pages as needed by the operating system.  Active memory pages exist in both RAM and on disk. Inactive pages are removed from the cache and written to disk when the main memory becomes full.
If processes are utilizing all main memory and need additional memory pages, a cascade of severe cache misses known as page faults will occur, often leading to a noticeable lag in the operating system responsiveness. This process together with the futile, repetitive page swapping that occurs is known as "thrashing". This frequently leads to high, runaway CPU utilization that can grind the system to a halt. In modern computers, thrashing may occur in the paging system (if there is not sufficient physical memory or the disk access time is overly long), or in the I/O communications subsystem (especially in conflicts over internal bus access), etc.
Depending on the configuration and algorithms involved, the throughput and latency of a system may degrade by multiple orders of magnitude. Thrashing is when the CPU performs 'productive' work less and 'swapping' work more. The overall memory access time may increase since the higher level memory is only as fast as the next lower level in the memory hierarchy. The CPU is busy swapping pages so much that it cannot respond to users' programs and interrupts as much as required. Thrashing occurs when there are too many pages in memory, and each page refers to another page. Real memory reduces its capacity to contain all the pages, so it uses 'virtual memory'. When each page in execution demands that page that is not currently in real memory (RAM) it places some pages on virtual memory and adjusts the required page on RAM. If the CPU is too busy doing this task, thrashing occurs.


=== Causes ===
In paged virtual memory systems, thrashing may be caused by programs or workloads that present insufficient locality of reference: if the working set of a program or a workload cannot be effectively held within physical memory, then constant data swapping, i.e., thrashing, may occur. The term was first used during the tape operating system days to describe the sound the tapes made when data was being rapidly written to and read.
A worst case might occur on VAX processors. A single MOVL crossing a page boundary could have a source operand using a displacement deferred addressing mode, where the longword containing the operand address crosses a page boundary, and a destination operand using a displacement deferred addressing mode, where the longword containing the operand address crosses a page boundary, and the source and destination could both cross page boundaries. This single instruction references ten pages; if not all are in RAM, each will cause a page fault. The total number of pages thus involved in this particular instruction is ten, and all ten pages must be simultaneously present in memory.  If any one of the ten pages cannot be swapped in (for example to make room for any of the other pages), the instruction will fault, and every attempt to restart it will fail until all ten pages can be swapped in.
A system thrashing is often a result of a sudden spike in page demand from a small number of running programs. Swap-token is a lightweight and dynamic thrashing protection mechanism. The basic idea is to set a token in the system, which is randomly given to a process that has page faults when thrashing happens. The process that has the token is given a privilege to allocate more physical memory pages to build its working set, which is expected to quickly finish its execution and release the memory pages to other processes. A timestamp is used to hand over the tokens one by one. The first version of swap-token is implemented in Linux. The second version is called preempt swap-token. In this updated swap-token implementation, a priority counter is set for each process to track the number of swap-out pages. The token is always given to the process with a high priority, which has a high number of swap-out pages. The length of the time stamp is not a constant but is determined by the priority: the higher the number of swap-out pages of a process, the longer the time stamp for it will be.


== Other uses ==
Thrashing is best known in the context of memory and storage, but analogous phenomena occur for other resources, including:

Cache thrashing
Where main memory is accessed in a pattern that leads to multiple main memory locations competing for the same cache lines, resulting in excessive cache misses. This is most likely to be problematic for caches with associativity.
Access patterns that cause cache contention include having an overly big set of "hot" data in memory or other forms of poor locality. With associative caches, access patterns that cause key collision also cause contention. A classic example of the latter is a strided increment loop for (k = 0; k < N; k += 256) v[k] += 1;.
TLB thrashing
Where the translation lookaside buffer (TLB) acting as a cache for the memory management unit (MMU) which translates virtual addresses to physical addresses is too small for the working set of pages. TLB thrashing can occur even if instruction cache or data cache thrashing is not occurring because these are cached in different sizes. Instructions and data are cached in small blocks (cache lines), not entire pages, but address lookup is done at the page level. Thus even if the code and data working sets fit into the cache, if the working sets are fragmented across many pages, the virtual address working set may not fit into TLB, causing TLB thrashing.
TLB thrashing can also occur when excess collisions happen in its internal associative memory (i.e. locations in memory compete for a few specific slots). This situation can happen when binary searching a large (≥ 512 KiB) buffer with a size that is an exact power of two. It can be prevented by spreading out the "key" for the internal associative memory (usually the lower bits of the address) by reducing access alignment; in binary search an offset 31⁄64 split can be used. This is an unusual case where excess alignment hurts performance.
Heap thrashing
Frequent garbage collection, due to failure to allocate memory for an object, due to insufficient free memory or insufficient contiguous free memory due to memory fragmentation is referred to as heap thrashing.
Process thrashing
A similar phenomenon occurs for processes: when the process working set cannot be coscheduled, i.e. such that not all interacting processes are scheduled to run at the same time, they experience "process thrashing" due to being repeatedly scheduled and unscheduled, progressing only slowly.


== See also ==

Page replacement algorithm – Algorithm for virtual memory implementation
Congestion collapse – Reduced quality of service due to high network trafficPages displaying short descriptions of redirect targets
Resource contention – In computing, a conflict over access to a shared resource
Out of memory – State of computer where no additional memory can be allocated
Software aging – Tendency of software to fail due to external changes or prolonged operation


== References ==

---page---

# Swap (computer programming)

In computer programming, the act of swapping two variables mutually exchanges their values. Usually, this is done with the data in memory. For example, in a program, two variables may be defined thus (in pseudocode):

After swap() is performed, x will contain the value 0 and y will contain 1; their values have been exchanged. This operation may be generalized to other types of values, such as strings and aggregated data types. Comparison sorts use  swaps to change the positions of data.
In many programming languages the swap function is built-in. In C++ overloads are provided allowing std::swap to exchange some large structures in O(1) time.


== Using a temporary variable ==

The simplest and probably most widely used method to swap two variables is to use a third temporary variable:

define swap (x, y)
    temp := x
    x := y
    y := temp

While this is conceptually simple and in many cases the only convenient way to swap two variables, it uses extra memory. Although this should not be a problem in most applications, the sizes of the values being swapped may be huge (which means the temporary variable may occupy a lot of memory as well), or the swap operation may need to be performed many times, as in sorting algorithms.
In addition, swapping two variables in object-oriented languages such as C++ may involve one call to the class constructor and destructor for the temporary variable, and three calls to the copy constructor. Some classes may allocate memory in the constructor and deallocate it in the destructor, thus creating expensive calls to the system. Copy constructors for classes containing a lot of data, e.g. in an array, may even need to copy the data manually.


== XOR swap ==

XOR swap uses the XOR operation to swap two numeric variables. It is generally touted to be faster than the naive method mentioned above; however it does have disadvantages. XOR swap is generally used to swap low-level data types, like integers. However, it is, in theory, capable of swapping any two values which can be represented by fixed-length bitstrings.


== Swap through addition and subtraction ==

This method swaps two variables by adding and subtracting their values. This is rarely used in practical applications, mainly because:

It can only swap numeric variables; it may not be possible or logical to add or subtract complex data types, like containers.
When swapping variables of a fixed size, arithmetic overflow becomes an issue.
It does not work generally for floating-point values, because floating-point arithmetic is non-associative.


== Swapping containers ==
Containers which allocate memory from the heap using pointers may be swapped in a single operation, by swapping the pointers alone. This is usually found in programming languages supporting pointers, like C or C++. The C++ Standard Library overloads its built-in std::swap(x, y) function to exchange the contents of containers efficiently this way.
As pointer variables are usually of a fixed size (e.g., most desktop computers have pointers 64 bits long), and they are numeric, they can be swapped quickly using XOR swap.


== Parallel assignment ==
Some languages, like Ruby, Julia or Python support parallel assignments, which simplifies the notation for swapping two variables: a, b = b, a. This is shorthand for an operation involving an intermediate data structure: in Python and Julia, a tuple; in Ruby, an array.
JavaScript 6+ supports destructuring operators which do the same thing: [a, b] = [b, a];.


== Function swap ==
Here, two globally scoped variables are passed by value through a function, eliminating the need for a temporary storage variable.


== Facilitation of swapping in modern computers ==


=== Dedicated instructions ===
Because of the many applications of swapping data in computers, most processors now provide the ability to swap variables directly through built-in instructions. x86 processors, for example, include an XCHG instruction to swap two registers directly without requiring that a third temporary register is used. A compare-and-swap instruction is even provided in some processor architectures, which compares and conditionally swaps two registers. This is used to support mutual exclusion techniques.
XCHG may not be as efficient as it seems. For example, in x86 processors, XCHG will implicitly lock access to any operands in memory to ensure the operation is atomic, and so may not be efficient when swapping memory. Such locking is important when it is used to implement thread-safe synchronization, as in mutexes. However, an XCHG is usually the fastest way to swap two machine-size words residing in registers. Register renaming may also be used to swap registers efficiently.


=== Parallel execution ===
With the advent of instruction pipelining in modern computers and multi-core processors facilitating parallel computing, two or more operations can be performed at once. This can speed up the swap using temporary variables and give it an edge over other algorithms. For example, the XOR swap algorithm requires sequential execution of three instructions. However, using two temporary registers, two processors executing in parallel can swap two variables in two clock cycles:

Step 1
 Processor 1: temp_1 := X
 Processor 2: temp_2 := Y

Step 2
 Processor 1: X := temp_2
 Processor 2: Y := temp_1

More temporary registers are used, and four instructions are needed instead of three. In any case, in practice this could not be implemented in separate processors, as it violates Bernstein's conditions for parallel computing. It would be infeasible to keep the processors sufficiently in sync with one another for this swap to have any significant advantage over traditional versions. However, it can be used to optimize swapping for a single processor with multiple load/store units.


== References ==

---page---

# Memory segmentation

Memory segmentation is an operating system memory management technique of dividing a computer's primary memory into segments or sections. In a computer system using segmentation, a reference to a memory location includes a value that identifies a segment and an offset (memory location) within that segment. Segments or sections are also used in object files of compiled programs when they are linked together into a program image and when the image is loaded into memory.
Segments usually correspond to natural divisions of a program such as individual routines or data tables, so segmentation is generally more visible to the programmer than paging alone. Segments may be created for program modules, or for classes of memory usage such as code segments and data segments. Certain segments may be shared between programs.
Segmentation was originally invented as a method by which system software could isolate software processes (tasks) and data they are using. It was intended to increase reliability of the systems running multiple processes simultaneously.


== Hardware implementation ==
In a system using segmentation, computer memory addresses consist of a segment id and an offset within the segment. A hardware memory management unit (MMU) is responsible for translating the segment and offset into a physical address, and for performing checks to make sure the translation can be done and that the reference to that segment and offset is permitted.
Each segment has a length and set of permissions (for example, read, write, execute) associated with it. A process is only allowed to make a reference into a segment if the type of reference is allowed by the permissions, and if the offset within the segment is within the range specified by the length of the segment. Otherwise, a hardware exception such as a segmentation fault is raised.
Segments may also be used to implement virtual memory. In this case each segment has an associated flag indicating whether it is present in main memory or not. If a segment is accessed that is not present in main memory, a "segment not present" exception is raised, and the operating system will read the segment into memory from secondary storage.
Segmentation is one method of implementing memory protection. Paging is another, and they can be combined. The size of a memory segment is generally not fixed and may be as small as a single byte.
Segmentation has been implemented several ways on various hardware, with or without paging. Intel x86 memory segmentation does not fit either model and is discussed separately below, and also in greater detail in a separate article.


=== Segmentation without paging ===
Associated with each segment is information that indicates where the segment is located in memory— the segment base. When a program references a memory location, the offset is added to the segment base to generate a physical memory address.
An implementation of virtual memory on a system using segmentation without paging requires that entire segments be swapped back and forth between main memory and secondary storage. When a segment is swapped in, the operating system has to allocate enough contiguous free memory to hold the entire segment. Often memory fragmentation results if there is not enough contiguous memory even though there may be enough in total.


=== Segmentation with paging ===
Instead of a memory location, the segment information includes the address of a page table for the segment.
When a program references a memory location the offset is translated to a memory address using the page table. A segment can be extended by allocating another memory page and adding it to the segment's page table.
An implementation of virtual memory on a system using segmentation with paging usually only moves individual pages back and forth between main memory and secondary storage, similar to a paged non-segmented system. Pages of the segment can be located anywhere in main memory and need not be contiguous. This usually results in a reduced amount of input/output between primary and secondary storage and reduced memory fragmentation.


== History ==
The Burroughs Corporation B5000 computer was one of the first to implement segmentation, and "perhaps the first commercial computer to provide virtual memory" based on segmentation. The B5000 is equipped with a segment information table called the Program Reference Table (PRT) which is used to indicate whether the corresponding segment resides in the main memory, to maintain the base address and the size of the segment. The later B6500 computer also implemented segmentation; a version of its architecture is still in use today on the Unisys ClearPath Libra servers.
The GE 645 computer, a modification of the GE-635 with segmentation and paging support added, was designed in 1964 to support Multics.
The Intel iAPX 432, begun in 1975, attempted to implement a true segmented architecture with memory protection on a microprocessor.
The 960MX version of the Intel i960 processors supported load and store instructions with the source or destination being an "access descriptor" for an object, and an offset into the object, with the access descriptor being in a 32-bit register and with the offset computed from a base offset in the next register and from an additional offset and, optionally, an index register specified in the instruction. An access descriptor contains permission bits and a 26-bit object index; the object index is an index into a table of object descriptors, giving an object type, an object length, and a physical address for the object's data, a page table for the object, or the top-level page table for a two-level page table for the object, depending on the object type.
Prime, Stratus, Apollo, IBM System/38, and IBM AS/400 (including IBM i) computers use memory segmentation.


== Examples ==


=== Burroughs large system architectures ===

Burroughs introduced segmentation on the B5000, followed by the compatible B5500 and B5700.
The later B6500 replaced the Program Reference Table (PRT) with a Saguaro stack, changed control word formats, changed descriptor formats and changed the mechanism for referring to a control word or descriptor.


==== B5000, B5500 and B5700 ====

Words in the B5000, B5500 and B5700 are 48 bits long. Descriptors have the uppermost bit set in the word. They reside in either the Program Reference Table (PRT) or the stack, and contain a presence bit indicating whether the data are present in memory. There are distinct data and program descriptors.


==== B6500, B7500 and successors ====

Words in the B6500 and its successors have 48 bits of data and 3 tag bits. The tag bits indicate the type of data contained in the word; there are several descriptor types, indicated by different tag bit values. Control words and descriptors reside in the Saguaro stack. Array segments may be paged.
The line includes the B6500, B6700, B7700, B6800, B6900, B5900, the A-series Burroughs and Unisys machines, and the current Clearpath MCP systems (Libra). While there have been a few enhancements over the years, particularly hardware advances, the architecture has changed little. The segmentation scheme has remained the same, see Segmented memory.


=== Multics architectures ===


=== S/370 architecture ===
In the IBM System/370 models with virtual storage (DAT) and 24-bit addresses, control register 0 specifies a segment size of either 64 KiB or 1 MiB and a page size of either 2 KiB or 4 KiB; control register 1 contains a Segment Table Designator (STD), which specifies the length and real address of the segment table. Each segment table entry contains a page table location, a page table length and an invalid bit. IBM later expanded the address size to 31 bits and added two bits to the segment table entries:

Segment-protection bit
Segment is read-only
Common-segment bit
The segment is shared between address spaces; this bit is set to optimize TLB use
Each of IBM's DAT implementations includes a translation cache, which IBM called a Translation Lookaside Buffer (TLB). While Principles of Operation discusses the TLB in general terms, the details are not part of the architecture and vary from model to model.
Starting with the 3031, 3032, and 3033 processor complexes, IBM offered a feature called Dual-address Space (DAS), which allows a program to switch between the translation tables for two address spaces, referred to as primary address space (CR1) and secondary address space (CR7), and to move data between the address spaces subject to protection key. DAS supports a translation table to convert a 16-bit address space number (ASN) to an STD, with privileged instructions to load the STD into CR1 (primary) or CR7 (secondary).


=== x86 architecture ===

Early x86 processors, beginning with the Intel 8086, provide crude memory segmentation and no memory protection (every byte of each segment is always available to any program.) The 16-bit segment registers allow for 65,536 segments; each segment begins at a fixed offset equal to 16 times the segment number; the segment starting address granularity is 16 bytes. Each segment grants read-write access to 64 KiB (65,536 bytes) of address space (this limit is set by the 16-bit PC and SP registers; the processor does no bounds checking). Offset+address exceeding 0xFFFFF wraps around to 0x00000. Each 64 KiB segment overlaps the next 4,095 segments; each physical address can be denoted by 4,096 segment–offset pairs. This scheme can address only 1 MiB (1024 KiB) of physical memory (and memory-mapped i/o). (Optional expanded memory hardware can add bank-switched memory under software control.) Intel retroactively named the sole operating mode of these x86 CPU models "real mode".
The Intel 80286 and later processors add "286 protected mode", which retains 16-bit addressing, and adds segmentation (without paging) and per-segment memory protection. For backward compatibility, all x86 CPUs start up in "real mode", with the same fixed overlapping 64 KiB segments, no memory protection, only 1 MiB physical address space, and some subtle differences (high memory area, unreal mode). In order to use its full 24-bit (16 MiB) physical address space and advanced MMU features, an 80286 or later processor must be switched into "protected mode" by software, usually the operating system or a DOS extender. If a program does not use the segment registers, or only puts values into them that it receives from the operating system, then identical code can run in real mode or protected mode, but most real-mode software computes new values for the segment registers, breaking this compatibility.
The Intel i386 and later processors add "386 protected mode", which uses 32-bit addressing, retains segmentation, and adds memory paging. In these processors, the segment table, rather than pointing to a page table for the segment, contains the segment address in linear memory. When paging is enabled, addresses in linear memory are then mapped to physical addresses using a separate page table. Most operating systems did not use the segmentation capability, opting to keep the base address in all segment registers equal to 0 at all times and provide per-page memory protection and swapping using only paging.  Some use the CS register to provide executable-space protection on processors lacking the NX bit or use the FS or GS registers to access thread-local storage.
The x86-64 architecture does not support segmentation in "long mode" (64-bit mode). Four of the segment registers: CS, SS, DS, and ES are forced to 0, and the limit to 264. The segment registers FS and GS can still have a nonzero base address. This allows operating systems to use these segments for special purposes such as thread-local storage.


== See also ==
BSS Segment
Data segment
Flat memory model
Memory management (operating systems)
Segmentation fault
Virtual address space
Virtual memory
x86 memory segmentation


== Notes ==


== References ==


== External links ==
IA-32 Intel Architecture Software Developer’s Manual Volume 3A: System Programming Guide. http://www.intel.com/products/processor/manuals/index.htm.
Operating Systems: Internals and Design Principles by William Stallings. Publisher: Prentice Hall. ISBN 0-13-147954-7. ISBN 978-0-13-147954-8.

---page---

# Page (computer memory)

A page, memory page, or virtual page is a fixed-length contiguous block of virtual memory, described by a single entry in a page table. It is the smallest unit of data for memory management in an operating system that uses virtual memory. Similarly, a page frame is the smallest fixed-length contiguous block of physical memory into which memory pages are mapped by the operating system.
A transfer of pages between main memory and an auxiliary store, such as a hard disk drive, is referred to as paging or swapping.


== Explanation ==
Computer memory is divided into pages so that information can be found more quickly.
The concept is named by analogy to the pages of a printed book. If a reader wanted to find, for example, the 5,000th word in the book, they could count from the first word. This would be time-consuming. It would be much faster if the reader had a listing of how many words are on each page. From this listing they could determine which page the 5,000th word appears on, and how many words to count on that page. This listing of the words per page of the book is analogous to a page table of a computer file system.


== Page size ==


=== Page size trade-off ===

Page size is usually determined by the processor architecture. Traditionally, pages in a system had uniform size, such as 4,096 bytes. However, processor designs often allow two or more, sometimes simultaneous, page sizes due to its benefits. There are several points that can factor into choosing the best page size.


==== Page table size ====
A system with a smaller page size uses more pages, requiring a page table that occupies more space. For example, if a 232 virtual address space is mapped to 4 KiB (212 bytes) pages, the number of virtual pages is 220 = (232 / 212). However, if the page size is increased to 32 KiB (215 bytes), only 217 pages are required. A multi-level paging algorithm can decrease the memory cost of allocating a large page table for each process by further dividing the page table up into smaller tables, effectively paging the page table.


==== TLB usage ====
Since every access to memory must be mapped from virtual to physical address, reading the page table every time can be quite costly. Therefore, a very fast kind of cache, the translation lookaside buffer (TLB), is often used. The TLB is of limited size, and when it cannot satisfy a given request (a TLB miss) the mapping must be fetched from the page table (either by hardware, firmware, or software, depending on the architecture) for the correct mapping. Larger page sizes mean that a TLB cache of the same size can keep track of larger amounts of memory, which avoids costly TLB misses.


==== Internal fragmentation ====
Rarely do processes require the use of an exact number of pages. As a result, the last page will likely only be partially full, wasting some amount of memory. Larger page sizes lead to a large amount of wasted memory, as more potentially unused portions of memory are loaded into the main memory. Smaller page sizes ensure a closer match to the actual amount of memory required in an allocation.
As an example, assume the page size is 1024 B. If a process allocates 1025 B, two pages must be used, resulting in 1023 B of unused space (where one page fully consumes 1024 B and the other only 1 B).


==== Disk access ====
When transferring from a rotational disk, much of the delay is caused by seek time, the time it takes to correctly position the read/write heads above the disk platters. Because of this, large sequential transfers are more efficient than several smaller transfers. Transferring the same amount of data from disk to memory often requires less time with larger pages than with smaller pages.


=== Getting page size programmatically ===
Most operating systems allow programs to discover the page size at runtime. This allows programs to use memory more efficiently by aligning allocations to this size and reducing overall internal fragmentation of pages.


==== Unix-like operating systems ====
Unix-like systems may use the system function sysconf(), as illustrated in the following example written in the C programming language.

In many Unix-like systems, the command-line utility getconf can be used.
For example, getconf PAGESIZE will return the page size in bytes.


==== Windows-based operating systems ====
Win32-based operating systems, such as those in the Windows 9x and Windows NT families, may use the system function GetSystemInfo() from kernel32.dll.


=== Multiple page sizes ===
Some instruction set architectures can support multiple page sizes, including pages significantly larger than the standard page size. The available page sizes depend on the instruction set architecture, processor type, and operating (addressing) mode. The operating system selects one or more sizes from the sizes supported by the architecture. Note that not all processors implement all defined larger page sizes. This support for larger pages (known as "huge pages" in Linux, "superpages" in FreeBSD, and "large pages" in Microsoft Windows and IBM AIX terminology) allows for "the best of both worlds", reducing the pressure on the TLB cache (sometimes increasing speed by as much as 15%) for large allocations while still keeping memory usage at a reasonable level for small allocations.

Starting with the Pentium Pro, and the AMD Athlon, x86 processors support 4 MiB pages (called Page Size Extension) (2 MiB pages if using PAE) in addition to their standard 4 KiB pages; newer x86-64 processors, such as AMD's newer AMD64 processors and Intel's Westmere and later Xeon processors can use 1 GiB pages in long mode. IA-64 supports as many as eight different page sizes, from 4 KiB up to 256 MiB, and some other architectures have similar features.  
Larger pages, despite being available in the processors used in most contemporary personal computers, are not in common use except in large-scale applications, the applications typically found in large servers and in computational clusters, and in the operating system itself. Commonly, their use requires elevated privileges, cooperation from the application making the large allocation (usually setting a flag to ask the operating system for huge pages), or manual administrator configuration; operating systems commonly, sometimes by design, cannot page them out to disk.
However, SGI IRIX has general-purpose support for multiple page sizes. Each individual process can provide hints and the operating system will automatically use the largest page size possible for a given region of address space. Later work  proposed transparent operating system support for using a mix of page sizes for unmodified applications through preemptible reservations, opportunistic promotions, speculative demotions, and fragmentation control.
Linux has supported huge pages on several architectures since the 2.6 series via the hugetlbfs filesystem and without hugetlbfs since 2.6.38.  Windows Server 2003 (SP1 and newer), Windows Vista and Windows Server 2008 support huge pages under the name of large pages. Windows 2000 and Windows XP support large pages internally, but do not expose them to applications. Reserving large pages under Windows requires a corresponding right that the system administrator must grant to the user because large pages cannot be swapped out under Windows. Beginning with version 9, Solaris supports large pages on SPARC and x86.
FreeBSD 7.2-RELEASE features superpages. Note that until recently in Linux, applications needed to be modified in order to use huge pages. The 2.6.38 kernel introduced support for transparent use of huge pages. On Linux kernels supporting transparent huge pages, as well as FreeBSD and Solaris, applications take advantage of huge pages automatically, without the need for modification.


== See also ==
Grant table
Page fault
Page table
Memory paging
Virtual memory
Zero page - a (often 256-bytes large) memory area at the very start of a processor's address room
Zero page (CP/M) - a 256-byte data structure at the start of a program


== References ==


== Further reading ==
Dandamudi, Sivarama P. (2003). Fundamentals of Computer Organization and Design (1st ed.). Springer. pp. 740–741. ISBN 0-387-95211-X.

---page---

# Working set

Working set is a concept in computer science which defines the amount of memory that a process requires in a given time interval.


== Definition ==
Peter Denning (1968) defines "the working set of information W(t,τ) of a process at time t to be the collection of information referenced by the process during the process time interval (t−τ,t)".
Typically the units of information in question are considered to be memory pages. This is suggested to be an approximation of the set of pages that the process will access in the future (say during the next τ time units), and more specifically is suggested to be an indication of what pages ought to be kept in main memory to allow most progress to be made in the execution of that process.


== Rationale ==
The effect of the choice of what pages to be kept in main memory (as distinct from being paged out to auxiliary storage) is important: if too many pages of a process are kept in main memory, then fewer other processes can be ready at any one time. If too few pages of a process are kept in main memory, then its page fault frequency is greatly increased and the number of active (non-suspended) processes currently executing in the system approaches zero.
The working set model states that a process can be in RAM if and only if all of the pages that it is currently using (often approximated by the most recently used pages) can be in RAM. The model is an all or nothing model, meaning if the pages it needs to use increases, and there is no room in RAM, the process is swapped out of memory to free the memory for other processes to use.
Often a heavily loaded computer has so many processes queued up that, if all the processes were allowed to run for one scheduling time slice, they would refer to more pages than there is RAM, causing the computer to "thrash".
By swapping some processes from memory, the result is that processes—even processes that were temporarily removed from memory—finish much sooner than they would if the computer attempted to run them all at once. The processes also finish much sooner than they would if the computer only ran one process at a time to completion since it allows other processes to run and make progress during times that one process is waiting on the hard drive or some other global resource.
In other words, the working set strategy prevents thrashing while keeping the degree of multiprogramming as high as possible. Thus it optimizes CPU utilization and throughput.


== Implementation ==
The main hurdle in implementing the working set model is keeping track of the working set. The working set window is a moving window. At each memory reference a new reference appears at one end and the oldest reference drops off the other end. A page is in the working set if it is referenced in the working set window.
To avoid the overhead of keeping a list of the last k referenced pages, the working set is often implemented by keeping track of the time t of the last reference, and considering the working set to be all pages referenced within a certain period of time.
The working set isn't a page replacement algorithm, but page-replacement algorithms can be designed to only remove pages that aren't in the working set for a particular process. One example is a modified version of the clock algorithm called WSClock.


== Variants ==
Working set can be divided into code working set and data working set. This distinction is important when code and data are separate at the relevant level of the memory hierarchy, as if either working set does not fit in that level of the hierarchy, thrashing will occur. In addition to the code and data themselves, on systems with virtual memory, the memory map (of virtual memory to physical memory) entries of the pages of the working set must be cached in the translation lookaside buffer (TLB) for the process to progress efficiently. This distinction exists because code and data are cached in small blocks (cache lines), not entire pages, but address lookup is done at the page level. Thus even if the code and data working sets fit into cache, if the working sets are split across many pages, the virtual address working set may not fit into TLB, causing TLB thrashing.
Analogs of working set exist for other limited resources, most significantly processes. If a set of processes requires frequent interaction between multiple processes, then it has a process working set that must be coscheduled in order to progress:

parallel programs have a process working set that must be coscheduled (scheduled for execution simultaneously) for the parallel program to make progress.
If the processes are not scheduled simultaneously – for example, if there are two processes but only one core on which to execute them – then the processes can only advance at the rate of one interaction per time slice.
Other resources include file handles or network sockets – for example, copying one file to another is most simply done with two file handles: one for input, one for output, and thus has a "file handle working set" size of two. If only one file handle is available, copying can still be done, but requires acquiring a file handle for the input, reading from it (say into a buffer), releasing it, then acquiring a file handle for the output, writing to it, releasing it, then acquiring the input file handle again and repeating. Similarly a server may require many sockets, and if it is limited would need to repeatedly release and re-acquire sockets. Rather than thrashing, these resources are typically required for the program, and if it cannot acquire enough resources, it simply fails.


== See also ==
Locality of reference
Resident set size
Working set size


== References ==

---page---

# Fragmentation (computing)

In computer storage, fragmentation is a phenomenon in the computer system which involves the distribution of data into smaller pieces so that storage space, such as computer memory or a hard drive, is used inefficiently, reducing capacity or performance and often both. The exact consequences of fragmentation depend on the specific system of storage allocation in use and the particular form of fragmentation. In many cases, fragmentation leads to storage space being "wasted", and programs will tend to run inefficiently due to the shortage of memory.


== Basic principle ==
In main memory fragmentation, when a computer program requests blocks of memory from the computer system, the blocks are allocated in chunks. When the computer program is finished with a chunk, it can free it back to the system, making it available to later be allocated again to another or the same program. The size and the amount of time a chunk is held by a program vary. During its lifespan, a computer program can request and free many chunks of memory. 
Fragmentation can occur when a block of memory is requested by a program and is allocated to that program, but the program has not freed (uncommitted) it. This leads to theoretically "available", unused memory being marked as allocated - which reduces the amount of globally available memory, making it harder for programs to request and access memory.
When a program is started, the free memory areas are long and contiguous. Over time and with use, the long contiguous regions become fragmented into smaller and smaller contiguous areas. Eventually, it may become impossible for the program to obtain large contiguous chunks of memory.


== Types ==
Fragmentation occurs whenever a piece of data or free space is broken into several pieces. Fragmentation is often accepted in return for improvements in speed or simplicity. Analogous phenomena occur for other resources such as processors; see below.


=== Memory ===
Memory fragmentation can be internal and external. Internal fragmentation occurs when memory allocation provides more space than needed, causing waste of free space. External fragmentation occurs when free memory is fragmented, preventing newer, larger blocks from being allocated.
In modern operating systems, the program receives fixed-size pages which it then allocates among different parts of itself (often by an allocator such as malloc). As a result, there are two layers of allocation that may each result in their own internal and external fragmentation: on the level of the memory allocator (e.g. malloc) and on the level of pages. (Older operating systems might not use pages, but programs still tend to use a two-level system to avoid excessive calls to the OS.)


==== Internal fragmentation ====

Due to the rules governing memory allocation, more computer memory is sometimes allocated than is needed. When this happens, the excess memory goes to waste. In this scenario, the unusable memory, known as slack space, is contained within an allocated region. This arrangement, termed fixed partitions, suffers from inefficient memory use - any process, no matter how small, occupies an entire partition. This waste is called internal fragmentation.

Memory paging creates internal fragmentation because an entire page frame (typically 4–64 KiB) will be allocated whether or not that much storage is needed.
malloc and similar allocators tend to provide a degree of alignment, so that memory can only be provided to programs in chunks (usually a multiple of 4 bytes). As a result if a program requests perhaps 29 bytes, it will actually get a chunk of 32 bytes.
Internal fragmentation on the allocator level is very difficult to reclaim after it has occurred; usually the best way to remove it is with a design change. For example, in dynamic memory allocation, memory pools drastically cut internal fragmentation by spreading the space overhead over a larger number of objects.
Internal fragmentation on the page level (which is external fragmentation on the allocator level) can be reclaimed by moving allocated blocks. This requires editing pointers to reflect the moving of allocated blocks, which is difficult for non-garbage-collected languages. Compacting garbage collectors perform pointer fixups as it compacts the virtual address space.


==== External fragmentation ====
External fragmentation arises when free memory is separated into small blocks and is interspersed by allocated memory. It is a weakness of certain storage allocation algorithms when they fail to order memory used by programs efficiently. The result is that, although free storage is available, it is effectively unusable because it is divided into pieces that are too small individually to satisfy the demands of the application. The term "external" refers to the fact that the unusable storage is outside the allocated regions.
For example, consider a situation wherein a program allocates three continuous blocks of memory and then frees the middle block. The memory allocator can use this free block of memory for future allocations. However, it cannot use this block if the memory to be allocated is larger in size than this free block.

External fragmentation on the page level can be reclaimed by an application's own allocator or garbage collector as it frees up and hands back (uncommits) pages to the OS.
External fragmentation on the page level can also be reclaimed by the operating system by moving pages in the physical address space and editing the page table to match. This is called page migration. The application is oblivious to the process because the virtual memory addresses remain unchanged.


=== File systems ===

Data fragmentation occurs when a collection of data in memory is broken up into many pieces that are not close together. File systems interact with block devices such as disk drives. These devices manage data in small, fixed-sized units called blocks or sectors, which file systems abstract into their own units called blocks or clusters.
When a file system is created, there is free space to store file blocks together contiguously. This allows for rapid sequential file reads and writes. However, as files are added, removed, and changed in size, the free space becomes externally fragmented, leaving only small holes in which to place new data. This is external fragmentation. File systems differ from memory in that they are designed with fragmentation in mind: when a new file is written, or when an existing file is extended, the operating system puts the new data in new non-contiguous groups of clusters (extents) to fit into the available holes. The new data blocks are necessarily scattered, slowing access due to seek time and rotational latency of the read/write head, and incurring additional overhead to manage additional locations. This is called file system fragmentation. The effect is even worse if a file which is divided into many small pieces is deleted, because this leaves similarly small regions of free space.
When writing a new file of a known size, if there are any empty holes that are larger than that file, the operating system can avoid data fragmentation by putting the file into any one of those holes. There are a variety of algorithms for selecting which of those potential holes to put the file; each of them is a heuristic approximate solution to the bin packing problem. The "best fit" algorithm chooses the smallest hole that is big enough. The "worst fit" algorithm chooses the largest hole. The "first-fit algorithm" chooses the first hole that is big enough. The "next fit" algorithm keeps track of where each file was written.
The "next fit" algorithm is faster than "first fit," which is in turn faster than "best fit," which is the same speed as "worst fit".
Just as compaction can eliminate external fragmentation, (external)  data fragmentation can be eliminated by rearranging data storage so that related pieces are close together. For example, the primary job of a defragmentation tool is to rearrange blocks on disk so that the blocks of each file are contiguous. Most defragmenting utilities also attempt to reduce or eliminate free space fragmentation. Some moving garbage collectors, utilities that perform automatic memory management, will also move related objects close together (this is called compacting) to improve cache performance.
Four kinds of systems never experience (external) data fragmentation—they always store every file contiguously. All four kinds have significant disadvantages compared to systems that allow at least some temporary data fragmentation:

Simply write each file contiguously. If there isn't already enough contiguous free space to hold the file, the system immediately fails to store the file—even when there are many little bits of free space from deleted files that add up to more than enough to store the file.
If there isn't already enough contiguous free space to hold the file, use a copying collector to convert many little bits of free space into one contiguous free region big enough to hold the file. This takes a lot more time than breaking the file up into fragments and putting those fragments into the available free space.
Write the file into any free block, through fixed-size blocks storage. If a programmer picks a fixed block size too small, the system immediately fails to store some files—files larger than the block size—even when many free blocks add up to more than enough to store the file. If a programmer picks a block size too big, a lot of space is wasted on internal fragmentation.
Some systems avoid dynamic allocation entirely, pre-storing (contiguous) space for all possible files they will need—for example, MultiFinder pre-allocates a chunk of RAM to each application as it was started according to how much RAM that application's programmer claimed it would need.
Internal fragmentation is rarely a concern on file systems because it does not have a global effect of making the entire file system's file allocation worse. It does cause a storage space overhead and slow down access to large sets of affected small files (the set as a whole can be considered "fragmented"). To combat this problem, filesystems such as ext4 and btrfs have an inline data or inline file feature to forgo allocating a cluster for these files and instead directly store it in the inode (file record).


=== Comparison ===
Compared to external fragmentation, overhead and internal fragmentation account for little loss in terms of wasted memory and reduced performance. It is defined as:

External Memory Fragmentation = 1 - ⁠Largest Block Of Free Memory/Total Free Memory⁠
Fragmentation of 0% means that all the free memory is in a single large block; fragmentation is 90% (for example) when 100 MB of free memory is present but the largest free block of memory for storage is just 10 MB.
External fragmentation tends to be less of a problem in file systems than in primary memory (RAM) storage systems, because programs usually require their RAM storage requests to be fulfilled with contiguous blocks, but file systems typically are designed to be able to use any collection of available blocks (fragments) to assemble a file which logically appears contiguous. Therefore, if a highly fragmented file or many small files are deleted from a full volume and then a new file with size equal to the newly freed space is created, the new file will simply reuse the same fragments that were freed by the deletion. If what was deleted was one file, the new file will be just as fragmented as that old file was, but in any case there will be no barrier to using all the (highly fragmented) free space to create the new file. In RAM, on the other hand, the storage systems used often cannot assemble a large block to meet a request from small noncontiguous free blocks, and so the request cannot be fulfilled and the program cannot proceed to do whatever it needed that memory for (unless it can reissue the request as a number of smaller separate requests).


== Problems ==


=== Storage failure ===
The most severe problem caused by fragmentation is causing a process or system to fail due to premature resource exhaustion: if a contiguous block must be stored and cannot be stored, failure occurs. Fragmentation causes this to occur even if there is enough of the resource, but not a contiguous amount. For example, if a computer has 4 GiB of memory and 2 GiB are free, but the memory is fragmented in an alternating sequence of 1 MiB used, 1 MiB free, then a request for 1 contiguous GiB of memory cannot be satisfied even though 2 GiB total are free.
In order to avoid this, the allocator may, instead of failing, trigger a defragmentation (or memory compaction cycle) or other resource reclamation, such as a major garbage collection cycle, in the hope that it will then be able to satisfy the request. This allows the process to proceed, but can severely impact performance.


=== Performance degradation ===
Fragmentation causes performance degradation for a number of reasons. Most basically, fragmentation increases the work required to allocate and access a resource. For example, on a hard drive or tape drive, sequential data reads are very fast, but seeking to a different address is slow, so reading or writing a fragmented file requires numerous seeks and is thus much slower, in addition to causing greater wear on the device.
Further, if a resource is not fragmented, allocation requests can simply be satisfied by returning a single block from the start of the free area.
However, if it is fragmented, the request requires either searching for a large enough free block, which may take a long time, or fulfilling the request by several smaller blocks (if this is possible), which results in this allocation being fragmented, and requiring additional overhead to manage the several pieces.
A subtler problem is that fragmentation may prematurely exhaust a cache, causing thrashing, due to caches holding blocks, not individual data. For example, suppose a program has a working set of 256 KiB, and is running on a computer with a 256 KiB cache (say L2 instruction+data cache), so the entire working set fits in cache and thus executes quickly, at least in terms of cache hits. Suppose further that it has 64 translation lookaside buffer (TLB) entries, each for a 4 KiB page: each memory access requires a virtual-to-physical translation, which is fast if the page is in cache (here TLB). If the working set is unfragmented, then it will fit onto exactly 64 pages (the page working set will be 64 pages), and all memory lookups can be served from cache. However, if the working set is fragmented, then it will not fit into 64 pages, and execution will slow due to thrashing: pages will be repeatedly added and removed from the TLB during operation. Thus cache sizing in system design must include a margin to account for fragmentation.
Memory fragmentation is one of the most severe problems faced by system managers. Over time, it leads to degradation of system performance. Eventually, memory fragmentation may lead to complete loss of (application-usable) free memory.
Memory fragmentation is a kernel programming level problem. During real-time computing of applications, fragmentation levels can reach as high as 99%, and may lead to system crashes or other instabilities. This type of system crash can be difficult to avoid, as it is impossible to anticipate the critical rise in levels of memory fragmentation. However, while it may not be possible for a system to continue running all programs in the case of excessive memory fragmentation, a well-designed system should be able to recover from the critical fragmentation condition by moving in some memory blocks used by the system itself to enable consolidation of free memory into fewer, larger blocks, or, in the worst case, by terminating some programs to free their memory and then defragmenting the resulting sum total of free memory. This will at least avoid a true crash in the sense of system failure and allow the system to continue running some programs, save program data, etc.
Fragmentation is a phenomenon of system software design; different software will be susceptible to fragmentation to different degrees, and it is possible to design a system that will never be forced to shut down or kill processes as a result of memory fragmentation.


== Analogous phenomena ==
While fragmentation is best known as a problem in memory allocation, analogous phenomena occur for other resources, notably processors. For example, in a system that uses time-sharing for preemptive multitasking, but that does not check if a process is blocked, a process that executes for part of its time slice but then blocks and cannot proceed for the remainder of its time slice wastes time because of the resulting internal fragmentation of time slices. More fundamentally, time-sharing itself causes external fragmentation of processes due to running them in fragmented time slices, rather than in a single unbroken run. The resulting cost of process switching and increased cache pressure from multiple processes using the same caches can result in degraded performance.
In concurrent systems, particularly distributed systems, when a group of processes must interact to progress, if the processes are scheduled at separate times or on separate machines (fragmented across time or machines), the time spent waiting for each other or in communicating with each other can severely degrade performance. Instead, performant systems require coscheduling of the group.
Some flash file systems have several different kinds of internal fragmentation involving "dead space" and "dark space".


== See also ==
Defragmentation
File system fragmentation
Memory management
Memory management (operating systems)
Block (data storage)
Data cluster


== References ==


== Sources ==
http://www.edn.com/design/systems-design/4333346/Handling-memory-fragmentation
http://www.sqlservercentral.com/articles/performance+tuning/performancemonitoringbyinternalfragmentationmeasur/2014/
C++ Footprint and Performance Optimization, R. Alexander; G. Bensley, Sams Publisher, First edition, Page no:128, ISBN no:9780672319044
Ibid, Page no:129

---page---

# CPU cache

A CPU cache is a hardware cache used by the central processing unit (CPU) of a computer to reduce the average cost (time or energy) to access data from the main memory. A cache is a smaller, faster memory, located closer to a processor core, which stores copies of the data from frequently used main memory locations, avoiding the need to always refer to main memory which may be tens to hundreds of times slower to access.
Cache memory is typically implemented with static random-access memory (SRAM), which requires multiple transistors to store a single bit. This makes it expensive in terms of the area it takes up, and in modern CPUs the cache is typically the largest part by chip area. The size of the cache needs to be balanced with the general desire for smaller chips which cost less. Some modern designs implement some or all of their cache using the physically smaller eDRAM, which is slower to use than SRAM but allows larger amounts of cache for any given amount of chip area.
Most CPUs have a hierarchy of multiple cache levels (L1, L2, often L3, and rarely even L4), with separate instruction-specific (I-cache) and data-specific (D-cache) caches at level 1. The different levels are implemented in different areas of the chip; L1 is located as close to a CPU core as possible and thus offers the highest speed due to short signal paths, but requires careful design. L2 caches are physically separate from the CPU and operate slower, but place fewer demands on the chip designer and can be made much larger without impacting the CPU design. L3 caches are generally shared among multiple CPU cores.
Other types of caches exist (that are not counted towards the "cache size" of the most important caches mentioned above), such as the translation lookaside buffer (TLB) which is part of the memory management unit (MMU) which most CPUs have. Input/output sections also often contain data buffers that serve a similar purpose.


== Overview ==
To access data in main memory, a multi-step process is used and each step introduces a delay. For instance, to read a value from memory in a simple computer system the CPU first selects the address to be accessed by expressing it on the address bus and waiting a fixed time to allow the value to settle. The memory device with that value, normally implemented in DRAM, holds that value in a very low-energy form that is not powerful enough to be read directly by the CPU. Instead, it has to copy that value from storage into a small buffer which is connected to the data bus. It then waits a certain time to allow this value to settle before reading the value from the data bus.
By locating the memory physically closer to the CPU the time needed for the buses to settle is reduced, and by replacing the DRAM with SRAM, which hold the value in a form that does not require amplification to be read, the delay within the memory itself is eliminated. This makes the cache much faster both to respond and to read or write. SRAM, however, requires anywhere from four to six transistors to hold a single bit, depending on the type, whereas DRAM generally uses one transistor and one capacitor per bit, which makes it able to store much more data for any given chip area.
Implementing some memory in a faster format can lead to large performance improvements. When trying to read from or write to a location in the memory, the processor checks whether the data from that location is already in the cache. If so, the processor will read from or write to the cache instead of the much slower main memory.
Many modern desktop, server, and industrial CPUs have at least three independent levels of caches (L1, L2 and L3) and different types of caches:

Translation lookaside buffer (TLB)
Used to speed up virtual-to-physical address translation for both executable instructions and data. A single TLB can be provided for access to both instructions and data, or a separate Instruction TLB (ITLB) and data TLB (DTLB) can be provided. However, the TLB cache is part of the memory management unit (MMU) and not directly related to the CPU caches.
Instruction cache (I-cache)
Used to speed executable instruction fetch; some specialized versions include micro-operation caches and branch target instruction caches.
Data cache (D-cache)
Used to speed data fetch and store.
Higher-level caches
caches above the I-cache and D-cache are usually organized as a hierarchy of more cache levels (L2, L3, etc.); see also multi-level caches below).


== History ==

Early examples of CPU caches include the Atlas 2 and the IBM System/360 Model 85 in the 1960s. The first CPUs that used a cache had only one level of cache; unlike later level 1 cache, it was not split into L1d (for data) and L1i (for instructions). Split L1 cache started in 1976 with the IBM 801 CPU, became mainstream in the late 1980s, and in 1997 entered the embedded CPU market with the ARMv5TE. As of 2015, even sub-dollar SoCs split the L1 cache. They also have L2 caches and, for larger processors, L3 caches as well. The L2 cache is usually not split, and acts as a common repository for the already split L1 cache. Every core of a multi-core processor has a dedicated L1 cache and is usually not shared between the cores. The L2 cache, and lower-level caches, may be shared between the cores. L4 cache is currently uncommon, and is generally dynamic random-access memory (DRAM) on a separate die or chip, rather than static random-access memory (SRAM). An exception to this is when eDRAM is used for all levels of cache, down to L1. Historically L1 was also on a separate die, however bigger die sizes have allowed integration of it as well as other cache levels, with the possible exception of the last level. Each extra level of cache tends to be smaller and faster than the lower levels.
Caches (like for RAM historically) have generally been sized in powers of: 2, 4, 8, 16 etc. KiB; when up to MiB sizes (i.e. for larger non-L1), very early on the pattern broke down, to allow for larger caches without being forced into the doubling-in-size paradigm, with e.g. Intel Core 2 Duo with 3 MiB L2 cache in April 2008. This happened much later for L1 caches, as their size is generally still a small number of KiB. The IBM zEC12 from 2012 is an exception however, to gain unusually large 96 KiB L1 data cache for its time, and e.g. the IBM z13 having a 96 KiB L1 instruction cache (and 128 KiB L1 data cache), and Intel Ice Lake-based processors from 2018, having 48 KiB L1 data cache and 48 KiB L1 instruction cache. In 2020, some Intel Atom CPUs (with up to 24 cores) have (multiple of) 4.5 MiB and 15 MiB cache sizes.


== Operation ==


=== Cache entries ===
Data is transferred between memory and cache in blocks of fixed size, called cache lines or cache blocks. When a cache line is copied from memory into the cache, a cache entry is created. The cache entry will include the copied data as well as the requested memory location (called a tag).
When the processor needs to read or write a location in memory, it first checks for a corresponding entry in the cache. The cache checks for the contents of the requested memory location in any cache lines that might contain that address. If the processor finds that the memory location is in the cache, a cache hit has occurred. However, if the processor does not find the memory location in the cache, a cache miss has occurred. In the case of a cache hit, the processor immediately reads or writes the data in the cache line. For a cache miss, the cache allocates a new entry and copies data from main memory, then the request is fulfilled from the contents of the cache.


=== Policies ===


==== Replacement policies ====

To make room for the new entry on a cache miss, the cache may have to evict one of the existing entries. The heuristic it uses to choose the entry to evict is called the replacement policy. The fundamental problem with any replacement policy is that it must predict which existing cache entry is least likely to be used in the future. Predicting the future is generally difficult, so there is no perfect method to choose among the variety of replacement policies available. One popular replacement policy, least-recently used (LRU), replaces the least recently accessed entry.
Marking some memory ranges as non-cacheable can improve performance, by avoiding caching of memory regions that are rarely re-accessed. This avoids the overhead of loading something into the cache without having any reuse. Cache entries may also be disabled or locked depending on the context.


==== Write policies ====

If data are written to the cache, at some point they must also be written to main memory; the timing of this write is known as the write policy. In a write-through cache, every write to the cache causes a write to main memory. Alternatively, in a write-back or copy-back cache, writes are not immediately mirrored to the main memory, with locations been written over being marked as dirty, being written back to the main memory only when they are evicted from the cache. For this reason, a read miss in a write-back cache may sometimes require two memory accesses to service: one to first write the dirty location to main memory, and then another to read the new location from memory. Also, a write to a main memory location that is not yet mapped in a write-back cache may evict an already dirty location, thereby freeing that cache space for the new memory location.
There are intermediate policies as well. The cache may be write-through, but the writes may be held in a store data queue temporarily, usually so multiple stores can be processed together (which can reduce bus turnarounds and improve bus utilization).
Cached data from the main memory may be changed by other entities (e.g., peripherals using direct memory access (DMA) or another core in a multi-core processor), in which case the copy in the cache may become out-of-date or stale. Alternatively, when a CPU in a multiprocessor system updates data in the cache, copies of data in caches associated with other CPUs become stale. Communication protocols between the cache managers that keep the data consistent are known as cache coherence protocols.


=== Cache performance ===
Cache performance measurement has become important in recent times where the speed gap between the memory performance and the processor performance is increasing exponentially. The cache was introduced to reduce this speed gap. Thus knowing how well the cache is able to bridge the gap in the speed of processor and memory becomes important, especially in high-performance systems. The cache hit rate and the cache miss rate play an important role in determining this performance. To improve the cache performance, reducing the miss rate becomes one of the necessary steps among other steps. Decreasing the access time to the cache also gives a boost to its performance and helps with optimization.


==== CPU stalls ====
The time taken to fetch one cache line from memory (read latency due to a cache miss) matters because the CPU will run out of work while waiting for the cache line. When a CPU reaches this state, it is called a stall. As CPUs become faster compared to main memory, stalls due to cache misses displace more potential computation; modern CPUs can execute hundreds of instructions in the time taken to fetch a single cache line from main memory.
Various techniques have been employed to keep the CPU busy during this time, including out-of-order execution in which the CPU attempts to execute independent instructions after the instruction that is waiting for the cache miss data. Another technology, used by many processors, is simultaneous multithreading (SMT), which allows an alternate thread to use the CPU core while the first thread waits for required CPU resources to become available.


== Associativity ==

The placement policy decides where in the cache a copy of a particular entry of main memory will go. If the placement policy is free to choose any entry in the cache to hold the copy, the cache is called fully associative. At the other extreme, if each entry in the main memory can go in just one place in the cache, the cache is direct-mapped. Many caches implement a compromise in which each entry in the main memory can go to any one of N places in the cache, and are described as N-way set associative. For example, the level-1 data cache in an AMD Athlon is two-way set associative, which means that any particular location in main memory can be cached in either of two locations in the level-1 data cache.
Choosing the right value of associativity involves a trade-off. If there are ten places to which the placement policy could have mapped a memory location, then to check if that location is in the cache, ten cache entries must be searched. Checking more places takes more power and chip area, and potentially more time. On the other hand, caches with more associativity suffer fewer misses (see conflict misses), so that the CPU wastes less time reading from the slow main memory. The general guideline is that doubling the associativity, from direct mapped to two-way, or from two-way to four-way, has about the same effect on raising the hit rate as doubling the cache size. However, increasing associativity more than four does not improve hit rate as much, and are generally done for other reasons (see virtual aliasing). Some CPUs can dynamically reduce the associativity of their caches in low-power states, which acts as a power-saving measure.
In order of worse but simple to better but complex:

Direct mapped cache – good best-case time, but unpredictable in the worst case
Two-way set associative cache
Two-way skewed associative cache
Four-way set-associative cache
Eight-way set-associative cache, a common choice for later implementations
12-way set associative cache, similar to eight-way
Fully associative cache – the best miss rates, but practical only for a small number of entries


=== Direct-mapped cache ===
In this cache organization, each location in the main memory can go in only one entry in the cache. Therefore, a direct-mapped cache can also be called a "one-way set associative" cache. It does not have a placement policy as such, since there is no choice of which cache entry's contents to evict. This means that if two locations map to the same entry, they may continually knock each other out. Although simpler, a direct-mapped cache needs to be much larger than an associative one to give comparable performance, and it is more unpredictable. Let x be block number in cache, y be block number of memory, and n be number of blocks in cache, then mapping is done with the help of the equation x = y mod n.


=== Two-way set associative cache ===
If each location in the main memory can be cached in either of two locations in the cache, one logical question is: which one of the two? The simplest and most commonly used scheme, shown in the right-hand diagram above, is to use the least significant bits of the memory location's address as the index for the cache memory, and to have two entries for each index. One benefit of this scheme is that the tags stored in the cache do not have to include that part of the main memory address which is implied by the cache memory's index. Since the cache tags have fewer bits, they require fewer transistors, take less space on the processor circuit board or on the microprocessor chip, and can be read and compared faster. Also LRU algorithm is especially simple since only one bit needs to be stored for each pair.


=== Speculative execution ===
One of the advantages of a direct-mapped cache is that it allows simple and fast speculation. Once the address has been computed, the one cache index which might have a copy of that location in memory is known. That cache entry can be read, and the processor can continue to work with that data before it finishes checking that the tag actually matches the requested address.
The idea of having the processor use the cached data before the tag match completes can be applied to associative caches as well. A subset of the tag, called a hint, can be used to pick just one of the possible cache entries mapping to the requested address. The entry selected by the hint can then be used in parallel with checking the full tag. The hint technique works best when used in the context of address translation, as explained below.


=== Two-way skewed associative cache ===
Other schemes have been suggested, such as the skewed cache, where the index for way 0 is direct, as above, but the index for way 1 is formed with a hash function. A good hash function has the property that addresses which conflict with the direct mapping tend not to conflict when mapped with the hash function, and so it is less likely that a program will suffer from an unexpectedly large number of conflict misses due to a pathological access pattern. The downside is extra latency from computing the hash function. Additionally, when it comes time to load a new line and evict an old line, it may be difficult to determine which existing line was least recently used, because the new line conflicts with data at different indexes in each way; LRU tracking for non-skewed caches is usually done on a per-set basis. Nevertheless, skewed-associative caches have major advantages over conventional set-associative ones.


=== Pseudo-associative cache ===
A true set-associative cache tests all the possible ways simultaneously, using something like a content-addressable memory. A pseudo-associative cache tests each possible way one at a time. A hash-rehash cache and a column-associative cache are examples of a pseudo-associative cache.
In the common case of finding a hit in the first way tested, a pseudo-associative cache is as fast as a direct-mapped cache, but it has a much lower conflict miss rate than a direct-mapped cache, closer to the miss rate of a fully associative cache.


=== Multicolumn cache ===
Comparing with a direct-mapped cache, a set associative cache has a reduced number of bits for its cache set index that maps to a cache set, where multiple ways or blocks stays, such as 2 blocks for a 2-way set associative cache and 4 blocks for a 4-way set associative cache. Comparing with a direct mapped cache, the unused cache index bits become a part of the tag bits. For example, a 2-way set associative cache contributes 1 bit to the tag and a 4-way set associative cache contributes 2 bits to the tag. The basic idea of the multicolumn cache is to use the set index to map to a cache set as a conventional set associative cache does, and to use the added tag bits to index a way in the set. For example, in a 4-way set associative cache, the two bits are used to index way 00, way 01, way 10, and way 11, respectively. This double cache indexing is called a "major location mapping", and its latency is equivalent to a direct-mapped access. Extensive experiments in multicolumn cache design shows that the hit ratio to major locations is as high as 90%. If cache mapping conflicts with a cache block in the major location, the existing cache block will be moved to another cache way in the same set, which is called "selected location". Because the newly indexed cache block is a most recently used (MRU) block, it is placed in the major location in multicolumn cache with a consideration of temporal locality. Since multicolumn cache is designed for a cache with a high associativity, the number of ways in each set is high; thus, it is easy find a selected location in the set. A selected location index by an additional hardware is maintained for the major location in a cache block.
Multicolumn cache remains a high hit ratio due to its high associativity, and has a comparable low latency to a direct-mapped cache due to its high percentage of hits in major locations. The concepts of major locations and selected locations in multicolumn cache have been used in several cache designs in ARM Cortex R chip, Intel's way-predicting cache memory, IBM's reconfigurable multi-way associative cache memory and Oracle's dynamic cache replacement way selection based on address tab bits.


== Cache entry structure ==
Cache row entries usually have the following structure:

The data block (cache line) contains the actual data fetched from the main memory. The tag contains (part of) the address of the actual data fetched from the main memory. The flag bits are discussed below.
The "size" of the cache is the amount of main memory data it can hold. This size can be calculated as the number of bytes stored in each data block times the number of blocks stored in the cache. (The tag, flag and error correction code bits are not included in the size, although they do affect the physical area of a cache.)
An effective memory address which goes along with the cache line (memory block) is split (MSB to LSB) into the tag, the index and the block offset.

The index describes which cache set that the data has been put in. The index length is ⌈log2(s)⌉ bits for s cache sets.
The block offset specifies the desired data within the data block stored within the cache row. Typically the effective address is in bytes, so the block offset length is ⌈log2(b)⌉ bits, where b is the number of bytes per data block.
The tag contains the most significant bits of the address, which are checked against all rows in the current set (the set has been retrieved by index) to see if this set contains the requested address. If it does, a cache hit occurs. The tag length in bits is as follows:

tag_length = address_length - index_length - block_offset_length
Some authors refer to the block offset as simply the "offset" or the "displacement".


=== Example ===
The original Pentium 4 processor had a four-way set associative L1 data cache of 8 KiB in size, with 64-byte cache blocks. Hence, there are 8 KiB / 64 = 128 cache blocks. The number of sets is equal to the number of cache blocks divided by the number of ways of associativity, what leads to 128 / 4 = 32 sets, and hence 25 = 32 different indices. There are 26 = 64 possible offsets. Since the CPU address is 32 bits wide, this implies 32 − 5 − 6 = 21 bits for the tag field.
The original Pentium 4 processor also had an eight-way set associative L2 integrated cache 256 KiB in size, with 128-byte cache blocks. This implies 32 − 8 − 7 = 17 bits for the tag field.


=== Flag bits ===
An instruction cache requires only one flag bit per cache row entry: a valid bit. The valid bit indicates whether or not a cache block has been loaded with valid data.
On power-up, the hardware sets all the valid bits in all the caches to "invalid". Some systems also set a valid bit to "invalid" at other times, such as when multi-master bus snooping hardware in the cache of one processor hears an address broadcast from some other processor, and realizes that certain data blocks in the local cache are now stale and should be marked invalid.
A data cache typically requires two flag bits per cache line – a valid bit and a dirty bit. Having a dirty bit set indicates that the associated cache line has been changed since it was read from main memory ("dirty"), meaning that the processor has written data to that line and the new value has not propagated all the way to main memory.


== Cache miss ==
A cache miss is a failed attempt to read or write a piece of data in the cache, which results in a main memory access with much longer latency. There are three kinds of cache misses: instruction read miss, data read miss, and data write miss.
Cache read misses from an instruction cache generally cause the largest delay, because the processor, or at least the thread of execution, has to wait (stall) until the instruction is fetched from main memory. Cache read misses from a data cache usually cause a smaller delay, because instructions not dependent on the cache read can be issued and continue execution until the data are returned from main memory, and the dependent instructions can resume execution. Cache write misses to a data cache generally cause the shortest delay, because the write can be queued and there are few limitations on the execution of subsequent instructions; the processor can continue until the queue is full. For a detailed introduction to the types of misses, see cache performance measurement and metric.


== Address translation ==
Most general purpose CPUs implement some form of virtual memory. To summarize, either each program running on the machine sees its own simplified address space, which contains code and data for that program only, or all programs run in a common virtual address space. A program executes by calculating, comparing, reading and writing to addresses of its virtual address space, rather than addresses of physical address space, making programs simpler and thus easier to write.
Virtual memory requires the processor to translate virtual addresses generated by the program into physical addresses in main memory. The portion of the processor that does this translation is known as the memory management unit (MMU). The fast path through the MMU can perform those translations stored in the translation lookaside buffer (TLB), which is a cache of mappings from the operating system's page table, segment table, or both.
For the purposes of the present discussion, there are three important features of address translation:

Latency: The physical address is available from the MMU some time, perhaps a few cycles, after the virtual address is available from the address generator.
Aliasing: Multiple virtual addresses can map to a single physical address. Most processors guarantee that all updates to that single physical address will happen in program order. To deliver on that guarantee, the processor must ensure that only one copy of a physical address resides in the cache at any given time.
Granularity: The virtual address space is broken up into pages. For instance, a 4 GiB virtual address space might be cut up into 1,048,576 pages of 4 KiB size, each of which can be independently mapped. There may be multiple page sizes supported; see virtual memory for elaboration.
One early virtual memory system, the IBM M44/44X, required an access to a mapping table held in core memory before every programmed access to main memory. With no caches, and with the mapping table memory running at the same speed as main memory this effectively cut the speed of memory access in half. Two early machines that used a page table in main memory for mapping, the IBM System/360 Model 67 and the GE 645, both had a small associative memory as a cache for accesses to the in-memory page table. Both machines predated the first machine with a cache for main memory, the IBM System/360 Model 85, so the first hardware cache used in a computer system was not a data or instruction cache, but rather a TLB.
Caches can be divided into four types, based on whether the index or tag correspond to physical or virtual addresses:

Physically indexed, physically tagged (PIPT) caches use the physical address for both the index and the tag. While this is simple and avoids problems with aliasing, it is also slow, as the physical address must be looked up (which could involve a TLB miss and access to main memory) before that address can be looked up in the cache.
Virtually indexed, virtually tagged (VIVT) caches use the virtual address for both the index and the tag. This caching scheme can result in much faster lookups, since the MMU does not need to be consulted first to determine the physical address for a given virtual address. However, VIVT suffers from aliasing problems, where several different virtual addresses may refer to the same physical address. The result is that such addresses would be cached separately despite referring to the same memory, causing coherency problems. Although solutions to this problem exist they do not work for standard coherence protocols. Another problem is homonyms, where the same virtual address maps to several different physical addresses. It is not possible to distinguish these mappings merely by looking at the virtual index itself, though potential solutions include: flushing the cache after a context switch, forcing address spaces to be non-overlapping, tagging the virtual address with an address space ID (ASID). Additionally, there is a problem that virtual-to-physical mappings can change, which would require flushing cache lines, as the VAs would no longer be valid. All these issues are absent if tags use physical addresses (VIPT).
Virtually indexed, physically tagged (VIPT) caches use the virtual address for the index and the physical address in the tag. The advantage over PIPT is lower latency, as the cache set can be looked up in parallel with the TLB translation, however the tag cannot be compared until the physical address is available. The advantage over VIVT is that since the tag has the physical address, the cache can detect homonyms. Theoretically, VIPT requires more tags bits because some of the index bits could differ between the virtual and physical addresses (for example bit 12 and above for 4 KiB pages) and would have to be included both in the virtual index and in the physical tag. In practice this is not an issue because, in order to avoid coherency problems, VIPT caches are designed to have no such index bits (e.g., by limiting the total number of bits for the index and the block offset to 12 for 4 KiB pages); this limits the size of VIPT caches to the page size times the associativity of the cache.
Physically indexed, virtually tagged (PIVT) caches are often claimed in literature to be useless and non-existing. However, the MIPS R6000 uses this cache type as the sole known implementation. The R6000 is implemented in emitter-coupled logic, which is an extremely fast technology not suitable for large memories such as a TLB. The R6000 solves the issue by putting the TLB memory into a reserved part of the second-level cache having a tiny, high-speed TLB "slice" on chip. The cache is indexed by the physical address obtained from the TLB slice. However, since the TLB slice only translates those virtual address bits that are necessary to index the cache and does not use any tags, false cache hits may occur, which is solved by tagging with the virtual address.
The speed of this recurrence (the load latency) is crucial to CPU performance, and so most modern level-1 caches are virtually indexed, which at least allows the MMU's TLB lookup to proceed in parallel with fetching the data from the cache RAM.
But virtual indexing is not the best choice for all cache levels. The cost of dealing with virtual aliases grows with cache size, and as a result most level-2 and larger caches are physically indexed.
Caches have historically used both virtual and physical addresses for the cache tags, although virtual tagging is now uncommon. If the TLB lookup can finish before the cache RAM lookup, then the physical address is available in time for tag compare, and there is no need for virtual tagging. Large caches, then, tend to be physically tagged, and only small, very low latency caches are virtually tagged. In recent general-purpose CPUs, virtual tagging has been superseded by virtual hints, as described below.


=== Homonym and synonym problems ===
A cache that relies on virtual indexing and tagging becomes inconsistent after the same virtual address is mapped into different physical addresses (homonym), which can be solved by using physical address for tagging, or by storing the address space identifier in the cache line. However, the latter approach does not help against the synonym problem, in which several cache lines end up storing data for the same physical address. Writing to such locations may update only one location in the cache, leaving the others with inconsistent data. This issue may be solved by using non-overlapping memory layouts for different address spaces, or otherwise the cache (or a part of it) must be flushed when the mapping changes.


=== Virtual tags and hints ===
The great advantage of virtual tags is that, for associative caches, they allow the tag match to proceed before the virtual to physical translation is done. However, coherence probes and evictions present a physical address for action. The hardware must have some means of converting the physical addresses into a cache index, generally by storing physical tags as well as virtual tags. For comparison, a physically tagged cache does not need to keep virtual tags, which is simpler. When a virtual to physical mapping is deleted from the TLB, cache entries with those virtual addresses will have to be flushed somehow. Alternatively, if cache entries are allowed on pages not mapped by the TLB, then those entries will have to be flushed when the access rights on those pages are changed in the page table.
It is also possible for the operating system to ensure that no virtual aliases are simultaneously resident in the cache. The operating system makes this guarantee by enforcing page coloring, which is described below. Some early RISC processors (SPARC, RS/6000) took this approach. It has not been used recently, as the hardware cost of detecting and evicting virtual aliases has fallen and the software complexity and performance penalty of perfect page coloring has risen.
It can be useful to distinguish the two functions of tags in an associative cache: they are used to determine which way of the entry set to select, and they are used to determine if the cache hit or missed. The second function must always be correct, but it is permissible for the first function to guess, and get the wrong answer occasionally.
Some processors (e.g. early SPARCs) have caches with both virtual and physical tags. The virtual tags are used for way selection, and the physical tags are used for determining hit or miss. This kind of cache enjoys the latency advantage of a virtually tagged cache, and the simple software interface of a physically tagged cache. It bears the added cost of duplicated tags, however. Also, during miss processing, the alternate ways of the cache line indexed have to be probed for virtual aliases and any matches evicted.
The extra area (and some latency) can be mitigated by keeping virtual hints with each cache entry instead of virtual tags. These hints are a subset or hash of the virtual tag, and are used for selecting the way of the cache from which to get data and a physical tag. Like a virtually tagged cache, there may be a virtual hint match but physical tag mismatch, in which case the cache entry with the matching hint must be evicted so that cache accesses after the cache fill at this address will have just one hint match. Since virtual hints have fewer bits than virtual tags distinguishing them from one another, a virtually hinted cache suffers more conflict misses than a virtually tagged cache.
Perhaps the ultimate reduction of virtual hints can be found in the Pentium 4 (Willamette and Northwood cores). In these processors the virtual hint is effectively two bits, and the cache is four-way set associative. Effectively, the hardware maintains a simple permutation from virtual address to cache index, so that no content-addressable memory (CAM) is necessary to select the right one of the four ways fetched.


=== Page coloring ===

Large physically indexed caches (usually secondary caches) run into a problem: the operating system rather than the application controls which pages collide with one another in the cache. Differences in page allocation from one program run to the next lead to differences in the cache collision patterns, which can lead to very large differences in program performance. These differences can make it very difficult to get a consistent and repeatable timing for a benchmark run.
To understand the problem, consider a CPU with a 1 MiB physically indexed direct-mapped level-2 cache and 4 KiB virtual memory pages. Sequential physical pages map to sequential locations in the cache until after 256 pages the pattern wraps around. We can label each physical page with a color of 0–255 to denote where in the cache it can go. Locations within physical pages with different colors cannot conflict in the cache.
Programmers attempting to make maximum use of the cache may arrange their programs' access patterns so that only 1 MiB of data need be cached at any given time, thus avoiding capacity misses. But they should also ensure that the access patterns do not have conflict misses. One way to think about this problem is to divide up the virtual pages the program uses and assign them virtual colors in the same way as physical colors were assigned to physical pages before. Programmers can then arrange the access patterns of their code so that no two pages with the same virtual color are in use at the same time. There is a wide literature on such optimizations (e.g. loop nest optimization), largely coming from the High Performance Computing (HPC) community.
The snag is that while all the pages in use at any given moment may have different virtual colors, some may have the same physical colors. In fact, if the operating system assigns physical pages to virtual pages randomly and uniformly, it is extremely likely that some pages will have the same physical color, and then locations from those pages will collide in the cache (this is the birthday paradox).
The solution is to have the operating system attempt to assign different physical color pages to different virtual colors, a technique called page coloring. Although the actual mapping from virtual to physical color is irrelevant to system performance, odd mappings are difficult to keep track of and have little benefit, so most approaches to page coloring simply try to keep physical and virtual page colors the same.
If the operating system can guarantee that each physical page maps to only one virtual color, then there are no virtual aliases, and the processor can use virtually indexed caches with no need for extra virtual alias probes during miss handling. Alternatively, the OS can flush a page from the cache whenever it changes from one virtual color to another. As mentioned above, this approach was used for some early SPARC and RS/6000 designs.
The software page coloring technique has been used to effectively partition the shared Last level Cache (LLC) in multicore processors. This operating system-based LLC management in multicore processors has been adopted by Intel.


== Cache hierarchy in a modern processor ==

Modern processors have multiple interacting on-chip caches. The operation of a particular cache can be completely specified by the cache size, the cache block size, the number of blocks in a set, the cache set replacement policy, and the cache write policy (write-through or write-back).
While all of the cache blocks in a particular cache are the same size and have the same associativity, typically the "higher-level" caches (called Level 1 cache) have a smaller number of blocks, smaller block size, and fewer blocks in a set, but have very short access times. "Lower-level" caches (i.e. Level 2 and below) have progressively larger numbers of blocks, larger block size, more blocks in a set, and relatively longer access times, but are still much faster than main memory.
Cache entry replacement policy is determined by a cache algorithm selected to be implemented by the processor designers. In some cases, multiple algorithms are provided for different kinds of work loads.


=== Specialized caches ===
Pipelined CPUs access memory from multiple points in the pipeline: instruction fetch, virtual-to-physical address translation, and data fetch (see classic RISC pipeline). The natural design is to use different physical caches for each of these points, so that no one physical resource has to be scheduled to service two points in the pipeline. Thus the pipeline naturally ends up with at least three separate caches (instruction, TLB, and data), each specialized to its particular role.


==== Victim cache ====

A victim cache is a cache used to hold blocks evicted from a CPU cache upon replacement. The victim cache lies between the main cache and its refill path, and holds only those blocks of data that were evicted from the main cache. The victim cache is usually fully associative, and is intended to reduce the number of conflict misses. Many commonly used programs do not require an associative mapping for all the accesses. In fact, only a small fraction of the memory accesses of the program require high associativity. The victim cache exploits this property by providing high associativity to only these accesses. It was introduced by Norman Jouppi from DEC in 1990.
Intel's Crystalwell variant of its Haswell processors introduced an on-package 128 MiB eDRAM Level 4 cache which serves as a victim cache to the processors' Level 3 cache. In the Skylake microarchitecture the Level 4 cache no longer works as a victim cache.


==== Trace cache ====

One of the more extreme examples of cache specialization is the trace cache (also known as execution trace cache) found in the Intel Pentium 4 microprocessors. A trace cache is a mechanism for increasing the instruction fetch bandwidth and decreasing power consumption (in the case of the Pentium 4) by storing traces of instructions that have already been fetched and decoded.
A trace cache stores instructions either after they have been decoded, or as they are retired. Generally, instructions are added to trace caches in groups representing either individual basic blocks or dynamic instruction traces. The Pentium 4's trace cache stores micro-operations resulting from decoding x86 instructions, providing also the functionality of a micro-operation cache. Having this, the next time an instruction is needed, it does not have to be decoded into micro-ops again.


==== Write Coalescing Cache (WCC) ====
Write Coalescing Cache is a special cache that is part of L2 cache in AMD's Bulldozer microarchitecture. Stores from both L1D caches in the module go through the WCC, where they are buffered and coalesced.
The WCC's task is reducing number of writes to the L2 cache.


==== Micro-operation (μop or uop) cache ====
A micro-operation cache (μop cache, uop cache or UC) is a specialized cache that stores micro-operations of decoded instructions, as received directly from the instruction decoders or from the instruction cache. When an instruction needs to be decoded, the μop cache is checked for its decoded form which is re-used if cached; if it is not available, the instruction is decoded and then cached.
One of the early works describing μop cache as an alternative frontend for the Intel P6 processor family is the 2001 paper "Micro-Operation Cache: A Power Aware Frontend for Variable Instruction Length ISA". Later, Intel included μop caches in its Sandy Bridge processors and in successive microarchitectures like Ivy Bridge and Haswell. AMD implemented a μop cache in their Zen microarchitecture.
Fetching complete pre-decoded instructions eliminates the need to repeatedly decode variable length complex instructions into simpler fixed-length micro-operations, and simplifies the process of predicting, fetching, rotating and aligning fetched instructions. A μop cache effectively offloads the fetch and decode hardware, thus decreasing power consumption and improving the frontend supply of decoded micro-operations. The μop cache also increases performance by more consistently delivering decoded micro-operations to the backend and eliminating various bottlenecks in the CPU's fetch and decode logic.
A μop cache has many similarities with a trace cache, although a μop cache is much simpler thus providing better power efficiency; this makes it better suited for implementations on battery-powered devices. The main disadvantage of the trace cache, leading to its power inefficiency, is the hardware complexity required for its heuristic deciding on caching and reusing dynamically created instruction traces.


==== Branch target instruction cache ====
A branch target cache or branch target instruction cache, the name used on ARM microprocessors, is a specialized cache which holds the first few instructions at the destination of a taken branch. This is used by low-powered processors which do not need a normal instruction cache because the memory system is capable of delivering instructions fast enough to satisfy the CPU without one. However, this only applies to consecutive instructions in sequence; it still takes several cycles of latency to restart instruction fetch at a new address, causing a few cycles of pipeline bubble after a control transfer. A branch target cache provides instructions for those few cycles avoiding a delay after most taken branches.
This allows full-speed operation with a much smaller cache than a traditional full-time instruction cache.


==== Smart cache ====
Smart cache is a level 2 or level 3 caching method for multiple execution cores, developed by Intel.
Smart Cache shares the actual cache memory between the cores of a multi-core processor. In comparison to a dedicated per-core cache, the overall cache miss rate decreases when cores do not require equal parts of the cache space. Consequently, a single core can use the full level 2 or level 3 cache while the other cores are inactive. Furthermore, the shared cache makes it faster to share memory among different execution cores.


=== Multi-level caches ===

Another issue is the fundamental tradeoff between cache latency and hit rate. Larger caches have better hit rates but longer latency. To address this tradeoff, many computers use multiple levels of cache, with small fast caches backed up by larger, slower caches. Multi-level caches generally operate by checking the fastest but smallest cache, level 1 (L1), first; if it hits, the processor proceeds at high speed. If that cache misses, the slower but larger next level cache, level 2 (L2), is checked, and so on, before accessing external memory.
As the latency difference between main memory and the fastest cache has become larger, some processors have begun to utilize as many as three levels of on-chip cache. Price-sensitive designs used this to pull the entire cache hierarchy on-chip, but by the 2010s some of the highest-performance designs returned to having large off-chip caches, which is often implemented in eDRAM and mounted on a multi-chip module, as a fourth cache level. In rare cases, such as in the mainframe CPU IBM z15 (2019), all levels down to L1 are implemented by eDRAM, replacing SRAM entirely (for cache, registers are still typically implemented using SRAM-based register files or flip-flop-based designs, rather than eDRAM). Apple's ARM-based Apple silicon series, starting with the A14 and M1, have a 192 KiB L1i cache for each of the high-performance cores, an unusually large amount; however the high-efficiency cores only have 128 KiB. Since then other processors such as Intel's Lunar Lake and Qualcomm's Oryon have also implemented similar L1i cache sizes.
The benefits of L3 and L4 caches depend on the application's access patterns. Examples of products incorporating L3 and L4 caches include the following:

Alpha 21164 (1995) had 1 to 64 MiB off-chip L3 cache.
AMD K6-III (1999) had motherboard-based L3 cache.
IBM POWER4 (2001) had off-chip L3 caches of 32 MiB per processor, shared among several processors.
Itanium 2 (2003) had a 6 MiB unified level 3 (L3) cache on-die; the Itanium 2 (2003) MX 2 module incorporated two Itanium 2 processors along with a shared 64 MiB L4 cache on a multi-chip module that was pin compatible with a Madison processor.
Intel's Xeon MP product codenamed "Tulsa" (2006) features 16 MiB of on-die L3 cache shared between two processor cores.
AMD Phenom (2007) with 2 MiB of L3 cache.
AMD Phenom II (2008) has up to 6 MiB on-die unified L3 cache.
Intel Core i7 (2008) has an 8 MiB on-die unified L3 cache that is inclusive, shared by all cores.
Intel Haswell CPUs with integrated Intel Iris Pro Graphics have 128 MiB of eDRAM acting essentially as an L4 cache.
Finally, at the other end of the memory hierarchy, the CPU register file itself can be considered the smallest, fastest cache in the system, with the special characteristic that it is scheduled in software—typically by a compiler, as it allocates registers to hold values retrieved from main memory for, as an example, loop nest optimization. However, with register renaming most compiler register assignments are reallocated dynamically by hardware at runtime into a register bank, allowing the CPU to break false data dependencies and thus easing pipeline hazards.
Register files sometimes also have hierarchy: The Cray-1 (circa 1976) had eight address "A" and eight scalar data "S" registers that were generally usable. There was also a set of 64 address "B" and 64 scalar data "T" registers that took longer to access, but were faster than main memory. The "B" and "T" registers were provided because the Cray-1 did not have a data cache. (The Cray-1 did, however, have an instruction cache.)


==== Multi-core chips ====
When considering a chip with multiple cores, there is a question of whether the caches should be shared or local to each core. Implementing shared cache inevitably introduces more wiring and complexity. But then, having one cache per chip, rather than core, greatly reduces the amount of space needed, and thus one can include a larger cache.
Typically, sharing the L1 cache is undesirable because the resulting increase in latency would make each core run considerably slower than a single-core chip. However, for the highest-level cache (usually L3, the last one called before accessing memory), having a global cache is desirable for several reasons, such as allowing a single core to use the whole cache, reducing data redundancy by making it possible for different processes or threads to share cached data, and reducing the complexity of utilized cache coherency protocols. For example, an eight-core chip with three levels may include an L1 cache for each core, one intermediate L2 cache for each pair of cores, and one L3 cache shared between all cores.
A shared highest-level cache (usually L3, called before accessing memory), is usually referred to as a last-level cache (LLC). Additional techniques are used for increasing the level of parallelism when LLC is shared between multiple cores, including slicing it into multiple pieces which are addressing certain ranges of memory addresses, and can be accessed independently.


==== Separate versus unified ====
In a separate cache structure, instructions and data are cached separately, meaning that a cache line is used to cache either instructions or data, but not both; various benefits have been demonstrated with separate data and instruction translation lookaside buffers. In a unified structure, this constraint is not present, and cache lines can be used to cache both instructions and data.


==== Exclusive versus inclusive ====
Multi-level caches introduce new design decisions. For instance, in some processors, all data in the L1 cache must also be somewhere in the L2 cache. These caches are called strictly inclusive. Other processors (like the AMD Athlon) have exclusive caches: data are guaranteed to be in at most one of the L1 and L2 caches, never in both. Still other processors (like the Intel Pentium II, III, and 4) do not require that data in the L1 cache also reside in the L2 cache, although it may often do so. There is no universally accepted name for this intermediate policy; two common names are "non-exclusive" and "partially-inclusive".
The advantage of exclusive caches is that they store more data. This advantage is larger when the exclusive L1 cache is comparable to the L2 cache, and diminishes if the L2 cache is many times larger than the L1 cache. When the L1 misses and the L2 hits on an access, the hitting cache line in the L2 is exchanged with a line in the L1. This exchange is quite a bit more work than just copying a line from L2 to L1, which is what an inclusive cache does.
One advantage of strictly inclusive caches is that when external devices or other processors in a multiprocessor system wish to remove a cache line from the processor, they need only have the processor check the L2 cache. In cache hierarchies which do not enforce inclusion, the L1 cache must be checked as well. As a drawback, there is a correlation between the associativities of L1 and L2 caches: if the L2 cache does not have at least as many ways as all L1 caches together, the effective associativity of the L1 caches is restricted. Another disadvantage of inclusive cache is that whenever there is an eviction in L2 cache, the (possibly) corresponding lines in L1 also have to get evicted in order to maintain inclusiveness. This is quite a bit of work, and would result in a higher L1 miss rate.
Another advantage of inclusive caches is that the larger cache can use larger cache lines, which reduces the size of the secondary cache tags. (Exclusive caches require both caches to have the same size cache lines, so that cache lines can be swapped on a L1 miss, L2 hit.) If the secondary cache is an order of magnitude larger than the primary, and the cache data are an order of magnitude larger than the cache tags, this tag area saved can be comparable to the incremental area needed to store the L1 cache data in the L2.


=== Scratchpad memory ===

Scratchpad memory (SPM), also known as scratchpad, scratchpad RAM or local store in computer terminology, is a high-speed internal memory used for temporary storage of calculations, data, and other work in progress.


=== Example: the K8 ===
To illustrate both specialization and multi-level caching, here is the cache hierarchy of the K8 core in the AMD Athlon 64 CPU.

The K8 has four specialized caches: an instruction cache, an instruction TLB, a data TLB, and a data cache. Each of these caches is specialized:

The instruction cache keeps copies of 64-byte lines of memory, and fetches 16 bytes each cycle. Each byte in this cache is stored in ten bits rather than eight, with the extra bits marking the boundaries of instructions (this is an example of predecoding). The cache has only parity protection rather than ECC, because parity is smaller and any damaged data can be replaced by fresh data fetched from memory (which always has an up-to-date copy of instructions).
The instruction TLB keeps copies of page table entries (PTEs). Each cycle's instruction fetch has its virtual address translated through this TLB into a physical address. Each entry is either four or eight bytes in memory. Because the K8 has a variable page size, each of the TLBs is split into two sections, one to keep PTEs that map 4 KiB pages, and one to keep PTEs that map 4 MiB or 2 MiB pages. The split allows the fully associative match circuitry in each section to be simpler. The operating system maps different sections of the virtual address space with different size PTEs.
The data TLB has two copies which keep identical entries. The two copies allow two data accesses per cycle to translate virtual addresses to physical addresses. Like the instruction TLB, this TLB is split into two kinds of entries.
The data cache keeps copies of 64-byte lines of memory. It is split into 8 banks (each storing 8 KiB of data), and can fetch two 8-byte data each cycle so long as those data are in different banks. There are two copies of the tags, because each 64-byte line is spread among all eight banks. Each tag copy handles one of the two accesses per cycle.
The K8 also has multiple-level caches. There are second-level instruction and data TLBs, which store only PTEs mapping 4 KiB. Both instruction and data caches, and the various TLBs, can fill from the large unified L2 cache. This cache is exclusive to both the L1 instruction and data caches, which means that any 8-byte line can only be in one of the L1 instruction cache, the L1 data cache, or the L2 cache. It is, however, possible for a line in the data cache to have a PTE which is also in one of the TLBs—the operating system is responsible for keeping the TLBs coherent by flushing portions of them when the page tables in memory are updated.
The K8 also caches information that is never stored in memory—prediction information. These caches are not shown in the above diagram. As is usual for this class of CPU, the K8 has fairly complex
branch prediction, with tables that help predict whether branches are taken and other tables which predict the targets of branches and jumps. Some of this information is associated with instructions, in both the level 1 instruction cache and the unified secondary cache.
The K8 uses an interesting trick to store prediction information with instructions in the secondary cache. Lines in the secondary cache are protected from accidental data corruption (e.g. by an alpha particle strike) by either ECC or parity, depending on whether those lines were evicted from the data or instruction primary caches. Since the parity code takes fewer bits than the ECC code, lines from the instruction cache have a few spare bits. These bits are used to cache branch prediction information associated with those instructions. The net result is that the branch predictor has a larger effective history table, and so has better accuracy.


=== More hierarchies ===
Other processors have other kinds of predictors (e.g., the store-to-load bypass predictor in the DEC Alpha 21264).
These predictors are caches in that they store information that is costly to compute. Some of the terminology used when discussing predictors is the same as that for caches (one speaks of a hit in a branch predictor), but predictors are not generally thought of as part of the cache hierarchy.
The K8 keeps the instruction and data caches coherent in hardware, which means that a store into an instruction closely following the store instruction will change that following instruction. Other processors, like those in the Alpha and MIPS family, have relied on software to keep the instruction cache coherent. Stores are not guaranteed to show up in the instruction stream until a program calls an operating system facility to ensure coherency.


=== Tag RAM ===

In computer engineering, a tag RAM is used to specify which of the possible memory locations is currently stored in a CPU cache. For a simple, direct-mapped design fast SRAM can be used. Higher associative caches usually employ content-addressable memory.


== Implementation ==

Cache reads are the most common CPU operation that takes more than a single cycle. Program execution time tends to be very sensitive to the latency of a level-1 data cache hit. A great deal of design effort, and often power and silicon area are expended making the caches as fast as possible.
The simplest cache is a virtually indexed direct-mapped cache. The virtual address is calculated with an adder, the relevant portion of the address extracted and used to index an SRAM, which returns the loaded data. The data are byte aligned in a byte shifter, and from there are bypassed to the next operation. There is no need for any tag checking in the inner loop – in fact, the tags need not even be read. Later in the pipeline, but before the load instruction is retired, the tag for the loaded data must be read, and checked against the virtual address to make sure there was a cache hit. On a miss, the cache is updated with the requested cache line and the pipeline is restarted.
An associative cache is more complicated, because some form of tag must be read to determine which entry of the cache to select. An N-way set-associative level-1 cache usually reads all N possible tags and N data in parallel, and then chooses the data associated with the matching tag. Level-2 caches sometimes save power by reading the tags first, so that only one data element is read from the data SRAM.

The adjacent diagram is intended to clarify the manner in which the various fields of the address are used. Address bit 31 is most significant, bit 0 is least significant. The diagram shows the SRAMs, indexing, and multiplexing for a 4 KiB, 2-way set-associative, virtually indexed and virtually tagged cache with 64 byte (B) lines, a 32-bit read width and 32-bit virtual address.
Because the cache is 4 KiB and has 64 B lines, there are just 64 lines in the cache, and we read two at a time from a Tag SRAM which has 32 rows, each with a pair of 21 bit tags. Although any function of virtual address bits 31 through 6 could be used to index the tag and data SRAMs, it is simplest to use the least significant bits.
Similarly, because the cache is 4 KiB and has a 4 B read path, and reads two ways for each access, the Data SRAM is 512 rows by 8 bytes wide.
A more modern cache might be 16 KiB, 4-way set-associative, virtually indexed, virtually hinted, and physically tagged, with 32 B lines, 32-bit read width and 36-bit physical addresses. The read path recurrence for such a cache looks very similar to the path above. Instead of tags, virtual hints are read, and matched against a subset of the virtual address. Later on in the pipeline, the virtual address is translated into a physical address by the TLB, and the physical tag is read (just one, as the virtual hint supplies which way of the cache to read). Finally the physical address is compared to the physical tag to determine if a hit has occurred.
Some SPARC designs have improved the speed of their L1 caches by a few gate delays by collapsing the virtual address adder into the SRAM decoders. (See sum-addressed decoder.)


=== History ===
The early history of cache technology is closely tied to the invention and use of virtual memory.  Because of scarcity and cost of semi-conductor memories, early mainframe computers in the 1960s used a complex hierarchy of physical memory, mapped onto a flat virtual memory space used by programs. The memory technologies would span semi-conductor, magnetic core, drum and disc. Virtual memory seen and used by programs would be flat and caching would be used to fetch data and instructions into the fastest memory ahead of processor access. Extensive studies were done to optimize the cache sizes. Optimal values were found to depend greatly on the programming language used with Algol needing the smallest and Fortran and Cobol needing the largest cache sizes.
In the early days of microcomputer technology, memory access was only slightly slower than register access. But since the 1980s the performance gap between processor and memory has been growing. Microprocessors have advanced much faster than memory, especially in terms of their operating frequency, so memory became a performance bottleneck. While it was technically possible to have all the main memory as fast as the CPU, a more economically viable path has been taken: use plenty of low-speed memory, but also introduce a small high-speed cache memory to alleviate the performance gap. This provided an order of magnitude more capacity—for the same price—with only a slightly reduced combined performance.


==== First TLB implementations ====
The first documented uses of a TLB were on the GE 645 and the IBM 360/67, both of which used an associative memory as a TLB.


==== First instruction cache ====
The first documented use of an instruction cache was on the CDC 6600.


==== First data cache ====
The first documented use of a data cache was on the IBM System/360 Model 85.


==== In 68k microprocessors ====
The 68010, released in 1982, has a "loop mode" which can be considered a tiny and special-case instruction cache that accelerates loops that consist of only two instructions. The 68020, released in 1984, replaced that with a typical instruction cache of 256 bytes, being the first 68k series processor to feature true on-chip cache memory.
The 68030, released in 1987, is basically a 68020 core with an additional 256-byte data cache, an on-chip memory management unit (MMU), a process shrink, and added burst mode for the caches.
The 68040, released in 1990, has split instruction and data caches of four kilobytes each.
The 68060, released in 1994, has the following: 8 KiB data cache (four-way associative), 8 KiB instruction cache (four-way associative), 96-byte FIFO instruction buffer, 256-entry branch cache, and 64-entry address translation cache MMU buffer (four-way associative).


==== In x86 microprocessors ====

As the x86 microprocessors reached clock rates of 20 MHz and above in the 386, small amounts of fast cache memory began to be featured in systems to improve performance. This was because the DRAM used for main memory had significant latency, up to 120 ns, as well as refresh cycles. The cache was constructed from more expensive, but significantly faster, SRAM memory cells, which at the time had latencies around 10–25 ns. The early caches were external to the processor and typically located on the motherboard in the form of eight or nine DIP devices placed in sockets to enable the cache as an optional extra or upgrade feature.
Some versions of the Intel 386 processor could support 16 to 256 KiB of external cache.
With the 486 processor, an 8 KiB cache was integrated directly into the CPU die. This cache was termed Level 1 or L1 cache to differentiate it from the slower on-motherboard, or Level 2 (L2) cache. These on-motherboard caches were much larger, with the most common size being 256 KiB. There were some system boards that contained sockets for the Intel 485Turbocache daughtercard which had either 64 or 128 Kbyte of cache memory. The popularity of on-motherboard cache continued through the Pentium MMX era but was made obsolete by the introduction of SDRAM and the growing disparity between bus clock rates and CPU clock rates, which caused on-motherboard cache to be only slightly faster than main memory.
The next development in cache implementation in the x86 microprocessors began with the Pentium Pro, which brought the secondary cache onto the same package as the microprocessor, clocked at the same frequency as the microprocessor.
On-motherboard caches enjoyed prolonged popularity thanks to the AMD K6-2 and AMD K6-III processors that still used Socket 7, which was previously used by Intel with on-motherboard caches. K6-III included 256 KiB on-die L2 cache and took advantage of the on-board cache as a third level cache, named L3 (motherboards with up to 2 MiB of on-board cache were produced). After the Socket 7 became obsolete, on-motherboard cache disappeared from the x86 systems.
The three-level caches were used again first with the introduction of the Intel Xeon MP "Foster Core", where the L3 cache was added to the CPU die. It became common for the total cache sizes to be increasingly larger in newer processor generations, and recently (as of 2011) it is not uncommon to find Level 3 cache sizes of tens of megabytes.
Intel introduced a Level 4 on-package cache with the Haswell microarchitecture. Crystalwell Haswell CPUs, equipped with the GT3e variant of Intel's integrated Iris Pro graphics, effectively feature 128 MiB of embedded DRAM (eDRAM) on the same package. This L4 cache is shared dynamically between the on-die GPU and CPU, and serves as a victim cache to the CPU's L3 cache.


==== In ARM microprocessors ====
The Apple M1 CPU has 128 or 192 KiB of L1 instruction cache for each core (important for latency/single-thread performance), depending on core type. This is an unusually large L1 cache for any CPU type (not just for a laptop); the total cache memory size is not unusually large (the total is more important for throughput) for a laptop, and much larger total (e.g. L3 or L4) sizes are available in IBM's mainframes.


==== Current research ====
Early cache designs focused entirely on the direct cost of cache and RAM and average execution speed.
More recent cache designs also consider energy efficiency, fault tolerance, and other goals.
There are several tools available to computer architects to help explore tradeoffs between the cache cycle time, energy, and area; the CACTI cache simulator and the SimpleScalar instruction set simulator are two open-source options.


=== Multi-ported cache ===
A multi-ported cache is a cache which can serve more than one request at a time. When accessing a traditional cache we normally use a single memory address, whereas in a multi-ported cache we may request N addresses at a time – where N is the number of ports that connected through the processor and the cache. The benefit of this is that a pipelined processor may access memory from different phases in its pipeline. Another benefit is that it allows the concept of super-scalar processors through different cache levels.


== See also ==


== Notes ==


== References ==


== External links ==

Memory part 2: CPU caches – an article on lwn.net by Ulrich Drepper describing CPU caches in detail
Evaluating Associativity in CPU Caches – Hill and Smith (1989) – introduces capacity, conflict, and compulsory classification
Cache Performance for SPEC CPU2000 Benchmarks – Hill and Cantin (2003) – This reference paper has been updated several times. It has thorough and lucidly presented simulation results for a reasonably wide set of benchmarks and cache organizations.
Memory Hierarchy in Cache-Based Systems Archived 2009-09-15 at the Wayback Machine – by Ruud van der Pas, 2002, Sun Microsystems – introductory article to CPU memory caching
A Cache Primer – by Paul Genua, P.E., 2004, Freescale Semiconductor, another introductory article
An 8-way set-associative cache – written in VHDL
Understanding CPU caching and performance – an article on Ars Technica by Jon Stokes
IBM POWER4 processor review – an article on ixbtlabs by Pavel Danilov
What is Cache Memory and its Types!
Memory Caching – a Princeton University lecture
CPU Cache Flushing Fallacy

---page---

# Virtual address space

In computing, a virtual address space (VAS) is an area of contiguous virtual memory locations, called virtual addresses, which an operating system makes available to a process for executing instructions and storing data, and which it maps to the address space of physical addresses in a computer's hardware memory. The range of virtual addresses usually starts at a low address and can extend to the highest address allowed by the computer's instruction set architecture and supported by the operating system's pointer size implementation, which can be 4 bytes for 32-bit or 8 bytes for 64-bit OS versions. This provides several benefits including security through process isolation, assuming each process is given a separate address space.


== Example ==
In the following description, the terminology used will be particular to the Windows NT operating system, but the concepts are applicable to other virtual memory operating systems.
When a new application on a 32-bit OS is executed, the process has a 4 GiB VAS: each one of the memory addresses (from 0 to 232 − 1) in that space can have a single byte as a value. Initially, none of them have values (- represents no value). Using or setting values in such a VAS would cause a memory exception.

            0                                           4 GiB
 VAS        |----------------------------------------------|

Then the application's executable file is mapped into the VAS. Addresses in the process VAS are mapped to bytes in the EXE file. The OS manages the mapping:

            0                                           4 GiB
 VAS        |---vvv----------------------------------------|
 mapping        |||
 file bytes     app

The symbol v represents values from bytes in the mapped file. Required DLL files are then mapped (this includes custom libraries in addition to system libraries such as kernel32.dll and user32.dll):

            0                                           4 GiB
 VAS        |---vvv--------vvvvvv---vvvv-------------------|
 mapping        |||        ||||||   ||||
 file bytes     app        kernel   user

The process then starts executing bytes in the EXE file. However, the only way the process can use or set - values in its VAS is to ask the OS to map them to bytes from a file. A common way to use VAS memory in this way is to map it to the page file. The page file is a single file, but multiple distinct sets of contiguous bytes can be mapped into a VAS:

            0                                           4 GiB
 VAS        |---vvv--------vvvvvv---vvvv---vv-----v----vvv-|
 mapping        |||        ||||||   ||||   ||     |    |||
 file bytes     app        kernel   user   system_page_file

And different parts of the page file can map into the VAS of different processes:

            0                                           4 GiB
 VAS        |---vvvv-------vvvvvv---vvvv---vv-----v----vvv-|
 mapping        ||||       ||||||   ||||   ||     |    |||
 file bytes     app1 app2  kernel   user   system_page_file
 mapping             ||||  ||||||   ||||       ||    |
 VAS 2      |--------vvvv--vvvvvv---vvvv-------vv----v-----|

On Microsoft Windows 32-bit, by default, only 2 GiB are made available to processes for their own use. The other 2 GiB are used by the operating system. On later 32-bit editions of Microsoft Windows, it is possible to extend the user-mode virtual address space to 3 GiB while only 1 GiB is left for kernel-mode virtual address space by marking the programs as IMAGE_FILE_LARGE_ADDRESS_AWARE and enabling the /3GB switch in the boot.ini file.
On Microsoft Windows 64-bit, in a process running an executable that was linked with /LARGEADDRESSAWARE:NO, the operating system artificially limits the user mode portion of the process's virtual address space to 2 GiB. This applies to both 32- and 64-bit executables. Processes running executables that were linked with the /LARGEADDRESSAWARE:YES option, which is the default for 64-bit Visual Studio 2010 and later, have access to more than 2 GiB of virtual address space: up to 4 GiB for 32-bit executables, up to 8 TiB for 64-bit executables in Windows through Windows 8, and up to 128 TiB for 64-bit executables in Windows 8.1 and later.
Allocating memory via C's malloc establishes the
page file as the backing store for any new virtual address space. However, a process can also explicitly map file bytes.


== Linux ==
For x86 32-bit CPUs, Linux allows splitting the user and kernel address ranges in different ways: 3G/1G user/kernel (default), 1G/3G user/kernel or 2G/2G user/kernel.


== See also ==
Linear address space
Single address space operating system


== References ==


== Further reading ==
Richter, Jeffrey. Advanced Windows. Microsoft Press.

---page---

# X86 memory segmentation

x86 memory segmentation is a term for the kind of memory segmentation characteristic of the Intel x86 computer instruction set architecture. The x86 architecture has supported memory segmentation since the original Intel 8086 (1978), but x86 memory segmentation is a plainly descriptive retronym. The introduction of memory segmentation mechanisms in this architecture reflects the legacy of earlier 80xx processors, which initially could only address 16 KB, or later 64 KB of memory (16,384 bytes or 65,536 bytes, respectively), and whose instructions and registers were optimised for the latter. Dealing with larger addresses and more memory was thus comparably slower, as that capability was somewhat grafted-on in the Intel 8086. Memory segmentation could keep programs compatible, relocatable in memory, and by confining significant parts of a program's operation to 64 KB segments, the program could still run faster.
In 1982, the Intel 80286 added support for virtual memory and memory protection; the original mode was renamed real mode, and the new version was named protected mode.  The x86-64 architecture, introduced in 2003, has largely dropped support for segmentation in 64-bit mode.
In both real and protected modes, the system uses 16-bit segment registers to derive the actual memory address. In real mode, the registers CS, DS, SS, and ES point to the currently used program code segment (CS), the current data segment (DS), the current stack segment (SS), and one extra segment determined by the system programmer (ES).  The Intel 80386, introduced in 1985, adds two additional segment registers, FS and GS, with no specific uses defined by the hardware. The way in which the segment registers are used differs between the two modes.
The choice of segment is normally defaulted by the processor according to the function being executed.  Instructions are always fetched from the code segment.  Any data reference to the stack, including any stack push or pop, uses the stack segment; data references indirected through the BP register typically refer to the stack and so they default to the stack segment.  The extra segment is the mandatory destination for string operations (for example MOVS or CMPS); for this one purpose only, the automatically selected segment register cannot be overridden.  All other references to data use the data segment by default.  The data segment is the default source for string operations, but it can be overridden. The instruction format allows an optional segment prefix byte which can be used to override the default segment for selected instructions if desired.


== Real mode ==

In real mode or V86 mode, the fundamental size of a segment is 65,536 bytes, with individual bytes being addressed using 16-bit offsets.
The 16-bit segment selector in the segment register is interpreted as the most significant 16 bits of a linear 20-bit address, called a segment address, of which the remaining four least significant bits are all zeros. The segment address is always added to a 16-bit offset in the instruction to yield a linear address, which is the same as physical address in this mode. For instance, the segmented address 06EFh:9234h (here the suffix "h" means hexadecimal) has a segment selector of 06EFh, representing a segment address of 06EF0h, to which the offset is added, yielding the linear address 06EF0h + 9234h = 10124h.
(The leading zeros of the linear address, segmented addresses, and the segment and offset fields are shown here for clarity. They are usually omitted.)

Because of the way the segment address and offset are added, a single linear address can be mapped to up to 212 = 4096 distinct segment:offset pairs. For example, the linear address 08124h can have the segmented addresses 06EFh:1234h, 0812h:0004h, 0000h:8124h, etc.  This could be confusing to programmers accustomed to unique addressing schemes, but it can also be used to advantage, for example when addressing multiple nested data structures.
While real mode segments are technically always 64 KB long, the practical effect is only that no segment can be longer than 64 KB, rather than that every segment as actually used in a program must be treated as 64 KB long – dealing with effectively smaller segments is possible: usable sizes range from 16 through 65,536 bytes, in 16-byte steps.  Because there is no protection or privilege limitation in real mode, it is still entirely up to the program to coordinate and keep within the bounds of any segments. This is true both when a segment is programmatically treated as smaller than, or the full 64 KB, but it is also true that any program can always access any memory by just changing segments, since it can arbitrarily set segment selectors to change segment addresses with absolutely no supervision. Therefore, while real mode can be thought of as allowing different segment lengths, and as allowing segments to be overlapping or non-overlapping as desired, none of this is restrictively enforced by the CPU.
The effective 20-bit address space of PC/XT-generation CPUs limits the addressable memory to 220 bytes, or 1,048,576 bytes (1 MB).  This derived directly from the hardware design of the Intel 8086 (and, subsequently, the closely related 8088), which had exactly 20 address pins.  (Both were packaged in 40-pin DIP packages; even with only 20 address lines, the address and data buses were multiplexed to fit all the address and data lines within the limited pin count.)

Each segment begins at a multiple of 16 bytes, called a paragraph, from the beginning of the linear (flat) address space. That is, at 16 byte intervals. Since all segments are technically 64 KB long, this explains how overlap can occur between segments and why any location in the linear memory address space can be accessed with many segment:offset pairs. The actual location of the beginning of a segment in the linear address space can be calculated with segment × 16. Such address translations are carried out by the segmentation unit of the CPU.


=== End-of-address-space quirkiness ===

The last segment, FFFFh (65535), begins at linear address FFFF0h (1048560), 16 bytes before the end of the 20-bit address space, and thus can access, with an offset of up to 65,536 bytes, up to 65,520 (65536−16) bytes past the end of the 20-bit address space of the 8086 or 8088 CPU. A further 4,094 next-highest 64K-segments also still cross that 1MB-threshold, but by less and less. On the 8086 and 8088 CPUs, these address accesses were wrapped around to the beginning of the address space such that 65535:16 would access address 0, and e.g. 65533:1000 would access address 952 of the linear address space. The fact that some programs written for the 8088 and 8086 relied on this quirky wrap-around as a feature led to the Gate A20 compatibility issues in later CPU generations, with the Intel 286 and above, where the linear address space was expanded past 20 bits.
In 16-bit real mode, enabling applications to make use of multiple memory segments for a single data structure (in order to access more memory than available in any one 64K-segment) is quite complex, but was viewed as a necessary evil for all but the smallest tools (which could do with less memory). The root of the problem is that no appropriate address-arithmetic instructions suitable for flat addressing of the entire memory range are available. Flat addressing is possible by applying multiple instructions, which however leads to slower programs.
The memory model concept derives from the setup of the segment registers. For example, in the tiny model CS=DS=ES=SS, that is the program's code, data, and stack are all contained within a single 64 KB segment. In the small memory model DS=SS, so both data and stack reside in the same segment; CS points to a different code segment of up to 64 KB.


== Protected mode ==


=== 80286 protected mode ===
The 80286's protected mode extends the processor's address space to 224 bytes (16 megabytes), but not by adjusting the shift value used to calculate a segment address from the value in a segment register.  Instead, each 16-bit segment register now contains an index into a table of segment descriptors containing 24-bit base addresses to which offsets are added. To support old software, the processor starts up in "real mode", a mode in which it uses the segmented addressing model of the 8086.  There is a small difference though: the resulting physical address is no longer truncated to 20 bits, so real mode pointers (but not 8086 pointers) can now refer to addresses from 10000016 through 10FFEF16.  This nearly 64-kilobyte region of memory was known as the High Memory Area (HMA), and later versions of DOS could use it to increase the available "conventional" memory (i.e. within the first MB), by moving parts of DOS from conventional memory into the HMA.  With the addition of the HMA, the total address space is approximately 1.06 MB.  Though the 80286 does not truncate real-mode addresses to 20 bits, a system containing an 80286 can do so with hardware external to the processor, by gating off the 21st address line, the A20 line.  The IBM PC AT provided the hardware to do this (for backward compatibility with software for the original IBM PC and PC/XT models), and so all subsequent "AT-class" PC clones did as well.
286 protected mode was seldom used as it would have excluded the large body of users with 8086/88 machines. Moreover, it still necessitated dividing memory into 64k segments like was done in real mode. This limitation can be worked around on 32-bit CPUs which permit the use of memory pointers greater than 64k in size, however as the Segment Limit field is only 24-bit long, the maximum segment size that can be created is 16MB (although paging can be used to allocate more memory, no individual segment may exceed 16MB). This method was commonly used on Windows 3.x applications to produce a flat memory space, although as the OS itself was still 16-bit, API calls could not be made with 32-bit instructions. Thus, it was still necessary to place all code that performs API calls in 64k segments.
Once 286 protected mode is invoked, it could not normally be exited except by performing a hardware reset. Machines following the rising IBM PC/AT standard could feign a reset to the CPU via the standardised keyboard controller, but this was significantly sluggish. Windows 3.x worked around both of these problems by intentionally triggering a triple fault in the interrupt-handling mechanisms of the CPU, which would cause the IBM AT-compatible hardware to reset the CPU, nearly instantly, thus causing it to drop back into real mode.


=== Detailed segmentation unit workflow ===
A logical address consists of a 16-bit segment selector (supplying 13+1 address bits) and a 16-bit offset. The segment selector must be located in one of the segment registers. That selector consists of a 2-bit Requested Privilege Level (RPL), a 1-bit Table Indicator (TI), and a 13-bit index.
When attempting address translation of a given logical address, the processor reads the 64-bit segment descriptor structure from either the Global Descriptor Table when TI=0 or the Local Descriptor Table when TI=1. It then performs the privilege check:

max(CPL, RPL) ≤ DPL
where CPL is the current privilege level (found in the lower 2 bits of the CS register), RPL is the requested privilege level from the segment selector, and DPL is the descriptor privilege level of the segment (found in the descriptor).  All privilege levels are integers in the range 0–3, where the lowest number corresponds to the highest privilege.
If the inequality is false, the processor generates a general protection (GP) fault.  Otherwise, address translation continues.  The processor then takes the 16-bit offset and compares it against the segment limit specified in the segment descriptor.  If it is larger, a GP fault is generated.  Otherwise, the processor adds the 24-bit segment base, specified in descriptor, to the offset, creating a linear physical address.
The privilege check is done only when the segment register is loaded, because segment descriptors are cached in hidden parts of the segment registers.


=== 80386 protected mode ===
In the Intel 80386 and later, protected mode retains the segmentation mechanism of 80286 protected mode, but a paging unit has been added as a second layer of address translation between the segmentation unit and the physical bus.  Also, importantly, address offsets are 32-bit (instead of 16-bit), and the segment base in each segment descriptor is also 32-bit (instead of 24-bit).  The general operation of the segmentation unit is otherwise unchanged.  The paging unit may be enabled or disabled; if disabled, operation is the same as on the 80286.  If the paging unit is enabled, addresses in a segment are now virtual addresses, rather than physical addresses as they were on the 80286.  That is, the segment starting address, the offset, and the final 32-bit address the segmentation unit derived by adding the two are all virtual (or logical) addresses when the paging unit is enabled.  When the segmentation unit generates and validates these 32-bit virtual addresses, the enabled paging unit finally translates these virtual addresses into physical addresses.  The physical addresses are 32-bit on the 386, but can be larger on newer processors which support Physical Address Extension.
As mentioned above, the 80386 also introduced two new general-purpose data segment registers, FS and GS, to the original set of four segment registers (CS, DS, ES, and SS).
A 386 CPU can be put back into real mode by clearing a bit in the CR0 control register, however this is a privileged operation in order to enforce security and robustness. By way of comparison, a 286 could only be returned to real mode by forcing a processor reset, e.g. by a triple fault or using external hardware.


== Later developments ==
The x86-64 architecture does not use segmentation in long mode (64-bit mode). Four of the segment registers, CS, SS, DS, and ES, are forced to base address 0, and the limit to 264. The segment registers FS and GS can still have a nonzero base address. This allows operating systems to use these segments for special purposes. Unlike the global descriptor table mechanism used by legacy modes, the base address of these segments is stored in a model-specific register. The x86-64 architecture further provides the special SWAPGS instruction, which allows swapping the kernel mode and user mode base addresses.
For instance, Microsoft Windows on x86-64 uses the GS segment to point to the Thread Environment Block, a small data structure for each thread, which contains information about exception handling, thread-local variables, and other per-thread state. Similarly, the Linux kernel uses the GS segment to store per-CPU data.
GS/FS are also used in gcc's thread-local storage and canary-based stack protector.


== Practices ==
Logical addresses can be explicitly specified in x86 assembly language, e.g. (AT&T syntax):

movl $42, %fs:(%eax)  ; Equivalent to M[fs:eax]<-42) in RTL

or in Intel syntax:

However, segment registers are usually used implicitly.

All CPU instructions are implicitly fetched from the code segment specified by the segment selector held in the CS register.
Most memory references come from the data segment specified by the segment selector held in the DS register.  These may also come from any segment specified by the segment selector held in the respective segment register, if a segment-override prefix precedes the instruction that makes the memory reference.  Most, but not all, instructions that use DS by default will accept any other override prefix.
Processor stack references, either implicitly (e.g. push and pop instructions) or explicitly (memory accesses using the (E)SP or (E)BP registers) use the stack segment specified by the segment selector held in the SS register.  For explicit references, the segment may be overridden.
String instructions (e.g. stos, movs, cmps) use the extra segment for the destination string specified by the segment selector held in the ES register.
Segmentation cannot be turned off on x86-32 processors (this is true for 64-bit mode as well, but beyond the scope of discussion), so many 32-bit operating systems simulate a flat memory model by setting all segments' bases to 0 in order to make segmentation neutral to programs.  For instance, the Linux kernel sets up only 4 general purpose segments:

Since the base is set to 0 in all cases and the limit 4 GiB, the segmentation unit does not affect the addresses the program issues before they arrive at the paging unit.  (This, of course, refers to 80386 and later processors, as the earlier x86 processors do not have a paging unit.)
Current Linux also uses GS to point to thread-local storage.
Segments can be defined to be either code, data, or system segments.  Additional permission bits are present to make segments read only, read/write, execute, etc.
In protected mode, code may always modify all segment registers except CS (the code segment selector).  This is because the current privilege level (CPL) of the processor is stored in the lower 2 bits of the CS register.  The only ways to raise the processor privilege level (and reload CS) are through the lcall (far call) and int (interrupt) instructions.  Similarly, the only ways to lower the privilege level (and reload CS) are through lret (far return) and iret (interrupt return) instructions.  In real mode, code may also modify the CS register by making a far jump (or using an undocumented POP CS instruction on the 8086 or 8088).  Of course, in real mode, there are no privilege levels; all programs have absolute unchecked access to all of memory and all CPU instructions.
For more information about segmentation, see the IA-32 manuals freely available on the AMD or Intel websites.


== Notes and references ==


== See also ==
x86 memory models
THE multiprogramming system
Split octal


== External links ==
Home of the IA-32 Intel Architecture Software Developer's Manual
The Segment:Offset Addressing Scheme