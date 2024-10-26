import pygame
import numpy as np
import librosa
import tkinter as tk
from tkinter import filedialog

# Function to load an MP3 file
def load_mp3_file():
    # Open a file dialog to select an MP3 file
    file_path = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
    if file_path:
        return file_path
    return None

# Initialize Pygame
pygame.init()

# Initialize Tkinter
root = tk.Tk()
root.withdraw()  # Hide the root window

# Load an MP3 file
filename = load_mp3_file()  # Prompt user to select an MP3 file
if filename:
    y, sr = librosa.load(filename, sr=None)

    # Set up the display
    screen_width = 800
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Circular Frequency Visualization')

    # Load the Bobobyte logo
    logo_image = pygame.image.load('bobabytelogo.png')  # Replace with your logo file path
    logo_image = pygame.transform.scale(logo_image, (300, 250))  # Scale the image down to 100x100 pixels
    logo_rect = logo_image.get_rect(center=(screen_width // 2, screen_height // 2))  # Center the logo
    background = pygame.image.load('backgroundforhacakthon.jpg')
    background = pygame.transform.scale(background, (screen_width, screen_height))
    background_rect = background.get_rect(center=(screen_width // 2, screen_height // 2))
    # Initialize Pygame mixer
    pygame.mixer.init(frequency=sr, size=-16, channels=2)
    pygame.mixer.music.load(filename)

    # Start playing the music
    pygame.mixer.music.play()

    # Main loop
    running = True
    clock = pygame.time.Clock()

    # Number of frequency bands (bars)
    num_bands = 32
    bar_length = 225  # Maximum length of the bars
    circle_radius = 80  # Smaller default radius for the central circle

    # Play/Pause variables
    is_playing = True

    # Color variable (single color slider)
    circle_color = [255, 255, 255]  # RGB for the central circle

    # Function to get frequency magnitudes
    def get_frequency_magnitudes(y, sr, current_pos):
        current_sample = int(current_pos * sr)
        window_size = 1024
        start = max(0, current_sample - window_size // 2)
        end = min(len(y), start + window_size)
        current_window = y[start:end]
        fft_result = np.fft.fft(current_window)
        magnitudes = np.abs(fft_result[:window_size // 2])  # Take the positive frequencies
        return magnitudes

    # Function to draw the play/pause button
    def draw_play_pause_button(x, y, width, height):
        if is_playing:
            pygame.draw.rect(screen, (0, 255, 0), (x, y, width, height))  # Green for play
            font = pygame.font.Font(None, 36)
            text = font.render("Pause", True, (0, 0, 0))
        else:
            pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height))  # Red for pause
            font = pygame.font.Font(None, 36)
            text = font.render("Play", True, (255, 255, 255))

        screen.blit(text, (x + width // 2 - text.get_width() // 2, y + height // 2 - text.get_height() // 2))

    # Function to draw the seek bar
    def draw_seek_bar(x, y, width, current_pos):
        pygame.draw.rect(screen, (200, 200, 200), (x, y, width, 20))  # Background of seek bar
        pygame.draw.rect(screen, (0, 255, 0), (x, y, width * (current_pos / total_duration), 20))  # Filled part

    # Function to draw a color slider
    # def draw_color_slider(x, y, width, color_value, label):
    #     pygame.draw.rect(screen, (200, 200, 200), (x, y, width, 20))  # Background of the slider
    #     pygame.draw.rect(screen, (color_value, color_value, color_value), (x, y, width * (color_value / 255), 20))  # Filled part
    #     font = pygame.font.Font(None, 24)
    #     text = font.render(label, True, (255, 255, 255))
    #     screen.blit(text, (x, y - 25))

    # Get total duration of the audio
    total_duration = librosa.get_duration(y=y, sr=sr)

    # Initialize variables for visualization
    last_normalized_magnitudes = np.zeros(num_bands)
    # Generate the waveform data
    waveform = y / np.max(np.abs(y))  # Normalize the waveform to fit within the screen height

    # Function to draw the waveform
    def draw_waveform():
        waveform_color = (255, 255, 255)  # Cyan color for the waveform
        waveform_height = screen_height // 4  # Height of the waveform area
        waveform_center_y = screen_height // 2  # Center of the waveform area

        # Calculate the current position in the waveform
        current_pos = pygame.mixer.music.get_pos() / 1000  # Convert milliseconds to seconds
        current_sample = int(current_pos * sr)
        window_size = 1024
        start = max(0, current_sample - window_size // 2)
        end = min(len(waveform), start + window_size)
        current_window = waveform[start:end]

        for i in range(len(current_window) - 1):
            x1 = int(i / len(current_window) * screen_width)
            y1 = int(waveform_center_y + current_window[i] * waveform_height)
            x2 = int((i + 1) / len(current_window) * screen_width)
            y2 = int(waveform_center_y + current_window[i + 1] * waveform_height)
            pygame.draw.line(screen, waveform_color, (x1, y1), (x2, y2), 1)

    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Check if play/pause button is clicked
                if 50 <= mouse_x <= 150 and 720 <= mouse_y <= 760:
                    is_playing = not is_playing
                    if is_playing:
                        pygame.mixer.music.unpause()
                    else:
                        pygame.mixer.music.pause()
                # Check if seek bar is clicked
                if 200 <= mouse_x <= 600 and 720 <= mouse_y <= 740:  # Adjusted height for the seek bar
                    seek_pos = (mouse_x - 200) / 400 * total_duration  # Calculate the position in seconds
                    pygame.mixer.music.set_pos(seek_pos)
                # Check if color slider is clicked
                if 50 <= mouse_x <= 250:
                    if 650 <= mouse_y <= 670:  # Color slider
                        circle_color[0] = int((mouse_x - 50) / 200 * 255)  # Adjust Red
                    elif 680 <= mouse_y <= 700:  # Color slider
                        circle_color[1] = int((mouse_x - 50) / 200 * 255)  # Adjust Green
                    elif 710 <= mouse_y <= 730:  # Color slider
                        circle_color[2] = int((mouse_x - 50) / 200 * 255)  # Adjust Blue
                # Check if size slider is clicked
                if 300 <= mouse_x <= 600 and 650 <= mouse_y <= 670:
                    circle_radius = int((mouse_x - 300) / 300 * 300)  # Size from 0 to 300

        # Clear the screen
        #screen.fill((0, 0, 0))

        #Draw background image
        screen.blit(background,background_rect)
        # Draw the waveform in the background
        draw_waveform()
        # Calculate the frequency magnitudes only if music is playing
        if pygame.mixer.music.get_busy() or is_playing:  # Check if music is still playing
            current_pos = pygame.mixer.music.get_pos() / 1000  # Convert milliseconds to seconds
            magnitudes = get_frequency_magnitudes(y, sr, current_pos)

            # Normalize and scale the magnitudes for drawing
            magnitudes = magnitudes[:num_bands]  # Limit to the number of bands
            max_magnitude = np.max(magnitudes)
            normalized_magnitudes = (magnitudes / max_magnitude) * bar_length if max_magnitude > 0 else np.zeros(num_bands)

            # Store the last normalized magnitudes to keep the visualizer visible when paused
            last_normalized_magnitudes = normalized_magnitudes.copy()

            # Draw bars around the circle
            center_x, center_y = screen_width // 2, screen_height // 2
            for i in range(num_bands):
                angle = (i / num_bands) * np.pi  # Calculate angle for each band (mirror on half)
                bar_length_scaled = last_normalized_magnitudes[i]  # Use the last magnitudes when paused

                # Calculate the starting position of the bar on the circumference of the circle
                start_x = center_x + circle_radius * np.cos(angle)
                start_y = center_y + circle_radius * np.sin(angle)

                # Calculate the end position of the bar
                end_x = start_x + bar_length_scaled * np.cos(angle)
                end_y = start_y + bar_length_scaled * np.sin(angle)

                # Color the bar based on its index
                color = (255, int(255 * (i / num_bands)), 0)  # Gradient from red to yellow
                pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 5)

                # Mirror the bars on the other half
                mirrored_angle = (i / num_bands) * -np.pi  # Mirror angle
                start_x_mirrored = center_x + circle_radius * np.cos(mirrored_angle)
                start_y_mirrored = center_y + circle_radius * np.sin(mirrored_angle)

                end_x_mirrored = start_x_mirrored + bar_length_scaled * np.cos(mirrored_angle)
                end_y_mirrored = start_y_mirrored + bar_length_scaled * np.sin(mirrored_angle)

                pygame.draw.line(screen, color, (start_x_mirrored, start_y_mirrored), (end_x_mirrored, end_y_mirrored), 5)

            # Draw the seek bar
            draw_seek_bar(200, 720, 400, current_pos)

        # Draw the play/pause button
        draw_play_pause_button(50, 720, 100, 40)

        # Draw color slider
        #draw_color_slider(50, 650, 200, circle_color[0], "Color Slider (Red to Blue)")

        


        # Draw size slider
        # pygame.draw.rect(screen, (200, 200, 200), (300, 650, 300, 20))  # Background of size slider
        # pygame.draw.rect(screen, (255, 255, 255), (300, 650, circle_radius, 20))  # Filled part for size
        # font = pygame.font.Font(None, 24)
        # text = font.render("Circle Size", True, (255, 255, 255))
        # screen.blit(text, (300, 620))

        # Draw the logo image in the center
        screen.blit(logo_image, logo_rect)  # Draw the logo at the center
        #Draw the background image
        
        # Update the display
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 frames per second

        

    # Clean up
    pygame.quit()
else:
    print("No file selected. Exiting...")