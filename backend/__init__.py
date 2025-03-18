"""
Backend module for server functionality and task management.

This module contains the Flask web server and task orchestration components.
"""

from .app import app
from .task_manager import task_manager, Task, TaskStatus

__all__ = ['app', 'task_manager', 'Task', 'TaskStatus']
