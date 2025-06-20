#!/usr/bin/env python3
"""
Simple test script to check if pygame sound is working
"""

import os
import sys
import pygame
import time

def main():
    print("Pygame Sound Test")
    print("-----------------")
    
    # Initialize pygame
    pygame.init()
    print(f"Pygame initialized: {pygame.get_init()}")
    
    # Initialize mixer with different settings to try
    pygame.mixer.quit()
    pygame.mixer.init(44100, -16, 2, 512)
    print(f"Mixer initialized: {pygame.mixer.get_init()}")
    
    # Set up paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_sounds_dir = os.path.join(base_dir, "snake_game_assets", "sounds")
    user_sounds_dir = os.path.join(base_dir, "sounds")
    
    print(f"\nChecking directories:")
    print(f"Base directory: {base_dir}")
    print(f"Default sounds directory exists: {os.path.exists(default_sounds_dir)}")
    print(f"User sounds directory exists: {os.path.exists(user_sounds_dir)}")
    
    # List sound files
    print("\nListing sound files in default directory:")
    if os.path.exists(default_sounds_dir):
        files = os.listdir(default_sounds_dir)
        for file in files:
            print(f"  - {file}")
    else:
        print("  Directory not found")
    
    print("\nListing sound files in user directory:")
    if os.path.exists(user_sounds_dir):
        files = os.listdir(user_sounds_dir)
        for file in files:
            print(f"  - {file}")
    else:
        print("  Directory not found")
    
    # Try to load and play sounds
    print("\nTrying to load and play sounds:")
    
    # Function to try loading a sound
    def try_sound(filename, directory):
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            print(f"  Found {filename} at {path}")
            try:
                sound = pygame.mixer.Sound(path)
                print(f"  Successfully loaded {filename}")
                print(f"  Playing {filename}...")
                sound.set_volume(1.0)  # Maximum volume
                sound.play()
                time.sleep(1)  # Wait for sound to play
                print(f"  Finished playing {filename}")
                return True
            except Exception as e:
                print(f"  Error loading/playing {filename}: {e}")
        else:
            print(f"  {filename} not found at {path}")
        return False
    
    # Try eat sound
    print("\nTesting eat sound:")
    if not try_sound("eat.wav", default_sounds_dir):
        try_sound("eat.mp3", default_sounds_dir)
    
    # Try game over sound
    print("\nTesting game over sound:")
    if not try_sound("game_over.wav", default_sounds_dir):
        try_sound("game_over.mp3", default_sounds_dir)
    
    # Try powerup sound
    print("\nTesting powerup sound:")
    if not try_sound("powerup.wav", default_sounds_dir):
        try_sound("powerup.mp3", default_sounds_dir)
    
    # Try background music
    print("\nTesting background music:")
    bg_path = os.path.join(default_sounds_dir, "background.mp3")
    if os.path.exists(bg_path):
        print(f"  Found background.mp3 at {bg_path}")
        try:
            pygame.mixer.music.load(bg_path)
            print("  Successfully loaded background music")
            print("  Playing background music...")
            pygame.mixer.music.set_volume(1.0)  # Maximum volume
            pygame.mixer.music.play()
            time.sleep(3)  # Play for 3 seconds
            pygame.mixer.music.stop()
            print("  Finished playing background music")
        except Exception as e:
            print(f"  Error with background music: {e}")
    else:
        print(f"  background.mp3 not found at {bg_path}")
    
    print("\nSound test complete")

if __name__ == "__main__":
    main()
