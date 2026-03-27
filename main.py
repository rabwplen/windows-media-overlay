import os
import sys
import asyncio
import threading

import tkinter as tk
import customtkinter as ctk

from PIL import Image, ImageDraw, ImageTk

from settings import SettingsWindow
from media_info import get_media_info, print_media_info, load_media_info


# - - - UIs basic colors for Overlay - - -
COLOR_BACKGROUND = "#000000"
COLOR_SECOND_BACKGROUND = "#080808"
COLOR_MAIN_TEXT = "#FFFFFF"
COLOR_SECONDARY_TEXT = "#BEBEBE"
COLOR_MUTED_TEXT = "#6E6E6E"

# - - - Standard UIs Positions - - -
POS_BACKGROUND =        {'relx': 0, 'rely': 0, 'x': 20, 'y': 0, "anchor": "nw"}

POS_CLOSE_BUTTON =      {'relx': 0, 'rely': 0, 'x': 0, 'y': 0, "anchor": "nw"}
POS_SETTINGS_BUTTON =   {'relx': 0, 'rely': 0, 'x': 0, 'y': 20, "anchor": "nw"}
POS_DRAG_HANDLE =       {'relx': 0, 'rely': 1, 'x': 0, 'y': 0, "anchor": "sw"}
POS_RESIZE_GRIP =       {'relx': 1, 'rely': 1, 'x': 0, 'y': 0, "anchor": "se"}

class Overlay(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # - - - just variables - - -
        self.settings_openned = False
        
        self.update_interval = 1000
        self.is_updating = True
        
        self.min_alpha = 0.6
        self.max_alpha = 0.9
        self.current_alpha = self.min_alpha
        self.fade_speed = 0.02
        self.fade_delay = 15
        self.fade_id = None         # ID for the fade animation
        self.leave_delay_id = None  # ID for the delayed fade out after mouse leave
        self.leave_pause = 1500
        
        # - - - window configuration - - -
        self.title("Media Overlay")
        self.geometry("330x100")
        self.attributes("-alpha", self.current_alpha)
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        # - - - UI elements - - -
        
        # main background frame
        self.main_background = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND, bg_color="transparent")
        self.main_background.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # track info frame
        self.background = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND, bg_color=COLOR_BACKGROUND, height=self.winfo_height(), width=(self.winfo_width()-20))
        self.background.place(**POS_BACKGROUND)
        
        
        # close button
        self.close_icon = ctk.CTkImage(light_image=Image.open("assets/close-icon.png"), size=(10, 10))
        
        self.close_button = ctk.CTkButton(self.main_background, text="", image=self.close_icon,
                                       width=20, height=20, corner_radius=0,
                                       fg_color=COLOR_BACKGROUND, hover_color="#1A1A1A",
                                       command=self.quit)
        self.close_button.place(**POS_CLOSE_BUTTON)
        
        # settings button (for future use)
        self.settings_icon = ctk.CTkImage(light_image=Image.open("assets/settings-icon.png"), size=(10, 10))
        
        self.settings_button = ctk.CTkButton(self.main_background, text="", image=self.settings_icon,
                                       width=20, height=20, corner_radius=0,
                                       fg_color=COLOR_BACKGROUND, hover_color="#1A1A1A",
                                       command=self.open_settings)
        self.settings_button.place(**POS_SETTINGS_BUTTON)

        # drag handle
        self.drag_icon = ctk.CTkImage(light_image=Image.open('assets/drag-icon.png'), size=(10, 10))

        self.drag_handle = ctk.CTkLabel(self.main_background, text="", image=self.drag_icon,
                                        width=20, height=20, corner_radius=0,
                                        fg_color=COLOR_BACKGROUND)
        self.drag_handle.place(**POS_DRAG_HANDLE)
        self.drag_handle.bind("<Button-1>", self.start_move)
        self.drag_handle.bind("<B1-Motion>", self.do_move)

        
        self.title_label = ctk.CTkLabel(self.background, text="Title", font=ctk.CTkFont(size=18, weight="bold",family="Segoe UI"), height=20,
                                        text_color=COLOR_MAIN_TEXT)
        self.title_label.place(x=96, y=0, anchor="nw")
        
        self.artist_label = ctk.CTkLabel(self.background, text="Artist", font=ctk.CTkFont(size=14, family="Segoe UI Semibold"),
                                        text_color=COLOR_SECONDARY_TEXT)
        self.artist_label.place(x=96, y=22, anchor="nw")
        
        self.track_duration = ctk.CTkLabel(self.background, text="0:00 / 0:00", font=ctk.CTkFont(size=12, family="Segoe UI"), text_color=COLOR_MUTED_TEXT)
        self.track_duration.place(x=96, y=-2, rely=1, anchor="sw")
        
        self.track_cover = ctk.CTkLabel(self.background, text="", width=90, height=90)
        self.track_cover.place(x=0, y=0, rely=0.5, anchor="w")
        
        self.after(self.update_interval, self.auto_update) 
    
    
    # - - - functions for window behavior - - -
    
    # auto update media info - - -
    def auto_update(self):
        if self.is_updating:
            on_get_media_info()  # Твоя функция, которая запускает поток
            
            # Планируем следующий вызов через заданный интервал
            self.after(self.update_interval, self.auto_update)
    
    # window dragging logic - - -
    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
    
    # fade in/out animation logic - - -
    def on_enter(self, event=None):
        if self.leave_delay_id:
            self.after_cancel(self.leave_delay_id)
            self.leave_delay_id = None
        
        self.cancel_fade()
        self.fade_to(self.max_alpha)

    def on_leave(self, event=None):
        if self.leave_delay_id:
            self.after_cancel(self.leave_delay_id)
        
        # start a delayed fade out after the mouse leaves the window
        self.leave_delay_id = self.after(self.leave_pause, lambda: (
            setattr(self, 'leave_delay_id', None),
            self.cancel_fade(),
            self.fade_to(self.min_alpha)
        ))

    def fade_to(self, target):
        if abs(self.current_alpha - target) > 0.01:
            if self.current_alpha < target:
                self.current_alpha = min(self.max_alpha, self.current_alpha + self.fade_speed)
            else:
                self.current_alpha = max(self.min_alpha, self.current_alpha - self.fade_speed)
            
            self.attributes("-alpha", self.current_alpha)
            self.fade_id = self.after(self.fade_delay, lambda: self.fade_to(target))

    def cancel_fade(self):
        if self.fade_id:
            self.after_cancel(self.fade_id)
            self.fade_id = None
    
    # open settings window - - -
    def open_settings(self):
        if getattr(self, "settings_openned", False):
            if hasattr(self, "settings_window") and self.settings_window.winfo_exists():
                self.settings_window.lift()
                self.settings_window.focus_force()
            return

        self.settings_openned = True
        self.settings_window = SettingsWindow(self)



def update_ui(data):
    if not data: # if no media info is available (for example no active media player is opened)
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


if __name__ == "__main__":
    app = Overlay()
    on_get_media_info()
    
    app.mainloop()