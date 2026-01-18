import os
import re
import qrcode
import tkinter as tk
from tkinter import messagebox
from urllib.parse import urlparse
from PIL import Image, ImageTk

class QRCodeGenerator:
    OUTPUT_DIR = "output"
    QR_PREVIEW_SIZE = (180, 180)

    def __init__(self):
        self.ensure_output_directory()
        self.window = self.create_ui()

    def ensure_output_directory(self):
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

    def normalize_url(self, url: str) -> str:
        return f"https://{url}" if not url.startswith(("http://", "https://")) else url

    def normalize_domain(self, domain: str) -> str:
        return domain.lower().lstrip("www.")

    def is_valid_domain(self, domain: str) -> bool:
        domain_pattern = r"^(?!\-)([A-Za-z0-9\-]+\.)+[A-Za-z]{2,}$"
        return bool(re.match(domain_pattern, domain))

    def is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and parsed.netloc and self.is_valid_domain(parsed.netloc)

    def domain_to_filename(self, domain: str) -> str:
        return f"{domain.replace('.', '_')}.png"

    def generate_qr_code(self, url: str) -> str:
        parsed = urlparse(url)
        domain = self.normalize_domain(parsed.netloc)
        file_name = self.domain_to_filename(domain)
        file_path = os.path.join(self.OUTPUT_DIR, file_name)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_path)

        return file_path

    def on_generate_click(self):
        raw_url = self.url_entry.get().strip()
        if not raw_url:
            messagebox.showerror("Input Error", "Please enter a URL.")
            return

        url = self.normalize_url(raw_url)
        if not self.is_valid_url(url):
            messagebox.showerror("Invalid URL", "Please enter a valid URL with a correct domain.")
            return

        self.preview_label.config(text=f"Preview URL:\n{url}")
        try:
            file_path = self.generate_qr_code(url)
            self.show_qr_preview(file_path)
            messagebox.showinfo("Success", f"QR Code generated successfully!\nSaved / Overwritten by domain:\n{file_path}")
        except Exception as error:
            messagebox.showerror("Error", f"Failed to generate QR Code.\n{error}")

    def show_qr_preview(self, image_path: str):
        image = Image.open(image_path)
        image = image.resize(self.QR_PREVIEW_SIZE, Image.Resampling.LANCZOS)
        qr_image_tk = ImageTk.PhotoImage(image)
        self.qr_preview_label.config(image=qr_image_tk, text="")
        self.qr_preview_label.image = qr_image_tk

    def create_ui(self):
        window = tk.Tk()
        window.title("QR Code Generator")
        window.geometry("520x430")
        window.resizable(False, False)

        tk.Label(window, text="QR Code Generator", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Label(window, text="Enter URL:").pack()
        self.url_entry = tk.Entry(window, width=60)
        self.url_entry.pack(pady=5)

        self.preview_label = tk.Label(window, text="Preview URL:\n", fg="blue", wraplength=480, justify="center")
        self.preview_label.pack(pady=8)

        tk.Button(window, text="Generate QR Code", command=self.on_generate_click, bg="black", fg="white", width=24).pack(pady=8)
        tk.Label(window, text="QR Code Preview:", font=("Arial", 10, "bold")).pack(pady=5)

        self.qr_preview_label = tk.Label(window, text="(QR Preview will appear here)", fg="gray")
        self.qr_preview_label.pack(pady=5)

        window.mainloop()

if __name__ == "__main__":
    QRCodeGenerator()
