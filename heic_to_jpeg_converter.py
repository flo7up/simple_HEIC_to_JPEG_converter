import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image
import pillow_heif
from send2trash import send2trash
import threading
import traceback

# Register HEIF format with Pillow
pillow_heif.register_heif_opener()

# Function to convert HEIC to JPEG
def convert_heic_to_jpeg(heic_path, jpeg_path, log):
    image = Image.open(heic_path)
    image.save(jpeg_path, "JPEG")
    log.insert(tk.END, f"Converted: {heic_path} to {jpeg_path}\n")

# Function to scan a folder and convert all HEIC files to JPEG
def convert_folder_heic_to_jpeg(folder_path, scan_subfolders, log, status):
    status.set("Converting...")  # Update status bar
    folder_path = os.path.normpath(folder_path)  # Normalize the folder path
    for dirpath, _, filenames in os.walk(folder_path):
        dirpath = os.path.normpath(dirpath)  # Normalize the directory path
        for file in filenames:
            if file.lower().endswith(".heic"):
                heic_file_path = os.path.join(dirpath, file)
                jpeg_file_path = os.path.join(dirpath, f"{os.path.splitext(file)[0]}.jpeg")

                heic_file_path = os.path.normpath(heic_file_path)  # Normalize the file path
                jpeg_file_path = os.path.normpath(jpeg_file_path)  # Normalize the output file path

                try:
                    convert_heic_to_jpeg(heic_file_path, jpeg_file_path, log)
                    
                    # Try moving the HEIC file to the bin after successful conversion
                    try:
                        send2trash(heic_file_path)
                        log.insert(tk.END, f"Moved {heic_file_path} to the recycle bin\n")
                    except OSError as e:
                        log.insert(tk.END, f"Error moving file to recycle bin: {heic_file_path}\n")
                        log.insert(tk.END, f"Error details: {str(e)}\n")
                
                except Exception as e:
                    log.insert(tk.END, f"Failed to convert {heic_file_path}: {str(e)}\n")
                    log.insert(tk.END, traceback.format_exc())

        if not scan_subfolders:
            break  # Do not process subfolders if the checkbox is not checked

    log.insert(tk.END, "All conversions are complete.\n")
    log.see(tk.END)  # Scroll to the end of the log
    status.set("Conversion completed.")  # Update status bar

# Function to be called when "Start" is clicked
def start_conversion(folder_path, scan_subfolders, log, status):
    if not folder_path:
        messagebox.showerror("Error", "Please select a folder.")
        return

    log.insert(tk.END, f"Starting conversion in folder: {folder_path}\n")
    log.insert(tk.END, "Scanning subfolders: {}\n".format("Yes" if scan_subfolders else "No"))

    # Run the conversion in a separate thread to keep the UI responsive
    threading.Thread(target=convert_folder_heic_to_jpeg, args=(folder_path, scan_subfolders, log, status)).start()

# Function to select folder
def select_folder(entry):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry.delete(0, tk.END)
        entry.insert(0, folder_selected)

# GUI Setup with better aesthetics
def create_gui():
    window = tk.Tk()
    window.title("HEIC to JPEG Converter")
    window.geometry("600x500")
    window.config(bg="#f0f0f0")

    # Font settings
    font_label = ("Helvetica", 10)
    font_button = ("Helvetica", 10, "bold")

    # Status bar
    status = tk.StringVar()
    status.set("Waiting to start...")
    status_bar = ttk.Label(window, textvariable=status, relief=tk.SUNKEN, anchor="w")
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Main frame for better structure
    main_frame = tk.Frame(window, bg="#f0f0f0", padx=10, pady=10)
    main_frame.pack(fill="both", expand=True)

    # Folder selection
    tk.Label(main_frame, text="Select Folder:", font=font_label, bg="#f0f0f0").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    folder_entry = tk.Entry(main_frame, width=40)
    folder_entry.grid(row=0, column=1, padx=10, pady=5)
    browse_button = tk.Button(main_frame, text="Browse", command=lambda: select_folder(folder_entry), font=font_button, bg="#007acc", fg="white", padx=10)
    browse_button.grid(row=0, column=2, padx=10, pady=5)

    # Checkbox for scanning subfolders
    scan_subfolders_var = tk.BooleanVar()
    scan_subfolders_check = tk.Checkbutton(main_frame, text="Scan subfolders", variable=scan_subfolders_var, font=font_label, bg="#f0f0f0")
    scan_subfolders_check.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    # Start button
    start_button = tk.Button(main_frame, text="Start", command=lambda: start_conversion(folder_entry.get(), scan_subfolders_var.get(), log, status), font=font_button, bg="#28a745", fg="white", padx=20)
    start_button.grid(row=2, column=1, pady=20)

    # Log window (ScrolledText widget for displaying progress)
    log = scrolledtext.ScrolledText(main_frame, width=70, height=15, font=("Courier", 10), wrap="word", bg="#eaeaea")
    log.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
    log.insert(tk.END, "Welcome to the HEIC to JPEG Converter.\n")

    # Start the Tkinter main loop
    window.mainloop()

if __name__ == "__main__":
    create_gui()