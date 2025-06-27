# MCP Local Files Server Setup Guide

This guide will help you set up a Python MCP (Model Context Protocol) server that provides GitHub Copilot with context from your local files through VSCode.

## Files Structure

```
mcp-local-files/
├── mcp_server.py          # Main server implementation
├── requirements.txt       # Python dependencies
├── config/
│   ├── mcp_settings.json  # MCP configuration
│   └── vscode_settings.json # VSCode settings
└── README.md             # This file
```

## Requirements File (requirements.txt)

```txt
# Core dependencies for MCP server
asyncio-stdlib
pathlib2>=2.3.0

# Optional: For enhanced file type detection
python-magic>=0.4.24
```

## Installation Steps

### 1. Python Environment Setup

```bash
# Create a virtual environment
python -m venv mcp-env

# Activate the virtual environment
# On Windows:
mcp-env\Scripts\activate
# On macOS/Linux:
source mcp-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. MCP Configuration

Create `~/.config/mcp/settings.json` (or `%APPDATA%\mcp\settings.json` on Windows):

```json
{
  "mcpServers": {
    "local-files": {
      "command": "python",
      "args": [
        "/path/to/your/mcp_server.py",
        "--root",
        "/path/to/your/project/directory"
      ],
      "env": {
        "PYTHONPATH": "/path/to/your/mcp-env/lib/python3.x/site-packages"
      }
    }
  }
}
```

### 3. VSCode Configuration

Add to your VSCode `settings.json`:

```json
{
  "github.copilot.enable": {
    "*": true,
    "yaml": true,
    "plaintext": true,
    "markdown": true
  },
  "github.copilot.advanced": {
    "length": 500,
    "temperature": 0.1
  },
  "mcp.servers": {
    "local-files": {
      "command": "python",
      "args": [
        "/absolute/path/to/mcp_server.py",
        "--root",
        "${workspaceFolder}"
      ],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### 4. GitHub Copilot Configuration

Create `.vscode/settings.json` in your project root:

```json
{
  "github.copilot.advanced": {
    "debug.overrideEngine": "codex",
    "debug.testOverrideProxyUrl": "http://localhost:8080",
    "debug.overrideProxyUrl": "http://localhost:8080"
  },
  "github.copilot.enable": {
    "*": true
  }
}
```

## Usage Instructions

### 1. Start the MCP Server

```bash
# Navigate to your project directory
cd /path/to/your/project

# Activate virtual environment
source mcp-env/bin/activate  # or mcp-env\Scripts\activate on Windows

# Start the server
python mcp_server.py --root . --max-file-size 2097152
```

### 2. VSCode Integration

1. Install the GitHub Copilot extension in VSCode
2. Install any MCP extension for VSCode (if available) or configure manually
3. Open your project in VSCode
4. The MCP server should automatically connect and provide file context

### 3. Testing the Setup

Create a test file to verify the setup works:

```python
# test_context.py
def example_function():
    """
    This function demonstrates that Copilot can see
    context from other files in the project
    """
    # Start typing here and Copilot should suggest
    # completions based on other files in your project
    pass
```

## Configuration Options

### Server Arguments

- `--root`: Root directory to serve files from (default: current directory)
- `--max-file-size`: Maximum file size to read in bytes (default: 1MB)

### Ignored Files/Patterns

The server automatically ignores:
- Binary files (images, executables, archives)
- Large files (configurable)
- Common non-source directories (node_modules, .git, __pycache__)
- Log files and temporary files

### Supported File Types

The server serves context from:
- Source code files (.py, .js, .ts, .jsx, .tsx, .java, .cpp, etc.)
- Configuration files (.json, .yaml, .toml, .ini)
- Documentation (.md, .txt, .rst)
- Web files (.html, .css, .scss)
- Scripts (.sh, .bat, .ps1)

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check Python path and virtual environment
   - Verify all dependencies are installed
   - Check file permissions

2. **VSCode can't connect to MCP server**
   - Verify the paths in settings.json are absolute
   - Check that the server is running
   - Look at VSCode Developer Console for errors

3. **No context in Copilot suggestions**
   - Ensure the MCP server is providing resources
   - Check the server logs in `mcp_server.log`
   - Verify file types are supported

### Debugging

1. **Check server logs**
   ```bash
   tail -f mcp_server.log
   ```

2. **Test server manually**
   ```bash
   echo '{"method": "resources/list", "id": 1}' | python mcp_server.py
   ```

3. **VSCode Developer Console**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Developer: Toggle Developer Tools"
   - Check Console and Network tabs for errors

## Security Considerations

- The server only reads files, never writes
- Files are filtered by type and size
- Sensitive patterns are automatically ignored
- Consider running in a restricted directory
- Be cautious with private repositories

## Performance Tips

1. **Optimize file scanning**
   - Use specific root directories rather than entire filesystem
   - Adjust max-file-size based on your needs
   - Add custom ignore patterns for large file types

2. **VSCode Performance**
   - Limit the workspace to relevant directories
   - Close unused files and directories
   - Consider excluding large folders in VSCode settings

## Advanced Configuration

### Custom File Filters

Edit the `ignored_patterns` and `allowed_extensions` in `mcp_server.py`:

```python
self.ignored_patterns = [
    '*.pyc', '__pycache__', '.git',
    # Add your custom patterns here
    'large_data/*', '*.generated.*'
]

self.allowed_extensions = {
    '.py', '.js', '.ts', '.jsx', '.tsx',
    # Add your custom extensions here
    '.custom', '.myext'
}
```

### Environment-Specific Settings

Create environment-specific configuration files:

```bash
# Development
python mcp_server.py --root ./src --max-file-size 5242880

# Production (smaller context)
python mcp_server.py --root ./core --max-file-size 1048576
```

## Integration with CI/CD

For automated environments, you can run the MCP server as a background service:

```bash
# Run as background service
nohup python mcp_server.py --root . > mcp_server.log 2>&1 &

# Or use systemd on Linux
sudo systemctl start mcp-local-files
```

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the server logs
3. Verify your configuration files
4. Test with a minimal setup first

The MCP server provides detailed logging to help diagnose issues. Always check `mcp_server.log` for error messages and debugging information.
