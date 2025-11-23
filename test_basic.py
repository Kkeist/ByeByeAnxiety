"""
Basic functionality test for ByeByeAnxiety
Run this to verify the core components work
"""
import sys
from datetime import datetime

# Test imports
print("Testing imports...")
try:
    from src.models import Task, TaskCategory, DiaryEntry, Person, FocusSession
    from src.utils import DataManager
    from src.agents import AnxietyKillerAgent, AskMeAgent
    print("[OK] All imports successful")
except Exception as e:
    print(f"[ERROR] Import error: {e}")
    sys.exit(1)

# Test DataManager
print("\nTesting DataManager...")
try:
    dm = DataManager("test_data")
    
    # Test task operations
    test_task = Task(
        id="test1",
        title="Test Task",
        description="This is a test",
        category=TaskCategory.TODAY_MUST,
        due_date=datetime.now().strftime("%Y-%m-%d")
    )
    dm.save_task(test_task)
    loaded_task = dm.get_task("test1")
    assert loaded_task.title == "Test Task"
    print("[OK] Task operations work")
    
    # Test diary operations
    test_entry = DiaryEntry(
        date=datetime.now().strftime("%Y-%m-%d"),
        content="Test diary entry"
    )
    dm.save_diary_entry(test_entry)
    loaded_entry = dm.get_diary_entry(test_entry.date)
    assert loaded_entry.content == "Test diary entry"
    print("[OK] Diary operations work")
    
    # Test social operations
    test_person = Person(
        id="person1",
        name="Test Person",
        personal_info="Test info"
    )
    dm.save_person(test_person)
    loaded_person = dm.get_person("person1")
    assert loaded_person.name == "Test Person"
    print("[OK] Social book operations work")
    
    # Test settings
    dm.save_setting("test_key", "test_value")
    value = dm.get_setting("test_key")
    assert value == "test_value"
    print("[OK] Settings operations work")
    
    print("\n[OK] DataManager tests passed!")
    
except Exception as e:
    print(f"[ERROR] DataManager error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Agent initialization (without API calls)
print("\nTesting Agent initialization...")
try:
    # These will fail without API keys, but should initialize
    anxiety_agent = AnxietyKillerAgent(llm_provider="gemini", api_key="test_key")
    ask_me_agent = AskMeAgent(llm_provider="gemini", api_key="test_key")
    print("[OK] Agents can be initialized")
except Exception as e:
    print(f"[ERROR] Agent initialization error: {e}")
    import traceback
    traceback.print_exc()

# Test UI imports (without actually showing UI)
print("\nTesting UI imports...")
try:
    from PyQt6.QtWidgets import QApplication
    from src.ui import MainWindow
    print("[OK] UI components can be imported")
except Exception as e:
    print(f"[ERROR] UI import error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Basic tests completed!")
print("="*50)
print("\nNext steps:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Get an API key from Google or Anthropic")
print("3. Run the app: python main.py")
print("4. Configure your API key in Settings")
print("\nNote: AI features require a valid API key to function.")

