# MCP Local Files Server - Complete Setup Guide

This guide provides **step-by-step instructions** to set up a Python MCP (Model Context Protocol) server that gives GitHub Copilot context from your local files through VSCode.

## 📋 What You'll Need

- Python 3.8 or higher
- VSCode with GitHub Copilot extension
- A project directory you want to provide context from

## 📁 File Structure

After setup, you'll have these files:

```
mcp-local-files/           # ← Create this directory
├── mcp_server.py          # ← Main server (save artifact 1 here)
├── launcher.py            # ← Setup script (save artifact 3 here)
└── README.md             # ← This guide (save artifact 2 here)
```

## 🚀 Step-by-Step Installation

### **STEP 1: Download and Setup Files**

1. **Create the MCP directory:**
   ```bash
   # Choose a location for the MCP server files
   mkdir ~/mcp-local-files
   cd ~/mcp-local-files
   ```

2. **Save the server files:**
   - Copy the `mcp_server.py` code from **Artifact 1** → Save as `mcp_server.py`
   - Copy the `launcher.py` code from **Artifact 3** → Save as `launcher.py`
   - Copy this README from **Artifact 2** → Save as `README.md`

3. **Make scripts executable (macOS/Linux only):**
   ```bash
   chmod +x mcp_server.py
   chmod +x launcher.py
   ```

### **STEP 2: Verify Python Installation**

1. **Check Python version:**
   ```bash
   python --version
   # OR
   python3 --version
   ```
   ✅ **Required:** Python 3.8 or higher

