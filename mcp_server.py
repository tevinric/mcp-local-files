
"""
MCP Server for Local File Context
Provides GitHub Copilot with context from local files through VSCode
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence
import argparse
import fnmatch
import mimetypes
from datetime import datetime

# MCP Protocol Implementation
class MCPServer:
    def __init__(self, root_path: str = None, max_file_size: int = 1024 * 1024):
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.max_file_size = max_file_size
        self.ignored_patterns = [
            '*.pyc', '__pycache__', '.git', '.gitignore', 'node_modules',
            '.vscode', '.idea', '*.log', '*.tmp', '.DS_Store', 'venv',
            '.env', '*.so', '*.dll', '*.exe', '*.bin', '*.zip', '*.tar.gz',
            '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.ico', '*.svg',
            '*.mp3', '*.mp4', '*.avi', '*.mov', '*.wav', '*.pdf'
        ]
        self.allowed_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss',
            '.json', '.xml', '.yaml', '.yml', '.md', '.txt', '.ini', '.cfg',
            '.conf', '.sh', '.bat', '.ps1', '.sql', '.r', '.cpp', '.c',
            '.h', '.hpp', '.java', '.go', '.rs', '.php', '.rb', '.swift',
            '.kt', '.scala', '.clj', '.hs', '.elm', '.dart', '.vue',
            '.svelte', '.astro', '.dockerfile', '.makefile', '.toml'
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mcp_server.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored based on patterns"""
        file_str = str(file_path)
        for pattern in self.ignored_patterns:
            if fnmatch.fnmatch(file_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True
        return False

    def is_text_file(self, file_path: Path) -> bool:
        """Check if file is a text file we can read"""
        if file_path.suffix.lower() in self.allowed_extensions:
            return True
        
        # Use mimetypes to check
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith('text/'):
            return True
            
        return False

    def read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content safely"""
        try:
            if file_path.stat().st_size > self.max_file_size:
                return f"[File too large: {file_path.stat().st_size} bytes]"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return f"[Error reading file: {e}]"

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file information"""
        try:
            stat = file_path.stat()
            return {
                'path': str(file_path.relative_to(self.root_path)),
                'absolute_path': str(file_path),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'extension': file_path.suffix,
                'is_text': self.is_text_file(file_path)
            }
        except Exception as e:
            self.logger.error(f"Error getting file info for {file_path}: {e}")
            return None

    def scan_directory(self, max_files: int = 1000) -> List[Dict[str, Any]]:
        """Scan directory for relevant files"""
        files = []
        try:
            for file_path in self.root_path.rglob('*'):
                if len(files) >= max_files:
                    break
                    
                if file_path.is_file() and not self.should_ignore_file(file_path):
                    if self.is_text_file(file_path):
                        file_info = self.get_file_info(file_path)
                        if file_info:
                            files.append(file_info)
        except Exception as e:
            self.logger.error(f"Error scanning directory: {e}")
        
        return files

    def get_file_content(self, relative_path: str) -> Optional[Dict[str, Any]]:
        """Get content of a specific file"""
        try:
            file_path = self.root_path / relative_path
            if not file_path.exists() or not file_path.is_file():
                return None
            
            if self.should_ignore_file(file_path) or not self.is_text_file(file_path):
                return None
            
            content = self.read_file_content(file_path)
            file_info = self.get_file_info(file_path)
            
            if file_info and content is not None:
                file_info['content'] = content
                return file_info
        except Exception as e:
            self.logger.error(f"Error getting file content for {relative_path}: {e}")
        
        return None

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        try:
            method = request.get('method')
            params = request.get('params', {})
            request_id = request.get('id')

            if method == 'initialize':
                return {
                    'id': request_id,
                    'result': {
                        'protocolVersion': '2024-11-05',
                        'capabilities': {
                            'resources': {
                                'subscribe': False,
                                'listChanged': False
                            },
                            'tools': {},
                            'prompts': {}
                        },
                        'serverInfo': {
                            'name': 'local-files-mcp-server',
                            'version': '1.0.0'
                        }
                    }
                }

            elif method == 'resources/list':
                files = self.scan_directory()
                resources = []
                
                for file_info in files:
                    resources.append({
                        'uri': f"file://{file_info['absolute_path']}",
                        'name': file_info['path'],
                        'description': f"Local file: {file_info['path']} ({file_info['size']} bytes)",
                        'mimeType': 'text/plain'
                    })
                
                return {
                    'id': request_id,
                    'result': {
                        'resources': resources
                    }
                }

            elif method == 'resources/read':
                uri = params.get('uri', '')
                if uri.startswith('file://'):
                    file_path = uri[7:]  # Remove 'file://' prefix
                    relative_path = Path(file_path).relative_to(self.root_path)
                    file_data = self.get_file_content(str(relative_path))
                    
                    if file_data:
                        return {
                            'id': request_id,
                            'result': {
                                'contents': [{
                                    'uri': uri,
                                    'mimeType': 'text/plain',
                                    'text': file_data['content']
                                }]
                            }
                        }
                
                return {
                    'id': request_id,
                    'error': {
                        'code': -32602,
                        'message': f"Resource not found: {uri}"
                    }
                }

            else:
                return {
                    'id': request_id,
                    'error': {
                        'code': -32601,
                        'message': f"Method not found: {method}"
                    }
                }

        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return {
                'id': request.get('id'),
                'error': {
                    'code': -32603,
                    'message': f"Internal error: {str(e)}"
                }
            }

    async def run_stdio(self):
        """Run MCP server using stdio transport"""
        self.logger.info(f"Starting MCP server for directory: {self.root_path}")
        
        try:
            while True:
                # Read JSON-RPC message from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    response = await self.handle_request(request)
                    
                    # Write response to stdout
                    print(json.dumps(response), flush=True)
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON received: {e}")
                    continue
                    
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")
        except Exception as e:
            self.logger.error(f"Server error: {e}")


def main():
    parser = argparse.ArgumentParser(description='MCP Server for Local Files')
    parser.add_argument('--root', type=str, default=None,
                        help='Root directory to serve files from (default: current directory)')
    parser.add_argument('--max-file-size', type=int, default=1024*1024,
                        help='Maximum file size to read in bytes (default: 1MB)')
    
    args = parser.parse_args()
    
    server = MCPServer(root_path=args.root, max_file_size=args.max_file_size)
    
    try:
        asyncio.run(server.run_stdio())
    except KeyboardInterrupt:
        print("Server stopped.")


if __name__ == '__main__':
    main()
