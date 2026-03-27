import tkinter as tk
import customtkinter as ctk

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.app = parent
        
        self.title("Settings")
        self.geometry("400x350")
        self.minsize(350, 250)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.default_padding = 5

        def on_close():
            self.app.settings_openned = False
            self.destroy()

        self.protocol("WM_DELETE_WINDOW", on_close)
        
        # - - - UI layout - - -
        
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10) 
        
        # (0 - labels, 1 - buttons, sliders, etc.)
        self.main_frame.grid_columnconfigure(0, weight=1, minsize=160)
        self.main_frame.grid_columnconfigure(1, weight=1, minsize=160)

        # overlay window size 
        self.resize_label = ctk.CTkLabel(self.main_frame, text="Overlay size: 1.0")
        self.resize_label.grid(row=0, column=0, padx=10, pady=self.default_padding, sticky="w")
        
        self.resize_slider = ctk.CTkSlider(self.main_frame, from_=1, to=2, number_of_steps=1, command=self.update_resize_label)
        self.resize_slider.set(1)
        self.resize_slider.grid(row=0, column=1, padx=10, pady=self.default_padding, sticky="e")
        
        # opacity 
        self.opacity_label = ctk.CTkLabel(self.main_frame, text="Base Opacity: 0.60")
        self.opacity_label.grid(row=1, column=0, padx=10, pady=self.default_padding, sticky="w")
        
        self.opacity_slider = ctk.CTkSlider(self.main_frame, from_=0.1, to=1.0, command=self.update_opacity_label)
        self.opacity_slider.set(0.6)
        self.opacity_slider.grid(row=1, column=1, padx=10, pady=self.default_padding, sticky="e")

        # theme selection
        self.theme_label = ctk.CTkLabel(self.main_frame, text="Theme:")
        self.theme_label.grid(row=2, column=0, padx=10, pady=self.default_padding, sticky="w")
        
        self.theme_menu = ctk.CTkOptionMenu(self.main_frame, values=["Dark", "Light", "System"])
        self.theme_menu.grid(row=2, column=1, padx=10, pady=self.default_padding, sticky="e")

        # show album cover
        self.cover_label = ctk.CTkLabel(self.main_frame, text="Show Album Cover:")
        self.cover_label.grid(row=3, column=0, padx=10, pady=self.default_padding, sticky="w")
        
        self.cover_switch = ctk.CTkSwitch(self.main_frame, text="") 
        self.cover_switch.grid(row=3, column=1, padx=10, pady=self.default_padding, sticky="e")
        self.cover_switch.select()

        # refresh interval
        self.refresh_label = ctk.CTkLabel(self.main_frame, text="Refresh Rate: 1000 ms")
        self.refresh_label.grid(row=4, column=0, padx=10, pady=self.default_padding, sticky="w")
        
        self.refresh_slider = ctk.CTkSlider(self.main_frame, from_=500, to=3000, number_of_steps=25, command=self.update_refresh_label)
        self.refresh_slider.set(1000)
        self.refresh_slider.grid(row=4, column=1, padx=10, pady=self.default_padding, sticky="e")

        # text alignment
        self.align_label = ctk.CTkLabel(self.main_frame, text="Text Alignment:")
        self.align_label.grid(row=5, column=0, padx=10, pady=self.default_padding, sticky="w")
        
        self.align_menu = ctk.CTkOptionMenu(self.main_frame, values=["Left", "Center", "Right"])
        self.align_menu.grid(row=5, column=1, padx=10, pady=self.default_padding, sticky="e")

        # apply button
        self.apply_settings_button = ctk.CTkButton(self.main_frame, text="Apply")
        self.apply_settings_button.grid(row=6, column=0, columnspan=2, pady=(20, 10))

    # --- methods for updating label text in real-time ---
    
    def update_resize_label(self, value):
        self.resize_label.configure(text=f"Overlay size: {value:.1f}")

    def update_opacity_label(self, value):
        self.opacity_label.configure(text=f"Base Opacity: {value:.2f}")
        
    def update_refresh_label(self, value):
        self.refresh_label.configure(text=f"Refresh Rate: {int(value)} ms")