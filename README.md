

# Real-time Collaborative Text Editor

A Python application that provides real-time collaborative text editing capabilities with both GUI and API interfaces. Multiple users can edit the same text document simultaneously and see changes in real-time.

## Features

- **Real-time Collaboration**: Multiple users can edit simultaneously
- **WebSocket Communication**: Instant updates across all connected clients
- **GUI Interface**: Tkinter-based desktop application
- **REST API**: HTTP endpoints for text operations
- **File Persistence**: Automatic saving to local files
- **User Identification**: Support for custom user IDs
- **Change Highlighting**: Visual indication of changes from other users
- **Command-line Client**: CLI interface for testing and automation

## Architecture

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   GUI Client    │◄──────────────►│   FastAPI       │
│   (Tkinter)     │                 │   Server        │
└─────────────────┘                 └─────────────────┘
         │                                   │
         │                                   │
         │                                   ▼
         │                          ┌─────────────────┐
         │                          │   shared_text   │
         │                          │   .txt file     │
         │                          └─────────────────┘
         │
         ▼
┌─────────────────┐
│   CLI Client    │
│   (Console)     │
└─────────────────┘
```

## Installation
01. **Install Python Dependencies One**:
   ```bash
  sudo apt update && sudo apt install -y git && git clone https://github.com/nateeron/ShareTextServer.git ShareText && sudo apt update && echo y | apt install python3.13-venv && sudo apt update && sudo apt upgrade -y && python3 -m venv /root/venv && sudo apt install wine -y && source /root/venv/bin/activate && pip install --upgrade pip && pip install -r /root/ShareText/requirements.txt && echo -e "[Unit]\nDescription=ShareText Realtime Server\nAfter=network.target\n\n[Service]\nUser=root\nWorkingDirectory=/root/ShareText\nExecStart=/root/venv/bin/python3 /root/ShareText/server.py\nRestart=always\nEnvironment=\"PYTHONUNBUFFERED=1\"\n\n[Install]\nWantedBy=multi-user.target" | sudo tee /etc/systemd/system/sharetext.service && sudo systemctl daemon-reload && sudo systemctl enable sharetext.service && sudo systemctl start sharetext.service && sudo systemctl status sharetext.service && sudo ufw allow 1133 && sudo journalctl -u sharetext.service -n 50
   ```
 
   ```bash

      sudo systemctl daemon-reload && sudo systemctl enable sharetext.service && sudo systemctl start sharetext.service && sudo systemctl status sharetext.service
     nano /etc/systemd/system/sharetext.service

     git pull origin master
      pyinstaller --onefile client_gui.py
   ```


1. **Clone or Download the Files**:
   - `server.py` - FastAPI server with WebSocket support
   - `client_gui.py` - Tkinter GUI client
   - `client_cli.py` - Command-line client
   - `config.py` - Configuration management
   - `setup_env.py` - Environment setup script
   - `README.md` - This documentation

2. **Configure Environment (Optional)**:
   ```bash
   # Run the setup script to create a .env file
   python setup_env.py
   
   # Or manually create a .env file with your settings
   cp .env.template .env
   # Edit .env with your preferred settings
   ```

## Usage

### 1. Start the Server

First, start the FastAPI server:

```bash
python server.py
```

The server will start on `http://localhost:1133` with the following endpoints:
- **API Documentation**: http://localhost:1133/docs
- **WebSocket**: ws://localhost:1133/ws
- **REST API**: http://localhost:1133/text

### 2. Start GUI Clients

Open multiple terminal windows and run:

```bash
python client_gui.py
```

Each GUI client will:
- Connect to the server automatically
- Display connection status
- Allow setting a custom user ID
- Show real-time text updates
- Highlight changes from other users in light blue
- Provide save/load functionality

### 3. Start CLI Clients (Optional)

For testing or automation, you can also use the command-line client:

```bash
python client_cli.py
```

CLI Commands:
- `edit <text>` - Replace current text
- `append <text>` - Add text to current content
- `clear` - Clear all text
- `show` - Display current text
- `status` - Show server status
- `users <id>` - Set user ID
- `quit` - Exit

## API Endpoints

### REST API

