from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.metrics import dp
import os
import subprocess
import platform
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from pytz import timezone as ZoneInfo

# Enhanced list of timezones with better coverage
TIMEZONES = [
    ("US/Pacific", "Pacific Time - US & Canada"),
    ("US/Mountain", "Mountain Time - US & Canada"),
    ("US/Central", "Central Time - US & Canada"),
    ("US/Eastern", "Eastern Time - US & Canada"),
    ("Europe/London", "London, Dublin"),
    ("Europe/Paris", "Paris, Berlin, Rome"),
    ("Europe/Stockholm", "Stockholm, Oslo, Copenhagen"),
    ("Europe/Moscow", "Moscow, St. Petersburg"),
    ("Asia/Kolkata", "India Standard Time"),
    ("Asia/Tokyo", "Japan Standard Time"),
    ("Asia/Shanghai", "Beijing, Shanghai"),
    ("Asia/Seoul", "Seoul"),
    ("Asia/Dubai", "Dubai, Abu Dhabi"),
    ("Australia/Sydney", "Sydney, Melbourne"),
    ("Australia/Perth", "Perth"),
    ("Pacific/Auckland", "Auckland, Wellington"),
    ("America/Sao_Paulo", "São Paulo, Rio de Janeiro"),
    ("America/Argentina/Buenos_Aires", "Buenos Aires"),
    ("Africa/Cairo", "Cairo"),
    ("Africa/Lagos", "Lagos, Abuja"),
    ("UTC", "Coordinated Universal Time"),
]

def get_utc_offset(tz_name):
    """Get the UTC offset for a timezone."""
    try:
        now = datetime.now(ZoneInfo(tz_name))
        offset_sec = now.utcoffset().total_seconds()
        sign = '+' if offset_sec >= 0 else '-'
        hours, remainder = divmod(abs(int(offset_sec)), 3600)
        minutes = remainder // 60
        return f"UTC{sign}{hours:02d}:{minutes:02d}"
    except Exception:
        return "UTC+00:00"

