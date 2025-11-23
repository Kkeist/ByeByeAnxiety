# ByeByeAnxiety Usage Guide

## Getting Started

### 1. Installation

First, install all required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Get API Keys

You need an API key from either:

- **Google Gemini** (Recommended for testing): https://makersuite.google.com/app/apikey
- **Anthropic Claude**: https://console.anthropic.com/

### 3. Run the Application

```bash
python main.py
```

## First Time Setup

1. When the application starts, click the **⚙️ Settings** button
2. Enter your API key (Gemini or Anthropic)
3. (Optional) Add user preferences to personalize AI responses
4. Click **OK** to save

## Features Overview

### 🤖 AI Assistants (Floating Windows)

#### Anxiety Killer 💙
- **Purpose**: Emotional support and task management
- **Features**:
  - Chat about your feelings and concerns
  - Get help organizing tasks
  - Receive encouragement and support
  - Break down overwhelming tasks
  
- **Message Types**:
  - **Free**: AI decides how to handle your message
  - **Chat**: Adds to your diary as a journal entry
  - **Inspiration**: Saves ideas for later
  - **Task**: Creates a new task

#### Ask Me 💚
- **Purpose**: ADHD-friendly learning assistant
- **Features**:
  - Ask questions about any topic
  - Get explanations broken down into simple steps
  - Each question creates a separate conversation
  - Search through past conversations

### 📋 Tasks

Organize your todos into categories:

- **Today Must Do**: Critical tasks for today
- **Future Tasks**: Tasks scheduled for specific dates
- **Long-term Goals**: Ongoing projects
- **Someday/Maybe**: Ideas and wishes

**Tips**:
- Click **+ Add Task** to create new tasks
- Check boxes to mark tasks complete
- Edit or delete tasks with the buttons
- AI celebrates when you complete tasks!

### ⏱️ Focus Timer

Pomodoro-style timer to help you stay focused:

1. Set duration (default: 25 minutes)
2. Click **Start**
3. Focus on your work
4. Earn points when you complete sessions
5. Use points to collect stickers (coming soon!)

### 📔 Diary

Keep track of your daily experiences:

- Click any date on the calendar to view/edit that day's entry
- Write freely about your day
- Dates with entries are highlighted in green
- AI can generate summaries (feature in development)

### 👥 Social Book

Remember important people in your life:

- Add people with their information
- Set birthdays with optional reminders
- Record preferences, events, and notes
- AI can remind you of upcoming birthdays

## Tips for ADHD Users

### Using Anxiety Killer Effectively

1. **Start your day**: Ask for help prioritizing tasks
2. **Feeling overwhelmed**: Request task breakdown
3. **Need motivation**: Chat about what's bothering you
4. **Celebrate wins**: Share completed tasks for encouragement

### Using Ask Me Effectively

1. **Ask "why" questions**: Understanding helps retention
2. **Request examples**: Concrete examples make concepts clear
3. **Break it down**: Ask for simpler explanations if needed
4. **Follow tangents**: It's okay to jump between topics!

### Task Management Tips

1. **Keep "Today Must Do" short**: 3-5 tasks maximum
2. **Use "Someday/Maybe"**: Capture ideas without pressure
3. **Break big tasks**: Use subtasks for complex projects
4. **Don't delete completed tasks immediately**: Review your progress!

### Focus Timer Tips

1. **Start small**: Try 15 minutes if 25 feels too long
2. **No judgment**: Stopping early is okay - you still earn points!
3. **Celebrate effort**: Every minute of focus counts
4. **Build gradually**: Increase duration as you build stamina

## Privacy & Data

- **All data stored locally**: Your information never leaves your computer
- **API calls**: Only your messages are sent to AI providers (Google/Anthropic)
- **No tracking**: We don't collect any analytics or usage data
- **Your control**: Delete or export data anytime from the data folder

## Troubleshooting

### AI assistants not responding

1. Check Settings → API Keys are entered correctly
2. Verify your API key is active (test on provider's website)
3. Check internet connection
4. Try switching between Gemini and Claude

### Application won't start

1. Ensure Python 3.8+ is installed
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Check for error messages in terminal

### Floating windows disappeared

- Use **View** menu → **Show Anxiety Killer** / **Show Ask Me**

## Keyboard Shortcuts

- **Enter**: Send message in chat windows
- **Ctrl+S**: Save diary entry (when focused)

## Data Location

All your data is stored in the `data/` folder:
- `tasks.json`: Your tasks
- `diary.json`: Diary entries
- `social.json`: Social book
- `focus.json`: Focus sessions
- `chat_history.json`: AI conversations
- `settings.json`: App settings

**Backup tip**: Copy the entire `data/` folder to backup your information!

## Getting Help

- Check this guide first
- Review the README.md for technical details
- Remember: The AI assistants are here to help you!

## Philosophy

This app is designed with ADHD in mind:

- **No judgment**: Every small step is celebrated
- **Flexible**: Use what works, ignore what doesn't
- **Supportive**: AI provides encouragement, not criticism
- **Privacy-first**: Your struggles are yours alone
- **Realistic**: We know life with ADHD is challenging

You're doing great just by being here. Take it one step at a time. 💙

