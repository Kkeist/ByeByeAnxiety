"""
Anxiety Killer Agent - Main emotional support and task management AI assistant
"""
import railtracks as rt
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class AnxietyKillerAgent:
    """AI agent that provides emotional support and helps manage tasks and anxiety"""
    
    def __init__(self, llm_provider: str = "gemini", api_key: str = "", user_preferences: str = "", data_manager=None):
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.user_preferences = user_preferences
        self.data_manager = data_manager
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the Railtracks agent with appropriate LLM"""
        # Create tools for the agent - define as standalone functions
        @rt.function_node
        def create_task_tool(title: str, description: str = "", category: str = "today_must", 
                            due_date: str = None, start_date: str = None) -> str:
            """
            Create a new task for the user.
            
            Args:
                title: Task title
                description: Task description
                category: Task category (today_must, future_date, long_term, someday_maybe)
                due_date: Due date in YYYY-MM-DD format (optional)
                start_date: When to start working on this task (optional)
            
            Returns:
                Confirmation message
            """
            if self.data_manager:
                from src.models import Task
                from datetime import datetime
                
                # Determine appropriate due date based on category
                if not due_date:
                    if category == "today_must":
                        due_date = datetime.now().strftime("%Y-%m-%d")
                    elif category == "future_date":
                        # Default to tomorrow if no date specified
                        from datetime import timedelta
                        due_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    else:
                        due_date = datetime.now().strftime("%Y-%m-%d")
                
                # Create the actual task
                task = Task(
                    id=datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    title=title,
                    description=description,
                    category=category,
                    due_date=due_date,
                    start_date=start_date
                )
                
                # Save to database
                self.data_manager.save_task(task)
                
                # Create encouraging message based on category
                category_messages = {
                    "today_must": f"✅ Added '{title}' to your today's must-do list! You've got this!",
                    "future_date": f"📅 Scheduled '{title}' for {due_date}. Great planning ahead!",
                    "long_term": f"🎯 Added '{title}' to your long-term goals. Every journey starts with a single step!",
                    "someday_maybe": f"💭 Added '{title}' to your someday/maybe list. It's great to capture all your ideas!"
                }
                
                message = category_messages.get(category, f"✅ Task '{title}' created successfully!")
                if start_date and start_date != due_date:
                    message += f" Remember to start working on it from {start_date}."
                
                return message
            else:
                return f"Task '{title}' noted (data manager not available)"
        
        @rt.function_node
        def update_diary_tool(content: str, entry_type: str = "note") -> str:
            """
            Add an entry to the user's diary.
            
            Args:
                content: Content to add to diary
                entry_type: Type of entry (note, achievement, reflection)
            
            Returns:
                Confirmation message
            """
            if self.data_manager:
                from src.models import DiaryEntry
                from datetime import datetime
                
                today = datetime.now().strftime("%Y-%m-%d")
                entry = self.data_manager.get_diary_entry(today)
                
                if not entry:
                    from src.models import DiaryEntry
                    entry = DiaryEntry(date=today)
                
                # Append to existing content
                if entry.content:
                    entry.content += f"\n\n[{entry_type.upper()}] {content}"
                else:
                    entry.content = f"[{entry_type.upper()}] {content}"
                
                self.data_manager.save_diary_entry(entry)
                return f"📔 Diary updated with {entry_type}! Your thoughts are safely recorded."
            else:
                return f"Diary entry noted: {content}"
        
        @rt.function_node
        def add_social_entry_tool(person_name: str, information: str, 
                                 category: str = "general") -> str:
            """
            Add or update information about a person in the social book.
            
            Args:
                person_name: Name of the person
                information: Information to record
                category: Category (personal_info, birthday, preferences, events, notes, or any custom field name)
            
            Returns:
                Confirmation message
            """
            if self.data_manager:
                from src.models import Person
                from datetime import datetime
                
                # Try to find existing person
                all_people = self.data_manager.get_all_people()
                person = None
                for p in all_people:
                    if p.name.lower() == person_name.lower():
                        person = p
                        break
                
                # Create new person if not found
                if not person:
                    person = Person(
                        id=datetime.now().strftime("%Y%m%d%H%M%S%f"),
                        name=person_name
                    )
                
                # Update based on category - append instead of replace
                category_lower = category.lower()
                if category_lower == "personal_info":
                    # Append to existing content
                    if person.personal_info:
                        person.personal_info = person.personal_info + "\n" + information
                    else:
                        person.personal_info = information
                elif category_lower == "birthday":
                    # Birthday is a single value, replace it
                    person.birthday = information
                elif category_lower == "preferences":
                    # Append to existing preferences
                    if person.preferences:
                        person.preferences = person.preferences + "\n" + information
                    else:
                        person.preferences = information
                elif category_lower == "notes":
                    # Append to existing notes
                    if person.notes:
                        person.notes = person.notes + "\n" + information
                    else:
                        person.notes = information
                elif category_lower == "events":
                    # Events are added to list
                    person.add_event(information)
                else:
                    # Custom field - append to existing value
                    if category in person.custom_fields:
                        person.custom_fields[category] = person.custom_fields[category] + "\n" + information
                    else:
                        person.custom_fields[category] = information
                
                # Save person
                self.data_manager.save_person(person)
                
                return f"✅ Updated {person_name}'s {category} in social book: {information}"
            else:
                return f"Added information about {person_name} to social book (data manager not available)"
        
        @rt.function_node
        def update_person_tool(person_name: str, field: str, value: str) -> str:
            """
            Update a specific field for a person in the social book.
            
            Args:
                person_name: Name of the person to update
                field: Field to update (name, personal_info, birthday, preferences, notes, or custom field name)
                value: New value for the field
            
            Returns:
                Confirmation message
            """
            if self.data_manager:
                from src.models import Person
                
                # Find person
                all_people = self.data_manager.get_all_people()
                person = None
                for p in all_people:
                    if p.name.lower() == person_name.lower():
                        person = p
                        break
                
                if not person:
                    return f"❌ Person '{person_name}' not found in social book. Use add_social_entry_tool to create a new entry."
                
                # Update field - append instead of replace (except for name and birthday)
                field_lower = field.lower()
                if field_lower == "name":
                    # Name should be replaced
                    person.name = value
                elif field_lower == "personal_info":
                    # Append to existing content
                    if person.personal_info:
                        person.personal_info = person.personal_info + "\n" + value
                    else:
                        person.personal_info = value
                elif field_lower == "birthday":
                    # Birthday is a single value, replace it
                    person.birthday = value
                elif field_lower == "preferences":
                    # Append to existing preferences
                    if person.preferences:
                        person.preferences = person.preferences + "\n" + value
                    else:
                        person.preferences = value
                elif field_lower == "notes":
                    # Append to existing notes
                    if person.notes:
                        person.notes = person.notes + "\n" + value
                    else:
                        person.notes = value
                else:
                    # Custom field - append to existing value
                    if field in person.custom_fields:
                        person.custom_fields[field] = person.custom_fields[field] + "\n" + value
                    else:
                        person.custom_fields[field] = value
                
                # Save person
                self.data_manager.save_person(person)
                
                return f"✅ Updated {person_name}'s {field} to: {value}"
            else:
                return f"Updated {person_name}'s {field} (data manager not available)"
        
        @rt.function_node
        def create_todolist_tool(name: str, description: str = "", task_titles: list = None) -> str:
            """
            Create a new todo list with optional initial tasks.
            
            Args:
                name: Name of the todo list
                description: Description of the todo list
                task_titles: List of task titles to add to the list (optional)
            
            Returns:
                Confirmation message
            """
            if self.data_manager:
                from datetime import datetime
                
                # Create tasks first if provided
                task_ids = []
                if task_titles:
                    for title in task_titles:
                        from src.models import Task
                        task = Task(
                            id=datetime.now().strftime("%Y%m%d%H%M%S%f"),
                            title=title,
                            description="",
                            category="today_must",
                            due_date=datetime.now().strftime("%Y-%m-%d")
                        )
                        self.data_manager.save_task(task)
                        task_ids.append(task.id)
                
                # Create todolist
                todolist = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "name": name,
                    "description": description,
                    "tasks": task_ids,
                    "created_at": datetime.now().isoformat(),
                    "created_by": "ai"
                }
                
                # Save todolist
                todolists = self.data_manager.get_setting("todolists", [])
                todolists.append(todolist)
                self.data_manager.save_setting("todolists", todolists)
                
                return f"📚 Created todo list '{name}' with {len(task_ids)} tasks! Perfect for organizing your thoughts!"
            else:
                return f"Todo list '{name}' noted (data manager not available)"
        
        @rt.function_node
        def break_down_task_tool(task_title: str, subtasks: list) -> str:
            """
            Break down a complex task into smaller subtasks.
            
            Args:
                task_title: The main task title to break down
                subtasks: List of subtask titles
            
            Returns:
                Confirmation message
            """
            if self.data_manager and subtasks:
                from datetime import datetime
                
                # Create a todo list for the broken down task
                todolist = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "name": f"📋 {task_title} - Breakdown",
                    "description": f"Subtasks for: {task_title}",
                    "tasks": [],
                    "created_at": datetime.now().isoformat(),
                    "created_by": "ai"
                }
                
                # Create subtasks
                task_ids = []
                for i, subtask in enumerate(subtasks, 1):
                    from src.models import Task
                    task = Task(
                        id=datetime.now().strftime("%Y%m%d%H%M%S%f"),
                        title=f"{i}. {subtask}",
                        description=f"Part of: {task_title}",
                        category="today_must",
                        due_date=datetime.now().strftime("%Y-%m-%d")
                    )
                    self.data_manager.save_task(task)
                    task_ids.append(task.id)
                
                todolist["tasks"] = task_ids
                
                # Save todolist
                todolists = self.data_manager.get_setting("todolists", [])
                todolists.append(todolist)
                self.data_manager.save_setting("todolists", todolists)
                
                return f"🔧 Broke down '{task_title}' into {len(subtasks)} manageable steps! Taking it one step at a time makes everything easier."
            else:
                return "I'd be happy to help break down tasks, but I need the subtasks list to work with."
        
        @rt.function_node
        def schedule_reminder_tool(person_name: str, event: str, date: str, reminder_days: int = 7) -> str:
            """
            Schedule a reminder for an important event (like birthdays).
            
            Args:
                person_name: Name of the person
                event: Type of event (birthday, anniversary, etc.)
                date: Date of the event (YYYY-MM-DD format)
                reminder_days: How many days before to remind (default 7)
            
            Returns:
                Confirmation message
            """
            if self.data_manager:
                # This would integrate with the social book
                social_contacts = self.data_manager.get_setting("social_contacts", [])
                
                # Find or create contact
                contact = None
                for c in social_contacts:
                    if c.get("name", "").lower() == person_name.lower():
                        contact = c
                        break
                
                if not contact:
                    contact = {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                        "name": person_name,
                        "events": []
                    }
                    social_contacts.append(contact)
                
                # Add event
                if "events" not in contact:
                    contact["events"] = []
                
                contact["events"].append({
                    "type": event,
                    "date": date,
                    "reminder_days": reminder_days
                })
                
                self.data_manager.save_setting("social_contacts", social_contacts)
                
                return f"📅 Set reminder for {person_name}'s {event} on {date}. I'll remind you {reminder_days} days before!"
            else:
                return f"Reminder for {person_name}'s {event} noted"
        
        tools = [create_task_tool, update_diary_tool, add_social_entry_tool, update_person_tool, create_todolist_tool, break_down_task_tool, schedule_reminder_tool]
        
        # Base system message for ADHD support
        base_system_message = """You are Anxiety Killer, a compassionate AI assistant designed to help individuals with ADHD manage their daily lives and reduce anxiety.

