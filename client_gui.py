"""
Real-time Collaborative Text Editor - GUI Client
===============================================

This GUI client connects to the collaborative text editor server
and provides a real-time editing interface using Tkinter.
Features:
- Real-time text editing with WebSocket connection
- Highlighting changes from other users
- Save functionality
- User identification
- Connection status display
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import asyncio
import json
import threading
import websockets
import requests
from datetime import datetime
import os
from typing import Optional

from dotenv import load_dotenv
import os
# Import configuration
load_dotenv(".env")
class Config:
    """Configuration class for the collaborative text editor"""
    # Client Configuration
    CLIENT_HOST: str = os.getenv("CLIENT_HOST")
    CLIENT_PORT: int = int(os.getenv("CLIENT_PORT", "1133"))
    
    # WebSocket Configuration
    WS_HOST: str = os.getenv("WS_HOST")
    WS_PORT: int = int(os.getenv("WS_PORT", "1133"))
    

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    @classmethod
    def get_server_url(cls) -> str:
        """Get the server URL for REST API calls"""
        return f"http://{cls.CLIENT_HOST}:{cls.CLIENT_PORT}"
    
    @classmethod
    def get_websocket_url(cls) -> str:
        """Get the WebSocket URL for real-time connections"""
        return f"ws://{cls.WS_HOST}:{cls.WS_PORT}/ws"
    
 
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("🔧 Current Configuration:")
        print(f"   WebSocket URL: {cls.get_websocket_url()}")
     

class CollaborativeTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Collaborative Text Editor")
        self.root.geometry("800x700")
        
        # Server configuration
        self.server_url = Config.get_websocket_url()
        self.api_url = Config.get_server_url()
        self.websocket = None
        self.connected = False
        self.user_id = "anonymous"
        
        # Text state
        self.current_text = ""
        self.last_sent_text = ""
        self.is_updating_from_server = False
        
        # Appearance settings
        self.bg_color = "white"
        self.text_color = "black"
        self.font_size = 12
        self.font_family = "Consolas"
        
        # Load saved preferences
        self.load_preferences()
        
        # GUI elements
        self.setup_gui()
        
        # Start connection
        self.connect_to_server()
        Config.print_config()
    def setup_gui(self):
        """Setup the GUI components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Changed from row 2 to row 3 to accommodate settings
        
        # Connection status
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.status_label.pack(side=tk.LEFT)
        
        self.user_count_label = ttk.Label(status_frame, text="Users: 0")
        self.user_count_label.pack(side=tk.RIGHT)
        
        # User ID frame
        user_frame = ttk.Frame(main_frame)
        user_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(user_frame, text="User ID:").pack(side=tk.LEFT)
        self.user_id_var = tk.StringVar(value=self.user_id)
        self.user_id_entry = ttk.Entry(user_frame, textvariable=self.user_id_var, width=20)
        self.user_id_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(user_frame, text="Set User ID", command=self.set_user_id).pack(side=tk.LEFT)
        
        # Appearance settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Appearance Settings", padding="5")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Color settings
        color_frame = ttk.Frame(settings_frame)
        color_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(color_frame, text="Background Color", command=self.choose_bg_color).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(color_frame, text="Text Color", command=self.choose_text_color).pack(side=tk.LEFT, padx=(0, 10))
        
        # Font size settings
        font_frame = ttk.Frame(settings_frame)
        font_frame.pack(fill=tk.X)
        
        ttk.Label(font_frame, text="Font Size:").pack(side=tk.LEFT)
        self.font_size_var = tk.IntVar(value=self.font_size)
        font_spinbox = ttk.Spinbox(
            font_frame, 
            from_=8, 
            to=32, 
            textvariable=self.font_size_var,
            width=5,
            command=self.update_font_size
        )
        font_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        # Font family dropdown
        ttk.Label(font_frame, text="Font:").pack(side=tk.LEFT)
        self.font_family_var = tk.StringVar(value=self.font_family)
        font_combo = ttk.Combobox(
            font_frame,
            textvariable=self.font_family_var,
            values=["Consolas", "Arial", "Times New Roman", "Courier New", "Verdana", "Georgia"],
            width=12,
            state="readonly"
        )
        font_combo.pack(side=tk.LEFT, padx=(5, 10))
        font_combo.bind('<<ComboboxSelected>>', self.update_font_family)
        
        ttk.Button(font_frame, text="Apply", command=self.apply_appearance_settings).pack(side=tk.RIGHT)
        
        # Text area
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Create text widget with scrollbar
        self.text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=(self.font_family, self.font_size),
            bg=self.bg_color,
            fg=self.text_color
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind text changes
        self.text_widget.bind('<KeyRelease>', self.on_text_change)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(button_frame, text="Save to File", command=self.save_to_file).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Load from File", command=self.load_from_file).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(button_frame, text="Reconnect", command=self.reconnect).pack(side=tk.RIGHT)
        
        # Configure text tags for highlighting
        self.text_widget.tag_configure("other_user", background="lightblue")
        self.text_widget.tag_configure("my_change", background="lightgreen")
    
    def set_user_id(self):
        """Set the user ID"""
        new_user_id = self.user_id_var.get().strip()
        if new_user_id:
            self.user_id = new_user_id
            messagebox.showinfo("User ID", f"User ID set to: {self.user_id}")
        else:
            messagebox.showerror("Error", "User ID cannot be empty")
    
    def choose_bg_color(self):
        """Choose background color"""
        color = colorchooser.askcolor(title="Choose Background Color", color=self.bg_color)
        if color[1]:  # color[1] contains the hex color string
            self.bg_color = color[1]
            self.apply_appearance_settings()
    
    def choose_text_color(self):
        """Choose text color"""
        color = colorchooser.askcolor(title="Choose Text Color", color=self.text_color)
        if color[1]:  # color[1] contains the hex color string
            self.text_color = color[1]
            self.apply_appearance_settings()
    
    def update_font_size(self):
        """Update font size from spinbox"""
        self.font_size = self.font_size_var.get()
        self.apply_appearance_settings()
    
    def update_font_family(self, event=None):
        """Update font family from combobox"""
        self.font_family = self.font_family_var.get()
        self.apply_appearance_settings()
    
    def apply_appearance_settings(self):
        """Apply current appearance settings to the text widget"""
        try:
            # Update text widget appearance
            self.text_widget.configure(
                font=(self.font_family, self.font_size),
                bg=self.bg_color,
                fg=self.text_color
            )
            
            # Update highlight tag colors to work with new background
            if self.bg_color == "#000000" or self.bg_color.lower() == "black":
                # Dark theme - use lighter highlight colors
                self.text_widget.tag_configure("other_user", background="#404040")
                self.text_widget.tag_configure("my_change", background="#006400")
            else:
                # Light theme - use standard highlight colors
                self.text_widget.tag_configure("other_user", background="lightblue")
                self.text_widget.tag_configure("my_change", background="lightgreen")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply appearance settings: {e}")
        
        # Save preferences after applying
        self.save_preferences()
    
    def save_preferences(self):
        """Save appearance preferences to a file"""
        try:
            preferences = {
                "bg_color": self.bg_color,
                "text_color": self.text_color,
                "font_size": self.font_size,
                "font_family": self.font_family
            }
            
            with open("editor_preferences.json", "w") as f:
                json.dump(preferences, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save preferences: {e}")
    
    def load_preferences(self):
        """Load appearance preferences from file"""
        try:
            if os.path.exists("editor_preferences.json"):
                with open("editor_preferences.json", "r") as f:
                    preferences = json.load(f)
                
                self.bg_color = preferences.get("bg_color", "white")
                self.text_color = preferences.get("text_color", "black")
                self.font_size = preferences.get("font_size", 12)
                self.font_family = preferences.get("font_family", "Consolas")
                
        except Exception as e:
            print(f"Failed to load preferences: {e}")
            # Use defaults if loading fails
    
    def connect_to_server(self):
        """Connect to the WebSocket server"""
        def connect():
            try:
                # First try to get current text via REST API
                response = requests.get(f"{self.api_url}/text", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    self.current_text = data["content"]
                    self.last_sent_text = self.current_text
                    
                    # Update GUI in main thread
                    self.root.after(0, self.update_text_display)
                
                # Connect to WebSocket
                asyncio.run(self.websocket_connection())
                
            except Exception as e:
                print(f"Connection error: {e}")
                self.root.after(0, lambda: self.status_label.config(text="Connection Failed", foreground="red"))
        
        # Run connection in separate thread
        threading.Thread(target=connect, daemon=True).start()
    
    async def websocket_connection(self):
        """Handle WebSocket connection and messages"""
        try:
            async with websockets.connect(self.server_url) as websocket:
                self.websocket = websocket
                self.connected = True
                self.root.after(0, lambda: self.status_label.config(text="Connected", foreground="green"))
                
                # Listen for messages
                async for message in websocket:
                    await self.handle_websocket_message(message)
                    
        except Exception as e:
            print(f"WebSocket error: {e}")
            self.connected = False
            self.root.after(0, lambda: self.status_label.config(text="Disconnected", foreground="red"))
    
    async def handle_websocket_message(self, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "initial_state":
                # Initial state from server
                self.current_text = data["content"]
                self.last_sent_text = self.current_text
                self.root.after(0, self.update_text_display)
                
            elif message_type == "text_update":
                # Text update from another user
                if data["user_id"] != self.user_id:
                    self.current_text = data["content"]
                    self.root.after(0, lambda: self.update_text_display(highlight_others=True))
                    
            elif message_type == "user_count_update":
                # User count update
                user_count = data["user_count"]
                self.root.after(0, lambda: self.user_count_label.config(text=f"Users: {user_count}"))
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
    
    def on_text_change(self, event=None):
        """Handle text changes in the GUI"""
        if self.is_updating_from_server:
            return
        
        current_text = self.text_widget.get("1.0", tk.END).rstrip('\n')
        
        # Only send if text actually changed
        if current_text != self.last_sent_text:
            self.last_sent_text = current_text
            self.send_text_update(current_text)
    
    def send_text_update(self, text):
        """Send text update to server via WebSocket"""
        if self.websocket and self.connected:
            message = {
                "type": "text_update",
                "content": text,
                "user_id": self.user_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send in separate thread
            threading.Thread(
                target=lambda: asyncio.run(self.websocket.send(json.dumps(message))),
                daemon=True
            ).start()
    
    def update_text_display(self, highlight_others=False):
        """Update the text display in the GUI"""
        self.is_updating_from_server = True
        
        # Clear current text
        self.text_widget.delete("1.0", tk.END)
        
        # Insert new text
        if self.current_text:
            self.text_widget.insert("1.0", self.current_text)
            
            # Highlight if it's from other users
            if highlight_others:
                self.text_widget.tag_add("other_user", "1.0", tk.END)
                # Remove highlight after 2 seconds
                self.root.after(2000, lambda: self.text_widget.tag_remove("other_user", "1.0", tk.END))
        
        self.is_updating_from_server = False
    
    def save_to_file(self):
        """Save current text to a local file"""
        try:
            filename = f"collaborative_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.text_widget.get("1.0", tk.END))
            messagebox.showinfo("Save", f"Text saved to {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file: {e}")
    
    def load_from_file(self):
        """Load text from a local file"""
        try:
            filename = simpledialog.askstring("Load File", "Enter filename to load:")
            if filename and os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update both local and server
                self.current_text = content
                self.last_sent_text = content
                self.update_text_display()
                self.send_text_update(content)
                
                messagebox.showinfo("Load", f"Text loaded from {filename}")
            elif filename:
                messagebox.showerror("Load Error", f"File {filename} not found")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load file: {e}")
    
    def reconnect(self):
        """Reconnect to the server"""
        self.connect_to_server()

def main():
    """Main function to start the GUI application"""
    root = tk.Tk()
    app = CollaborativeTextEditor(root)
    
    # Handle window close
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    print("Starting Collaborative Text Editor GUI Client...")
    print(f"Connecting to server at: {Config.get_server_url()}")
    print(f"WebSocket endpoint: {Config.get_websocket_url()}")
    main()