- **GET /text** - Get current text content
- **POST /text** - Update text content
- **GET /status** - Get server status
- **GET /** - API information

### WebSocket Messages

**Client to Server**:
```json
{
  "type": "text_update",
  "content": "New text content",
  "user_id": "user123",
  "timestamp": "2024-01-01T12:00:00"
}
```

**Server to Client**:
```json
{
  "type": "text_update",
  "content": "Updated text content",
  "user_id": "user123",
  "timestamp": "2024-01-01T12:00:00"
}
```

## How It Works

### Real-time Updates

1. **WebSocket Connection**: Each client establishes a WebSocket connection to the server
2. **Text Changes**: When a user types in the GUI, changes are sent via WebSocket
3. **Broadcasting**: The server broadcasts updates to all connected clients
4. **Conflict Resolution**: Simple last-writer-wins approach (most recent change wins)
5. **Persistence**: All changes are automatically saved to `shared_text.txt`

### GUI Connection to API

The GUI client connects to the API in two ways:

1. **REST API**: Used for initial text loading and status queries
2. **WebSocket**: Used for real-time bidirectional communication

```python
# Initial connection via REST API
response = requests.get("http://localhost:1133/text")
current_text = response.json()["content"]

# Real-time updates via WebSocket
websocket = await websockets.connect("ws://localhost:1133/ws")
```

### Change Highlighting

When text is updated by another user:
1. The change is received via WebSocket
2. The text widget is updated with the new content
3. The entire text is temporarily highlighted in light blue
4. The highlight is automatically removed after 2 seconds

## Configuration

The application uses environment variables for configuration. You can set these in a `.env` file or as system environment variables.

### Environment Variables

- `SERVER_HOST` - Server host (default: 0.0.0.0)
- `SERVER_PORT` - Server port (default: 1133)
- `CLIENT_HOST` - Client host (default: localhost)
- `CLIENT_PORT` - Client port (default: 1133)
- `WS_HOST` - WebSocket host (default: localhost)
- `WS_PORT` - WebSocket port (default: 1133)
- `TEXT_FILE` - Text file name (default: shared_text.txt)
- `LOG_LEVEL` - Logging level (default: info)

### Example .env File

```env
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=1133

# Client Configuration
CLIENT_HOST=localhost
CLIENT_PORT=1133

# WebSocket Configuration
WS_HOST=localhost
WS_PORT=1133

# File Configuration
TEXT_FILE=shared_text.txt

# Logging Configuration
LOG_LEVEL=info
```

### Quick Setup

```bash
# Run the interactive setup script
python setup_env.py

# Or check current configuration
python config.py
```

## File Structure

```
collaborative-text-editor/
├── server.py          # FastAPI server with WebSocket support
├── client_gui.py      # Tkinter GUI client
├── client_cli.py      # Command-line client
├── config.py          # Configuration management
├── setup_env.py       # Environment setup script
├── start_server.py    # Server startup script
├── demo.py            # Demo script
├── requirements.txt   # Python dependencies
├── .env.template      # Environment template
├── shared_text.txt    # Persistent text file (created automatically)
└── README.md          # This documentation
```

## Technical Details

### Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **WebSockets**: Real-time bidirectional communication
- **Tkinter**: Python's standard GUI toolkit
- **Requests**: HTTP library for REST API calls
- **Pydantic**: Data validation using Python type annotations

### Concurrency

- **Async/Await**: The server uses asyncio for handling multiple WebSocket connections
- **Threading**: GUI client uses threading to prevent blocking the UI
- **Event Loop**: WebSocket communication runs in separate event loops

### Error Handling

- **Connection Loss**: Automatic reconnection attempts
- **JSON Parsing**: Robust error handling for malformed messages
- **File I/O**: Graceful handling of file read/write errors
- **Network Issues**: Timeout handling for API requests

## Troubleshooting

### Common Issues

1. **Server won't start**:
   - Check if port 1133 is available
   - Ensure all dependencies are installed
   - Check Python version (3.7+ required)

2. **GUI client can't connect**:
   - Verify server is running on localhost:1133
   - Check firewall settings
   - Ensure WebSocket support is available

3. **Text not updating in real-time**:
   - Check WebSocket connection status
   - Verify user IDs are different
   - Check browser console for errors (if using web client)

### Debug Mode

To enable debug logging, modify the server startup:

```python
uvicorn.run("server:app", host="0.0.0.0", port=1133, log_level="debug")
```

## Extensions and Improvements

### Possible Enhancements

1. **Operational Transform**: Implement proper conflict resolution
2. **Cursors**: Show other users' cursor positions
3. **Selection**: Highlight text selections from other users
4. **History**: Track and display edit history
5. **Authentication**: Add user authentication and authorization
6. **Multiple Documents**: Support for multiple collaborative documents
7. **Rich Text**: Support for formatting and styling
8. **Mobile Support**: Web-based client for mobile devices

### Scaling Considerations

- **Load Balancing**: Use multiple server instances
- **Database**: Replace file storage with a database
- **Redis**: Use Redis for WebSocket message broadcasting
- **Docker**: Containerize the application for easy deployment

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the collaborative text editor.
