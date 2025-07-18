import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from database_manager import DatabaseManager
from run_face_recognition import FaceRecognitionSystem
from enhanced_encoder import EnhancedEncoder
import os
import cv2
import time
from PIL import Image, ImageTk
import numpy as np

class MainGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Face Recognition Access Control System")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        self.db_manager = DatabaseManager()
        self.face_system = FaceRecognitionSystem()
        self.encoder = EnhancedEncoder()
        self.captured_image = None  # Initialize captured_image
        
        self.create_main_interface()
    
    def create_main_interface(self):
        """Create the main interface with LOGIN and CHECK buttons"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main title
        title_label = tk.Label(self.root, text="Face Recognition Access Control", 
                              font=("Arial", 24, "bold"), fg='white', bg='#2c3e50')
        title_label.pack(pady=50)
        
        # Subtitle
        subtitle_label = tk.Label(self.root, text="Secure Access Management System", 
                                 font=("Arial", 14), fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(expand=True)
        
        # LOGIN button
        login_btn = tk.Button(button_frame, text="LOGIN", font=("Arial", 16, "bold"),
                             bg='#3498db', fg='white', width=15, height=2,
                             command=self.show_login_dialog)
        login_btn.pack(pady=20)
        
        # CHECK button
        check_btn = tk.Button(button_frame, text="CHECK", font=("Arial", 16, "bold"),
                             bg='#e74c3c', fg='white', width=15, height=2,
                             command=self.start_face_check)
        check_btn.pack(pady=20)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             font=("Arial", 10), fg='#bdc3c7', bg='#34495e')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def show_login_dialog(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Admin Login")
        login_window.geometry("400x300")
        login_window.configure(bg='#34495e')
        login_window.grab_set()  # Make it modal
        login_window.transient(self.root)  # Center the window
        
        # Title
        title_label = tk.Label(login_window, text="Administrator Login", 
                              font=("Arial", 18, "bold"), fg='white', bg='#34495e')
        title_label.pack(pady=30)
        
        # Username field
        tk.Label(login_window, text="Username:", font=("Arial", 12), 
                fg='white', bg='#34495e').pack(pady=5)
        username_entry = tk.Entry(login_window, font=("Arial", 12), width=25)
        username_entry.pack(pady=5)
        
        # Password field
        tk.Label(login_window, text="Password:", font=("Arial", 12), 
                fg='white', bg='#34495e').pack(pady=5)
        password_entry = tk.Entry(login_window, font=("Arial", 12), width=25, show="*")
        password_entry.pack(pady=5)
        
        # Login button
        def attempt_login():
            username = username_entry.get()
            password = password_entry.get()
            
            if self.db_manager.verify_admin(username, password):
                login_window.destroy()
                self.root.withdraw()  # Hide main window
                self.show_admin_panel()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password", parent=login_window)
        login_btn = tk.Button(login_window, text="Login", font=("Arial", 12, "bold"),
                             bg='#27ae60', fg='white', command=attempt_login)
        login_btn.pack(pady=20)
        
        # Cancel button
        cancel_btn = tk.Button(login_window, text="Cancel", font=("Arial", 12),
                              bg='#e74c3c', fg='white', 
                              command=login_window.destroy)
        cancel_btn.pack(pady=5)
        
        # Focus on username entry
        username_entry.focus()
        
        # Bind Enter key to login
        login_window.bind('<Return>', lambda event: attempt_login())
    
    def show_admin_panel(self):
        """Show the admin management panel"""
        self.admin_window = tk.Toplevel()
        self.admin_window.title("Admin Panel")
        self.admin_window.geometry("1000x700")
        self.admin_window.configure(bg='#2c3e50')

        # Add close handler to show main window again
        def on_admin_close():
            self.admin_window.destroy()
            self.root.deiconify()  # Show main window again

        self.admin_window.protocol("WM_DELETE_WINDOW", on_admin_close)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.admin_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Users Management Tab
        users_frame = ttk.Frame(notebook)
        notebook.add(users_frame, text="Users Management")
        self.create_users_tab(users_frame)
        
        # Access Logs Tab
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Access Logs")
        self.create_logs_tab(logs_frame)
        
        # Settings Tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        self.create_settings_tab(settings_frame)
    
    def create_users_tab(self, parent):
        """Create the users management tab"""
        # Top frame for buttons
        top_frame = tk.Frame(parent, bg='#ecf0f1')
        top_frame.pack(fill='x', padx=10, pady=5)
        
        # Add user button
        add_btn = tk.Button(top_frame, text="Add User", bg='#27ae60', fg='white',
                           command=self.show_add_user_dialog)
        add_btn.pack(side='left', padx=5)
        
        # Edit user button
        edit_btn = tk.Button(top_frame, text="Edit User", bg='#f39c12', fg='white',
                            command=self.show_edit_user_dialog)
        edit_btn.pack(side='left', padx=5)
        
        # Delete user button
        delete_btn = tk.Button(top_frame, text="Delete User", bg='#e74c3c', fg='white',
                              command=self.delete_user)
        delete_btn.pack(side='left', padx=5)
        
        # Refresh button
        refresh_btn = tk.Button(top_frame, text="Refresh", bg='#3498db', fg='white',
                               command=self.refresh_users_list)
        refresh_btn.pack(side='left', padx=5)
        
        # Users list
        columns = ('ID', 'User ID', 'Name', 'Phone', 'Status', 'Created')
        self.users_tree = ttk.Treeview(parent, columns=columns, show='headings')
        
        # Define column headings
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.users_tree.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        # Load users
        self.refresh_users_list()
    
    def create_logs_tab(self, parent):
        """Create the access logs tab"""
        # Top frame for controls
        top_frame = tk.Frame(parent, bg='#ecf0f1')
        top_frame.pack(fill='x', padx=10, pady=5)
        
        # Refresh logs button
        refresh_logs_btn = tk.Button(top_frame, text="Refresh Logs", bg='#3498db', fg='white',
                                    command=self.refresh_logs_list)
        refresh_logs_btn.pack(side='left', padx=5)
        
        # Clear logs button
        clear_logs_btn = tk.Button(top_frame, text="Clear Logs", bg='#e74c3c', fg='white',
                                  command=self.clear_logs)
        clear_logs_btn.pack(side='left', padx=5)
        
        # Logs list
        log_columns = ('ID', 'User ID', 'Name', 'Access Time', 'Status')
        self.logs_tree = ttk.Treeview(parent, columns=log_columns, show='headings')
        
        # Define column headings
        for col in log_columns:
            self.logs_tree.heading(col, text=col)
            self.logs_tree.column(col, width=120)
        
        # Scrollbar for logs
        logs_scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.logs_tree.yview)
        self.logs_tree.configure(yscrollcommand=logs_scrollbar.set)
        
        # Pack logs treeview and scrollbar
        self.logs_tree.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        logs_scrollbar.pack(side='right', fill='y')
        
        # Load logs
        self.refresh_logs_list()
    
    def create_settings_tab(self, parent):
        """Create the settings tab"""
        # Encodings management section
        encodings_frame = tk.LabelFrame(parent, text="Encodings Management", 
                                       font=("Arial", 12, "bold"), bg='#ecf0f1')
        encodings_frame.pack(fill='x', padx=10, pady=10)
        
        # Regenerate encodings button
        regen_btn = tk.Button(encodings_frame, text="Regenerate Encodings", 
                             bg='#f39c12', fg='white', font=("Arial", 12),
                             command=self.regenerate_encodings)
        regen_btn.pack(pady=10)
        
        # Admin management section
        admin_frame = tk.LabelFrame(parent, text="Admin Management", 
                                   font=("Arial", 12, "bold"), bg='#ecf0f1')
        admin_frame.pack(fill='x', padx=10, pady=10)
        
        # Create new admin button
        new_admin_btn = tk.Button(admin_frame, text="Create New Admin", 
                                 bg='#27ae60', fg='white', font=("Arial", 12),
                                 command=self.show_create_admin_dialog)
        new_admin_btn.pack(pady=10)
        
        # System info section
        info_frame = tk.LabelFrame(parent, text="System Information", 
                                  font=("Arial", 12, "bold"), bg='#ecf0f1')
        info_frame.pack(fill='x', padx=10, pady=10)
        
        # System info labels
        self.info_text = tk.Text(info_frame, height=10, width=80, state='disabled')
        self.info_text.pack(pady=10)
        
        # Update system info
        self.update_system_info()
    
    def start_face_check(self):
        """Start face recognition checking"""
        self.root.withdraw()  # Hide main window
        
        def camera_thread():
            try:
                self.face_system.start_camera_check()
                self.root.deiconify()  # Show main window when done
                self.status_var.set("Camera stopped")
            except Exception as e:
                messagebox.showerror("Camera Error", f"Failed to start camera: {str(e)}", parent=self.root)
                self.root.deiconify()  # Show main window on error
                self.status_var.set("Camera error")
        
        # Start camera in a separate thread
        thread = threading.Thread(target=camera_thread, daemon=True)
        thread.start()
    
    def show_add_user_dialog(self):
        """Show dialog to add new user with only Name, Phone, and Camera Capture"""
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add New User")
        self.add_window.geometry("500x500")
        self.add_window.configure(bg='#34495e')
        self.add_window.grab_set()
        self.captured_image = None  # Reset captured image

        # Title
        title_label = tk.Label(self.add_window, text="Add New User", 
                              font=("Arial", 18, "bold"), fg='white', bg='#34495e')
        title_label.pack(pady=20)

        # Form fields
        fields = [
            ("Name*:", "name"),
            ("Phone:", "phone")
        ]

        self.entries = {}
        for label_text, field_name in fields:
            tk.Label(self.add_window, text=label_text, font=("Arial", 12), 
                    fg='white', bg='#34495e').pack(pady=5)
            entry = tk.Entry(self.add_window, font=("Arial", 12), width=30)
            entry.pack(pady=5)
            self.entries[field_name] = entry

        # Camera capture section
        tk.Label(self.add_window, text="Photo*: Press 'C' to capture", 
                 font=("Arial", 12), fg='white', bg='#34495e').pack(pady=10)

        capture_btn = tk.Button(self.add_window, text="Open Camera", 
                               command=self.start_camera_capture,
                               bg='#3498db', fg='white', font=("Arial", 12))
        capture_btn.pack(pady=10)

        # Preview label
        self.image_preview = tk.Label(self.add_window, bg='#34495e')
        self.image_preview.pack(pady=10)

        # Buttons
        button_frame = tk.Frame(self.add_window, bg='#34495e')
        button_frame.pack(pady=20)
        
        save_btn = tk.Button(button_frame, text="Save", command=self.save_user,
                        bg='#27ae60', fg='white', font=("Arial", 12))
        save_btn.pack(side='left', padx=10)
    
        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.add_window.destroy,
                          bg='#e74c3c', fg='white', font=("Arial", 12))
        cancel_btn.pack(side='left', padx=10)
    
    def save_user(self):
        name = self.entries['name'].get().strip()
        phone = self.entries['phone'].get().strip()

        if not name:
            messagebox.showerror("Error", "Name is required!", parent=self.add_window)
            return

        # Check if an image has been captured (use explicit None check)
        if self.captured_image is None:
            messagebox.showerror("Error", "Please capture an image first!", parent=self.add_window)
            return

        # Generate user ID based on name and timestamp
        user_id = f"{name.lower().replace(' ', '_')}_{int(time.time())}"

        # Save captured image to temp file
        temp_image_path = f"temp_capture_{user_id}.jpg"
        cv2.imwrite(temp_image_path, self.captured_image)

        # Add to system
        success, message = self.encoder.add_new_person(
            temp_image_path, user_id, name, "", phone, ""
        )

        # Clean up temp file
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)

        if success:
            messagebox.showinfo("Success", message, parent=self.add_window)
            self.add_window.destroy()
            self.refresh_users_list()
            self.face_system.reload_encodings()
        else:
            messagebox.showerror("Error", message, parent=self.add_window)
    
    def show_edit_user_dialog(self):
        """Show dialog to edit selected user"""
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a user to edit", parent=self.admin_window)
            return
        
        user_data = self.users_tree.item(selected_item)['values']
        user_id = user_data[1]
        
        edit_window = tk.Toplevel(self.admin_window)
        edit_window.title("Edit User")
        edit_window.geometry("400x500")
        edit_window.configure(bg='#34495e')
        edit_window.grab_set()
        
        # Title
        title_label = tk.Label(edit_window, text=f"Edit User: {user_data[2]}", 
                              font=("Arial", 18, "bold"), fg='white', bg='#34495e')
        title_label.pack(pady=20)
        
        # Form fields
        fields = [
            ("Name:", "name", user_data[2]),
            ("Phone:", "phone", user_data[3]),  # Phone is at index 3
        ]
        
        entries = {}
        for label_text, field_name, current_value in fields:
            tk.Label(edit_window, text=label_text, font=("Arial", 12), 
                    fg='white', bg='#34495e').pack(pady=5)
            entry = tk.Entry(edit_window, font=("Arial", 12), width=30)
            entry.insert(0, current_value)
            entry.pack(pady=5)
            entries[field_name] = entry
        
        # Status dropdown
        tk.Label(edit_window, text="Status:", font=("Arial", 12), 
                fg='white', bg='#34495e').pack(pady=5)
        status_var = tk.StringVar(value=user_data[4])  # Status is at index 4
        status_combo = ttk.Combobox(edit_window, textvariable=status_var, 
                                   values=['active', 'inactive'], state='readonly')
        status_combo.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(edit_window, bg='#34495e')
        button_frame.pack(pady=20)
        
        def update_user():
            name = entries['name'].get().strip()
            phone = entries['phone'].get().strip()
            status = status_var.get()
            
            if not name:
                messagebox.showerror("Error", "Name is required!", parent=edit_window)
                return
            
            # Only update the fields we have in the UI
            self.db_manager.update_user(user_id, name=name, phone=phone, status=status)
            messagebox.showinfo("Success", "User updated successfully!", parent=edit_window)
            edit_window.destroy()
            self.refresh_users_list()
        
        update_btn = tk.Button(button_frame, text="Update", command=update_user,
                              bg='#27ae60', fg='white', font=("Arial", 12))
        update_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=edit_window.destroy,
                              bg='#e74c3c', fg='white', font=("Arial", 12))
        cancel_btn.pack(side='left', padx=10)
    
    def start_camera_capture(self):
        self.camera_window = tk.Toplevel(self.add_window)
        self.camera_window.title("Camera Capture - Press 'C' to Capture")
        self.camera_window.attributes('-topmost', True)  # Ensure it's on top

        # Create video capture
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open camera", parent=self.add_window)
            self.camera_window.destroy()
            return

        # Create label for video feed
        self.video_label = tk.Label(self.camera_window)
        self.video_label.pack()

        # Start video feed
        self.update_camera_feed()

        # Bind capture key
        self.camera_window.bind('c', self.capture_image)
        self.camera_window.bind('C', self.capture_image)

        # Handle window close
        self.camera_window.protocol("WM_DELETE_WINDOW", self.close_camera)
        self.camera_window.focus_force()  # Force focus to receive key presses
    
    def update_camera_feed(self):
        """Update the camera feed in the GUI"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Convert to RGB and resize for display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb = cv2.resize(frame_rgb, (640, 480))

                # Convert to PhotoImage
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)

                # Update label
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            # Schedule next update if window still exists
            if hasattr(self, 'camera_window') and self.camera_window.winfo_exists():
                self.camera_window.after(10, self.update_camera_feed)
    
    def capture_image(self, event=None):
        """Capture the current frame from camera"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.captured_image = frame.copy()
                self.close_camera()

                # Show preview in main window
                preview_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                preview_img = cv2.resize(preview_img, (200, 200))
                img = Image.fromarray(preview_img)
                imgtk = ImageTk.PhotoImage(image=img)

                self.image_preview.imgtk = imgtk
                self.image_preview.configure(image=imgtk)

                # Show success message
                messagebox.showinfo("Success", "Image captured successfully!", parent=self.add_window)
    
    def close_camera(self):
        """Close camera and cleanup"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        if hasattr(self, 'camera_window') and self.camera_window.winfo_exists():
            self.camera_window.destroy()

    def delete_user(self):
        """Delete selected user"""
        selected_item = self.users_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a user to delete", parent=self.admin_window)
            return
        user_data = self.users_tree.item(selected_item)['values']
        user_id = user_data[1]
        name = user_data[2]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{name}'?", parent=self.admin_window):
            success, message = self.encoder.remove_person(user_id)
            if success:
                messagebox.showinfo("Success", message, parent=self.admin_window)
                self.refresh_users_list()
                self.face_system.reload_encodings()
            else:
                messagebox.showerror("Error", message, parent=self.admin_window)
    
    def refresh_users_list(self):
        """Refresh the users list"""
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Load users from database
        users = self.db_manager.get_all_users()
        for user in users:
            # Only include ID, User ID, Name, Phone, Status, Created
            display_data = (user[0], user[1], user[2], user[4], user[6], user[7])
            self.users_tree.insert('', 'end', values=display_data)
    
    def refresh_logs_list(self):
        """Refresh the access logs list"""
        # Clear existing items
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        
        # Load logs from database
        logs = self.db_manager.get_access_logs()
        for log in logs:
            log_id, user_id, access_time, access_granted, name = log
            status = "GRANTED" if access_granted else "DENIED"
            display_name = name if name else "Unknown"
            self.logs_tree.insert('', 'end', values=(log_id, user_id, display_name, access_time, status))
    
    def clear_logs(self):
        """Clear all access logs"""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all access logs?", parent=self.admin_window):
            # This would require adding a method to DatabaseManager
            messagebox.showinfo("Info", "This feature will be implemented in the next version", parent=self.admin_window)
    
    def regenerate_encodings(self):
        """Regenerate face encodings"""
        if messagebox.askyesno("Confirm", "This will regenerate all face encodings. Continue?", parent=self.admin_window):
            self.status_var.set("Regenerating encodings...")
            
            def regen_thread():
                if self.encoder.generate_encoded_images():
                    self.face_system.reload_encodings()
                    self.status_var.set("Encodings regenerated successfully")
                    messagebox.showinfo("Success", "Encodings regenerated successfully!", parent=self.admin_window)
                else:
                    self.status_var.set("Failed to regenerate encodings")
                    messagebox.showerror("Error", "Failed to regenerate encodings", parent=self.admin_window)
            
            thread = threading.Thread(target=regen_thread, daemon=True)
            thread.start()
    
    def show_create_admin_dialog(self):
        """Show dialog to create new admin"""
        admin_window = tk.Toplevel(self.admin_window)
        admin_window.title("Create New Admin")
        admin_window.geometry("400x300")
        admin_window.configure(bg='#34495e')
        admin_window.grab_set()
        
        # Title
        title_label = tk.Label(admin_window, text="Create New Admin", 
                              font=("Arial", 18, "bold"), fg='white', bg='#34495e')
        title_label.pack(pady=30)
        
        # Username field
        tk.Label(admin_window, text="Username:", font=("Arial", 12), 
                fg='white', bg='#34495e').pack(pady=5)
        username_entry = tk.Entry(admin_window, font=("Arial", 12), width=25)
        username_entry.pack(pady=5)
        
        # Password field
        tk.Label(admin_window, text="Password:", font=("Arial", 12), 
                fg='white', bg='#34495e').pack(pady=5)
        password_entry = tk.Entry(admin_window, font=("Arial", 12), width=25, show="*")
        password_entry.pack(pady=5)
        
        # Confirm password field
        tk.Label(admin_window, text="Confirm Password:", font=("Arial", 12), 
                fg='white', bg='#34495e').pack(pady=5)
        confirm_entry = tk.Entry(admin_window, font=("Arial", 12), width=25, show="*")
        confirm_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(admin_window, bg='#34495e')
        button_frame.pack(pady=20)
        
        def create_admin():
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Username and password are required!", parent=admin_window)
                return
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match!", parent=admin_window)
                return
            
            if len(password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters!", parent=admin_window)
                return
            
            if self.db_manager.create_admin(username, password):
                messagebox.showinfo("Success", "Admin created successfully!", parent=admin_window)
                admin_window.destroy()
            else:
                messagebox.showerror("Error", "Username already exists!", parent=admin_window)
        
        create_btn = tk.Button(button_frame, text="Create", command=create_admin,
                              bg='#27ae60', fg='white', font=("Arial", 12))
        create_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=admin_window.destroy,
                              bg='#e74c3c', fg='white', font=("Arial", 12))
        cancel_btn.pack(side='left', padx=10)
    
    def update_system_info(self):
        """Update system information display"""
        info_text = f"""
System Status:
- Database: Connected
- Face Recognition: Ready
- Camera: Available

Statistics:
- Total Users: {len(self.db_manager.get_all_users())}
- Recent Access Logs: {len(self.db_manager.get_access_logs(50))}

Configuration:
- Recognition Confidence: 60%
- Cooldown Period: 2 seconds
- Max Log Entries: 100

Default Admin Credentials:
- Username: admin
- Password: admin123

Instructions:
1. Add users through the Users Management tab
2. Upload clear face photos for better recognition
3. Use the CHECK button to test face recognition
4. Monitor access through the Access Logs tab
        """
        
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        self.info_text.config(state='disabled')
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = MainGUI()
    app.run()