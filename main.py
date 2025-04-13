import sqlite3
import sys
from tkinter import *
from tkinter import ttk, messagebox
import os
from datetime import datetime


def get_db_path():
    """Returns the correct database path whether running from source or installed"""
    # Try AppData location first (installed version)
    appdata_path = os.path.join(os.getenv('APPDATA'), 'ChurchMS', 'church.db')
    
    if os.path.exists(appdata_path):
        return appdata_path
    
    # Fall back to local directory (development version)
    local_path = 'church.db'
    return local_path


def first_time_setup():
    """Handles first-run database setup"""
    db_path = get_db_path()
    db_dir = os.path.dirname(db_path)
    
    # Create directory if needed
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Create database if it doesn't exist
    if not os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            conn.close()
            # Initialize database tables here if needed
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to create database:\n{e}")
            return False
    return True

# Initialize database
if not first_time_setup():
    sys.exit(1)

 
def create_auto_backup():
    backup_dir = "database_backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    backup_path = os.path.join(backup_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    try:
        with open(backup_path, 'wb') as f:
            for line in conn.iterdump():
                f.write(f'{line}\n'.encode('utf-8'))
    except Exception as e:
        messagebox.showwarning("Backup Warning", f"Auto-backup failed:\n{e}")


# Connect to database
try:
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
except sqlite3.Error as e:
    messagebox.showerror("Database Error", f"Failed to connect to database:\n{e}")
    sys.exit(1)

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY,
    name TEXT,
    phone TEXT,
    email TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY,
    member_id INTEGER,
    event_name TEXT,
    date TEXT,
    FOREIGN KEY (member_id) REFERENCES members(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
)
""")
conn.commit()

# ================== FUNCTIONS ==================
def load_members():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM members")
    for row in cursor.fetchall():
        tree.insert("", END, values=row)

def validate_date(date_str):
    try:
        year, month, day = map(int, date_str.split('-'))
        return len(date_str) == 10 and 1 <= month <= 12 and 1 <= day <= 31
    except ValueError:
        return False

def load_members_for_attendance():
    attendance_listbox.delete(0, END)  # Clear existing entries
    cursor.execute("SELECT id, name FROM members ORDER BY name")
    for member in cursor.fetchall():
        attendance_listbox.insert(END, f"{member[0]}: {member[1]}")

def validate_member():
    if not name_entry.get().strip():
        messagebox.showerror("Error", "Name is required")
        return False
    if not phone_entry.get().strip().isdigit():
        messagebox.showerror("Error", "Phone must contain only numbers")
        return False
    return True


def add_member():
    if not validate_member():
        return
    try:
        cursor.execute(
            "INSERT INTO members (name, phone, email, role) VALUES (?, ?, ?, ?)",
            (name_entry.get(), phone_entry.get(), email_entry.get(), role_entry.get())
        )
        conn.commit()
        load_members()
        load_members_for_attendance()  # Update attendance list too
        clear_entries()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add member: {e}")

def update_member():
    if not validate_member():
        return
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "No member selected!")
        return
    try:
        cursor.execute(
            "UPDATE members SET name=?, phone=?, email=?, role=? WHERE id=?",
            (name_entry.get(), phone_entry.get(), email_entry.get(), role_entry.get(), tree.item(selected)["values"][0])
        )
        conn.commit()
        load_members()
        load_members_for_attendance()  # Update attendance list too
        clear_entries()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update member: {e}")

def delete_member():
    selected = tree.focus()
    if not selected:
        messagebox.showerror("Error", "No member selected!")
        return
    try:
        cursor.execute("DELETE FROM members WHERE id=?", (tree.item(selected)["values"][0],))
        conn.commit()
        load_members()
        load_members_for_attendance()  # Update attendance list too
        clear_entries()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete member: {e}")

def clear_entries():
    name_entry.delete(0, END)
    phone_entry.delete(0, END)
    email_entry.delete(0, END)
    role_entry.delete(0, END)

def on_select(event):
    selected = tree.focus()
    if selected:
        data = tree.item(selected)["values"]
        clear_entries()
        name_entry.insert(0, data[1])
        phone_entry.insert(0, data[2])
        email_entry.insert(0, data[3])
        role_entry.insert(0, data[4])

def refresh_event_list():
    """Load all event names into the dropdown"""
    try:
        cursor.execute("SELECT DISTINCT event_name FROM attendance ORDER BY event_name")
        event_dropdown['values'] = [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Failed to load events:\n{str(e)}")

def load_attendance_records():
    """Show who attended the selected event"""
    event_name = event_var.get()
    
    if not event_name:
        return  # Silent return - no error needed
    
    # Clear existing data
    for row in attendance_tree.get_children():
        attendance_tree.delete(row)
    
    try:
        cursor.execute("""
            SELECT m.id, m.name, strftime('%Y-%m-%d', a.date) 
            FROM attendance a
            JOIN members m ON a.member_id = m.id
            WHERE a.event_name = ?
            ORDER BY a.date DESC
        """, (event_name,))
        
        records = cursor.fetchall()
        if not records:
            attendance_tree.insert("", END, values=("No records", "", ""))
        else:
            for row in records:
                attendance_tree.insert("", END, values=row)
                
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Failed to load attendance:\n{e}")

def save_attendance():
    status_var.set("Saving attendance...")
    # Get and validate inputs
    event_name = event_entry.get().strip()
    date_str = date_entry.get().strip()
    
    if not event_name:
        messagebox.showerror("Error", "Please enter an event name!")
        return
    if not date_str:
        messagebox.showerror("Error", "Please enter a date!")
        return
    
    # Validate date format (YYYY-MM-DD)
    if not validate_date(date_str):
        messagebox.showerror("Error", "Please use valid YYYY-MM-DD format (e.g. 2023-12-25)")
        return
    
    # Check member selection
    selected_indices = attendance_listbox.curselection()
    if not selected_indices:
        messagebox.showerror("Error", "Please select at least one member!")
        return
    
    # Process in transaction
    try:
        # 1. Save event type if new
        cursor.execute("INSERT OR IGNORE INTO events (name) VALUES (?)", (event_name,))
        
        # 2. Save all attendance records
        for index in selected_indices:
            member_id = attendance_listbox.get(index).split(":")[0].strip()
            cursor.execute(
                """INSERT INTO attendance (member_id, event_name, date) 
                VALUES (?, ?, ?)""",
                (member_id, event_name, date_str)
            )
        
        conn.commit()
        
        # 3. Update UI
        messagebox.showinfo("Success", 
            f"Saved attendance for {len(selected_indices)} members!\n"
            f"Event: {event_name}\n"
            f"Date: {date_str}")
        
        event_entry.delete(0, END)
        date_entry.delete(0, END)
        load_attendance_records()
        refresh_event_list()
        
    except sqlite3.Error as e:
        conn.rollback()
        messagebox.showerror("Database Error", 
            f"Failed to save attendance:\n{str(e)}")
    status_var.set("Attendance saved successfully")
    
        
def backup_database():
    backup_dir = os.path.join(os.getenv('APPDATA'), 'ChurchMS', 'database_backups')
    try:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        # Rest of backup code...
    except Exception as e:
        messagebox.showerror("Error", f"Cannot create backups:\n{e}")

# ================== UI SETUP ==================
root = Tk()
root.title("Church Management System Lite")

# Create Notebook (tab system)
notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

#Adding style to the tabs
style = ttk.Style()
style.configure('TNotebook.Tab', padding=[20,5])  # More tab padding
style.configure('Treeview', rowheight=25)  # Taller rows in tables

# ===== MEMBERS TAB =====
members_tab = Frame(notebook)
notebook.add(members_tab, text="Members")

# Left Frame (Form)
left_frame = Frame(members_tab, padx=10, pady=10)
left_frame.pack(side=LEFT, fill=Y)

Label(left_frame, text="Name:").grid(row=0, column=0, sticky=W)
name_entry = Entry(left_frame, width=25)
name_entry.grid(row=0, column=1, pady=5)

Label(left_frame, text="Phone:").grid(row=1, column=0, sticky=W)
phone_entry = Entry(left_frame, width=25)
phone_entry.grid(row=1, column=1, pady=5)

Label(left_frame, text="Email:").grid(row=2, column=0, sticky=W)
email_entry = Entry(left_frame, width=25)
email_entry.grid(row=2, column=1, pady=5)

Label(left_frame, text="Role:").grid(row=3, column=0, sticky=W)
role_entry = Entry(left_frame, width=25)
role_entry.grid(row=3, column=1, pady=5)

# Buttons
Button(left_frame, text="Add Member", command=add_member).grid(row=4, column=0, columnspan=2, pady=10)
Button(left_frame, text="Update Member", command=update_member).grid(row=5, column=0, columnspan=2)
Button(left_frame, text="Delete Member", command=delete_member).grid(row=6, column=0, columnspan=2, pady=10)
Button(left_frame, text="Backup Database", command=backup_database).grid(row=7, column=0, columnspan=2, pady=10)


# Right Frame (Table)
right_frame = Frame(members_tab)
right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

# Treeview (Table)
tree = ttk.Treeview(right_frame, columns=("ID", "Name", "Phone", "Email", "Role"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Name", text="Name")
tree.heading("Phone", text="Phone")
tree.heading("Email", text="Email")
tree.heading("Role", text="Role")
tree.pack(fill=BOTH, expand=True)

# Scrollbar
scrollbar = ttk.Scrollbar(right_frame, orient=VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)

# ===== ATTENDANCE TAB =====
attendance_tab = Frame(notebook)
notebook.add(attendance_tab, text="Attendance")

# Recording Section
Label(attendance_tab, text="Record New Attendance", font=('Arial', 10, 'bold')).pack()

# Event Entry
Label(attendance_tab, text="Event Name:").pack(pady=5)
event_entry = Entry(attendance_tab, width=30)
event_entry.pack()

# Date Entry
Label(attendance_tab, text="Date (YYYY-MM-DD):").pack(pady=5)
date_entry = Entry(attendance_tab, width=30)
date_entry.pack()

# Listbox for Members
Label(attendance_tab, text="Select Present Members:").pack(pady=5)
attendance_listbox = Listbox(attendance_tab, selectmode=MULTIPLE, height=15)
attendance_listbox.pack(fill=BOTH, expand=True, padx=10)

Button(attendance_tab, text="Save Attendance", command=save_attendance).pack(pady=10)
Button(attendance_tab, text="Clear Selection", 
       command=lambda: attendance_listbox.selection_clear(0, END)).pack(pady=5)

# Viewing Section
Label(attendance_tab, text="\nView Past Attendance", font=('Arial', 10, 'bold')).pack()

# Event selector
event_var = StringVar()
event_dropdown = ttk.Combobox(attendance_tab, textvariable=event_var, state='readonly')
event_dropdown.bind("<<ComboboxSelected>>", lambda e: load_attendance_records())
event_dropdown.pack(pady=5)

# Attendance table
attendance_tree = ttk.Treeview(attendance_tab, columns=("ID", "Name", "Date"), show="headings", height=8)
attendance_tree.heading("ID", text="Member ID")
attendance_tree.heading("Name", text="Name")
attendance_tree.heading("Date", text="Date")
attendance_tree.column("ID", width=80)
attendance_tree.column("Name", width=150)
attendance_tree.column("Date", width=100)
attendance_tree.pack(fill=BOTH, expand=True)

# Scrollbar
scrollbar = ttk.Scrollbar(attendance_tab, orient=VERTICAL, command=attendance_tree.yview)
attendance_tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)

# Load button
Button(attendance_tab, text="Refresh List", command=lambda: [refresh_event_list(), load_attendance_records()]).pack(pady=5)

# Initialize data
load_members()
load_members_for_attendance()
tree.bind("<ButtonRelease-1>", on_select)

refresh_event_list()
if event_dropdown['values']:
    event_var.set(event_dropdown['values'][0])
    load_attendance_records()



menubar = Menu(root)
root.config(menu=menubar)

# File menu
file_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Backup Database", command=backup_database)
file_menu.add_command(label="Exit", command=root.quit)

# Help menu
help_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Church Management System\nVersion 1.0"))


status_var = StringVar()
status_var.set("Ready")
status_bar = Label(root, textvariable=status_var, bd=1, relief=SUNKEN, anchor=W)
status_bar.pack(side=BOTTOM, fill=X)


root.mainloop()