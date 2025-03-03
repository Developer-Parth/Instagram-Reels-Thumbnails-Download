import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import instaloader
import itertools
import os
from datetime import datetime
from PIL import Image, ImageTk
import requests

class InstaReelDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Developer Parth")
        self.root.geometry("400x800")  # Increased height to accommodate new features
        self.root.configure(bg='black')

        self.colors = itertools.cycle(['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet'])
        self.animating = True

        # Title Label
        self.label_title = tk.Label(self.root, text="Dev Parth", bg="black", fg="white", font=("Helvetica", 20, "bold"))
        self.label_title.pack(pady=10)

        # URL Entry
        self.label_url = tk.Label(self.root, text="Enter Instagram Reel URLs (comma-separated):", bg="black", fg="white")
        self.label_url.pack(pady=5)
        self.entry_url = tk.Entry(self.root, width=50)
        self.entry_url.pack(pady=5)

        # Buttons Frame for Paste and Clear Buttons
        self.frame_buttons = tk.Frame(self.root, bg="black")
        self.frame_buttons.pack(pady=5)

        # Paste and Clear Buttons
        self.button_paste = tk.Button(self.frame_buttons, text="Paste", command=self.paste_url, bg="blue", fg="white")
        self.button_paste.pack(side=tk.LEFT, padx=5)
        self.button_clear = tk.Button(self.frame_buttons, text="Clear", command=self.clear_url, bg="yellow", fg="black")
        self.button_clear.pack(side=tk.LEFT, padx=5)

        # Custom Naming Pattern
        self.label_naming_pattern = tk.Label(self.root, text="Custom Naming Pattern:", bg="black", fg="white")
        self.label_naming_pattern.pack(pady=5)
        self.entry_naming_pattern = tk.Entry(self.root, width=50)
        self.entry_naming_pattern.insert(0, "{username}_{date}_{shortcode}.mp4")  # Default pattern
        self.entry_naming_pattern.pack(pady=5)

        # Other Buttons
        self.button_fav_dir = tk.Button(self.root, text="Set Favorite Directory", command=self.set_fav_directory, bg="green", fg="white")
        self.button_fav_dir.pack(pady=5)
        self.button_download = tk.Button(self.root, text="Download Reels", command=self.download_reels, bg="red", fg="white")
        self.button_download.pack(pady=5)
        self.button_download_thumbnail = tk.Button(self.root, text="Download Thumbnails", command=self.download_thumbnails, bg="purple", fg="white")
        self.button_download_thumbnail.pack(pady=5)
        self.button_history = tk.Button(self.root, text="View History", command=self.view_history, bg="orange", fg="black")
        self.button_history.pack(pady=5)

        # Favorite Directory Label
        self.label_fav_dir = tk.Label(self.root, text="Favorite Directory: Not set", bg="black", fg="white")
        self.label_fav_dir.pack(pady=5)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient='horizontal', length=300, mode='determinate')
        self.progress.pack(pady=10)
        self.progress_label = tk.Label(self.root, text="", bg="black", fg="white")
        self.progress_label.pack(pady=5)

        # Dark Mode Toggle
        self.dark_mode = tk.BooleanVar(value=True)
        self.toggle_dark_mode = tk.Checkbutton(self.root, text="Dark Mode", variable=self.dark_mode, command=self.switch_mode, bg="black", fg="white", selectcolor="grey")
        self.toggle_dark_mode.pack(pady=5)

        # History Log - Initially Hidden
        self.history_log = tk.Listbox(self.root, width=50, height=10)
        
        self.fav_directory = None
        self.animate()

    def animate(self):
        color = next(self.colors)
        self.root.config(highlightbackground=color, highlightcolor=color, highlightthickness=2)
        self.button_paste.config(highlightbackground=color, highlightcolor=color, highlightthickness=2)
        self.button_fav_dir.config(highlightbackground=color, highlightcolor=color, highlightthickness=2)
        self.button_download.config(highlightbackground=color, highlightcolor=color, highlightthickness=2)

        if self.animating:
            self.root.after(100, self.animate)

    def paste_url(self):
        self.entry_url.delete(0, tk.END)
        self.entry_url.insert(0, self.root.clipboard_get())

    def set_fav_directory(self):
        self.fav_directory = filedialog.askdirectory()
        if self.fav_directory:
            self.label_fav_dir.config(text=f"Favorite Directory: {self.fav_directory}")

    def update_progress(self, value):
        self.progress['value'] = value
        self.progress_label.config(text=f"{value}%")
        self.root.update_idletasks()

    def download_reels(self):
        urls = self.entry_url.get().split(',')
        if not urls:
            messagebox.showerror("Error", "Please enter at least one URL")
            return
        if not self.fav_directory:
            messagebox.showerror("Error", "Please set a favorite directory")
            return
        
        naming_pattern = self.entry_naming_pattern.get()
        
        for idx, url in enumerate(urls):
            url = url.strip()
            if url:
                try:
                    self.update_progress(0)
                    loader = instaloader.Instaloader(download_videos=True, dirname_pattern=self.fav_directory)
                    post = instaloader.Post.from_shortcode(loader.context, url.split("/")[-2])
                    filename = naming_pattern.format(username=post.owner_username, date=post.date_utc.strftime('%Y-%m-%d'), shortcode=post.shortcode)
                    loader.download_post(post, target=os.path.join(self.fav_directory, filename))
                    self.update_progress(int((idx + 1) / len(urls) * 100))
                    self.history_log.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {url}")
                except Exception as e:
                    messagebox.showerror("Error", f"Error: {e}")
                    self.update_progress(0)

        messagebox.showinfo("Success", "Download complete")

    def download_thumbnails(self):
        urls = self.entry_url.get().split(',')
        if not urls:
            messagebox.showerror("Error", "Please enter at least one URL")
            return
        if not self.fav_directory:
            messagebox.showerror("Error", "Please set a favorite directory")
            return
        
        for idx, url in enumerate(urls):
            url = url.strip()
            if url:
                try:
                    shortcode = url.split("/")[-2]
                    loader = instaloader.Instaloader(download_videos=False, download_comments=False)
                    post = instaloader.Post.from_shortcode(loader.context, shortcode)
                    thumbnail_url = post.url
                    thumbnail_response = requests.get(thumbnail_url)
                    thumbnail_path = os.path.join(self.fav_directory, f"{shortcode}_thumbnail.jpg")
                    with open(thumbnail_path, 'wb') as f:
                        f.write(thumbnail_response.content)
                    self.history_log.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Thumbnail: {url}")
                except Exception as e:
                    messagebox.showerror("Error", f"Error: {e}")

        messagebox.showinfo("Success", "Thumbnails download complete")

    def switch_mode(self):
        if self.dark_mode.get():
            self.root.configure(bg='black')
            self.label_title.configure(bg='black', fg='white')
            self.label_url.configure(bg='black', fg='white')
            self.label_fav_dir.configure(bg='black', fg='white')
            self.label_naming_pattern.configure(bg='black', fg='white')
            self.toggle_dark_mode.configure(bg='black', fg='white', selectcolor="grey")
            self.progress_label.configure(bg='black', fg='white')
        else:
            self.root.configure(bg='white')
            self.label_title.configure(bg='white', fg='black')
            self.label_url.configure(bg='white', fg='black')
            self.label_fav_dir.configure(bg='white', fg='black')
            self.label_naming_pattern.configure(bg='white', fg='black')
            self.toggle_dark_mode.configure(bg='white', fg='black', selectcolor="grey")
            self.progress_label.configure(bg='white', fg='black')

    def clear_url(self):
        self.entry_url.delete(0, tk.END)

    def view_history(self):
        if self.history_log.winfo_ismapped():
            self.history_log.pack_forget()
        else:
            self.history_log.pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = InstaReelDownloader(root)
    root.mainloop()
