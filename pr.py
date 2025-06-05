import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
import threading
import yt_dlp
import re
import datetime
import os

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("800x400")
        self.root.resizable(False, False)

        icon_path = "Solo\\SQL\\Graphics-Vibe-Classic-3d-Social-Youtube.256.png"
        if os.path.exists(icon_path):
            self.icon = PhotoImage(file=icon_path)
            self.root.iconphoto(True, self.icon)

        self.download_path = tk.StringVar(value="Path not selected")
        self.progress_var = tk.DoubleVar(value=0)
        self.mode = tk.StringVar(value="url")
        self.previous_input = ""

        self.left_frame = tk.Frame(root, width=300, height=400, bg="black")
        self.left_frame.pack(side="left", fill="y")

        self.info_label = tk.Label(
            self.left_frame,
            text="Video info",
            justify="left",
            anchor="nw",
            fg="white",
            bg="black",
            font=("Arial", 10),
            wraplength=290
        )
        self.info_label.pack(padx=10, pady=10, anchor="nw", fill="both")

        self.search_results_listbox = tk.Listbox(self.left_frame, width=45, bg="black", fg="white")
        self.search_results_listbox.pack(pady=5, padx=10, anchor="nw", fill="both")
        self.search_results_listbox.bind('<<ListboxSelect>>', self.on_search_result_select)
        self.search_results = []

        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side="right", fill="both", expand=True)

        mode_frame = tk.Frame(self.right_frame)
        mode_frame.pack(pady=5)
        tk.Radiobutton(mode_frame, text="URL", variable=self.mode, value="url", command=self.update_mode).pack(side="left")
        tk.Radiobutton(mode_frame, text="Search", variable=self.mode, value="search", command=self.update_mode).pack(side="left")

        self.search_button = tk.Button(self.right_frame, text="Search", command=self.manual_search)
        self.search_button.pack_forget()

        self.input_label = tk.Label(self.right_frame, text="YouTube video URL:")
        self.input_entry = tk.Entry(self.right_frame, width=60)

        self.choose_path_button = tk.Button(self.right_frame, text="Choose folder...", command=self.choose_path)
        self.path_label = tk.Label(self.right_frame, textvariable=self.download_path, fg="blue")

        self.progress_label = tk.Label(self.right_frame, text="Progress: ---")
        self.progress_bar = ttk.Progressbar(self.right_frame, orient="horizontal", length=400, mode="determinate", variable=self.progress_var)

        self.download_button = tk.Button(self.right_frame, text="Download Video", command=self.start_download_thread)
        self.exit_button = tk.Button(self.right_frame, text="Exit", command=self.exit)

        self.input_label.pack(pady=5)
        self.input_entry.pack(pady=5)
        self.choose_path_button.pack(pady=5)
        self.path_label.pack(pady=2)
        self.progress_label.pack(pady=5)
        self.progress_bar.pack(pady=5)
        self.download_button.pack(pady=10)
        self.exit_button.pack(pady=5)

    def update_mode(self):
        mode = self.mode.get()
        if mode == "url":
            self.input_label.config(text="YouTube video URL:")
            self.search_button.pack_forget()
            self.search_results_listbox.delete(0, tk.END)
        else:
            self.input_label.config(text="Enter search topic:")
            self.search_button.pack(before=self.input_label, pady=5)

    def choose_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)

    def manual_search(self):
        query = self.input_entry.get().strip()
        self.update_search_results(query)

    def update_video_info(self, url):
        pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$'
        if not re.match(pattern, url):
            self.info_label.config(text="Enter a valid URL.")
            return

        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
            title = info.get('title', 'N/A')
            uploader = info.get('uploader', 'N/A')
            upload_date = info.get('upload_date', '')
            date_str = 'N/A'
            if upload_date:
                date_str = datetime.datetime.strptime(upload_date, '%Y%m%d').strftime('%d.%m.%Y')

            info_text = f"Title: {title}\nUploader: {uploader}\nDate: {date_str}"
            self.info_label.config(text=info_text)
        except Exception as e:
            self.info_label.config(text=f"Error: {e}")

    def update_search_results(self, query):
        if not query:
            self.info_label.config(text="Enter a topic to search.")
            self.search_results_listbox.delete(0, tk.END)
            return

        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                search_query = f"ytsearch5:{query}"
                info = ydl.extract_info(search_query, download=False)
                entries = info.get('entries', [])
                self.search_results = entries
                self.search_results_listbox.delete(0, tk.END)
                for idx, entry in enumerate(entries):
                    title = entry.get('title', 'No title')
                    uploader = entry.get('uploader', 'No uploader')
                    upload_date = entry.get('upload_date', '')
                    date_str = 'N/A'
                    if upload_date:
                        date_str = datetime.datetime.strptime(upload_date, '%Y%m%d').strftime('%d.%m.%Y')
                    display_text = f"{idx+1}. {title} | {uploader} | {date_str}"
                    self.search_results_listbox.insert(tk.END, display_text)
                self.info_label.config(text="Select a video from the list.")
        except Exception as e:
            self.info_label.config(text=f"Search error: {e}")
            self.search_results_listbox.delete(0, tk.END)

    def on_search_result_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            selected_video = self.search_results[index]
            video_url = selected_video.get('webpage_url', '')
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, video_url)
            self.mode.set("url")
            self.update_mode()
            self.update_video_info(video_url)

    def start_download_thread(self):
        thread = threading.Thread(target=self.download_video)
        thread.start()

    def download_video(self):
        url = self.input_entry.get().strip()
        path = self.download_path.get()
        if not url or path == "Path not selected":
            messagebox.showwarning("Error", "Please enter a URL and select a folder.")
            return

        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '0.0%').strip()
                try:
                    val = float(percent.strip('%'))
                    self.progress_var.set(val)
                    self.progress_label.config(text=f"Progress: {percent}")
                except:
                    pass
                self.root.update_idletasks()
            elif d['status'] == 'finished':
                self.progress_label.config(text="Download complete!")
                self.progress_var.set(100)
                self.root.update_idletasks()
                messagebox.showinfo("Done", f"Video downloaded to:\n{path}")

        ydl_opts = {
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
            'quiet': True,
            'noplaylist': True,
            'format': 'mp4',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download video:\n{str(e)}")

    def exit(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
