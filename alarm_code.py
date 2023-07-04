import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from io import BytesIO
from PIL import ImageTk, Image
import datetime
import time
import subprocess
class AlarmApp:
    
    def __init__(self):
        icon_path = r"C:\Users\R3XED\Downloads\alarm\clock.ico"
        self.window = tk.Tk()
        self.window.iconbitmap(icon_path)
        
        self.window.title("Alarm App with Spotify API")
        self.style = ThemedStyle(self.window)
        self.style.theme_use("equilux")
        self.window.configure(bg=self.style.lookup("TFrame", "background"))
        self.style.configure("TLabel", foreground="white", font=("Arial", 12))  # Set label text color and font
        self.style.configure("TButton", font=("Arial", 12))  # Set button font

     
       

        # Improve responsiveness
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(2, weight=1)

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id='YOUR_CLIENTEID',
            client_secret='YOUR_SECRETID',
            redirect_uri='http://localhost:8888/callback',
            scope='user-library-read,user-modify-playback-state,user-read-playback-state'
        ))

        self.results = []
        self.cover_images_cache = {}  # Store the cached cover images
        self.alarms = []
        self.create_widgets()

    def create_widgets(self):
        # Create frames for better organization
        frame_ampm_alarm = ttk.Frame(self.window)
        frame_ampm_alarm.pack(side=tk.BOTTOM, padx=10, pady=10,anchor=tk.W)

        frame_time_search = ttk.Frame(self.window)
        frame_time_search.pack(side=tk.LEFT, padx=10, pady=10,anchor=tk.W)

        frame_cover = ttk.Frame(self.window)
        frame_cover.pack(side=tk.RIGHT, padx=10,fill=tk.BOTH, pady=10, anchor=tk.E)

        self.create_cover_image_label(frame_cover)
        self.create_time_widgets(frame_time_search)
        self.create_search_widgets(frame_time_search)
        self.create_ampm_widgets(frame_ampm_alarm)
        self.create_alarm_button(frame_ampm_alarm)




    def create_time_widgets(self, parent):
        label_time = ttk.Label(parent, text="Alarm Time (HH:MM):")
        label_time.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.entry_time = ttk.Entry(parent, font=("Arial", 12))
        self.entry_time.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

    def create_search_widgets(self, parent):
        label_search = ttk.Label(parent, text="Search Song:")
        label_search.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.entry_search = ttk.Entry(parent, font=("Arial", 12))
        self.entry_search.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        btn_search = ttk.Button(parent, text="Search", command=self.search_song)
        btn_search.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

        self.combo_results = ttk.Combobox(parent, state="readonly", postcommand=self.show_dropdown, font=("Arial", 12))
        self.combo_results.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)

    def create_ampm_widgets(self, parent):
        label_ampm = ttk.Label(parent, text="AM/PM:")
        label_ampm.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.var_ampm = tk.StringVar()
        self.radio_am = ttk.Radiobutton(parent, text="AM", variable=self.var_ampm, value="AM", style="TRadiobutton")
        self.radio_am.grid(row=0, column=1, padx=5, pady=5)

        self.radio_pm = ttk.Radiobutton(parent, text="PM", variable=self.var_ampm, value="PM", style="TRadiobutton")
        self.radio_pm.grid(row=0, column=2, padx=5, pady=5)

    def create_alarm_button(self, parent):
        btn_set_alarm = ttk.Button(parent, text="Set Alarm", command=self.set_alarm)
        btn_set_alarm.grid(row=0, column=0, padx=5, pady=10)

    def create_cover_image_label(self, parent):
        self.cover_image_label = ttk.Label(parent)
        self.cover_image_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NE)
    






    def search_song(self):
        query = self.entry_search.get()
        if query:
            self.results = self.sp.search(q=query, limit=10, type='track')['tracks']['items']
            song_options = [f"{track['name']} - {track['artists'][0]['name']}" for track in self.results]
            self.combo_results['values'] = song_options
            print("Song search results updated.")

            # Download cover images and cache them
            self.download_and_cache_cover_images()
            
            # Enable the dropdown menu after cover images are downloaded
            self.show_dropdown()
    def download_and_cache_cover_images(self):
        self.cover_images_cache = {}
        for track in self.results:
            image_url = track["album"]["images"][0]["url"]
            image_data = requests.get(image_url).content
            image_hd = Image.open(BytesIO(image_data))
            image_big = image_hd.resize((200,200))
            # Resize the image to a smaller version for the dropdown menu
            image_small = image_hd.resize((45, 45))

            # Create PhotoImages for both versions
            photo_hd = ImageTk.PhotoImage(image_big)
            photo_small = ImageTk.PhotoImage(image_small)

            # Cache both PhotoImages using the track URI as the key
            track_uri = track["uri"]
            self.cover_images_cache[track_uri] = {"hd": photo_hd, "small": photo_small}

    
   # Método para mostrar el menú desplegable
    def show_dropdown(self):
        if self.results:
            self.dropdown_options = []

            for track in self.results:
                track_name = track["name"]
                artist_name = track["artists"][0]["name"]
                track_uri = track["uri"]

                # Get the cached cover images
                cover_images = self.cover_images_cache.get(track_uri)
                photo_small = cover_images["small"]

                # Create a dictionary with the track details and the corresponding small image
                option = {"track_name": track_name, "artist_name": artist_name, "photo_small": photo_small, "track_uri": track_uri}
                self.dropdown_options.append(option)

            # Create the custom dropdown menu
            self.dropdown_menu = tk.Menu(self.window, tearoff=0)

            for option in self.dropdown_options:
                self.dropdown_menu.add_command(
                    label=f"{option['track_name']} - {option['artist_name']}",
                    image=str(option['photo_small']),  # Convert the image reference to string
                    compound=tk.LEFT,
                    command=lambda o=option: self.select_song(o)
                )

            self.dropdown_menu.post(self.combo_results.winfo_rootx(),
                                    self.combo_results.winfo_rooty() + self.combo_results.winfo_height())
            print("Dropdown menu shown.")
        else:
            print("No results to show in the dropdown menu.")

    def select_song(self, option):
        self.combo_results.set(f"{option['track_name']} - {option['artist_name']}")
        self.load_cover_image(option)

        # Hide the dropdown menu
        self.hide_dropdown()

    def load_cover_image(self, option):
        track_uri = option["track_uri"]
        cover_images = self.cover_images_cache.get(track_uri)

        if cover_images is not None:
            photo_hd = cover_images["hd"]

            # Añadir un marco alrededor de la imagen
            frame = tk.Frame(self.window, bd=3, relief=tk.SOLID)
            frame.pack()

            # Mostrar la imagen en el marco
            image_label = tk.Label(frame, image=photo_hd)
            image_label.pack()

            # Actualizar la imagen en el marco
            image_label.config(image=photo_hd)
            image_label.image = photo_hd
        else:
            print("Cover image not found in cache.")


    def hide_dropdown(self):
        if self.dropdown_menu:
            self.dropdown_menu.unpost()
            self.dropdown_menu.destroy()
            self.dropdown_menu = None
            print("Dropdown menu hidden.")

    def play_song(self, song_uri):
        devices = self.sp.devices()
        if len(devices['devices']) > 0:
            device_id = devices['devices'][0]['id']
            self.sp.start_playback(device_id=device_id, uris=[song_uri])
        else:
            print("No active devices found on Spotify.")
            try:
                subprocess.Popen(["spotify"])
                time.sleep(5)  # Wait for Spotify to open (adjust the delay if needed)
                devices = self.sp.devices()
                if len(devices['devices']) > 0:
                    device_id = devices['devices'][0]['id']
                    self.sp.start_playback(device_id=device_id, uris=[song_uri])
                else:
                    print("No active devices found on Spotify after opening the application.")
            except FileNotFoundError:
                print("Spotify application not found. Please make sure Spotify is installed on your computer.")

    def set_alarm(self):
        alarm_time = self.entry_time.get()
        ampm = self.var_ampm.get()

        # Format the alarm time as HH:MM:SS
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alarm_time = f"{current_time.split()[0]} {alarm_time}:00 {ampm}"

        # Get the time difference between current time and alarm time in seconds
        time_difference = (datetime.datetime.strptime(alarm_time, "%Y-%m-%d %I:%M:%S %p") -
                           datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")).total_seconds()

        if time_difference <= 0:
            print("Invalid alarm time. Please enter a future time.")
            return

        print(f"Alarm set for {alarm_time}.")

        # Wait for the specified time before playing the song
        time.sleep(time_difference)

        # Play the selected song
        selected_index = self.combo_results.current()
        if selected_index >= 0:
            selected_track = self.results[selected_index]
            selected_uri = selected_track['uri']
            self.play_song(selected_uri)
        else:
            print("No song selected.")

    def run(self):
        self.window.mainloop()


if __name__ == '__main__':
    app = AlarmApp()
    app.run()