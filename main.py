import os
import sys
import asyncio
import threading

import tkinter as tk
import customtkinter as ctk

from PIL import Image, ImageDraw, ImageTk

from media_info import get_media_info, print_media_info, load_media_info


# UIs basic colors for Overlay
COLOR_BACKGROUND = "#000000"
COLOR_SECOND_BACKGROUND = "#080808"
COLOR_MAIN_TEXT = "#FFFFFF"
COLOR_SECONDARY_TEXT = "#BEBEBE"
COLOR_MUTED_TEXT = "#6E6E6E"

# Standard UIs Positions
POS_BACKGROUND = {'relx': 0, 'rely': 0, 'x': 20, 'y': 0, "anchor": "nw"}

POS_CLOSE_BUTTON = {'relx': 0, 'rely': 0, 'x': 0, 'y': 0, "anchor": "nw"}
POS_SETTINGS_BUTTON = {'relx': 0, 'rely': 0, 'x': 2, 'y': 28, "anchor": "nw"}
POS_DRAG_HANDLE = {'relx': 0, 'rely': 1, 'x': 0, 'y': 0, "anchor": "sw"}
POS_RESIZE_GRIP = {'relx': 1, 'rely': 1, 'x': 0, 'y': 0, "anchor": "se"}

class Overlay(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Media Overlay")
        self.geometry("330x100")
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        
        
        self.main_background = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND, bg_color="transparent")
        self.main_background.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # track info frame
        self.background = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND, bg_color=COLOR_BACKGROUND, height=self.winfo_height(), width=(self.winfo_width()-20))
        self.background.place(**POS_BACKGROUND)
        
        
        self.close_icon = ctk.CTkImage(light_image=Image.open("assets/close-icon.png"), size=(10, 10))
        
        self.close_button = ctk.CTkButton(self.main_background, text="", image=self.close_icon,
                                       width=20, height=20, corner_radius=0,
                                       fg_color=COLOR_BACKGROUND, hover_color="#1A1A1A",
                                       command=quit_app)
        self.close_button.place(**POS_CLOSE_BUTTON)

        self.drag_icon = ctk.CTkImage(light_image=Image.open('assets/drag-icon.png'), size=(10, 10))

        self.drag_handle = ctk.CTkLabel(self.main_background, text="", image=self.drag_icon,
                                        width=20, height=20, corner_radius=0,
                                        fg_color=COLOR_BACKGROUND)
        self.drag_handle.place(**POS_DRAG_HANDLE)
        self.drag_handle.bind("<Button-1>", self.start_move)
        self.drag_handle.bind("<B1-Motion>", self.do_move)

        
        self.title_label = ctk.CTkLabel(self.background, text="Title", font=ctk.CTkFont(size=18, weight="bold",family="Segoe UI"), height=20,
                                        text_color=COLOR_MAIN_TEXT)
        self.title_label.place(x=95, y=0, anchor="nw")
        
        self.artist_label = ctk.CTkLabel(self.background, text="Artist", font=ctk.CTkFont(size=14, family="Segoe UI Semibold"),
                                        text_color=COLOR_SECONDARY_TEXT)
        self.artist_label.place(x=95, y=22, anchor="nw")
        
        self.track_duration = ctk.CTkLabel(self.background, text="0:00 / 0:00", font=ctk.CTkFont(size=12, family="Segoe UI"), text_color=COLOR_MUTED_TEXT)
        self.track_duration.place(x=95, y=-2, rely=1, anchor="sw")
        
        self.track_cover = ctk.CTkLabel(self.background, text="", width=90, height=90)
        self.track_cover.place(x=0, y=0, rely=0.5, anchor="w")
        
        
        self.update_button = ctk.CTkButton(self, text="get media info", corner_radius=0, width=20, command=on_get_media_info)
        self.update_button.place(x=0, y=0, relx=1, rely=1, anchor="se")
    
    
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



def update_ui(data):
    if not data:
        app.title_label.configure(text="No Media Active")
        app.artist_label.configure(text="Unknown artist")
        app.track_duration.configure(text="0:00 / 0:00")
        app.track_cover.configure(image=None, text="")
        return

    app.title_label.configure(text=data["title"])
    app.artist_label.configure(text=data["artist"])
    app.track_duration.configure(text=f"{data['position']} / {data['duration']}")
    
    if data["cover_image"]:
        img = data["cover_image"].resize((90, 90))
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(90, 90))
        app.track_cover.configure(image=ctk_img)
        app.track_cover.image = ctk_img
    else:
        app.track_cover.configure(image=None, text="")

def on_get_media_info():
    threading.Thread(
        target=load_media_info, 
        args=(app, update_ui), 
        daemon=True
    ).start()


def quit_app():
    print("bye!")
    app.quit()

# def on_get_media_info():
#     data = asyncio.run(get_media_info())

#     if not data:
#         app.title_label.configure(text="Title: No Media Active")
#         app.artist_label.configure(text="Artist: -")
#         return

#     app.title_label.configure(text=data["title"])
#     app.artist_label.configure(text=data["artist"])

#     if data["cover_image"]:
#         img = data["cover_image"].resize((90, 90))
#         ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(90, 90))
#         app.track_cover.configure(image=ctk_img)
#         app.track_cover.image = ctk_img
#     else:
#         app.track_cover.configure(image=None, text="")



if __name__ == "__main__":
    app = Overlay()
    app.mainloop()