2. **If Python is not installed:**
   - **Windows:** Download from [python.org](https://python.org)
   - **macOS:** `brew install python3` or download from python.org
   - **Linux:** `sudo apt install python3` (Ubuntu/Debian) or `sudo yum install python3` (RHEL/CentOS)

### **STEP 3: Setup Your Project**

1. **Navigate to your project directory:**
   ```bash
   # Example: Replace with your actual project path
   cd ~/my-awesome-project
   ```

2. **Run the automated setup:**
   ```bash
   # Point to where you saved the MCP files
   python ~/mcp-local-files/launcher.py setup --project .
   ```

   This will automatically:
   - Create VSCode configuration files
   - Set up MCP server configuration
   - Install any needed dependencies

### **STEP 4: VSCode Configuration (Manual Method)**

**If the automated setup doesn't work, follow these manual steps:**

#### **A. Install GitHub Copilot Extension**

1. Open VSCode
2. Go to Extensions tab (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "GitHub Copilot"
4. Install the official GitHub Copilot extension
5. Sign in to your GitHub account when prompted

#### **B. Configure VSCode Settings**

1. **Open VSCode User Settings:**
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
   - Type "Preferences: Open User Settings (JSON)"
   - Click on it

2. **Add this configuration to your settings.json:**
   ```json
   {
     "github.copilot.enable": {
       "*": true,
       "yaml": true,
       "plaintext": true,
       "markdown": true
     },
     "mcp.servers": {
       "local-files": {
         "command": "python",
         "args": [
           "/Users/YOUR_USERNAME/mcp-local-files/mcp_server.py",
           "--root",
           "${workspaceFolder}"
         ],
         "cwd": "${workspaceFolder}"
       }
     }
   }
   ```

   **⚠️ IMPORTANT:** Replace `/Users/YOUR_USERNAME/mcp-local-files/mcp_server.py` with the **absolute path** to where you saved `mcp_server.py`

   **Finding the absolute path:**
   ```bash
   # In the mcp-local-files directory, run:
   pwd
   # Copy the output and add /mcp_server.py to the end
   ```

#### **C. Project-Specific Settings (Recommended)**

1. **In your project directory, create `.vscode` folder:**
   ```bash
   # From your project root
   mkdir .vscode
   ```

2. **Create `.vscode/settings.json` file:**
   ```bash
   # Create the file
   touch .vscode/settings.json
   ```

3. **Add this content to `.vscode/settings.json`:**
   ```json
   {
     "github.copilot.enable": {
       "*": true,
       "yaml": true,
       "plaintext": true,
       "markdown": true
     },
     "mcp.servers": {
       "local-files": {
         "command": "python",
         "args": [
           "/ABSOLUTE/PATH/TO/mcp_server.py",
           "--root",
           "${workspaceFolder}"
         ],
         "cwd": "${workspaceFolder}"
       }
     }
   }
   ```

   **Again, replace `/ABSOLUTE/PATH/TO/mcp_server.py` with your actual path.**

### **STEP 5: Start the MCP Server**

#### **Option A: Using the Launcher (Recommended)**

```bash
# From your project directory
python ~/mcp-local-files/launcher.py start --project .
```

#### **Option B: Manual Start**

```bash
# Navigate to your project
cd ~/my-awesome-project

# Start the server
python ~/mcp-local-files/mcp_server.py --root . --max-file-size 2097152
```

**You should see output like:**
```
2024-06-27 10:30:00 - __main__ - INFO - Starting MCP server for directory: /Users/username/my-awesome-project
```

### **STEP 6: Test the Setup**

1. **Keep the MCP server running** (don't close the terminal)

2. **Open VSCode in your project:**
   ```bash
   # From your project directory
   code .
   ```

3. **Create a test file:**
   - Create a new file called `test_copilot.py`
   - Add this code:
   ```python
   # test_copilot.py
   def analyze_project_files():
       """
       This function should get suggestions based on other files in the project.
       Start typing below and see if Copilot suggests code based on your local files.
       """
       # Start typing here...
   ```

4. **Test Copilot suggestions:**
   - Start typing in the function
   - Copilot should suggest completions based on your other project files
   - Look for suggestions that reference your existing functions, classes, or variables

## ✅ Verification Steps

### **Verify MCP Server is Working**

1. **Check server logs:**
   ```bash
   # The server creates a log file in your project directory
   tail -f mcp_server.log
   ```

   **Look for these messages:**
   ```
   INFO - Starting MCP server for directory: /your/project/path
   INFO - Scanned X files successfully
   ```

2. **Test server manually:**
   ```bash
   # In a new terminal, test the server response
   echo '{"method": "resources/list", "id": 1, "params": {}}' | python ~/mcp-local-files/mcp_server.py --root .
   ```

   **Expected output:** JSON response with your project files listed

### **Verify VSCode Integration**

1. **Check VSCode settings:**
   - Press `Ctrl+Shift+P` / `Cmd+Shift+P`
   - Type "Preferences: Open Settings (JSON)"
   - Verify your MCP configuration is there

2. **Check Developer Console:**
   - Press `Ctrl+Shift+P` / `Cmd+Shift+P`
   - Type "Developer: Toggle Developer Tools"
   - Check Console tab for MCP-related messages

3. **Test Copilot:**
   - Open an existing file in your project
   - Start typing a function that should reference other files
   - Copilot suggestions should include context from your local files

## 🔧 Common Issues & Solutions

### **Issue 1: "python command not found"**

**Solution:**
```bash
# Try python3 instead
python3 ~/mcp-local-files/mcp_server.py --root .

# Or find your Python path
which python
which python3

# Use the full path in VSCode settings
```

### **Issue 2: "Permission denied" error**

**Solution:**
```bash
# Make sure files are executable
chmod +x ~/mcp-local-files/mcp_server.py
chmod +x ~/mcp-local-files/launcher.py

# Check file ownership
ls -la ~/mcp-local-files/
```

### **Issue 3: VSCode can't find MCP server**

**Solution:**
1. **Verify absolute paths in settings.json**
2. **Check the path exists:**
   ```bash
   ls -la /your/absolute/path/to/mcp_server.py
   ```
3. **Test the command manually:**
   ```bash
   # Copy the exact command from your VSCode settings and test it
   python /your/absolute/path/to/mcp_server.py --root . --max-file-size 1048576
   ```

### **Issue 4: No context in Copilot suggestions**

**Solutions:**
1. **Verify the server is reading files:**
   ```bash
   # Check the logs for file scanning messages
   grep "Scanned" mcp_server.log
   ```

2. **Check file types are supported:**
   - The server only reads text files (.py, .js, .ts, .md, etc.)
   - Binary files and large files are ignored

3. **Restart VSCode:**
   - Close VSCode completely
   - Restart the MCP server
   - Reopen VSCode

### **Issue 5: Server crashes or stops**

**Solution:**
```bash
# Check the detailed error logs
cat mcp_server.log

# Common fixes:
# 1. Reduce max file size
python ~/mcp-local-files/mcp_server.py --root . --max-file-size 524288

# 2. Exclude problematic directories
# Edit mcp_server.py and add to ignored_patterns:
# 'large_folder/*', 'problematic_dir'
```

## 📂 File Locations Reference

### **MCP Server Files**
```
~/mcp-local-files/
├── mcp_server.py     # The main server
├── launcher.py       # Setup and start script
└── README.md         # This guide
```

### **VSCode Configuration Files**
```
# Global VSCode settings
~/.config/Code/User/settings.json          # Linux
~/Library/Application Support/Code/User/settings.json  # macOS
%APPDATA%\Code\User\settings.json          # Windows

# Project-specific settings
your-project/.vscode/settings.json         # Project settings (recommended)
```

### **MCP Configuration Files**
```
# Global MCP settings (created by launcher.py)
~/.config/mcp/settings.json                # Linux/macOS
%APPDATA%\mcp\settings.json               # Windows
```

### **Log Files**
```
your-project/mcp_server.log                # Server logs (created automatically)
```

## 🎯 Quick Commands Reference

### **Setup Commands**
```bash
# Initial setup
python ~/mcp-local-files/launcher.py setup --project .

# Start server
python ~/mcp-local-files/launcher.py start --project .

# Update configuration only
python ~/mcp-local-files/launcher.py config --project .
```

### **Manual Server Commands**
```bash
# Basic start
python ~/mcp-local-files/mcp_server.py --root .

# With custom file size limit (5MB)
python ~/mcp-local-files/mcp_server.py --root . --max-file-size 5242880

# Serve specific directory
python ~/mcp-local-files/mcp_server.py --root ./src
```

### **Debug Commands**
```bash
# View live logs
tail -f mcp_server.log

# Test server response
echo '{"method": "resources/list", "id": 1}' | python ~/mcp-local-files/mcp_server.py --root .

# Check Python version
python --version

# Find Python location
which python
```

## 🔒 Security & Performance Notes

### **Security**
- Server only reads files (never writes)
- Automatically ignores sensitive files (.env, .git, etc.)
- File size limits prevent reading huge files
- Only serves text-based source files

### **Performance**
- Default 1MB file size limit (configurable)
- Ignores binary files and common build artifacts
- Scans up to 1000 files by default
- Add custom ignore patterns for large datasets

### **Customization**
Edit `mcp_server.py` to customize:
```python
# Add custom ignored patterns
self.ignored_patterns = [
    '*.pyc', '__pycache__', '.git',
    'your_large_folder/*',  # Add custom patterns
    '*.backup'
]

# Add custom file extensions
self.allowed_extensions = {
    '.py', '.js', '.ts',
    '.custom',  # Add your custom extensions
    '.myformat'
}
```

---

## 📞 Getting Help

If you're still having issues:

1. **Check the logs first:** `tail -f mcp_server.log`
2. **Verify all paths are absolute and correct**
3. **Test the server manually before VSCode integration**
4. **Make sure GitHub Copilot extension is active**
5. **Try restarting VSCode and the MCP server**

The setup should take about 5-10 minutes once you have Python and VSCode installed. Most issues are related to incorrect file paths or permissions.
