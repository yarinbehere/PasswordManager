import json
import os
import string
from random import choice, randint, shuffle
from tkinter import *
from tkinter import messagebox
from urllib.parse import urlparse
import clipboard
import pyAesCrypt
import pyperclip

bufferSize = 64 * 1024
password = "password"

"""
--------------------------- SEARCH FUNCTION --------------------------- 
"""


def search_password():
    website = website_entry.get()
    try:
        with open("data.json") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Error", message="No Data File Found.")
    else:
        if website == "":
            messagebox.showinfo(title="Error", message="Please enter Website.")
            return
        if website in data:
            email = data[website]["email"]
            password = data[website]["password"]
            messagebox.showinfo(title=website, message=f"Email: {email}\nPassword: {password}")
        else:
            messagebox.showinfo(title="Error", message=f'No details for "{website}" exists.')


"""
--------------------------- GENERATE FUNCTION --------------------------- 
"""


def generate_password():
    password_entry.delete(0, 'end')
    symbols = ['!', '#', '$', '%', '&', '@', '?', '*', '+']

    password_lower_letters = [choice(list(string.ascii_lowercase)) for _ in range(randint(4, 6))]
    password_upper_letters = [choice(list(string.ascii_uppercase)) for _ in range(randint(2, 4))]
    password_symbols = [choice(symbols) for _ in range(randint(1, 2))]
    password_numbers = [choice(list(string.digits)) for _ in range(randint(3, 4))]

    password_list = password_lower_letters + password_upper_letters + password_symbols + password_numbers
    shuffle(password_list)

    password = "".join(password_list)
    password_entry.insert(0, password)
    pyperclip.copy(password)


"""
--------------------------- SAVE FUNCTION --------------------------- 
"""


def save_password():
    website = website_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    new_data = {
        website: {
            "email": email,
            "password": password,
        }
    }

    if len(website) == 0 or len(password) == 0:
        messagebox.showinfo(title="Error", message="Please check for empty fields.")
    else:
        is_ok = messagebox.askokcancel(title=website,
                                       message=f"Confirm following info: \nWebsite: {website} \nEmail: {email} "
                                               f"\nPassword: {password} \nIs this correct?")
        if is_ok:
            try:
                with open("data.json", "r") as data_file:
                    # Reading old data
                    data = json.load(data_file)
            except FileNotFoundError:
                with open("data.json", "w") as data_file:
                    json.dump(new_data, data_file, indent=4)
            else:
                # Updating old data with new data
                data.update(new_data)
                with open("data.json", "w") as data_file:
                    # Saving updated data
                    json.dump(data, data_file, indent=4)
            finally:
                website_entry.delete(0, END)
                password_entry.delete(0, END)
            # subprocess.run(['open', "data.json"], check=True)


def on_closing():
    try:
        pyAesCrypt.encryptFile("data.json", "data.json.aes", password, bufferSize)
        os.remove("data.json")
    except OSError:
        print(OSError)
    finally:
        window.destroy()


"""
--------------------------- UI INIT --------------------------- 
"""
window = Tk()
window.title("PasswordManager")
window.config(padx=35, pady=35)

canvas = Canvas(height=200, width=200)
logo_img = PhotoImage(file='logo.png')
canvas.create_image(100, 100, image=logo_img)
canvas.grid(row=0, column=1)

website_label = Label(text="Website:")
website_label.grid(row=1, column=0)
email_label = Label(text="Email/Username:")
email_label.grid(row=2, column=0)
password_label = Label(text="Password:")
password_label.grid(row=3, column=0)

website_entry = Entry(width=20)
website_entry.grid(row=1, column=1, columnspan=1)

website_title = ""
if urlparse(clipboard.paste()).hostname is not None:
    website_title = urlparse(clipboard.paste()).hostname

website_entry.insert(0, website_title)

website_entry.focus()
email_entry = Entry(width=20)
email_entry.grid(row=2, column=1, columnspan=1)
email_entry.insert(0, "your@mail.com")
password_entry = Entry(width=20)
password_entry.grid(row=3, column=1)

search_button = Button(text="Search", width=16, command=search_password)
search_button.grid(row=1, column=2)
generate_password_button = Button(text="Generate Password", command=generate_password, width=16)
generate_password_button.grid(row=3, column=2)
save_button = Button(text="Save Password", width=20, command=save_password)
save_button.grid(row=4, column=1, columnspan=1, pady=10)
save_button.config(pady=5)

window.protocol("WM_DELETE_WINDOW", on_closing)

try:
    pyAesCrypt.decryptFile("data.json.aes", "data.json", password, bufferSize)
except OSError:
    print(OSError)

window.mainloop()
