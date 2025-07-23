import customtkinter as ctk
from tkinter import messagebox
import threading
import os
import sys
from pathlib import Path

from clipper import download_and_clip_playlist, ensure_binaries


class AutoClipperApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AutoClipper")
        self.geometry("900x600")
        ctk.set_default_color_theme("dark-blue")

        # variables
        self.url_var = ctk.StringVar()
        self.clip_len_var = ctk.StringVar(value="10")
        self.log_var = ctk.StringVar(value="Ready.\n")
        self.auto_segment_var = ctk.BooleanVar(value=True)
        self.mute_var = ctk.BooleanVar()
        self.delete_var = ctk.BooleanVar()
        self.format_var = ctk.StringVar(value="mp4")
        self.progress_var = ctk.DoubleVar()

        self._build_ui()

    def _build_ui(self):
        # configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # sidebar
        sidebar = ctk.CTkFrame(self)
        sidebar.grid(row=0, column=0, sticky="nsw", padx=5, pady=5)
        sidebar.grid_rowconfigure((2, 3, 4, 5), weight=1)

        ctk.CTkLabel(sidebar, text="AutoClipper", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=10, padx=10)
        self.start_btn = ctk.CTkButton(sidebar, text="Download & Clip", command=self.start_task)
        self.start_btn.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        ctk.CTkButton(sidebar, text="View Output Folder", command=self.open_output).grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.cancel_btn = ctk.CTkButton(sidebar, text="Cancel Task", state="disabled", command=self.cancel_task)
        self.cancel_btn.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkOptionMenu(sidebar, values=["Dark", "Light", "System"], command=self.change_theme).grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkOptionMenu(sidebar, values=["100%", "125%", "150%"], command=self.change_scaling).grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        # main panel
        main = ctk.CTkFrame(self)
        main.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        main.grid_columnconfigure(0, weight=1)

        self.log_box = ctk.CTkTextbox(main, state="normal")
        self.log_box.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.log_box.insert("end", self.log_var.get())
        self.log_box.configure(state="disabled")
        self.url_entry = ctk.CTkEntry(main, textvariable=self.url_var, placeholder_text="YouTube Playlist URL")
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.clip_length = ctk.CTkComboBox(main, values=["5", "10", "15", "20", "25", "30", "60"], variable=self.clip_len_var)
        self.clip_length.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.format_buttons = ctk.CTkSegmentedButton(main, values=["mp4", "webm", "mkv"], variable=self.format_var)
        self.format_buttons.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.progress = ctk.CTkSlider(main, from_=0, to=100, state="disabled", variable=self.progress_var)
        self.progress.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ctk.CTkButton(main, text="Start", command=self.start_task).grid(row=4, column=0, columnspan=2, pady=10)

        # right panel
        right = ctk.CTkFrame(self)
        right.grid(row=0, column=2, sticky="nse", padx=5, pady=5)
        right.grid_columnconfigure(0, weight=1)
        ctk.CTkCheckBox(right, text="Auto-segment into clips", variable=self.auto_segment_var).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkSwitch(right, text="Mute audio", variable=self.mute_var).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkSwitch(right, text="Delete original", variable=self.delete_var).grid(row=2, column=0, padx=10, pady=5, sticky="w")

    def log(self, message: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see("end")

    def start_task(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a playlist URL")
            return
        self.start_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        t = threading.Thread(target=self.worker, daemon=True)
        t.start()

    def worker(self):
        try:
            output = Path("output")
            output.mkdir(exist_ok=True)
            download_and_clip_playlist(
                url=self.url_var.get().strip(),
                output_dir=output,
                clip_length=int(self.clip_len_var.get()),
                log_callback=self.log,
                mute=self.mute_var.get(),
                delete_original=self.delete_var.get(),
                format=self.format_var.get(),
                progress_callback=self.update_progress,
            )
            self.log("Completed.")
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.start_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")
            self.progress_var.set(0)

    def cancel_task(self):
        messagebox.showinfo("Cancel", "Cancellation is not implemented yet.")

    def update_progress(self, value: float):
        self.progress_var.set(value)

    def open_output(self):
        output = Path("output")
        output.mkdir(exist_ok=True)
        os.startfile(output)

    def change_theme(self, mode: str):
        ctk.set_appearance_mode(mode.lower())

    def change_scaling(self, scaling: str):
        scale = int(scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(scale)


def main():
    base_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    ensure_binaries(base_dir, lambda _m: None)
    app = AutoClipperApp()
    app.mainloop()


if __name__ == "__main__":
    main()
