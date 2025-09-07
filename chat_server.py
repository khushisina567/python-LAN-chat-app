 
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

class ChatClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = None
        self.connected = False
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("LAN Chat App")
        self.root.geometry("600x500")
        self.root.configure(bg="#2C3E50")
        
        # Chat display area
        self.chat_area = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD, 
            width=60, 
            height=20,
            bg="#ECF0F1",
            fg="#2C3E50",
            font=("Arial", 10)
        )
        self.chat_area.pack(padx=10, pady=10)
        self.chat_area.config(state=tk.DISABLED)
        
        # Message input area
        input_frame = tk.Frame(self.root, bg="#2C3E50")
        input_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.msg_entry = tk.Entry(
            input_frame, 
            font=("Arial", 12),
            bg="#ECF0F1",
            fg="#2C3E50"
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind("<Return>", self.send_message_event)
        
        self.send_btn = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg="#3498DB",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Disconnected")
        status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#2C3E50",
            fg="#ECF0F1"
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Protocol for closing window
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def connect_to_server(self):
        """Connect to the chat server"""
        # Get server details
        host = simpledialog.askstring("Server", "Enter server IP:", parent=self.root)
        if not host:
            return
            
        port = 12345  # Default port
        
        # Get nickname
        self.nickname = simpledialog.askstring("Nickname", "Choose a nickname:", parent=self.root)
        if not self.nickname:
            return
            
        try:
            # Connect to server
            self.client_socket.connect((host, port))
            self.connected = True
            
            # Handle nickname validation
            response = self.client_socket.recv(1024).decode('utf-8')
            if response == "NICK":
                self.client_socket.send(self.nickname.encode('utf-8'))
                response = self.client_socket.recv(1024).decode('utf-8')
                
                if response == "ACCEPTED":
                    # Start thread to receive messages
                    receive_thread = threading.Thread(target=self.receive_messages)
                    receive_thread.daemon = True
                    receive_thread.start()
                    
                    self.status_var.set(f"Connected as {self.nickname}")
                    self.display_message("System", "Connected to server. Type /help for commands.")
                else:
                    messagebox.showerror("Error", "Nickname already in use")
                    self.client_socket.close()
                    self.connected = False
                    
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
            self.connected = False
            
    def receive_messages(self):
        """Receive messages from the server"""
        while self.connected:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message == "EXIT":
                    break
                    
                # Check if it's a command response
                if message.startswith("Muted") or message.startswith("Unmuted") or message.startswith("User") or message.startswith("Unknown"):
                    self.display_message("System", message)
                else:
                    # Display the message
                    self.display_message("", message)
                    
            except:
                self.display_message("System", "Disconnected from server")
                self.connected = False
                self.status_var.set("Disconnected")
                break
                
    def send_message(self):
        """Send a message to the server"""
        message = self.msg_entry.get()
        if message and self.connected:
            try:
                self.client_socket.send(message.encode('utf-8'))
                if message.startswith('/exit'):
                    self.connected = False
                    self.status_var.set("Disconnected")
                self.msg_entry.delete(0, tk.END)
            except:
                self.display_message("System", "Failed to send message")
                self.connected = False
                self.status_var.set("Disconnected")
                
    def send_message_event(self, event):
        """Event handler for sending messages"""
        self.send_message()
        
    def display_message(self, sender, message):
        """Display a message in the chat area"""
        self.chat_area.config(state=tk.NORMAL)
        if sender:
            self.chat_area.insert(tk.END, f"{sender}: {message}\n")
        else:
            self.chat_area.insert(tk.END, f"{message}\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
        
    def on_closing(self):
        """Handle application closing"""
        if self.connected:
            try:
                self.client_socket.send("/exit".encode('utf-8'))
            except:
                pass
        self.root.destroy()
        
    def run(self):
        """Run the client application"""
        # Connect to server after mainloop starts
        self.root.after(100, self.connect_to_server)
        self.root.mainloop()

if __name__ == "__main__":
    client = ChatClient()
    client.run()