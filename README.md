# Church Management System Lite  

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)  
![SQLite](https://img.shields.io/badge/SQLite-3-green.svg)  
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange.svg)  

A lightweight desktop application for managing church members and attendance records.

## Features

### Member Management
- Add, edit, and delete member records
- Store member details:
  - Name
  - Phone number
  - Email address
  - Role in church

### Attendance Tracking
- Record attendance for events
- View past attendance records
- Filter by event name
- Multi-select members for bulk recording

### Data Management
- Automatic database backups
- Manual backup option
- SQLite database (auto-created)

## Requirements

- Python 3.x
- Tkinter (included with Python)
- SQLite3 (Python standard library)

## Installation

1. Clone or download the repository:
```bash
git clone https://github.com/adermgram/church-management-system.git
cd church-management-system`
```
2. Run the application:
```bash
python main.py
```
  The database (church.db) will be created automatically on first run.
## Usage

### Members Tab
- **Add Member**: Fill the form → Click "Add Member"
- **Update Member**: Select member → Edit form → Click "Update Member"
- **Delete Member**: Select member → Click "Delete Member"

### Attendance Tab
1. **Record Attendance**:
   - Enter Event Name
   - Enter Date (YYYY-MM-DD)
   - Select attending members
   - Click "Save Attendance"

2. **View Records**:
   - Select event from dropdown
   - Attendance displays automatically

### Backups
- Automatic backups in `database_backups/` folder
- Manual backups via "Backup Database" button

## Database Schema

```sql
CREATE TABLE members (
    id INTEGER PRIMARY KEY,
    name TEXT,
    phone TEXT,
    email TEXT,
    role TEXT
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY,
    member_id INTEGER,
    event_name TEXT,
    date TEXT,
    FOREIGN KEY (member_id) REFERENCES members(id)
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);
```

## ❓ FAQ

### **Q: Where is my data stored?**  
**A:** In `church.db` (SQLite file created automatically in the same folder as the script).

### **Q: How can I restore from a backup?**  
**A:**  
1. Locate your backup file in the `database_backups/` folder  
2. Copy it to your main folder  
3. Rename it to `church.db`  

### **Q: Can I edit the database directly?**  
**A:** Yes, but with caution:  
- Use [DB Browser for SQLite](https://sqlitebrowser.org/)  
- Always create a backup first  
- Don't modify table structures  

### **Q: The application won't start - what should I do?**  
**A:**  
1. Ensure you have Python 3 installed  
2. Try running from command line to see error messages:  
   ```bash
   python main.py
   ```
## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Permissions include:**
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

**Limitations:**
- ❌ No liability
- ❌ No warranty

## 📸 Screenshots

### Members Management
![image](https://github.com/user-attachments/assets/c5894f4f-8e9e-4d08-9a62-026d4f7a57c6)

*View and edit member records*

### Attendance Tracking
![image](https://github.com/user-attachments/assets/570ea2b4-8dbe-464d-b727-9411db304dfc)
  
*Record and view attendance*

