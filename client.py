"""
Chat Client - Premium Elegant GUI using Tkinter
"""
from tkinter import Tk, Frame, Label, Button, Entry, Canvas, Scrollbar, simpledialog, Toplevel, StringVar, IntVar, Checkbutton, OptionMenu
from tkinter import LEFT, RIGHT, Y, X, BOTH, END, DISABLED, NORMAL, W, E, NW, NE, SE, SW
import socket
import threading
import time
import random

# Server configuration
HOST = '127.0.0.1'
PORT = 55555

# Font constants
FONT_PRIMARY = "Segoe UI"
MSG_PLACEHOLDER = "Type a message..."

# Premium color palette
COLORS = {
    "bg_primary": "#0f0f13",        # Deep black
    "bg_secondary": "#1a1a23",      # Dark charcoal
    "bg_tertiary": "#252532",       # Lighter charcoal
    "accent": "#6366f1",            # Indigo accent
    "accent_hover": "#818cf8",     # Light indigo
    "text_primary": "#f8fafc",      # White text
    "text_secondary": "#94a3b8",    # Gray text
    "text_muted": "#64748b",        # Muted text
    "success": "#10b981",          # Green
    "error": "#ef4444",             # Red
    "border": "#2d2d3a",           # Subtle border
    "message_sent": "#312e81",     # Indigo message bg
    "message_received": "#1e1b4b", # Dark indigo bg
}

