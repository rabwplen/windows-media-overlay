import os
import sys
import asyncio

import tkinter as tk
import customtkinter as ctk

from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager

from PIL import Image, ImageDraw, ImageTk
    

def quit_app():
    print("bye!")
    app.quit()
    
async def get_media_info():
    sessions = await GlobalSystemMediaTransportControlsSessionManager.request_async()
    session = sessions.get_current_session()

    if not session:
        print("No active media session (get_media_info)")
        return

    info = await session.try_get_media_properties_async()
    

    return {
        "title":    info.title or "-",
        "artist":   info.artist or "-",
        "album":    info.album_title or "-",
        "album_artist": info.album_artist or "-"
        # "thumbnail": info.thumbnail or "-"
    }
    
async def get_main():
    data = await get_media_info()

    if not data:
        print("No active media session (main)")
        return

    print(" - - - Current Media - - - ")
    for key, value in data.items():
        print(f"{key}: {value}")
    print()

class MediaInfoWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Media Info")
        self.geometry("400x200")
        
        self.update_button = ctk.CTkButton(self, text="Get Media Info", command=self.on_get_media_info)
        self.update_button.pack(pady=20)
        
        self.title_label = ctk.CTkLabel(self, text="Title: -")
        self.title_label.pack()
        self.artist_label = ctk.CTkLabel(self, text="Artist: -")
        self.artist_label.pack()
        self.album_label = ctk.CTkLabel(self, text="Album: -")
        self.album_label.pack()
        
    def on_get_media_info(self):
        asyncio.run(get_main())
        data = asyncio.run(get_media_info())
        
        if data:
            # Если данные есть, обновляем текст
            self.title_label.configure(text=f"Title: {data['title']}")
            self.artist_label.configure(text=f"Artist: {data['artist']}")
            self.album_label.configure(text=f"Album: {data['album']}")
        else:
            # Если плеера нет, выводим заглушку, чтобы не было ошибки
            self.title_label.configure(text="Title: No Media Active")
            self.artist_label.configure(text="Artist: -")
            self.album_label.configure(text="Album: -")


# UIs basic colors for Overlay
COLOR_BACKGROUND = "#000000"
COLOR_SECOND_BACKGROUND = "#080808"
COLOR_MAIN_TEXT = "#FFFFFF"
COLOR_SECONDARY_TEXT = "#BEBEBE"
COLOR_MUTED_TEXT = "#6E6E6E"
COLOR_CONTROL_PANEL = "#000000"

class Overlay(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Media Overlay")
        self.geometry("330x100")
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        
        
        self.backgound_frame = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND, bg_color="transparent", width=330-20, height=0)
        self.backgound_frame.place(x=20, y=0, relheight=1)
        
        self.side_buttons = ctk.CTkFrame(self,fg_color=COLOR_BACKGROUND, bg_color="transparent", width=20, height=0)
        self.side_buttons.place(x=0, y=0, relheight=1)
        
        
        self.close_icon = ctk.CTkImage(light_image=Image.open("assets/close-icon.png"), size=(8, 8))
        
        self.close_button = ctk.CTkButton(self.side_buttons, text="", image=self.close_icon,
                                       width=20, height=20,
                                       fg_color="#ff0000", hover_color="#ff4d4d",
                                       command=quit_app)
        self.close_button.place(x=0, y=0, rely=0, anchor="nw")

        self.drag_handle = ctk.CTkFrame(self.side_buttons,
                                        width=20, height=20,
                                        fg_color="#ECECEC")
        self.drag_handle.place(x=0, y=0, rely=1, anchor="sw")
        self.drag_handle.bind("<Button-1>", self.start_move)
        self.drag_handle.bind("<B1-Motion>", self.do_move)
        
        self.title_label = ctk.CTkLabel(self.backgound_frame, text="Title: -")
        self.title_label.place(x=2, y=0)
        
        self.artist_label = ctk.CTkLabel(self.backgound_frame, text="Artist: -")
        self.artist_label.place(x=2, y=25)
        
        self.album_label = ctk.CTkLabel(self.backgound_frame, text="Album: -")
        self.album_label.place(x=2, y=50)
    
    
    # window dragging logic
    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")



if __name__ == "__main__":
    app = Overlay()
    media_info = MediaInfoWindow(app)
    app.mainloop()