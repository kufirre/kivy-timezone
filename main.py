from kivy.lang import Builder
from kivymd.app import MDApp
from timezone_screen import TimezoneScreen
from kivy.core.window import Window

class TimezoneApp(MDApp):
    def build(self):
        # Set monochrome theme
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Gray"  # Monochrome palette
        self.theme_cls.accent_palette = "Gray"
        
        # Set window properties for desktop testing
        Window.size = (336, 536)  # Slightly smaller for better fit
        Window.minimum_width = 320
        Window.minimum_height = 480
        
        # Load the KV file
        Builder.load_file("timezone_screen.kv")
        
        # Return the main screen
        return TimezoneScreen()

if __name__ == "__main__":
    TimezoneApp().run()
