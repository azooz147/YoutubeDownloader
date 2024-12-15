import os
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import yt_dlp as youtube_dl


output_path = "downloads"
ffmpeg_path = r'C:/ffmpeg/bin/ffmpeg.exe'
download_cancelled = threading.Event()
download_paused = threading.Event()  
current_download = None
download_thread = None


def download_video(url, quality, download_type):
    global download_cancelled, download_paused, current_download
    ydl_opts = {
        'ffmpeg_location': ffmpeg_path,
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'noplaylist': True
    }

    if download_type == 'video':
        ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best'
    elif download_type == 'audio':
        ydl_opts['format'] = 'bestaudio'

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            download_cancelled.clear()
            download_paused.clear()
            current_download = ydl
            ydl.download([url])

            if not download_cancelled.is_set():
                messagebox.showinfo("Success", f"Downloaded {download_type} successfully!")
            else:
                messagebox.showinfo("Cancelled", "Download was cancelled.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        update_ui_for_idle()


def update_ui_for_idle():
    download_button.config(state="normal")
    progress_bar['value'] = 0  # Reset progress bar after download completes


def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        root.after(0, update_progress_bar, percent)
    elif d['status'] == 'finished':
        print(f"Download finished: {d['filename']}")
        root.after(0, update_progress_bar, 100)


def update_progress_bar(percent):
    progress_bar['value'] = percent
    root.update_idletasks()


def start_download():
    url = url_entry.get()
    quality = quality_var.get()
    download_type = download_type_var.get()

    download_button.config(state="disabled")  # Disable the download button while downloading
    progress_bar['value'] = 0  # Reset the progress bar at the start

    global download_thread
    download_thread = threading.Thread(target=download_video, args=(url, quality, download_type))
    download_thread.start()


def choose_output_folder():
    global output_path
    folder = filedialog.askdirectory(initialdir=output_path, title="Select Output Folder")
    if folder:
        output_path = folder
        output_label.config(text=f"Output folder: {output_path}")


def on_close():
    if download_thread and download_thread.is_alive():
        if messagebox.askokcancel("Quit", "Download in progress. Are you sure you want to quit?"):
            download_cancelled.set()  # Signal cancellation of download
            root.quit()
    else:
        root.quit()


# Create the main window
root = tk.Tk()
root.title("YouTube Downloader")

# Create a main frame to hold all widgets
main_frame = tk.Frame(root, padx=20, pady=20)
main_frame.pack(padx=20, pady=20)

# URL input frame
url_frame = tk.Frame(main_frame)
url_frame.grid(row=0, column=0, pady=10, sticky="w")

tk.Label(url_frame, text="Enter YouTube URL:").pack(side="left")
url_entry = tk.Entry(url_frame, width=40)
url_entry.pack(side="left", padx=5)

# Quality selection frame
quality_frame = tk.Frame(main_frame)
quality_frame.grid(row=1, column=0, pady=10, sticky="w")

tk.Label(quality_frame, text="Video Quality:").pack(side="left")
quality_var = tk.StringVar(value="720")
quality_menu = tk.OptionMenu(quality_frame, quality_var, "720", "1080", "480", "360")
quality_menu.pack(side="left", padx=5)

# Download type selection frame
download_type_frame = tk.Frame(main_frame)
download_type_frame.grid(row=2, column=0, pady=10, sticky="w")

tk.Label(download_type_frame, text="Download Type:").pack(side="left")
download_type_var = tk.StringVar(value="video")
download_type_menu = tk.OptionMenu(download_type_frame, download_type_var, "video", "audio")
download_type_menu.pack(side="left", padx=5)

# Output folder selection
output_button_frame = tk.Frame(main_frame)
output_button_frame.grid(row=3, column=0, pady=10, sticky="w")

output_button = tk.Button(output_button_frame, text="Output", command=choose_output_folder)
output_button.pack(side="left", padx=5)

output_label = tk.Label(output_button_frame, text=f"Output: {output_path}")
output_label.pack(side="left", padx=5)

# Progress bar frame
progress_frame = tk.Frame(main_frame)
progress_frame.grid(row=4, column=0, pady=20, sticky="w")

progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=350, mode="determinate")
progress_bar.pack(pady=5)

# Download button
download_button = tk.Button(main_frame, text="Download", command=start_download, width=20)
download_button.grid(row=5, column=0, pady=10)

# Closing the application gracefully
root.protocol("WM_DELETE_WINDOW", on_close)

# Start the Tkinter event loop
root.mainloop()