class CustomMenuItem(TwoLineListItem):
    """Custom menu item for monochrome styling with dividers."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set consistent height for menu items
        self.height = dp(60)  # Fixed height for consistent spacing

class TimezoneScreen(MDScreen):
    selected_timezone = StringProperty("")
    current_timezone = StringProperty("")
    button_active = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu = None
        Clock.schedule_once(self.initialize_timezone, 0.1)
    
    def initialize_timezone(self, dt):
        """Initialize the timezone after the UI is built."""
        tz = self.get_current_timezone()
        if not tz or tz.lower() == 'unknown':
            tz = 'UTC'
        self.current_timezone = tz
        self.selected_timezone = tz
        
    def get_current_timezone(self):
        """Get current system timezone with better cross-platform support."""
        system = platform.system()
        
        # macOS
        if system == "Darwin":
            try:
                result = subprocess.run(['readlink', '/etc/localtime'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Extract timezone from path like /usr/share/zoneinfo/America/New_York
                    path = result.stdout.strip()
                    if '/zoneinfo/' in path:
                        return path.split('/zoneinfo/')[-1]
                        
                # Alternative method for macOS
                result = subprocess.run(['ls', '-la', '/etc/localtime'], capture_output=True, text=True)
                if '/zoneinfo/' in result.stdout:
                    return result.stdout.split('/zoneinfo/')[-1].strip()
            except Exception:
                pass
        
        # Linux
        elif system == "Linux":
            try:
                if os.path.exists('/etc/timezone'):
                    with open('/etc/timezone', 'r') as f:
                        return f.read().strip()
                        
                result = subprocess.run(['timedatectl'], capture_output=True, text=True)
                for line in result.stdout.splitlines():
                    if 'Time zone:' in line:
                        return line.split('Time zone:')[1].split()[0]
            except Exception:
                pass
        
        # Fallback: try to get from datetime
        try:
            import time
            return time.tzname[0] if hasattr(time, 'tzname') else 'UTC'
        except Exception:
            return "UTC"

    def get_time_for_tz(self, tz_name):
        """Get current time for a specific timezone."""
        try:
            now = datetime.now(ZoneInfo(tz_name))
            return now.strftime('%I:%M %p').lstrip('0')  # Remove leading zero
        except Exception:
            return "--:--"

    def get_dropdown_label(self, tz_name):
        """Create a formatted label for the dropdown button."""
        if not tz_name:
            return "Select Timezone"
            
        # Find display name
        display_name = next((d for t, d in TIMEZONES if t == tz_name), tz_name)
        time_str = self.get_time_for_tz(tz_name)
        utc_offset = get_utc_offset(tz_name)
        
        return f"{display_name}\n{utc_offset} • {time_str}"
    
    def get_main_label(self, tz_name):
        """Get the main label for the timezone selector."""
        if not tz_name:
            return "Select a timezone"
        return next((d for t, d in TIMEZONES if t == tz_name), tz_name)
    
    def get_sub_label(self, tz_name):
        """Get the sub label for the timezone selector."""
        if not tz_name:
            return "Tap to choose your timezone"
        time_str = self.get_time_for_tz(tz_name)
        utc_offset = get_utc_offset(tz_name)
        return f"{utc_offset} • {time_str}"

    def open_menu(self):
        """Open the timezone selection menu."""
        if self.menu:
            self.menu.dismiss()
            
        menu_items = []
        for tz_name, display_name in TIMEZONES:
            current_time = self.get_time_for_tz(tz_name)
            utc_offset = get_utc_offset(tz_name)
            is_selected = (tz_name == self.selected_timezone)
            
            # Shorten display name if too long
            shortened_name = display_name if len(display_name) <= 35 else display_name[:32] + "..."
            
            menu_items.append({
                "viewclass": "CustomMenuItem", 
                "text": shortened_name,
                "secondary_text": f"{utc_offset} • {current_time}",
                "on_release": lambda tz=tz_name: self.menu_callback(tz),
                "md_bg_color": (0, 0, 0, 1) if is_selected else (1, 1, 1, 1),  # Black for selected, white for others
                "text_color": (1, 1, 1, 1) if is_selected else (0, 0, 0, 1),  # White text on black, black text on white
                "secondary_text_color": (0.8, 0.8, 0.8, 1) if is_selected else (0.4, 0.4, 0.4, 1),
                "_no_ripple_effect": False,
                "height": dp(60),  # Consistent height as numeric value
                "divider": "Full",  # Add full-width divider between items
            })
            
        # Calculate dropdown width to match button width
        button = self.ids.timezone_button
        
        self.menu = MDDropdownMenu(
            caller=button,
            items=menu_items,
            width_mult=6,  # Even wider dropdown for better text display
            max_height=button.height * 6,  # Relative to button height (allows ~6 items)
            background_color=(1, 1, 1, 1),  # White background
            elevation=0,  # No elevation
            border_margin=dp(0),
            position="center",  # Center on the button
        )
        
        # Add black outline border like the button (without constraining width)
        def setup_menu_appearance(dt):
            if self.menu and hasattr(self.menu, 'ids') and 'md_menu' in self.menu.ids:
                menu_widget = self.menu.ids.md_menu
                
                # Add black border outline like the button
                with menu_widget.canvas.after:
                    from kivy.graphics import Color, Line
                    Color(0, 0, 0, 1)  # Black border
                    Line(
                        rounded_rectangle=(
                            menu_widget.x, menu_widget.y,
                            menu_widget.width, menu_widget.height,
                            dp(8)
                        ),
                        width=2
                    )
                    
        from kivy.clock import Clock
        Clock.schedule_once(setup_menu_appearance, 0.2)
        self.menu.open()

    def menu_callback(self, tz_name):
        """Handle timezone selection."""
        self.selected_timezone = tz_name
        if self.menu:
            self.menu.dismiss()
            
        # Show feedback to user
        from kivymd.toast import toast
        display_name = next((d for t, d in TIMEZONES if t == tz_name), tz_name)
        toast(f"Timezone changed to {display_name}")
        
        # Try to set system timezone (this will only work on some systems)
        self.set_system_timezone(tz_name)
        
        print(f"Selected timezone: {tz_name}")

    def set_system_timezone(self, tz_name):
        """Attempt to set system timezone (requires appropriate permissions)."""
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                subprocess.run(['sudo', 'systemsetup', '-settimezone', tz_name], 
                             check=True, capture_output=True)
            elif system == "Linux":
                # Method 1: Update /etc/timezone (Debian/Ubuntu)
                if os.path.exists('/etc/timezone'):
                    with open('/etc/timezone', 'w') as f:
                        f.write(tz_name + '\n')
                    subprocess.run(['sudo', 'dpkg-reconfigure', '-f', 'noninteractive', 'tzdata'], 
                                 check=True, capture_output=True)
                else:
                    # Method 2: Use timedatectl (systemd systems)
                    subprocess.run(['sudo', 'timedatectl', 'set-timezone', tz_name], 
                                 check=True, capture_output=True)
            
            self.current_timezone = tz_name
            from kivymd.toast import toast
            toast("System timezone updated successfully!")
            
        except subprocess.CalledProcessError:
            from kivymd.toast import toast
            toast("Could not update system timezone - permission denied")
        except PermissionError:
            from kivymd.toast import toast
            toast("Permission denied - run with administrator privileges")
        except Exception as e:
            from kivymd.toast import toast
            toast(f"Failed to update system timezone: {str(e)}")

