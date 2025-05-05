import socket
import threading
from tkinter import *
from tkinter import simpledialog, ttk, messagebox
from datetime import datetime

HOST = '127.0.0.1'
PORT = 50002

class Client:
    def __init__(self, host, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
        except Exception as e:
            print(f"[ERROR] Failed to connect to server at {host}:{port} - {e}")
            messagebox.showerror("Connection Error", f"Could not connect to server at {host}:{port}")
            self.sock = None

        self.nickname = None
        self.room = None

        self.gui_done = False
        self.running = True
        self.is_dark_mode = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        bg = "#1e1e1e" if self.is_dark_mode else "#ffffff"
        fg = "white" if self.is_dark_mode else "black"
        self.win.configure(bg=bg)
        self.chat_label.config(bg=bg, fg=fg)
        self.text_area.config(bg="#2e2e2e" if self.is_dark_mode else "#f0f0f0", fg=fg)
        self.msg_label.config(bg=bg, fg=fg)
        self.input_area.config(bg="#2e2e2e" if self.is_dark_mode else "#f0f0f0", fg=fg)
        self.send_button.config(bg="#007acc" if self.is_dark_mode else "#d0eaff", fg=fg)
        self.leave_button.config(bg="#d9534f", fg="white")
        self.emoji_frame.config(bg=bg)
        self.button_frame.config(bg=bg)
        self.theme_button.config(bg="#6c757d", fg="white")
        self.room_label.config(bg=bg, fg=fg)
        self.room_combo.config(background="#f0f0f0", foreground="black")

    def gui_loop(self):
        self.win = Tk()
        self.win.title("PyChatRoom")

        self.chat_label = Label(self.win, text="Chat", font=("Arial", 14, "bold"))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = Text(self.win, font=("Courier", 12), height=20)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state=DISABLED)

        self.msg_label = Label(self.win, text="Message", font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=(10, 0))

        self.input_area = Text(self.win, height=3, font=("Courier", 12))
        self.input_area.pack(padx=20, pady=(5, 10))

        self.button_frame = Frame(self.win)
        self.button_frame.pack(padx=20, pady=(0, 10))

        self.send_button = Button(self.button_frame, text="Send", command=self.write, font=("Arial", 12, "bold"))
        self.send_button.grid(row=0, column=0, padx=5)

        self.leave_button = Button(self.button_frame, text="Leave Chat", command=self.stop, bg="#d9534f", fg="white", font=("Arial", 12, "bold"))
        self.leave_button.grid(row=0, column=1, padx=5)

        self.theme_button = Button(self.button_frame, text="Toggle Theme", command=self.toggle_theme, font=("Arial", 12))
        self.theme_button.grid(row=0, column=2, padx=5)

        self.emoji_frame = Frame(self.win)
        self.emoji_frame.pack(padx=20, pady=(0, 10))

        emojis = ['😊', '😂', '👍', '❤️', '🎉']
        for idx, emoji in enumerate(emojis):
            btn = Button(self.emoji_frame, text=emoji, width=3, command=lambda e=emoji: self.insert_emoji(e), font=("Arial", 12))
            btn.grid(row=0, column=idx, padx=3)

        self.room_label = Label(self.win, text="Choose Room:", font=("Arial", 12))
        self.room_label.pack(padx=20, pady=(5, 0))

        self.room_combo = ttk.Combobox(self.win, values=["General", "Python", "Gaming", "AI"])
        self.room_combo.pack(padx=20, pady=(0, 10))
        self.room_combo.set("General")
        self.room_combo.bind("<<ComboboxSelected>>", self.change_room)

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=self.win)
        self.room = self.room_combo.get()

        self.gui_done = True
        self.apply_theme()
        self.win.mainloop()

    def insert_emoji(self, emoji):
        self.input_area.insert(END, emoji)

def write(self):
    if not self.sock:
        print("[ERROR] Socket is not connected.")
        return

    message_content = self.input_area.get('1.0', 'end').strip()
    if message_content:  # Only proceed if the message isn't empty or whitespace
        timestamp = datetime.now().strftime('%H:%M')
        message = f"[{self.room}] {self.nickname} [{timestamp}]: {message_content}"
        try:
            self.sock.send(message.encode('utf-8'))
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
        self.input_area.delete('1.0', END)
    else:
        print("[INFO] Empty message not sent.")


    def change_room(self, event=None):
        new_room = self.room_combo.get()
        if new_room != self.room:
            leave_msg = f"[{self.room}] {self.nickname} 👋 has left the room."
            join_msg = f"[{new_room}] {self.nickname} 👋 has joined the room."

            try:
                self.sock.send(leave_msg.encode('utf-8'))
                self.sock.send(join_msg.encode('utf-8'))
            except:
                pass

            self.room = new_room
            if self.gui_done:
                self.text_area.config(state=NORMAL)
                self.text_area.delete('1.0', END)
                self.text_area.config(state=DISABLED)

    def stop(self):
        self.running = False
        if self.sock and self.nickname and self.room:
            goodbye_message = f"[{self.room}] {self.nickname} 👋 has left the chat."
            try:
                self.sock.send(goodbye_message.encode('utf-8'))
            except:
                pass
        self.win.destroy()
        if self.sock:
            self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                if not self.sock:
                    break
                message = self.sock.recv(1024).decode('utf-8')
                if self.gui_done:
                    self.text_area.config(state=NORMAL)
                    self.text_area.insert('end', message + '\n')
                    self.text_area.yview(END)
                    self.text_area.config(state=DISABLED)
            except ConnectionAbortedError:
                break
            except:
                print("An error occurred!")
                if self.sock:
                    self.sock.close()
                break

if __name__ == "__main__":
    client = Client(HOST, PORT)
