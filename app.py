from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

from engine import generate_sheet


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()
TEMPLATE_FILE = BASE_DIR / "weekly_schedule_template.html"


def browse_csv() -> None:
    file_path = filedialog.askopenfilename(
        title="Select Schedule CSV",
        filetypes=[("CSV files", "*.csv")]
    )
    if file_path:
        csv_path_var.set(file_path)


def generate() -> None:
    csv_path_text = csv_path_var.get().strip()

    if not csv_path_text:
        messagebox.showerror("Missing File", "Please choose a schedule CSV file.")
        return

    csv_path = Path(csv_path_text)

    if not csv_path.exists():
        messagebox.showerror("File Not Found", "The selected CSV file does not exist.")
        return

    try:
        df = pd.read_csv(csv_path)

        if "date" not in df.columns:
            messagebox.showerror("Invalid CSV", "CSV must include a 'date' column.")
            return

        df["date"] = pd.to_datetime(df["date"])
        first_date = df["date"].min()

        year = int(first_date.year)
        month = int(first_date.month)

        output_dir = csv_path.parent
        output_html = output_dir / f"weekly_schedule_{year}_{month:02d}.html"
        output_summary = output_dir / f"monthly_assignment_summary_{year}_{month:02d}.csv"

        warnings, row_count, year, month = generate_sheet(
            csv_path=csv_path,
            template_path=TEMPLATE_FILE,
            output_html=output_html,
            output_summary=output_summary,
        )

        msg = (
            f"Sheet created:\n\n"
            f"{output_html.name}\n"
            f"{output_summary.name}\n\n"
            f"Saved in:\n{output_dir}\n\n"
            f"Rows created: {row_count}\n"
            f"Club number will be filled in by hand on the printed sheet."
        )

        if warnings:
            msg += "\n\nWarnings:\n- " + "\n- ".join(warnings)

        messagebox.showinfo("Done", msg)

    except Exception as e:
        messagebox.showerror("Error", str(e))


root = tk.Tk()
root.title("TBC Schedule Generator")
root.geometry("600x260")
root.resizable(False, False)
root.configure(bg="white")

csv_path_var = tk.StringVar()

frame = tk.Frame(root, padx=24, pady=20, bg="white")
frame.pack(fill="both", expand=True)

title = tk.Label(
    frame,
    text="TBC Schedule Generator",
    font=("Segoe UI", 16, "bold"),
    bg="white"
)
title.grid(row=0, column=0, columnspan=3, sticky="w")

subtitle = tk.Label(
    frame,
    text="Generate a monthly accountability sheet from a schedule CSV",
    font=("Segoe UI", 9),
    fg="#555",
    bg="white"
)
subtitle.grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 16))

tk.Label(
    frame,
    text="Schedule CSV",
    font=("Segoe UI", 10, "bold"),
    bg="white"
).grid(row=2, column=0, sticky="w")

entry = tk.Entry(
    frame,
    textvariable=csv_path_var,
    width=42,
    font=("Segoe UI", 9),
    relief="solid",
    borderwidth=1
)
entry.grid(row=2, column=1, padx=(10, 10), pady=6)

browse_btn = tk.Button(
    frame,
    text="Browse",
    command=browse_csv,
    font=("Segoe UI", 9),
    width=10
)
browse_btn.grid(row=2, column=2)

generate_btn = tk.Button(
    frame,
    text="Generate Sheet",
    command=generate,
    font=("Segoe UI", 10, "bold"),
    bg="#1f6feb",
    fg="white",
    activebackground="#155ab6",
    activeforeground="white",
    relief="flat",
    padx=18,
    pady=8,
    cursor="hand2"
)
generate_btn.grid(row=3, column=1, sticky="w", pady=(18, 14))

info = tk.Label(
    frame,
    text="Select a monthly CSV, generate, then print from the browser preview.",
    font=("Segoe UI", 9),
    fg="#333",
    bg="white"
)
info.grid(row=4, column=0, columnspan=3, sticky="w", pady=(4, 2))

note = tk.Label(
    frame,
    text="Club number is left blank to be written by hand.",
    font=("Segoe UI", 9),
    fg="#333",
    bg="white"
)
note.grid(row=5, column=0, columnspan=3, sticky="w")

credit = tk.Label(
    frame,
    text="Made by Cooper Davis",
    font=("Segoe UI", 8),
    fg="#888",
    bg="white"
)
credit.grid(row=6, column=2, sticky="e", pady=(16, 0))

root.mainloop()