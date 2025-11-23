# Installation Guide for ByeByeAnxiety

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Internet connection for AI features

## Step-by-Step Installation

### 1. Install Python Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- `railtracks` - AI agent framework
- `railtracks-cli` - Railtracks command-line tools
- `google-generativeai` - Google Gemini API
- `anthropic` - Anthropic Claude API
- `PyQt6` - GUI framework
- `tinydb` - Local database
- `python-dateutil` - Date utilities

### 2. Verify Installation

Run the test script to verify everything is installed correctly:

```bash
python test_basic.py
```

You should see:
```
Testing imports...
[OK] All imports successful

Testing DataManager...
[OK] Task operations work
[OK] Diary operations work
[OK] Social book operations work
[OK] Settings operations work
...
```

### 3. Get an API Key

Choose one of these providers:

#### Option A: Google Gemini (Recommended for beginners)
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

#### Option B: Anthropic Claude
1. Go to https://console.anthropic.com/
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new key
5. Copy the key

**Note**: Both services may require payment after free tier limits.

### 4. Run the Application

#### Windows:
```bash
python main.py
```
Or double-click `run.bat`

#### Mac/Linux:
```bash
python main.py
```
Or run `./run.sh` (may need `chmod +x run.sh` first)

### 5. Configure API Key

1. Click the **⚙️ Settings** button in the app
2. Paste your API key in the appropriate field
3. (Optional) Add user preferences
4. Click **OK**

## Troubleshooting

### "ModuleNotFoundError"

**Problem**: Missing Python packages

**Solution**:
```bash
pip install -r requirements.txt --force-reinstall
```

### "No module named 'PyQt6'"

**Problem**: PyQt6 not installed properly

**Solution**:
```bash
pip install PyQt6 --upgrade
```

### "API key invalid"

**Problem**: Incorrect or expired API key

**Solution**:
1. Verify the key is copied correctly (no extra spaces)
2. Check if the key is active on the provider's website
3. Try generating a new key

### Application won't start

**Problem**: Python version or system issues

**Solution**:
1. Check Python version: `python --version` (should be 3.8+)
2. Try running with: `python -u main.py` to see full errors
3. Check if all dependencies installed: `pip list`

### Floating windows not showing

**Problem**: Windows positioned off-screen

**Solution**:
- Use menu: **View → Show Anxiety Killer / Show Ask Me**

## Platform-Specific Notes

### Windows
- Works with Python from python.org or Microsoft Store
- May need to use `python` or `py` command
- Antivirus might flag first run (false positive)

### macOS
- May need to install Python from python.org (not system Python)
- First run might ask for permissions
- Use `python3` instead of `python`

### Linux
- Install PyQt6 dependencies: `sudo apt-get install python3-pyqt6`
- May need: `sudo apt-get install python3-pip`
- Use `python3` instead of `python`

## Virtual Environment (Recommended)

To avoid conflicts with other Python projects:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run app
python main.py
```

## Updating

To update to a newer version:

1. Backup your `data/` folder
2. Download new version
3. Run: `pip install -r requirements.txt --upgrade`
4. Copy your `data/` folder back

## Uninstalling

1. Backup `data/` folder if you want to keep your information
2. Delete the project folder
3. (Optional) Remove Python packages:
   ```bash
   pip uninstall railtracks railtracks-cli google-generativeai anthropic PyQt6 tinydb python-dateutil
   ```

## Need Help?

- Check USAGE.md for how to use the app
- Review README.md for project overview
- Make sure your API key is valid and has credits
- Test internet connection

## Success!

If you see the main window with tabs and floating AI assistants, you're all set! 🎉

Read USAGE.md to learn how to use all the features.

