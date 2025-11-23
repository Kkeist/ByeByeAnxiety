"""Data persistence manager using TinyDB"""
from tinydb import TinyDB, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from pathlib import Path

from src.models import Task, DiaryEntry, Person, FocusSession, FocusStats


class DataManager:
    """Manages all data persistence for the application"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize databases
        self.tasks_db = TinyDB(self.data_dir / "tasks.json")
        self.diary_db = TinyDB(self.data_dir / "diary.json")
        self.social_db = TinyDB(self.data_dir / "social.json")
        self.focus_db = TinyDB(self.data_dir / "focus.json")
        self.chat_db = TinyDB(self.data_dir / "chat_history.json")
        self.settings_db = TinyDB(self.data_dir / "settings.json")
    
    # Task Management
    def save_task(self, task: Task) -> None:
        """Save or update a task"""
        Task_query = Query()
        existing = self.tasks_db.search(Task_query.id == task.id)
        if existing:
            self.tasks_db.update(task.to_dict(), Task_query.id == task.id)
        else:
            self.tasks_db.insert(task.to_dict())
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        Task_query = Query()
        result = self.tasks_db.search(Task_query.id == task_id)
        return Task.from_dict(result[0]) if result else None
    
    def get_tasks_by_category(self, category: str) -> List[Task]:
        """Get all tasks in a category"""
        Task_query = Query()
        results = self.tasks_db.search(Task_query.category == category)
        return [Task.from_dict(t) for t in results]
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return [Task.from_dict(t) for t in self.tasks_db.all()]
    
    def delete_task(self, task_id: str) -> None:
        """Delete a task and remove it from all todolists"""
        Task_query = Query()
        self.tasks_db.remove(Task_query.id == task_id)
        
        # Remove task from all todolists
        self.remove_task_from_all_todolists(task_id)
    
    def remove_task_from_all_todolists(self, task_id: str):
        """Remove a task from all todolists"""
        try:
            todolists = self.get_setting("todolists", [])
            updated = False
            
            for todolist in todolists:
                if task_id in todolist.get("tasks", []):
                    todolist["tasks"].remove(task_id)
                    updated = True
            
            if updated:
                self.save_setting("todolists", todolists)
        except Exception as e:
            print(f"Error removing task from todolists: {e}")
    
    def get_tasks_by_date(self, date: str) -> List[Task]:
        """Get tasks for a specific date"""
        Task_query = Query()
        results = self.tasks_db.search(Task_query.due_date == date)
        return [Task.from_dict(t) for t in results]
    
    # Diary Management
    def save_diary_entry(self, entry: DiaryEntry) -> None:
        """Save or update a diary entry"""
        Entry_query = Query()
        existing = self.diary_db.search(Entry_query.date == entry.date)
        if existing:
            self.diary_db.update(entry.to_dict(), Entry_query.date == entry.date)
        else:
            self.diary_db.insert(entry.to_dict())
    
    def get_diary_entry(self, date: str) -> Optional[DiaryEntry]:
        """Get diary entry for a specific date"""
        Entry_query = Query()
        result = self.diary_db.search(Entry_query.date == date)
        return DiaryEntry.from_dict(result[0]) if result else None
    
    def get_all_diary_entries(self) -> List[DiaryEntry]:
        """Get all diary entries"""
        return [DiaryEntry.from_dict(e) for e in self.diary_db.all()]
    
    # Social Book Management
    def save_person(self, person: Person) -> None:
        """Save or update a person"""
        Person_query = Query()
        existing = self.social_db.search(Person_query.id == person.id)
        if existing:
            self.social_db.update(person.to_dict(), Person_query.id == person.id)
        else:
            self.social_db.insert(person.to_dict())
    
    def get_person(self, person_id: str) -> Optional[Person]:
        """Get a person by ID"""
        Person_query = Query()
        result = self.social_db.search(Person_query.id == person_id)
        return Person.from_dict(result[0]) if result else None
    
    def get_all_people(self) -> List[Person]:
        """Get all people"""
        return [Person.from_dict(p) for p in self.social_db.all()]
    
    def delete_person(self, person_id: str) -> None:
        """Delete a person"""
        Person_query = Query()
        self.social_db.remove(Person_query.id == person_id)
    
    # Focus Session Management
    def save_focus_session(self, session: FocusSession) -> None:
        """Save a focus session"""
        self.focus_db.insert(session.to_dict())
    
    def get_focus_stats(self) -> FocusStats:
        """Get focus statistics"""
        sessions = [FocusSession.from_dict(s) for s in self.focus_db.all()]
        stats = FocusStats()
        for session in sessions:
            if session.completed:
                stats.add_session(session)
        return stats
    
    def get_recent_focus_sessions(self, limit: int = 10) -> List[FocusSession]:
        """Get recent focus sessions"""
        all_sessions = [FocusSession.from_dict(s) for s in self.focus_db.all()]
        return sorted(all_sessions, key=lambda x: x.start_time, reverse=True)[:limit]
    
    def get_focus_sessions_by_date(self, date: str) -> List[FocusSession]:
        """Get focus sessions for a specific date"""
        all_sessions = [FocusSession.from_dict(s) for s in self.focus_db.all()]
        # Filter sessions that started on the given date
        sessions_on_date = [s for s in all_sessions if s.start_time and s.start_time.startswith(date)]
        return sorted(sessions_on_date, key=lambda x: x.start_time)
    
    # Chat History Management
    def save_chat_message(self, agent_name: str, role: str, content: str, 
                         conversation_id: Optional[str] = None) -> None:
        """Save a chat message"""
        message = {
            "agent": agent_name,
            "conversation_id": conversation_id or "main",
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.chat_db.insert(message)
    
    def get_chat_history(self, agent_name: str, conversation_id: Optional[str] = None,
                        limit: Optional[int] = None, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get chat history for an agent, optionally filtered by date"""
        Chat_query = Query()
        conv_id = conversation_id or "main"
        results = self.chat_db.search(
            (Chat_query.agent == agent_name) & (Chat_query.conversation_id == conv_id)
        )
        
        # Filter by date if provided
        if date:
            results = [r for r in results if r.get('timestamp', '').startswith(date)]
        
        # Sort by timestamp
        results = sorted(results, key=lambda x: x['timestamp'])
        if limit:
            results = results[-limit:]
        return results
    
    def get_all_conversations(self, agent_name: str) -> List[str]:
        """Get all conversation IDs for an agent"""
        Chat_query = Query()
        results = self.chat_db.search(Chat_query.agent == agent_name)
        conv_ids = set(r['conversation_id'] for r in results)
        return sorted(list(conv_ids))
    
    def delete_conversation(self, agent_name: str, conversation_id: str) -> None:
        """Delete a conversation"""
        Chat_query = Query()
        self.chat_db.remove(
            (Chat_query.agent == agent_name) & (Chat_query.conversation_id == conversation_id)
        )
    
    # Settings Management
    def save_setting(self, key: str, value: Any) -> None:
        """Save a setting"""
        Setting_query = Query()
        existing = self.settings_db.search(Setting_query.key == key)
        data = {"key": key, "value": value}
        if existing:
            self.settings_db.update(data, Setting_query.key == key)
        else:
            self.settings_db.insert(data)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting"""
        Setting_query = Query()
        result = self.settings_db.search(Setting_query.key == key)
        return result[0]['value'] if result else default
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        all_records = self.settings_db.all()
        if not all_records:
            return {}
        
        # Handle both old format (direct key-value) and new format (key/value structure)
        result = {}
        for record in all_records:
            if 'key' in record and 'value' in record:
                # New format
                result[record['key']] = record['value']
            else:
                # Old format - the record itself contains the settings
                for key, value in record.items():
                    if key not in ['doc_id']:  # Skip TinyDB metadata
                        result[key] = value
        
        return result
    
    def clear_all_data(self):
        """Clear all application data (for testing/reset purposes)"""
        # Clear all databases
        self.tasks_db.truncate()
        self.diary_db.truncate()
        self.social_db.truncate()
        self.focus_db.truncate()
        self.chat_db.truncate()
        
        # Clear settings but keep API keys and preferences
        # (or clear everything - user's choice)
        # For now, we'll clear everything except API keys
        all_settings = self.get_all_settings()
        self.settings_db.truncate()
        
        # Restore only API keys if they exist
        if "gemini_api_key" in all_settings:
            self.save_setting("gemini_api_key", all_settings["gemini_api_key"])
        if "anthropic_api_key" in all_settings:
            self.save_setting("anthropic_api_key", all_settings["anthropic_api_key"])
        
        # Clear todolists
        self.save_setting("todolists", [])
        self.save_setting("user_points", 0)
        self.save_setting("user_stickers", {})

