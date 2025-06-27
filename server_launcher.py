#!/usr/bin/env python3
"""
MCP Server Launcher
Easy launcher for the MCP Local Files Server
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path


def find_python_executable():
    """Find the best Python executable to use"""
    # Check for virtual environment
    if 'VIRTUAL_ENV' in os.environ:
        venv_python = Path(os.environ['VIRTUAL_ENV']) / 'bin' / 'python'
        if venv_python.exists():
            return str(venv_python)
    
    # Check for common Python executables
    for python_cmd in ['python3', 'python']:
        try:
            result = subprocess.run([python_cmd, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return python_cmd
        except FileNotFoundError:
            continue
    
    raise RuntimeError("No Python executable found")


def create_vscode_config(project_path, server_path):
    """Create or update VSCode configuration"""
    vscode_dir = project_path / '.vscode'
    vscode_dir.mkdir(exist_ok=True)
    
    settings_file = vscode_dir / 'settings.json'
    
    # Load existing settings or create new
    settings = {}
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        except json.JSONDecodeError:
            print("Warning: Existing settings.json is invalid, creating new one")
    
    # Add MCP server configuration
    python_exec = find_python_executable()
    
    mcp_config = {
        "mcp.servers": {
            "local-files": {
                "command": python_exec,
                "args": [
                    str(server_path),
                    "--root",
                    "${workspaceFolder}"
                ],
                "cwd": "${workspaceFolder}"
            }
        },
        "github.copilot.enable": {
            "*": True,
            "yaml": True,
            "plaintext": True,
            "markdown": True
        }
    }
    
    # Merge with existing settings
    settings.update(mcp_config)
    
    # Write back to file
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    
    print(f"✓ Created/updated VSCode configuration: {settings_file}")


def create_global_mcp_config(server_path, project_path):
    """Create global MCP configuration"""
    # Determine config directory based on OS
    if os.name == 'nt':  # Windows
        config_dir = Path(os.environ.get('APPDATA', '')) / 'mcp'
    else:  # macOS/Linux
        config_dir = Path.home() / '.config' / 'mcp'
    
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'settings.json'
    
    python_exec = find_python_executable()
    
    config = {
        "mcpServers": {
            "local-files": {
                "command": python_exec,
                "args": [
                    str(server_path),
                    "--root",
                    str(project_path)
                ]
            }
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Created global MCP configuration: {config_file}")


def install_dependencies():
    """Install required Python dependencies"""
    python_exec = find_python_executable()
    
    print("Installing Python dependencies...")
    try:
        subprocess.run([python_exec, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True)
        print("✓ pip updated successfully")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not update pip: {e}")
    
    print("✓ Dependencies installed (no external packages required)")


def main():
    parser = argparse.ArgumentParser(description='MCP Server Launcher and Setup')
    parser.add_argument('action', choices=['setup', 'start', 'config'], 
                       help='Action to perform')
    parser.add_argument('--project', type=str, default='.',
                       help='Project directory (default: current directory)')
    parser.add_argument('--server', type=str, 
                       help='Path to mcp_server.py (default: same directory as launcher)')
    parser.add_argument('--max-file-size', type=int, default=1024*1024,
                       help='Maximum file size in bytes (default: 1MB)')
    
    args = parser.parse_args()
    
    # Resolve paths
    project_path = Path(args.project).resolve()
    if args.server:
        server_path = Path(args.server).resolve()
    else:
        server_path = Path(__file__).parent / 'mcp_server.py'
    
    if not server_path.exists():
        print(f"Error: MCP server not found at {server_path}")
        print("Please ensure mcp_server.py is in the same directory or specify with --server")
        sys.exit(1)
    
    print(f"Project directory: {project_path}")
    print(f"MCP server: {server_path}")
    print()
    
    if args.action == 'setup':
        print("🚀 Setting up MCP Local Files Server...")
        
        # Install dependencies
        install_dependencies()
        
        # Create configurations
        create_vscode_config(project_path, server_path)
        create_global_mcp_config(server_path, project_path)
        
        print()
        print("✅ Setup complete!")
        print()
        print("Next steps:")
        print("1. Open your project in VSCode")
        print("2. Install GitHub Copilot extension if not already installed")
        print("3. Run: python launcher.py start")
        print("4. Start coding - Copilot should now have context from your local files!")
        
    elif args.action == 'config':
        print("⚙️  Updating configuration...")
        create_vscode_config(project_path, server_path)
        create_global_mcp_config(server_path, project_path)
        print("✅ Configuration updated!")
        
    elif args.action == 'start':
        print("🚀 Starting MCP Local Files Server...")
        print(f"Serving files from: {project_path}")
        print("Press Ctrl+C to stop the server")
        print()
        
        # Change to project directory
        os.chdir(project_path)
        
        # Start the server
        python_exec = find_python_executable()
        cmd = [
            python_exec, str(server_path),
            '--root', str(project_path),
            '--max-file-size', str(args.max_file_size)
        ]
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n✅ Server stopped")


if __name__ == '__main__':
    main()
