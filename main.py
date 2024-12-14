import tkinter as tk
from tkinter import messagebox, simpledialog
import math


class BuddySystemMemoryAllocator:
    def __init__(self, total_memory_size=1024):
        self.total_memory_size = total_memory_size
        self.memory_blocks = {total_memory_size: 1}
        self.allocated_blocks = {}
        self.free_blocks = {total_memory_size: 1}
        self.allocation_log = []
        self.current_step = 1  # Add a class-level step tracker

    def merge_buddies(self, start_block_size):
        """
        Recursively merge buddy blocks
        """
        current_block_size = start_block_size
        while current_block_size < self.total_memory_size:
            merged = False
            for block_size in sorted(self.free_blocks.keys()):
                if block_size == current_block_size:
                    buddy_size = block_size
                    if self.free_blocks.get(buddy_size, 0) >= 2:
                        self.free_blocks[buddy_size] -= 2
                        merged_size = buddy_size * 2
                        self.free_blocks[merged_size] = self.free_blocks.get(merged_size, 0) + 1
                        self.allocation_log.append(
                            f"   Merged two {buddy_size} KB blocks into one {merged_size} KB block")
                        current_block_size = merged_size
                        merged = True
                        break
            if not merged:
                break

        self.free_blocks = {k: v for k, v in self.free_blocks.items() if v > 0}

    def allocate_memory(self, size):
        self.allocation_log = []
        allocation_size = 2 ** math.ceil(math.log2(size))

        self.allocation_log.append(f"{self.current_step}. Process for allocating {size} KB:")
        self.allocation_log.append(f"   Required block size: {allocation_size} KB")

        for block_size, count in sorted(self.free_blocks.items()):
            if block_size >= allocation_size and count > 0:
                self.free_blocks[block_size] -= 1
                self.allocated_blocks[allocation_size] = self.allocated_blocks.get(allocation_size, 0) + 1

                current_block_size = block_size
                while current_block_size > allocation_size:
                    current_block_size //= 2
                    self.free_blocks[current_block_size] = self.free_blocks.get(current_block_size, 0) + 1

                    if current_block_size * 2 != block_size:
                        self.allocation_log.append(
                            f"   Split {current_block_size * 2} KB block into two {current_block_size} KB blocks")

                self.allocation_log.append(f"   Successfully allocated {allocation_size} KB block")
                self.free_blocks = {k: v for k, v in self.free_blocks.items() if v > 0}

                self.current_step += 1
                return allocation_size

        self.allocation_log.append("   Allocation failed: No suitable memory block available")
        self.current_step += 1
        return None

    def free_memory(self, size):
        self.allocation_log = []
        block_size = 2 ** math.ceil(math.log2(size))

        self.allocation_log.append(f"{self.current_step}. Process for freeing {size} KB:")
        self.allocation_log.append(f"   Block size to free: {block_size} KB")

        if self.allocated_blocks.get(block_size, 0) > 0:
            self.allocated_blocks[block_size] -= 1
            if self.allocated_blocks[block_size] == 0:
                del self.allocated_blocks[block_size]

            self.free_blocks[block_size] = self.free_blocks.get(block_size, 0) + 1
            self.allocation_log.append(f"   Successfully freed {block_size} KB block")
            self.allocation_log.append(f"   Added {block_size} KB block back to free memory")

            self.merge_buddies(block_size)

            self.allocation_log.append("\n   Current Memory State:")
            for size in sorted(self.free_blocks.keys(), reverse=True):
                count = self.free_blocks[size]
                if count > 0:
                    self.allocation_log.append(f"   - {count} free block(s) of {size} KB")

            for size in sorted(self.allocated_blocks.keys(), reverse=True):
                count = self.allocated_blocks[size]
                if count > 0:
                    self.allocation_log.append(f"   - {count} allocated block(s) of {size} KB")

            self.current_step += 1
            return True
        else:
            self.allocation_log.append("   Error: No allocated block of this size found")
            self.current_step += 1
            return False


class BuddySystemGUI:
    def __init__(self, master):
        self.master = master
        master.title("Buddy System Memory Allocation")
        master.geometry("600x800")

        self.title_label = tk.Label(
            master,
            text="Buddy System Memory Allocation",
            font=("Helvetica", 16, "bold"),
            pady=10
        )
        self.title_label.pack()

        self.allocator = BuddySystemMemoryAllocator()

        # Memory Allocation Frame
        self.alloc_frame = tk.Frame(master)
        self.alloc_frame.pack(pady=10)

        tk.Label(self.alloc_frame, text="Memory Allocation Size (KB):").pack(side=tk.LEFT)
        self.alloc_entry = tk.Entry(self.alloc_frame, width=10)
        self.alloc_entry.pack(side=tk.LEFT, padx=5)

        self.alloc_button = tk.Button(
            master=self.alloc_frame,
            text="Allocate",
            command=self.allocate,
            bg='#90EE90',  # Light green
            fg='black',
            activebackground='#98FB98',
            padx=10,
            pady=5
        )
        self.alloc_button.pack(side=tk.LEFT)

        # Memory Deallocation Frame
        self.free_frame = tk.Frame(master)
        self.free_frame.pack(pady=10)

        tk.Label(self.free_frame, text="Memory to Free (KB):").pack(side=tk.LEFT)
        self.free_entry = tk.Entry(self.free_frame, width=10)
        self.free_entry.pack(side=tk.LEFT, padx=5)

        self.free_button = tk.Button(
            master=self.free_frame,
            text="Free",
            command=self.free_memory,
            bg='#ADD8E6',  # Light blue
            fg='black',
            activebackground='#87CEFA',
            padx=10,
            pady=5
        )
        self.free_button.pack(side=tk.LEFT)

        # Log Display
        self.status_text = tk.Text(master, height=30, width=70)
        self.status_text.pack(pady=10)

    def allocate(self):
        try:
            size = int(self.alloc_entry.get())
            allocated_size = self.allocator.allocate_memory(size)

            self.status_text.delete(1.0, tk.END)

            for log_entry in self.allocator.allocation_log:
                self.status_text.insert(tk.END, log_entry + "\n")

            if allocated_size:
                messagebox.showinfo("Success", f"Allocated {allocated_size} KB")
            else:
                messagebox.showerror("Error", "No suitable memory block found")

            self.alloc_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")

    def free_memory(self):
        try:
            size = int(self.free_entry.get())
            self.status_text.delete(1.0, tk.END)

            success = self.allocator.free_memory(size)
            for log_entry in self.allocator.allocation_log:
                self.status_text.insert(tk.END, log_entry + "\n")

            if success:
                messagebox.showinfo("Success", f"Freed {size} KB")
            else:
                messagebox.showerror("Error", "Failed to free memory block")

            self.free_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")


def main():
    root = tk.Tk()
    app = BuddySystemGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()