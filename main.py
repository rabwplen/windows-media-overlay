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
COLOR_MAIN_TEXT = "#FFFFFF"
COLOR_SECONDARY_TEXT = "#BEBEBE"
COLOR_MUTED_TEXT = "#6E6E6E"

# - - - Default UIs Positions - - -
POS_BACKGROUND          = {'relx': 0, 'rely': 0, 'x': 0, 'y': 0, "anchor": "nw"}

POS_CLOSE_BUTTON        = {'relx': 0, 'rely': 0, 'x': 0, 'y': 0, "anchor": "nw"}
POS_SETTINGS_BUTTON     = {'relx': 0, 'rely': 0, 'x': 0, 'y': 20, "anchor": "nw"}
POS_DRAG_HANDLE         = {'relx': 0, 'rely': 1, 'x': 0, 'y': 0, "anchor": "sw"}
POS_RESIZE_GRIP         = {'relx': 1, 'rely': 1, 'x': 0, 'y': 0, "anchor": "se"}

POS_TITLE_LABEL         = {'relx': 0, 'rely': 0, 'x': 115, 'y': 0, "anchor": "nw"}
POS_ARTIST_LABEL        = {'relx': 0, 'rely': 0, 'x': 115, 'y': 22, "anchor": "nw"}
POS_DURATION_LABEL      = {'relx': 0, 'rely': 1, 'x': 115, 'y': -5, "anchor": "sw"}
POS_COVER_IMAGE         = {'relx': 0, 'rely': 0.5, 'x': 22, 'y': 0, "anchor": "w"}

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
        
        self.vertical_align = "Top"
        self.horizontal_align = "Left"
        
        self.show_cover = True
        
        # - - - window configuration - - -
        self.title("Media Overlay")
        self.geometry("330x100")
        self.attributes("-alpha", self.current_alpha)
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        # - - - UI elements - - -
        
        # overlay background
        self.background = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND, bg_color="transparent", corner_radius=10)
        self.background.place(x=0, y=0, relwidth=1, relheight=1)
        
        
        # close button
        self.close_icon = ctk.CTkImage(light_image=Image.open("assets/close-icon.png"), size=(9, 9))
        
        self.close_button = ctk.CTkButton(self.background, text="", image=self.close_icon,
                                       width=20, height=20, corner_radius=0,
                                       fg_color=COLOR_BACKGROUND, hover_color="#1A1A1A", bg_color="transparent",
                                       command=self.quit)
        self.close_button.place(**POS_CLOSE_BUTTON)
        
        # settings button (for future use)
        self.settings_icon = ctk.CTkImage(light_image=Image.open("assets/settings-icon.png"), size=(9, 9))
        
        self.settings_button = ctk.CTkButton(self.background, text="", image=self.settings_icon,
                                       width=20, height=20, corner_radius=0,
                                       fg_color=COLOR_BACKGROUND, hover_color="#1A1A1A",
                                       command=self.open_settings)
        self.settings_button.place(**POS_SETTINGS_BUTTON)

        # drag handle
        self.drag_icon = ctk.CTkImage(light_image=Image.open('assets/drag-icon.png'), size=(10, 10))

        self.drag_handle = ctk.CTkLabel(self.background, text="", image=self.drag_icon,
                                        width=20, height=20, corner_radius=0,
                                        fg_color=COLOR_BACKGROUND)
        self.drag_handle.place(**POS_DRAG_HANDLE)
        self.drag_handle.bind("<Button-1>", self.start_move)
        self.drag_handle.bind("<B1-Motion>", self.do_move)

        
        # track title label
        self.title_label = ctk.CTkLabel(self.background, text="Title", font=ctk.CTkFont(size=18, weight="bold",family="Segoe UI"),
                                        text_color=COLOR_MAIN_TEXT,
                                        width=210, height=20)
        self.title_label.place(**POS_TITLE_LABEL)
        
        # track artist label
        self.artist_label = ctk.CTkLabel(self.background, text="Artist", font=ctk.CTkFont(size=14, family="Segoe UI Semibold"),
                                        text_color=COLOR_SECONDARY_TEXT,
                                        width=210)
        self.artist_label.place(**POS_ARTIST_LABEL)
        
        # track duration label
        self.track_duration = ctk.CTkLabel(self.background, text="0:00 / 0:00", font=ctk.CTkFont(size=12, family="Segoe UI"),
                                           text_color=COLOR_MUTED_TEXT,
                                           width=210)
        self.track_duration.place(**POS_DURATION_LABEL)
        
        # track cover image
        self.track_cover = ctk.CTkLabel(self.background, text="", width=88, height=88)
        self.track_cover.place(**POS_COVER_IMAGE)
        
        
        # no media info frame
        self.nmi_frame = ctk.CTkFrame(self.background, fg_color=COLOR_BACKGROUND, bg_color="transparent")
        
        # no media info label
        self.nmi_label = ctk.CTkLabel(self.nmi_frame, text="No media playing", font=ctk.CTkFont(size=14, family="Segoe UI"), text_color=COLOR_MUTED_TEXT)
        self.nmi_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        self.nmi_label.bind("<Button-1>", self.start_move)
        self.nmi_label.bind("<B1-Motion>", self.do_move)
        
        self.after(self.update_interval, self.auto_update) 
    
    
    # - - - functions for window behavior - - -
    
    # ui layout - - -
    def setup_ui(self):
        print("setup ui")
        
        self.update_idletasks()
        self.title_label.lift()
        
        current_size = f"{self.winfo_width()}x{self.winfo_height()}"
        correct_x = 0
        additional_width_size = 0
        additional_width_cover = 0
        
        
        # update labels width
        if current_size == "330x100":
            print("small")
            additional_width_size = 0
        elif current_size == "420x100":
            print("big")
            additional_width_size = 90

        # update cover visibility
        if self.show_cover:
            correct_x = 115
            additional_width_cover = 0
            self.track_cover.place(**POS_COVER_IMAGE)
            
        else:
            correct_x = 22
            additional_width_cover = 93
            self.track_cover.place_forget()
        
        # update text alignment
        if self.vertical_align == "Top":
            self.title_label.place_configure(**{**POS_TITLE_LABEL, 'x': correct_x})
            self.artist_label.place_configure(**{**POS_ARTIST_LABEL, 'x': correct_x})
            self.track_duration.place_configure(**{**POS_DURATION_LABEL, 'x': correct_x})
        elif self.vertical_align == "Middle":
            self.title_label.place_configure(**{**POS_TITLE_LABEL, 'y': -25, 'rely': 0.5, 'x': correct_x})
            self.artist_label.place_configure(**{**POS_ARTIST_LABEL, 'y': -3, 'rely': 0.5, 'x': correct_x})
            self.track_duration.place_configure(**{**POS_DURATION_LABEL, 'x': correct_x})
        elif self.vertical_align == "Bottom":
            self.title_label.place_configure(**{**POS_TITLE_LABEL, 'y': 70, 'x': correct_x})
            self.artist_label.place_configure(**{**POS_ARTIST_LABEL, 'y': 52, 'x': correct_x})
            self.track_duration.place_configure(**{**POS_DURATION_LABEL, 'y': -80, 'x': correct_x})
        
        if self.horizontal_align == "Left":
            self.title_label.configure(anchor="nw")
            self.artist_label.configure(anchor="nw")
            self.track_duration.configure(anchor="sw")
        elif self.horizontal_align == "Center":
            self.title_label.configure(anchor="n")
            self.artist_label.configure(anchor="n")
            self.track_duration.configure(anchor="s")
        elif self.horizontal_align == "Right":
            self.title_label.configure(anchor="ne")
            self.artist_label.configure(anchor="ne")
            self.track_duration.configure(anchor="se")
        
        # update text width
        additional_width = additional_width_size + additional_width_cover
        self.title_label.configure(width=210 + additional_width)
        self.artist_label.configure(width=210 + additional_width)
        self.track_duration.configure(width=210 + additional_width)

    # auto update media info - - -
    def auto_update(self):
        if self.is_updating:
            on_get_media_info()
            
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
        # app.track_cover.image = None
        app.nmi_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        app.nmi_frame.lift()
        app.close_button.lift()
        app.settings_button.lift()
        return
    if app.nmi_frame.winfo_ismapped(): app.nmi_frame.place_forget()
        

    app.title_label.configure(text=data["title"])
    app.artist_label.configure(text=data["artist"])
    app.track_duration.configure(text=f"{data['position']} / {data['duration']}")
    
    if data["cover_image"]:
        img = data["cover_image"].resize((app.track_cover.winfo_width(), app.track_cover.winfo_height()))
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(app.track_cover.winfo_width(), app.track_cover.winfo_height()))
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
    app.setup_ui()
    
    app.mainloop()