Core Principles:
- Always be patient, supportive, and encouraging
- Celebrate every small achievement, no matter how minor
- Never judge or criticize the user
- Break down complex tasks into manageable steps
- Provide emotional validation and support
- Help users feel safe and understood
- Remember that ADHD is not a character flaw but a different way of thinking

Your Tools and When to Use Them:
1. create_task_tool: When users mention things they need to do
   - Categories: today_must (urgent), future_date (scheduled), long_term (habits/goals), someday_maybe (ideas/wishes)
   - Always ask "When do you need this done?" to choose the right category
2. create_todolist_tool: For organizing related tasks into projects
3. break_down_task_tool: When users feel overwhelmed by complex tasks
4. update_diary_tool: For recording daily experiences, achievements, or reflections
5. add_social_entry_tool: For adding information about people in social book
   - Categories: personal_info, birthday, preferences, events, notes, or any custom field name
   - Can create new person or add to existing one
   - IMPORTANT: This APPENDS to existing content (does not replace), except for birthday which replaces
6. update_person_tool: For updating specific fields of an existing person
   - Fields: name, personal_info, birthday, preferences, notes, or any custom field
   - IMPORTANT: This APPENDS to existing content (does not replace), except for name and birthday which replace
7. schedule_reminder_tool: For important dates like birthdays or events

