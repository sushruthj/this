from pydub import AudioSegment
import os

def rip_audio_cd(source_path, output_path):
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)

    # Load the audio CD
    audio_cd = AudioSegment.from_file(source_path, format='cdda')

    # Get the number of audio tracks on the CD
    num_tracks = len(audio_cd)
    print(f"Found {num_tracks} tracks on the audio CD.")

    # Rip each track as a separate audio file
    for track_num, track in enumerate(audio_cd):
        # Convert track number to 2-digit format (e.g., 01, 02)
        track_num_str = str(track_num + 1).zfill(2)

        # Set the output file name based on track number
        output_file = os.path.join(output_path, f"Track{track_num_str}.mp3")

        # Export the track as an MP3 file
        track.export(output_file, format="mp3")

        print(f"Track {track_num_str} ripped successfully.")

# Usage example
source_cd_path = "/dev/sr0"   # The path to your audio CD device
output_folder = "./home/jay/Everything/Music"   # The path to the folder where you want to save the ripped audio files

rip_audio_cd(source_cd_path, output_folder)
