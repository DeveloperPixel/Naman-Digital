"""
Task Manager Desktop App - MVP Implementation
A simple desktop application for managing tasks with due date reminders
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
import json
import os
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Optional
import uuid
from tkcalendar import DateEntry  # Import DateEntry from tkcalendar


# Data Models
class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Status(Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


@dataclass
class Task:
    id: str
    title: str
    description: str
    due_date: str  # ISO format date string
    priority: str
    status: str
    created_date: str
    updated_date: str
    category: str = "General"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def is_overdue(self):
        if self.status == Status.COMPLETED.value:
            return False
        try:
            due = datetime.fromisoformat(self.due_date).date()
            return due < date.today()
        except:
            return False

    def days_until_due(self):
        try:
            due = datetime.fromisoformat(self.due_date).date()
            today = date.today()
            return (due - today).days
        except:
            return None


class TaskManager:
    def __init__(self, data_file="tasks.json"):
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.load_tasks()

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.save_tasks()

    def update_task(self, task_id: str, updated_task: Task):
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks[i] = updated_task
                self.save_tasks()
                return True
        return False

    def delete_task(self, task_id: str):
        self.tasks = [task for task in self.tasks if task.id != task_id]
        self.save_tasks()

    def get_task(self, task_id: str) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_all_tasks(self) -> List[Task]:
        return self.tasks

    def get_overdue_tasks(self) -> List[Task]:
        return [task for task in self.tasks if task.is_overdue()]

    def save_tasks(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump([task.to_dict() for task in self.tasks], f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def load_tasks(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                self.tasks = [Task.from_dict(task_data) for task_data in data]
            except Exception as e:
                print(f"Error loading tasks: {e}")
                self.tasks = []


class TaskDialog:
    def __init__(self, parent, task=None):
        self.parent = parent
        self.task = task
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Task" if task is None else "Edit Task")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()

        if task:
            self.populate_fields()

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")

    def create_widgets(self):
        # Title
        ttk.Label(self.dialog, text="Title:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.title_entry = ttk.Entry(self.dialog, width=40)
        self.title_entry.grid(row=0, column=1, padx=10, pady=5)

        # Description
        ttk.Label(self.dialog, text="Description:").grid(row=1, column=0, sticky="nw", padx=10, pady=5)
        self.desc_text = tk.Text(self.dialog, width=30, height=4)
        self.desc_text.grid(row=1, column=1, padx=10, pady=5)

        # Due Date (using DateEntry)
        ttk.Label(self.dialog, text="Due Date:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.due_date_entry = DateEntry(self.dialog, width=37, date_pattern="yyyy-mm-dd")
        self.due_date_entry.grid(row=2, column=1, padx=10, pady=5)

        # Priority
        ttk.Label(self.dialog, text="Priority:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.priority_var = tk.StringVar(value=Priority.MEDIUM.value)
        priority_combo = ttk.Combobox(self.dialog, textvariable=self.priority_var,
                                      values=[p.value for p in Priority], state="readonly")
        priority_combo.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Status
        ttk.Label(self.dialog, text="Status:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.status_var = tk.StringVar(value=Status.PENDING.value)
        status_combo = ttk.Combobox(self.dialog, textvariable=self.status_var,
                                    values=[s.value for s in Status], state="readonly")
        status_combo.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Category
        ttk.Label(self.dialog, text="Category:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        self.category_entry = ttk.Entry(self.dialog, width=40)
        self.category_entry.grid(row=5, column=1, padx=10, pady=5)
        self.category_entry.insert(0, "General")

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Save", command=self.save_task).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side="left", padx=5)

        # Focus on title entry
        self.title_entry.focus()

    def populate_fields(self):
        if self.task:
            self.title_entry.insert(0, self.task.title)
            self.desc_text.insert("1.0", self.task.description)
            self.due_date_entry.set_date(self.task.due_date.split('T')[0])  # Set the date in the DateEntry
            self.priority_var.set(self.task.priority)
            self.status_var.set(self.task.status)
            self.category_entry.delete(0, tk.END)
            self.category_entry.insert(0, self.task.category)

    def save_task(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Error", "Title is required!")
            return

        description = self.desc_text.get("1.0", tk.END).strip()
        due_date = self.due_date_entry.get_date().isoformat()  # Get the date from DateEntry

        # Create or update task
        now = datetime.now().isoformat()

        if self.task:  # Editing existing task
            self.result = Task(
                id=self.task.id,
                title=title,
                description=description,
                due_date=due_date + "T00:00:00",
                priority=self.priority_var.get(),
                status=self.status_var.get(),
                created_date=self.task.created_date,
                updated_date=now,
                category=self.category_entry.get().strip()
            )
        else:  # Creating new task
            self.result = Task(
                id=str(uuid.uuid4()),
                title=title,
                description=description,
                due_date=due_date + "T00:00:00",
                priority=self.priority_var.get(),
                status=self.status_var.get(),
                created_date=now,
                updated_date=now,
                category=self.category_entry.get().strip()
            )

        self.dialog.destroy()


class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("800x600")

        self.task_manager = TaskManager()

        self.create_widgets()
        self.refresh_task_list()

        # Check for overdue tasks on startup
        self.check_overdue_tasks()

    def create_widgets(self):
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Task", command=self.add_task)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill="x", padx=5, pady=5)

        ttk.Button(toolbar, text="Add Task", command=self.add_task).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Edit Task", command=self.edit_task).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Delete Task", command=self.delete_task).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Mark Complete", command=self.mark_complete).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Refresh", command=self.refresh_task_list).pack(side="left", padx=2)

        # Task List
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview for task list
        columns = ("Title", "Due Date", "Priority", "Status", "Category")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        # Configure columns
        self.tree.heading("Title", text="Title")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Category", text="Category")

        self.tree.column("Title", width=200)
        self.tree.column("Due Date", width=100)
        self.tree.column("Priority", width=80)
        self.tree.column("Status", width=100)
        self.tree.column("Category", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Status Bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief="sunken")
        self.status_bar.pack(side="bottom", fill="x")

        # Bind double-click to edit
        self.tree.bind("<Double-1>", lambda e: self.edit_task())

    def add_task(self):
        dialog = TaskDialog(self.root)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            self.task_manager.add_task(dialog.result)
            self.refresh_task_list()
            self.status_bar.config(text="Task added successfully")

    def edit_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to edit")
            return

        item = self.tree.item(selected[0])
        task_id = item['values'][0] if item['values'] else None

        # Find task by title (since we don't show ID in the tree)
        task = None
        for t in self.task_manager.get_all_tasks():
            if t.title == item['values'][0]:
                task = t
                break

        if not task:
            messagebox.showerror("Error", "Task not found")
            return

        dialog = TaskDialog(self.root, task)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            self.task_manager.update_task(task.id, dialog.result)
            self.refresh_task_list()
            self.status_bar.config(text="Task updated successfully")

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            item = self.tree.item(selected[0])

            # Find and delete task
            for task in self.task_manager.get_all_tasks():
                if task.title == item['values'][0]:
                    self.task_manager.delete_task(task.id)
                    break

            self.refresh_task_list()
            self.status_bar.config(text="Task deleted successfully")

    def mark_complete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to mark as complete")
            return

        item = self.tree.item(selected[0])

        # Find and update task
        for task in self.task_manager.get_all_tasks():
            if task.title == item['values'][0]:
                updated_task = Task(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    due_date=task.due_date,
                    priority=task.priority,
                    status=Status.COMPLETED.value,
                    created_date=task.created_date,
                    updated_date=datetime.now().isoformat(),
                    category=task.category
                )
                self.task_manager.update_task(task.id, updated_task)
                break

        self.refresh_task_list()
        self.status_bar.config(text="Task marked as complete")

    def refresh_task_list(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add tasks to tree
        for task in self.task_manager.get_all_tasks():
            due_date_str = task.due_date.split('T')[0]  # Just the date part

            # Color code based on status and due date
            tags = []
            if task.status == Status.COMPLETED.value:
                tags.append("completed")
            elif task.is_overdue():
                tags.append("overdue")
            elif task.days_until_due() is not None and task.days_until_due() <= 1:
                tags.append("due_soon")

            self.tree.insert("", "end", values=(
                task.title,
                due_date_str,
                task.priority,
                task.status,
                task.category
            ), tags=tags)

        # Configure tags
        self.tree.tag_configure("completed", background="lightgreen")
        self.tree.tag_configure("overdue", background="lightcoral")
        self.tree.tag_configure("due_soon", background="lightyellow")

        # Update status bar
        total_tasks = len(self.task_manager.get_all_tasks())
        overdue_tasks = len(self.task_manager.get_overdue_tasks())
        completed_tasks = len([t for t in self.task_manager.get_all_tasks() if t.status == Status.COMPLETED.value])

        self.status_bar.config(text=f"Total: {total_tasks} | Completed: {completed_tasks} | Overdue: {overdue_tasks}")

    def check_overdue_tasks(self):
        overdue_tasks = self.task_manager.get_overdue_tasks()
        if overdue_tasks:
            task_list = "\n".join([f"• {task.title}" for task in overdue_tasks[:5]])
            if len(overdue_tasks) > 5:
                task_list += f"\n... and {len(overdue_tasks) - 5} more"

            messagebox.showwarning(
                "Overdue Tasks",
                f"You have {len(overdue_tasks)} overdue task(s):\n\n{task_list}"
            )


def main():
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()