Proactive Assistance:
- When users mention tasks → Offer to create them with appropriate scheduling
- When users feel overwhelmed → Suggest breaking tasks into smaller steps
- When users mention projects → Propose creating organized todo lists
- When users share experiences → Offer to record in diary
- When users mention people/dates → Suggest adding to social book

Communication Style:
- Keep responses concise but warm
- Use encouraging language and emojis
- Ask clarifying questions to provide better help
- Always offer practical, actionable solutions
- Be proactive in suggesting organization tools

Remember: The user is doing their best, and every step forward deserves recognition. Your goal is to make their life more organized and less anxious."""

        if self.user_preferences:
            base_system_message += f"\n\nUser Preferences:\n{self.user_preferences}"
        
        # Select LLM based on provider
        if self.llm_provider == "gemini":
            llm = rt.llm.GeminiLLM("gemini-2.5-flash", api_key=self.api_key)
        else:  # anthropic/claude
            llm = rt.llm.AnthropicLLM("claude-3-5-sonnet-20241022", api_key=self.api_key)
        
        # Create the agent
        self.agent = rt.agent_node(
            name="Anxiety Killer",
            llm=llm,
            system_message=base_system_message,
            tool_nodes=tools
        )
    
    def create_task_tool(self, title: str, description: str, category: str = "today_must", 
                        due_date: Optional[str] = None) -> str:
        """
        Create a new task for the user.
        
        Args:
            title: Task title
            description: Task description
            category: Task category (today_must, future_date, long_term, someday_maybe)
            due_date: Due date in YYYY-MM-DD format (optional)
        
        Returns:
            Confirmation message
        """
        # This will be connected to the actual task manager
        return f"Task '{title}' created successfully in category '{category}'"
    
    def update_diary_tool(self, content: str, entry_type: str = "note") -> str:
        """
        Add an entry to the user's diary.
        
        Args:
            content: Content to add to diary
            entry_type: Type of entry (note, achievement, reflection)
        
        Returns:
            Confirmation message
        """
        return f"Diary updated with {entry_type}"
    
    def add_social_entry_tool(self, person_name: str, information: str, 
                             category: str = "general") -> str:
        """
        Add or update information about a person in the social book.
        
        Args:
            person_name: Name of the person
            information: Information to record
            category: Category (personal_info, birthday, preferences, events, notes, or any custom field name)
        
        Returns:
            Confirmation message
        """
        if self.data_manager:
            from src.models import Person
            from datetime import datetime
            
            # Try to find existing person
            all_people = self.data_manager.get_all_people()
            person = None
            for p in all_people:
                if p.name.lower() == person_name.lower():
                    person = p
                    break
            
            # Create new person if not found
            if not person:
                person = Person(
                    id=datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    name=person_name
                )
            
            # Update based on category - append instead of replace
            category_lower = category.lower()
            if category_lower == "personal_info":
                # Append to existing content
                if person.personal_info:
                    person.personal_info = person.personal_info + "\n" + information
                else:
                    person.personal_info = information
            elif category_lower == "birthday":
                # Birthday is a single value, replace it
                person.birthday = information
            elif category_lower == "preferences":
                # Append to existing preferences
                if person.preferences:
                    person.preferences = person.preferences + "\n" + information
                else:
                    person.preferences = information
            elif category_lower == "notes":
                # Append to existing notes
                if person.notes:
                    person.notes = person.notes + "\n" + information
                else:
                    person.notes = information
            elif category_lower == "events":
                # Events are added to list
                person.add_event(information)
            else:
                # Custom field - append to existing value
                if category in person.custom_fields:
                    person.custom_fields[category] = person.custom_fields[category] + "\n" + information
                else:
                    person.custom_fields[category] = information
            
            # Save person
            self.data_manager.save_person(person)
            
            return f"✅ Updated {person_name}'s {category} in social book: {information}"
        else:
            return f"Added information about {person_name} to social book (data manager not available)"
    
    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a message to the agent and get a response.
        
        Args:
            message: User's message
            context: Optional context (diary entries, tasks, etc.)
        
        Returns:
            Agent's response
        """
        # Add context to message if provided
        full_message = message
        if context:
            context_str = "\n\nCurrent Context:\n"
            if "tasks" in context:
                context_str += f"Tasks: {json.dumps(context['tasks'], indent=2)}\n"
            if "recent_diary" in context:
                context_str += f"Recent Diary: {context['recent_diary']}\n"
            
            # Add mentions information (tasks, todolists, people, etc.)
            if "mentions" in context and context["mentions"]:
                context_str += "\nMentioned Items:\n"
                for mention_key, mention_data in context["mentions"].items():
                    if mention_data.get('type') == 'task':
                        context_str += f"- Task: {mention_data.get('title', 'Unknown')} "
                        context_str += f"(Category: {mention_data.get('category', 'N/A')}, "
                        context_str += f"Due: {mention_data.get('due_date', 'N/A')})\n"
                        if mention_data.get('description'):
                            context_str += f"  Description: {mention_data.get('description')}\n"
                    elif mention_data.get('type') == 'todolist':
                        context_str += f"- TodoList: {mention_data.get('name', 'Unknown')} "
                        context_str += f"({mention_data.get('task_count', 0)} tasks)\n"
                    elif mention_data.get('type') == 'person':
                        context_str += f"- Person: {mention_data.get('name', 'Unknown')}\n"
                        if mention_data.get('personal_info'):
                            context_str += f"  Personal Info: {mention_data.get('personal_info')}\n"
                        if mention_data.get('birthday'):
                            context_str += f"  Birthday: {mention_data.get('birthday')}\n"
                        if mention_data.get('preferences'):
                            context_str += f"  Preferences: {mention_data.get('preferences')}\n"
                        if mention_data.get('events'):
                            context_str += f"  Events: {', '.join(mention_data.get('events', []))}\n"
                        if mention_data.get('notes'):
                            context_str += f"  Notes: {mention_data.get('notes')}\n"
                        if mention_data.get('custom_fields'):
                            for field, value in mention_data.get('custom_fields', {}).items():
                                context_str += f"  {field}: {value}\n"
                    elif mention_data.get('type') == 'diary':
                        context_str += f"- Diary Entry: {mention_data.get('date', 'Unknown')}\n"
                        if mention_data.get('has_entry'):
                            context_str += f"  Content Preview: {mention_data.get('content_preview', 'N/A')}\n"
                    elif mention_data.get('type') == 'calendar':
                        context_str += f"- Calendar: {mention_data.get('date', 'Unknown')} "
                        context_str += f"({mention_data.get('task_count', 0)} tasks)\n"
                        if mention_data.get('tasks'):
                            for task in mention_data.get('tasks', [])[:5]:
                                context_str += f"  - {task.get('title', 'Unknown')}\n"
            
            full_message = message + context_str
        
        # Call the agent
        response = await rt.call(self.agent, full_message)
        return response.text
    
    async def generate_daily_summary(self, diary_content: str, context: str) -> str:
        """
        Generate a daily summary based on context (chats, tasks, activities).
        Note: diary_content is kept for compatibility but not used.
        
        Args:
            diary_content: Not used (kept for compatibility)
            context: Summary context with tasks, chats, and activities
        
        Returns:
            Daily summary
        """
        summary_prompt = f"""Please create a warm, encouraging daily summary for the user.

{context}

Create a summary that:
1. Acknowledges what was accomplished (celebrate even small wins!)
2. Reflects on the day's activities and interactions
3. Provides gentle encouragement for tomorrow
4. Keeps a positive, supportive tone
5. Focuses on tasks completed, chat interactions, and activities - NOT on any user-written diary content

Keep it concise but heartfelt (under 150 words)."""

        response = await rt.call(self.agent, summary_prompt)
        return response.text
    
    async def suggest_task_breakdown(self, task_title: str, task_description: str) -> List[str]:
        """
        Suggest how to break down a task into smaller steps.
        
        Args:
            task_title: Title of the task
            task_description: Description of the task
        
        Returns:
            List of suggested subtasks
        """
        breakdown_prompt = f"""Help break down this task into smaller, manageable steps:

Task: {task_title}
Description: {task_description}

Provide 3-5 concrete, actionable subtasks. Each subtask should:
- Be small enough to complete in one sitting
- Be clearly defined
- Build toward completing the main task

Format your response as a simple numbered list."""

        response = await rt.call(self.agent, breakdown_prompt)
        # Parse the response into a list
        lines = response.text.strip().split('\n')
        subtasks = [line.strip('0123456789. ') for line in lines if line.strip() and line[0].isdigit()]
        return subtasks
    
    def update_preferences(self, new_preferences: str):
        """Update user preferences and reinitialize agent"""
        self.user_preferences = new_preferences
        self._initialize_agent()
    
    def update_api_key(self, api_key: str, provider: str):
        """Update API key and provider"""
        self.api_key = api_key
        self.llm_provider = provider
        self._initialize_agent()

