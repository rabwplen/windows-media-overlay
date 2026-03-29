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
        
        
        def setup_settings_labels():
            # variables
            window_size = f"{parent.winfo_width()}x{parent.winfo_height()}"
            
            # resize
            resize_value = 1 if window_size == "330x100" else 2
            self.update_resize_label(resize_value)
            
            # opacity
            self.update_opacity_label(parent.min_alpha)
            
            # refresh rate
            self.update_refresh_label(parent.update_interval)
            
            # vertical alignment
            self.vertical_align_menu.set(parent.vertical_align)
            
            # horizontal alignment
            self.horizontal_align_menu.set(parent.horizontal_align)

            # cover visibility
            if parent.show_cover: self.cover_switch.select()
            else: self.cover_switch.deselect()
                
        
        def apply_settings():
            apply_resize = self.resize_slider.get()
            apply_opacity = self.opacity_slider.get()
            apply_refresh = self.refresh_slider.get()
            
            # resize
            parent.geometry("330x100" if apply_resize == 1 else "420x100")
            
            # opacity
            parent.min_alpha = apply_opacity
            parent.current_alpha = apply_opacity
            parent.attributes("-alpha", parent.current_alpha)
            
            # refresh rate
            parent.update_interval = int(apply_refresh)
            
            # vertical alignment
            parent.vertical_align = self.vertical_align_menu.get()
            
            # horizontal alignment
            parent.horizontal_align = self.horizontal_align_menu.get()
            
            # cover visibility
            parent.show_cover = self.cover_switch.get()
            
            # update ui and settings labels - - -
            parent.setup_ui()
        
        # - - - UI layout - - -
        
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10) 
        
        # (0 - labels, 1 - buttons, sliders, etc.)
        self.main_frame.grid_columnconfigure(0, weight=1, minsize=160)
        self.main_frame.grid_columnconfigure(1, weight=1, minsize=160)

        # overlay window size 
        self.resize_label = ctk.CTkLabel(self.main_frame, text="Overlay size:")
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
        
        # refresh interval
        self.refresh_label = ctk.CTkLabel(self.main_frame, text="Refresh Rate: 1000 ms")
        self.refresh_label.grid(row=2, column=0, padx=10, pady=self.default_padding, sticky="w")
        
        self.refresh_slider = ctk.CTkSlider(self.main_frame, from_=500, to=3000, number_of_steps=25, command=self.update_refresh_label)
        self.refresh_slider.set(1000)
        self.refresh_slider.grid(row=2, column=1, padx=10, pady=self.default_padding, sticky="e")
        
        # horizontal alignment
        self.horizontal_align_label = ctk.CTkLabel(self.main_frame, text="Horizontal Alignment:")
        self.horizontal_align_label.grid(row=3, column=0, padx=10, pady=self.default_padding, sticky="w")
        
        self.horizontal_align_menu = ctk.CTkOptionMenu(self.main_frame, values=["Left", "Center", "Right"])
        self.horizontal_align_menu.grid(row=3, column=1, padx=10, pady=self.default_padding, sticky="e")
        
        # vertical alignment
        self.vertical_align_label = ctk.CTkLabel(self.main_frame, text="Vertical Alignment:")
        self.vertical_align_label.grid(row=4, column=0, padx=10, pady=self.default_padding, sticky="w")
        
        self.vertical_align_menu = ctk.CTkOptionMenu(self.main_frame, values=["Top", "Middle", "Bottom"])
        self.vertical_align_menu.grid(row=4, column=1, padx=10, pady=self.default_padding, sticky="e")

        # show album cover
        self.cover_label = ctk.CTkLabel(self.main_frame, text="Show Album Cover:")
        self.cover_label.grid(row=5, column=0, padx=10, pady=self.default_padding, sticky="w")
        
        self.cover_switch = ctk.CTkSwitch(self.main_frame, text="")
        self.cover_switch.grid(row=5, column=1, padx=10, pady=self.default_padding, sticky="e")

        # apply button
        self.apply_settings_button = ctk.CTkButton(self.main_frame, text="Apply", command=apply_settings)
        self.apply_settings_button.grid(row=6, column=0, columnspan=2, pady=(20, 10))
        
        setup_settings_labels() # on open


    # --- methods for updating label text in real-time ---
    
    def update_resize_label(self, value):
        value_text = "330x100" if value == 1 else "420x100"
        self.resize_label.configure(text=f"Overlay size: {value_text}")
        self.resize_slider.set(value)

    def update_opacity_label(self, value):
        self.opacity_label.configure(text=f"Base Opacity: {value:.2f}")
        self.opacity_slider.set(value)

    def update_refresh_label(self, value):
        self.refresh_label.configure(text=f"Refresh Rate: {int(value)} ms")
        self.refresh_slider.set(value)