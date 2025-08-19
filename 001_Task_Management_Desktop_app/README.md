# Task Manager Desktop Application

## Project Structure 📁
```
task-manager/
│
├── app.py              # Main application file
├── tasks.json         # Task storage file
└── README.md          # Documentation
```

## Features 🌟
- **Modern UI**: Golden-purple themed interface
- **Task Management**: Create, edit, delete tasks
- **Smart Calendar**: Built-in date picker
- **Priority Levels**: Low, Medium, High
- **Status Tracking**: Pending, In Progress, Completed
- **Categories**: Organize tasks by category
- **Auto-save**: Automatic JSON storage
- **Notifications**: Overdue task alerts

## Installation Guide 🚀

### Prerequisites
- Python 3.7 or higher
- Windows OS
- Visual Studio Code (recommended)

### Setup Steps
```bash
# Clone Repository
git clone https://github.com/DeveloperPixel/Naman-Digital.git
cd task-manager

# Create Virtual Environment
python -m venv venv
venv\Scripts\activate

# Install Dependencies
pip install tkcalendar
```

## Development Guide 👨‍💻

### Running the Application
```bash
python app.py
```

### Code Examples

#### Creating a New Task
```python
from datetime import datetime
import uuid

task = Task(
    id=str(uuid.uuid4()),
    title="Sample Task",
    description="Task description",
    due_date="2025-08-19T00:00:00",
    priority="Medium",
    status="Pending",
    created_date=datetime.now().isoformat(),
    updated_date=datetime.now().isoformat(),
    category="General"
)
```

## User Guide 📖

### Task Operations
1. **Add Task**
   - Click "Add Task" button
   - Fill required fields
   - Use calendar for due date
   - Set priority and status
   - Click Save

2. **Edit Task**
   - Double-click task
   - Update fields
   - Save changes

3. **Delete Task**
   - Select task
   - Click "Delete"
   - Confirm action

4. **Complete Task**
   - Select task
   - Click "Mark Complete"

### Interface Elements
- **Toolbar**: Quick access buttons
- **Task List**: Main view of tasks
- **Status Bar**: System messages
- **Menu Bar**: File operations

## Technical Details 🔧

### Dependencies
- `tkinter`: GUI framework
- `tkcalendar`: Date picker widget
- `json`: Data storage
- `uuid`: Unique ID generation
- `datetime`: Date handling

### File Structure
- `app.py`: Application logic
- `tasks.json`: Data storage
- `README.md`: Documentation

## Contributing 🤝

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## Debugging 🐛

### Common Issues
1. **Task not saving**
   - Check file permissions
   - Verify JSON format

2. **Calendar not showing**
   - Verify tkcalendar installation
   - Check Python version

## Testing 🧪

Run tests in VS Code:
1. Open Command Palette (Ctrl+Shift+P)
2. Select "Python: Run Tests"

## License 📄
MIT License

## Support 💬
- GitHub Issues
- Email: support@example.com

## Version History 📝
- v1.0.0: Initial release
- v1.1.0: Golden-purple theme
- v1.2.0: Calendar integration

---

*Generated: August 19, 2025*
