import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

class DestinationWindow:
    def __init__(self, root, file_name, destinations, on_confirm, on_cancel):
        self.root = root
        self.file_name = file_name
        self.destinations_file = "destinations.txt"
        self.destinations = destinations
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        # Create a new top-level window for destination selection
        self.window = tk.Toplevel(root)
        self.window.title(f"Move: {self.file_name}")
        self.center_window(self.window, 400, 350)  # Center window on the screen

        # Label showing the file to move
        self.label = tk.Label(self.window, text=f"Select destination for {self.file_name}")
        self.label.pack(pady=10)

        self.truncated_dest = []
        max_length = 40
        for dest in self.destinations:
            if len(dest) > max_length:
                truncated = dest[:20] + ' ...' + dest[-20:]
            else:
                truncated = dest
            self.truncated_dest.append(truncated)

        # Listbox to display destinations
        self.listbox = tk.Listbox(self.window, height=10, width=40)
        for destination in self.truncated_dest:
            self.listbox.insert(tk.END, destination)
        self.listbox.pack(pady=10)

        # Add New Destination button
        self.add_button = tk.Button(self.window, text="Add New Destination", command=self.add_new_destination)
        self.add_button.pack(pady=5)

        # Frame to horizontally align buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)

        # Confirm button
        self.confirm_button = tk.Button(button_frame, text="Confirm", command=self.confirm_selection)
        self.confirm_button.pack(side=tk.LEFT, padx=10)

        # Cancel button
        self.cancel_button = tk.Button(button_frame, text="Cancel", command=self.cancel_selection)
        self.cancel_button.pack(side=tk.LEFT, padx=10)

    def center_window(self, window, width, height):
        # Get screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculate position for the window to be centered
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)

        # Set window geometry
        window.geometry(f'{width}x{height}+{position_right}+{position_top}')

    def confirm_selection(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_destination = self.destinations[selected_index[0]]
            print(f"File {self.file_name} will be moved to {selected_destination}.")
            self.on_confirm(selected_destination)
            self.window.destroy()  # Close the window after confirming
        else:
            print("No selection made. Please select a destination from the list.")

    def cancel_selection(self):
        # Log cancel and move to next file
        print(f"File {self.file_name} was skipped.")
        self.on_cancel()
        self.window.destroy()  # Close the window after canceling

    def add_new_destination(self):
        # Ask the user to select a new destination directory
        new_dest = filedialog.askdirectory(title="Select New Destination")
        if new_dest:
            if new_dest not in self.destinations:
                self.destinations.append(new_dest)
                if len(new_dest) > 40:
                    truncated = new_dest[:20] + ' ...' + new_dest[-20:]
                    self.listbox.insert(tk.END, truncated)
                else:
                    self.listbox.insert(tk.END, new_dest)
                print(f"New destination added: {new_dest}")
                self.save_destinations()  # Save updated list to the file

    def save_destinations(self):
        """ Save the current destinations list to the file. """
        with open(self.destinations_file, "w") as f:
            for destination in self.destinations:
                f.write(f"{destination}\n")


class FileMoverApp:
    def __init__(self, root):
        self.root = root
        self.destinations_file = "destinations.txt"
        self.destinations = self.load_destinations()
        self.source_folder = self.select_source_folder()
        if not self.source_folder:
            self.source_folder = os.getcwd()

        self.file_list = [f for f in os.listdir(self.source_folder) if os.path.isfile(os.path.join(self.source_folder, f))]
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_frame = tk.Frame(frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.label_left = tk.Label(self.left_frame, text="Files to Move:")
        self.label_left.pack(pady=10)

        self.file_listbox = tk.Listbox(self.left_frame, width=30, height=10)
        for file in self.file_list:
            self.file_listbox.insert(tk.END, file)
        self.file_listbox.pack(pady=10)

        self.middle_frame = tk.Frame(frame)
        self.middle_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        self.reload_button = tk.Button(self.middle_frame, text="Reload", command=self.load_destinations)
        self.reload_button.pack(pady=10)

        self.right_frame = tk.Frame(frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.label_right = tk.Label(self.right_frame, text="Stored Locations:")
        self.label_right.pack(pady=10)

        self.dest_listbox = tk.Listbox(self.right_frame, width=30, height=10)

        for destination in self.destinations:
            self.dest_listbox.insert(tk.END, destination)
        self.dest_listbox.pack(pady=10)

        self.move_button = tk.Button(self.root, text="Move All Files", command=self.move_file)
        self.move_button.pack(pady=10)

    def select_source_folder(self):
        folder = filedialog.askdirectory(title="Select Source Folder", initialdir=os.getcwd())
        return folder if folder else None

    def move_file(self):
        # Start a loop to go through all files
        self.process_next_file(0)

    def process_next_file(self, index):
        if index < len(self.file_list):
            file_name = self.file_list[index]
            self.open_destination_window(file_name, index)
        else:
            print("All files have been processed.")

    def open_destination_window(self, file_name, file_index):
        # Open the destination window for selecting a destination
        def on_confirm(destination):
            # Move the file once a destination is selected
            source_file_path = os.path.join(self.source_folder, file_name)
            destination_file_path = os.path.join(destination, file_name)
            try:
                shutil.move(source_file_path, destination_file_path)
                print(f"File {file_name} moved to {destination}")
                self.file_listbox.delete(self.file_listbox.get(0, tk.END).index(file_name))  # Remove file from the listbox
                # Process next file
                self.process_next_file(file_index + 1)
            except Exception as e:
                print(f"Error moving file {file_name}: {str(e)}")

        def on_cancel():
            # Skip the current file and move to the next
            self.process_next_file(file_index + 1)

        # Open the DestinationWindow and pass the callback functions (on_confirm and on_cancel)
        DestinationWindow(self.root, file_name, self.destinations, on_confirm, on_cancel)

    def load_destinations(self):
        if not os.path.exists(self.destinations_file):
            with open(self.destinations_file, "w") as f:
                pass
        
        with open(self.destinations_file, "r") as f:
            destinations = f.read().splitlines()
        
        return destinations


if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Mover")
    app = FileMoverApp(root)
    root.mainloop()


