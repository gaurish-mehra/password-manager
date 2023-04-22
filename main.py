import tkinter as tk
from tkinter import ttk, messagebox
from cryptography.fernet import Fernet
import jsonlines
import base64


class PasswordManager:
    def __init__(self):
        self.key = None
        self.load_key()

        self.window = tk.Tk()
        self.window.title("Password Manager")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.window.configure(bg="#f7f7f7")

        style = ttk.Style(self.window)
        style.configure("TButton", padding=10, font=(
            "Segoe UI", 12), foreground="#f7f7f7", background="#b24242")
        style.map("TButton", background=[
                  ('pressed', '#3b5998'), ('active', '#b24242')])

        ttk.Label(self.window, text="Username:", font=(
            "Segoe UI", 14), background="#f7f7f7").place(x=40, y=50)
        self.username_entry = ttk.Entry(
            self.window, font=("Segoe UI", 14), width=20)
        self.username_entry.place(x=150, y=50)

        ttk.Label(self.window, text="Password:", font=(
            "Segoe UI", 14), background="#f7f7f7").place(x=40, y=100)
        self.password_entry = ttk.Entry(
            self.window, font=("Segoe UI", 14), width=20, show="*")
        self.password_entry.place(x=150, y=100)

        ttk.Button(self.window, text="Add Password",
                   command=self.add_password).place(x=80, y=160)
        ttk.Button(self.window, text="Display Passwords",
                   command=self.display_passwords).place(x=210, y=160)

        self.dark_theme = False
        ttk.Button(self.window, text="Dark Theme",
                   command=self.toggle_theme).place(x=150, y=220)

        self.window.mainloop()

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        bg_color = "#212121" if self.dark_theme else "#f7f7f7"
        fg_color = "#f7f7f7" if self.dark_theme else "#212121"
        self.window.configure(bg=bg_color)
        for child in self.window.winfo_children():
            if isinstance(child, ttk.Button):
                child.configure(style="TButton",
                                foreground=fg_color, background="#4267b2")
            else:
                child.configure(background=bg_color, foreground=fg_color)

    def load_key(self):
        try:
            with open("key.key", "rb") as f:
                self.key = f.read()
        except FileNotFoundError:
            self.generate_key()

    def generate_key(self):
        self.key = Fernet.generate_key()
        with open("key.key", "wb") as f:
            f.write(self.key)

    def add_password(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        fernet = Fernet(self.key)
        ciphertext = fernet.encrypt(bytes(username + ":" + password, 'utf-8'))
        b64_ciphertext = base64.b64encode(ciphertext).decode('utf-8')
        with jsonlines.open("passwords.jsonl", mode="a") as writer:
            writer.write({"ciphertext": b64_ciphertext})
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            messagebox.showinfo("Success", "Password added successfully")

    def display_passwords(self):
        with jsonlines.open("passwords.jsonl") as reader:
            fernet = Fernet(self.key)
            passwords = []
            for data in reader:
                b64_ciphertext = data["ciphertext"]
                ciphertext = base64.b64decode(b64_ciphertext)
                plaintext = fernet.decrypt(ciphertext).decode('utf-8')
                username, password = plaintext.split(':')
                passwords.append((username, password))

            # Create a new window to display the passwords
            password_window = tk.Toplevel(self.window)
            password_window.title("Passwords")
            password_window.geometry("300x200")
            password_window.configure(bg="#212121")

            # Create a label to display the passwords
            password_label = tk.Label(password_window, text="\n".join(
                [f"{username}: {password}" for username, password in passwords]))
            password_label.configure(
                bg="#d16969", borderwidth=2, relief="groove", padx=10, pady=10)
            password_label.pack()

            # Create a button to close the window
            close_button = tk.Button(
                password_window, text="Close", command=password_window.destroy,
                bg="#ff1744", fg="white", bd=0, padx=10, pady=5,
                font=("Helvetica", 12, "bold"), borderwidth=0,
                highlightthickness=0, relief="flat",
                activebackground="#d50000", activeforeground="white")
            close_button.pack(pady=10)


if __name__ == '__main__':
    PasswordManager()