class ChatClient:
    def __init__(self):
        self.root = Tk()
        self.root.title("Chat Application")
        self.root.geometry("800x600")
        self.root.configure(bg=COLORS["bg_primary"])
        self.root.minsize(600, 400)
        
        # Center window on screen
        self.center_window()
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = None
        self.running = True
        self.connected_users = []
        
        # Custom fonts
        self.setup_fonts()
        self.setup_gui()
        self.setup_animations()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = 800
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_fonts(self):
        """Setup custom fonts"""
        self.font_title = (FONT_PRIMARY, 18, "bold")
        self.font_heading = (FONT_PRIMARY, 14, "bold")
        self.font_body = (FONT_PRIMARY, 10)
        self.font_message = (FONT_PRIMARY, 10)
        self.font_input = (FONT_PRIMARY, 11)
        self.font_small = (FONT_PRIMARY, 8)
        self.font_username = (FONT_PRIMARY, 9, "bold")
        
    def setup_animations(self):
        """Setup animation states"""
        self.hover_states = {}
        self.animation_speed = 200
        
    def setup_gui(self):
        """Set up the premium GUI components"""
        # Main container with sidebar layout
        self.main_container = Frame(self.root, bg=COLORS["bg_primary"])
        self.main_container.pack(fill=BOTH, expand=True)
        
        # Sidebar for users
        self.create_sidebar(self.main_container)
        
        # Chat area (right side)
        chat_area = Frame(self.main_container, bg=COLORS["bg_primary"])
        chat_area.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Header
        self.create_header(chat_area)
        
        # Messages area
        self.create_messages_area(chat_area)
        
        # Input area
        self.create_input_area(chat_area)
        
        # Status bar
        self.create_status_bar(chat_area)
        
    def create_header(self, parent):
        """Create premium header"""
        header = Frame(parent, bg=COLORS["bg_secondary"], height=70)
        header.pack(fill=X, pady=0)
        header.pack_propagate(False)
        
        # Logo/Icon with glow effect
        icon_label = Label(
            header,
            text="💬",
            font=(FONT_PRIMARY, 28),
            bg=COLORS["bg_secondary"]
        )
        icon_label.pack(side=LEFT, padx=(20, 10))
        
        # Title and subtitle
        title_frame = Frame(header, bg=COLORS["bg_secondary"])
        title_frame.pack(side=LEFT, fill=Y, pady=15)
        
        title_label = Label(
            title_frame,
            text="Helloy",
            font=self.font_title,
            fg=COLORS["text_primary"],
            bg=COLORS["bg_secondary"]
        )
        title_label.pack(anchor=W)
        
        subtitle_label = Label(
            title_frame,
            text="Connected",
            font=self.font_small,
            fg=COLORS["success"],
            bg=COLORS["bg_secondary"]
        )
        subtitle_label.pack(anchor=W)
        
        # Header actions frame
        actions_frame = Frame(header, bg=COLORS["bg_secondary"])
        actions_frame.pack(side=RIGHT, padx=(0, 15), fill=Y)
        
        # Search button
        search_btn = Button(
            actions_frame,
            text="🔍",
            font=(FONT_PRIMARY, 14),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_secondary"],
            activebackground=COLORS["bg_tertiary"],
            bd=0,
            padx=12,
            cursor="hand2",
            command=self.show_search
        )
        search_btn.pack(side=LEFT, pady=20)
        
        # Settings button
        settings_btn = Button(
            actions_frame,
            text="⚙",
            font=(FONT_PRIMARY, 16),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_secondary"],
            activebackground=COLORS["bg_tertiary"],
            bd=0,
            padx=12,
            cursor="hand2",
            command=self.show_settings
        )
        settings_btn.pack(side=LEFT, pady=20)
        
        # Separator
        sep = Frame(parent, bg=COLORS["border"], height=1)
        sep.pack(fill=X)
        
    def create_sidebar(self, parent):
        """Create sidebar with connected users"""
        sidebar = Frame(parent, bg=COLORS["bg_secondary"], width=200)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)
        
        # Sidebar header
        sidebar_header = Frame(sidebar, bg=COLORS["bg_secondary"], height=60)
        sidebar_header.pack(fill=X, pady=(0, 10))
        sidebar_header.pack_propagate(False)
        
        users_label = Label(
            sidebar_header,
            text="Online Users",
            font=self.font_heading,
            fg=COLORS["text_primary"],
            bg=COLORS["bg_secondary"]
        )
        users_label.pack(anchor=W, padx=15, pady=(15, 0))
        
        # Users count
        self.users_count_label = Label(
            sidebar_header,
            text="0 online",
            font=self.font_small,
            fg=COLORS["text_muted"],
            bg=COLORS["bg_secondary"]
        )
        self.users_count_label.pack(anchor=W, padx=15)
        
        # Separator
        sep = Frame(sidebar, bg=COLORS["border"], height=1)
        sep.pack(fill=X, padx=10)
        
        # Users list container
        users_container = Frame(sidebar, bg=COLORS["bg_secondary"])
        users_container.pack(fill=BOTH, expand=True, padx=10)
        
        # Canvas for scrolling users
        self.users_canvas = Canvas(
            users_container,
            bg=COLORS["bg_secondary"],
            highlightthickness=0
        )
        self.users_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Users scrollbar
        users_scrollbar = Scrollbar(
            users_container,
            command=self.users_canvas.yview,
            bg=COLORS["bg_tertiary"],
            troughcolor=COLORS["bg_secondary"],
            activebackground=COLORS["accent"],
            bd=0,
            width=4
        )
        users_scrollbar.pack(side=RIGHT, fill=Y)
        self.users_canvas.configure(yscrollcommand=users_scrollbar.set)
        
        # Users frame
        self.users_frame = Frame(self.users_canvas, bg=COLORS["bg_secondary"])
        self.users_canvas.create_window((0, 0), window=self.users_frame, anchor=NW)
        self.users_frame.bind("<Configure>", lambda e: self.users_canvas.configure(scrollregion=self.users_canvas.bbox("all")))
        
        # Add self to users list
        self.update_users_list()
        
        # Vertical separator
        v_sep = Frame(parent, bg=COLORS["border"], width=1)
        v_sep.pack(side=LEFT, fill=Y)
        
    def update_users_list(self):
        """Update the users list in sidebar"""
        # Clear existing users
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        # Add self
        self.add_user_to_sidebar(self.nickname if self.nickname else "You", is_me=True)
        
        # Add other users
        for user in self.connected_users:
            self.add_user_to_sidebar(user, is_me=False)
        
        # Update count
        total = len(self.connected_users) + 1
        self.users_count_label.config(text=f"{total} online")
        
    def add_user_to_sidebar(self, username, is_me=False):
        """Add a user to the sidebar list"""
        user_frame = Frame(self.users_frame, bg=COLORS["bg_tertiary"], padx=10, pady=8)
        user_frame.pack(fill=X, pady=(0, 5))
        
        # Avatar circle
        avatar = Frame(user_frame, bg=COLORS["accent"], width=32, height=32)
        avatar.pack(side=LEFT)
        avatar.pack_propagate(False)
        
        # Avatar initial
        initial = username[0].upper() if username else "?"
        Label(
            avatar,
            text=initial,
            font=(FONT_PRIMARY, 12, "bold"),
            fg=COLORS["text_primary"],
            bg=COLORS["accent"]
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Username and status
        name_frame = Frame(user_frame, bg=COLORS["bg_tertiary"])
        name_frame.pack(side=LEFT, padx=(10, 0), fill=Y, expand=True)
        
        name_label = Label(
            name_frame,
            text=username + (" (You)" if is_me else ""),
            font=self.font_username,
            fg=COLORS["text_primary"],
            bg=COLORS["bg_tertiary"]
        )
        name_label.pack(anchor=W)
        
        # Online indicator
        status_label = Label(
            name_frame,
            text="● Online",
            font=self.font_small,
            fg=COLORS["success"],
            bg=COLORS["bg_tertiary"]
        )
        status_label.pack(anchor=W)
        
    def create_messages_area(self, parent):
        """Create messages display area"""
        # Messages container with rounded border
        msg_container = Frame(parent, bg=COLORS["bg_secondary"])
        msg_container.pack(fill=BOTH, expand=True, padx=15, pady=(15, 10))
        
        # Canvas for scrolling
        self.canvas = Canvas(
            msg_container,
            bg=COLORS["bg_secondary"],
            highlightthickness=0,
            highlightbackground=COLORS["bg_secondary"]
        )
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Scrollbar
        scrollbar = Scrollbar(
            msg_container,
            command=self.canvas.yview,
            bg=COLORS["bg_tertiary"],
            troughcolor=COLORS["bg_secondary"],
            activebackground=COLORS["accent"],
            bd=0,
            width=6
        )
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Messages frame
        self.messages_frame = Frame(self.canvas, bg=COLORS["bg_secondary"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.messages_frame, anchor=NW)
        
        self.messages_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Welcome message
        self.add_message("Welcome to Chat", "welcome", "System")
        
    def on_frame_configure(self, event=None):
        """Reset scroll region"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def on_canvas_configure(self, event):
        """Resize messages frame to fit canvas"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def create_input_area(self, parent):
        """Create premium input area"""
        input_container = Frame(parent, bg=COLORS["bg_primary"], height=80)
        input_container.pack(fill=X, pady=(0, 10))
        input_container.pack_propagate(False)
        
        # Input wrapper with border and rounded corners effect
        input_wrapper = Frame(input_container, bg=COLORS["bg_tertiary"], padx=5, pady=5)
        input_wrapper.pack(side=LEFT, fill=BOTH, expand=True, padx=(15, 10))
        
        # Inner input frame
        inner_input = Frame(input_wrapper, bg=COLORS["bg_tertiary"])
        inner_input.pack(fill=BOTH, expand=True)
        
        # Message entry
        self.msg_entry = Entry(
            inner_input,
            font=self.font_input,
            bg=COLORS["bg_tertiary"],
            fg=COLORS["text_muted"],
            insertbackground=COLORS["accent"],
            bd=0,
            highlightthickness=0
        )
        self.msg_entry.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 5), pady=10)
        self.msg_entry.insert(0, MSG_PLACEHOLDER)
        self.msg_entry.bind("<FocusIn>", lambda e: self.on_entry_focus(False))
        self.msg_entry.bind("<FocusOut>", lambda e: self.on_entry_focus(True))
        self.msg_entry.bind("<Return>", self.send_message)
        
        # Send button with hover effect
        self.send_btn = Button(
            inner_input,
            text="Send",
            font=(FONT_PRIMARY, 10, "bold"),
            fg=COLORS["text_primary"],
            bg=COLORS["accent"],
            activebackground=COLORS["accent_hover"],
            activeforeground=COLORS["text_primary"],
            bd=0,
            padx=25,
            pady=8,
            cursor="hand2",
            command=self.send_message
        )
        self.send_btn.pack(side=LEFT, padx=(5, 5))
        
        # Bind hover events
        self.send_btn.bind("<Enter>", lambda e: self.on_button_hover(True, self.send_btn))
        self.send_btn.bind("<Leave>", lambda e: self.on_button_hover(False, self.send_btn))
        
    def on_button_hover(self, is_hover, button):
        """Handle button hover effects"""
        if is_hover:
            button.config(bg=COLORS["accent_hover"])
        else:
            button.config(bg=COLORS["accent"])
        
    def create_status_bar(self, parent):
        """Create status bar"""
        status = Frame(parent, bg=COLORS["bg_secondary"], height=25)
        status.pack(fill=X)
        
        self.status_label = Label(
            status,
            text="Not connected",
            font=self.font_small,
            fg=COLORS["text_muted"],
            bg=COLORS["bg_secondary"]
        )
        self.status_label.pack(side=LEFT, padx=15)
        
        # Version info
        version_label = Label(
            status,
            text="v2.0",
            font=self.font_small,
            fg=COLORS["text_muted"],
            bg=COLORS["bg_secondary"]
        )
        version_label.pack(side=RIGHT, padx=15)
        
    def on_entry_focus(self, is_blur):
        """Handle entry focus events"""
        if is_blur and not self.msg_entry.get():
            self.msg_entry.insert(0, MSG_PLACEHOLDER)
            self.msg_entry.config(fg=COLORS["text_muted"])
        elif not is_blur:
            current = self.msg_entry.get()
            if current == MSG_PLACEHOLDER:
                self.msg_entry.delete(0, END)
            self.msg_entry.config(fg=COLORS["text_primary"])
            
    def connect_to_server(self):
        """Connect to the chat server"""
        try:
            self.client_socket.connect((HOST, PORT))
            self.client_socket.send(self.nickname.encode('utf-8'))
            self.status_label.config(text=f"Connected as {self.nickname}", fg=COLORS["success"])
            self.add_message("Connected to server", "success", "System")
            return True
        except Exception as e:
            self.add_message(f"Connection failed: {e}", "error", "System")
            return False
    
    def receive_messages(self):
        """Receive messages from server in a separate thread"""
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.root.after(0, lambda m=message: self.add_message(m, "received", ""))
            except Exception:
                break
    
    def send_message(self, event=None):
        """Send a message to the server"""
        message = self.msg_entry.get().strip()
        
        # Clear placeholder text
        if message == MSG_PLACEHOLDER:
            return
            
        if message:
            try:
                self.client_socket.send(message.encode('utf-8'))
                self.add_message(message, "sent", self.nickname)
                self.msg_entry.delete(0, END)
            except Exception:
                self.add_message("Failed to send message", "error", "System")
    
    def add_message(self, message, msg_type, sender):
        """Add a message to the messages display"""
        msg_frame = Frame(self.messages_frame, bg=COLORS["bg_secondary"])
        msg_frame.pack(fill=X, pady=(5, 0))
        
        # Determine colors based on message type
        if msg_type == "sent":
            bg_color = COLORS["message_sent"]
            prefix = "You"
            align = E
        elif msg_type == "received":
            bg_color = COLORS["message_received"]
            prefix = sender if sender else "Unknown"
            align = W
        elif msg_type == "welcome":
            bg_color = COLORS["bg_tertiary"]
            prefix = ""
            align = "center"
        elif msg_type == "success":
            bg_color = COLORS["bg_tertiary"]
            prefix = ""
            align = "center"
        elif msg_type == "error":
            bg_color = "#3f1a1a"
            prefix = ""
            align = "center"
        else:
            bg_color = COLORS["bg_tertiary"]
            prefix = ""
            align = "center"
        
        if msg_type in ["sent", "received"]:
            # Message bubble with side alignment
            bubble = Frame(msg_frame, bg=bg_color, padx=15, pady=10)
            bubble.pack(fill=X, padx=10)
            
            # Sender name with avatar
            sender_frame = Frame(bubble, bg=bg_color)
            sender_frame.pack(fill=X)
            
            # Avatar circle
            avatar = Frame(sender_frame, bg=COLORS["accent"], width=24, height=24)
            avatar.pack(side=LEFT)
            avatar.pack_propagate(False)
            
            # Avatar initial
            initial = (sender or "?")[0].upper()
            Label(
                avatar,
                text=initial,
                font=(FONT_PRIMARY, 9, "bold"),
                fg=COLORS["text_primary"],
                bg=COLORS["accent"]
            ).place(relx=0.5, rely=0.5, anchor="center")
            
            # Sender name
            sender_label = Label(
                sender_frame,
                text=prefix,
                font=(FONT_PRIMARY, 9, "bold"),
                fg=COLORS["accent"],
                bg=bg_color
            )
            sender_label.pack(side=LEFT, padx=(8, 0))
            
            # Timestamp
            timestamp = time.strftime("%H:%M")
            time_label = Label(
                sender_frame,
                text=timestamp,
                font=(FONT_PRIMARY, 7),
                fg=COLORS["text_muted"],
                bg=bg_color
            )
            time_label.pack(side=RIGHT)
            
            # Message text with word wrap
            msg_label = Label(
                bubble,
                text=message,
                font=self.font_message,
                fg=COLORS["text_primary"],
                bg=bg_color,
                wraplength=450,
                justify=LEFT
            )
            msg_label.pack(anchor=W, pady=(5, 0))
        else:
            # System message (centered)
            system_frame = Frame(msg_frame, bg=bg_color, padx=20, pady=10)
            system_frame.pack(fill=X, padx=50)
            
            # Icon based on message type
            icon = "ℹ" if msg_type == "welcome" else "✓" if msg_type == "success" else "✕" if msg_type == "error" else ""
            
            if icon:
                icon_label = Label(
                    system_frame,
                    text=icon,
                    font=(FONT_PRIMARY, 12),
                    fg=COLORS["success"] if msg_type == "success" else COLORS["error"] if msg_type == "error" else COLORS["text_muted"],
                    bg=bg_color
                )
                icon_label.pack(side=LEFT, padx=(0, 8))
            
            msg_label = Label(
                system_frame,
                text=message,
                font=(FONT_PRIMARY, 9),
                fg=COLORS["text_secondary"],
                bg=bg_color
            )
            msg_label.pack()
    
    def show_settings(self):
        """Show settings menu"""
        settings_win = Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("400x450")
        settings_win.configure(bg=COLORS["bg_primary"])
        settings_win.resizable(False, False)
        
        # Center settings window
        settings_win.transient(self.root)
        settings_win.grab_set()
        
        # Header
        header = Frame(settings_win, bg=COLORS["bg_secondary"], height=60)
        header.pack(fill=X)
        header.pack_propagate(False)
        
        Label(
            header,
            text="⚙ Settings",
            font=self.font_title,
            fg=COLORS["text_primary"],
            bg=COLORS["bg_secondary"]
        ).pack(pady=15)
        
        # Settings content
        content = Frame(settings_win, bg=COLORS["bg_primary"])
        content.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Server Settings
        Label(
            content,
            text="Server",
            font=self.font_heading,
            fg=COLORS["accent"],
            bg=COLORS["bg_primary"]
        ).pack(anchor=W, pady=(10, 10))
        
        # Host
        Frame(content, bg=COLORS["border"], height=1).pack(fill=X, pady=(0, 10))
        
        host_frame = Frame(content, bg=COLORS["bg_primary"])
        host_frame.pack(fill=X, pady=5)
        
        Label(
            host_frame,
            text="Host:",
            font=self.font_body,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_primary"],
            width=10,
            anchor=W
        ).pack(side=LEFT)
        
        host_entry = Entry(
            host_frame,
            font=self.font_body,
            bg=COLORS["bg_tertiary"],
            fg=COLORS["text_primary"],
            bd=0,
            highlightthickness=0
        )
        host_entry.insert(0, HOST)
        host_entry.pack(side=LEFT, fill=X, expand=True)
        
        # Port
        port_frame = Frame(content, bg=COLORS["bg_primary"])
        port_frame.pack(fill=X, pady=5)
        
        Label(
            port_frame,
            text="Port:",
            font=self.font_body,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_primary"],
            width=10,
            anchor=W
        ).pack(side=LEFT)
        
        port_entry = Entry(
            port_frame,
            font=self.font_body,
            bg=COLORS["bg_tertiary"],
            fg=COLORS["text_primary"],
            bd=0,
            highlightthickness=0
        )
        port_entry.insert(0, str(PORT))
        port_entry.pack(side=LEFT, fill=X, expand=True)
        
        # Appearance Settings
        Label(
            content,
            text="Appearance",
            font=self.font_heading,
            fg=COLORS["accent"],
            bg=COLORS["bg_primary"]
        ).pack(anchor=W, pady=(20, 10))
        
        Frame(content, bg=COLORS["border"], height=1).pack(fill=X, pady=(0, 10))
        
        # Theme
        theme_frame = Frame(content, bg=COLORS["bg_primary"])
        theme_frame.pack(fill=X, pady=5)
        
        Label(
            theme_frame,
            text="Theme:",
            font=self.font_body,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_primary"],
            width=10,
            anchor=W
        ).pack(side=LEFT)
        
        theme_var = StringVar(value="dark")
        theme_menu = OptionMenu(
            theme_frame,
            theme_var,
            "dark",
            "light"
        )
        theme_menu.config(
            font=self.font_body,
            bg=COLORS["bg_tertiary"],
            fg=COLORS["text_primary"],
            bd=0,
            highlightthickness=0
        )
        theme_menu["menu"].config(
            bg=COLORS["bg_tertiary"],
            fg=COLORS["text_primary"]
        )
        theme_menu.pack(side=LEFT, fill=X, expand=True)
        
        # Notifications
        notif_frame = Frame(content, bg=COLORS["bg_primary"])
        notif_frame.pack(fill=X, pady=5)
        
        Label(
            notif_frame,
            text="Notify:",
            font=self.font_body,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_primary"],
            width=10,
            anchor=W
        ).pack(side=LEFT)
        
        notif_var = IntVar(value=1)
        Checkbutton(
            notif_frame,
            text="Enable notifications",
            variable=notif_var,
            font=self.font_body,
            fg=COLORS["text_primary"],
            bg=COLORS["bg_primary"],
            activebackground=COLORS["bg_primary"],
            activeforeground=COLORS["text_primary"],
            selectcolor=COLORS["bg_primary"]
        ).pack(side=LEFT)
        
        # About Section
        Label(
            content,
            text="About",
            font=self.font_heading,
            fg=COLORS["accent"],
            bg=COLORS["bg_primary"]
        ).pack(anchor=W, pady=(20, 10))
        
        Frame(content, bg=COLORS["border"], height=1).pack(fill=X, pady=(0, 10))
        
        about_frame = Frame(content, bg=COLORS["bg_tertiary"], padx=15, pady=15)
        about_frame.pack(fill=X)
        
        Label(
            about_frame,
            text="Helloy Chat",
            font=(FONT_PRIMARY, 12, "bold"),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_tertiary"]
        ).pack()
        
        Label(
            about_frame,
            text="Version 2.0",
            font=self.font_small,
            fg=COLORS["text_muted"],
            bg=COLORS["bg_tertiary"]
        ).pack()
        
        Label(
            about_frame,
            text="Premium GUI Chat Application",
            font=self.font_small,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_tertiary"]
        ).pack(pady=(5, 0))
        
        # Buttons
        btn_frame = Frame(settings_win, bg=COLORS["bg_secondary"], height=50)
        btn_frame.pack(fill=X)
        btn_frame.pack_propagate(False)
        
        Button(
            btn_frame,
            text="Cancel",
            font=self.font_body,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_tertiary"],
            activebackground=COLORS["bg_tertiary"],
            bd=0,
            padx=20,
            cursor="hand2",
            command=settings_win.destroy
        ).pack(side=LEFT, padx=10, pady=10)
        
        Button(
            btn_frame,
            text="Save",
            font=self.font_body,
            fg=COLORS["text_primary"],
            bg=COLORS["accent"],
            activebackground=COLORS["accent_hover"],
            bd=0,
            padx=20,
            cursor="hand2",
            command=lambda: self.save_settings(
                host_entry.get(),
                port_entry.get(),
                theme_var.get(),
                notif_var.get(),
                settings_win
            )
        ).pack(side=RIGHT, padx=10, pady=10)
        
    def save_settings(self, host, port, theme, notifications, window):
        """Save settings and apply"""
        global HOST, PORT
        
        # Validate port
        try:
            PORT = int(port)
        except ValueError:
            self.add_message("Invalid port number", "error", "System")
            return
        
        HOST = host
        self.add_message(f"Settings saved - Host: {HOST}, Port: {PORT}", "success", "System")
        window.destroy()
    
    def show_search(self):
        """Show search functionality"""
        pass
    
    def run(self):
        """Run the chat client"""
        self.root.withdraw()
        
        # Ask for nickname
        self.nickname = simpledialog.askstring(
            "Welcome",
            "Enter your username:",
            parent=self.root
        )
        
        if not self.nickname:
            self.nickname = f"User{random.randint(1000, 9999)}"
        
        self.root.deiconify()
        self.root.title(f"Chat - {self.nickname}")
        
        # Connect to server
        if self.connect_to_server():
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        self.running = False
        try:
            self.client_socket.close()
        except Exception:
            pass
        self.root.destroy()

if __name__ == "__main__":
    client = ChatClient()
    client.run()