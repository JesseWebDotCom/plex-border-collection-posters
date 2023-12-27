import argparse
import os
from plexapi.server import PlexServer
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import re

# Constants
PLEX_URL = "http://127.0.0.1:32400"  # Replace with your actual plex url
PLEX_TOKEN = "acb123xyzblahreplaceme"  # Replace with your actual plex token

def create_directory(directory_path):
    os.makedirs(directory_path, exist_ok=True)

def calculate_border_size(width, percentage):
    return round(width * (percentage / 100))

def sanitize_file_name(file_name):
    # Remove /
    file_name = file_name.replace('/', '')

    # Remove :
    file_name = file_name.replace(':', '')

    # Define a regular expression to match invalid characters including | and /
    invalid_chars = re.compile(r'[<>"\\|?*\x00-\x1F]')

    # Replace invalid characters with underscores
    return re.sub(invalid_chars, '_', file_name)

def download_poster(item, title):
    poster_url = f"{PLEX_URL}{item.thumb}"

    # Download the poster image
    print(f"{title:<50}{'DOWNLOADING':<15}", end="\r", flush=True)
    response = requests.get(poster_url, headers={"X-Plex-Token": PLEX_TOKEN})
    original_image = Image.open(BytesIO(response.content))

    return resize_image(original_image)

def resize_image(original_image):
    # Calculate aspect ratio
    original_width, original_height = original_image.size

    # Calculate the desired width for a 3:2 aspect ratio based on the original height
    desired_width = int((2 / 3) * original_height)

    # Calculate the corresponding height for the 3:2 aspect ratio
    desired_height = int(desired_width * (3 / 2))

    # Check if resizing is necessary
    if original_width == desired_width and original_height == desired_height:
        return original_image  # Return the original image if dimensions are correct

    # Calculate the amount to crop from each side
    crop_width_amount = (original_width - desired_width) // 2
    crop_height_amount = (original_height - desired_height) // 2

    # Crop the image to achieve the desired aspect ratio
    cropped_img = original_image.crop((crop_width_amount, crop_height_amount, original_width - crop_width_amount, original_height - crop_height_amount))

    return cropped_img

def save_original(original_path, original_image):
    # Save the original poster to the temp folder
    original_image.save(original_path, format='PNG')

def get_paths(title, asset_directory):
    original_path = os.path.join(asset_directory, "originals", f"{title}.png")
    modified_path = os.path.join(asset_directory, "modified", f"{title}.png")
    return original_path, modified_path

def draw_border(image, border_size, outer_color, inner_color, inner_size):
    # Draw the outer border
    draw = ImageDraw.Draw(image)
    width, height = image.size
    draw.rectangle([0, 0, width, height], outline=outer_color, width=border_size)

    # Draw the inner border
    draw.rectangle([border_size, border_size, width - border_size, height - border_size], outline=inner_color, width=inner_size)

def process_upload(original_image, modified_path, title, outer_border_percent, inner_border_percent, outer_border_color, inner_border_color):
    global uploaded_count, error_count  # Declare global variables

    # Calculate the border sizes based on percentages
    width, height = original_image.size
    outer_border_size = calculate_border_size(width, outer_border_percent)
    inner_border_size = calculate_border_size(width, inner_border_percent)

    # Create a new image with the original size
    bordered_image = Image.new("RGB", (width, height), "white")

    # Paste the original image onto the new image
    bordered_image.paste(original_image, (0, 0))

    # Draw borders on the new image
    draw_border(bordered_image, outer_border_size, outer_border_color, inner_border_color, inner_border_size)

    # Save the modified poster to the temp folder
    bordered_image.save(modified_path, format='PNG')
    print(f"{title:<50}{'UPLOADED':<15}", end="\r", flush=True)
    uploaded_count += 1

def process_collection(item, action, asset_directory, outer_border_percent, inner_border_percent, outer_border_color, inner_border_color):
    global downloaded_count, modified_count, error_count, skipped_count  # Declare global variables

    title = sanitize_file_name(item.title)

    if action =="list":
        print(f"\n{title:<50}{'SKIPPED':<15}Action is list", end="\r", flush=True)
        skipped_count += 1
        return

    print(f"\n{title:<50}{'PROCESSING':<15}", end="\r", flush=True)

    # Get the collection poster URL
    if item.thumb is None:
        print(f"{title:<50}{'SKIPPED':<15}No poster found", end="\r", flush=True)
        skipped_count += 1
        return

    # Calculate the paths for original and modified images
    create_directory(os.path.join(asset_directory, "originals"))
    create_directory(os.path.join(asset_directory, "modified"))
    original_path, modified_path = get_paths(title, asset_directory)

    # Check if the modified file already exists
    if os.path.exists(modified_path):
        print(f"{title:<50}{'SKIPPED':<15}Modified already exists", end="\r", flush=True)
        skipped_count += 1
        return

    # Check if the original already exists
    if os.path.exists(original_path):
        original_image = Image.open(original_path)
    else:
        try:
            print(f"{title:<50}{'DOWNLOADING':<15}", end="\r", flush=True)
            original_image = download_poster(item, title)
            save_original(original_path, original_image)
            downloaded_count += 1
        except Exception as e:
            print(f"{title:<50}{'ERRORED':<15}{'Downloading: ' + str(e).title()}", end="\r", flush=True)
            error_count += 1
            return

    # Draw borders around the original image
    if action == "upload":
        try:
            print(f"{title:<50}{'UPLOADING':<15}", end="\r", flush=True)
            process_upload(original_image, modified_path, title, outer_border_percent, inner_border_percent, outer_border_color, inner_border_color)
            modified_count += 1
        except Exception as e:
            print(f"{title:<50}{'ERRORED':<15}{'Uploading: ' + str(e).title()}", end="\r", flush=True)
            error_count += 1
       
# Global counters
downloaded_count = 0
modified_count = 0
uploaded_count = 0
error_count = 0
skipped_count = 0

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Download and modify Plex collection posters.")
parser.add_argument("--action", choices=["download", "upload", "list"], default="download", nargs="?", help="Action to specify the actions to be taken.")
parser.add_argument("--library-name", required=True, help="Name of the Plex library.")
parser.add_argument("--asset-directory", required=True, help="Path to the asset directory.")
parser.add_argument("--outer-border-percent", type=float, default=2, help="Percentage of outer border size relative to the image width.")
parser.add_argument("--inner-border-percent", type=float, default=1, help="Percentage of inner border size relative to the image width.")
parser.add_argument("--outer-border-color", default="white", help="Color of the outer border.")
parser.add_argument("--inner-border-color", default="black", help="Color of the inner border.")
args = parser.parse_args()

# Print script arguments
print("Script Arguments:")
print(f"  Action: {args.action}")
print(f"  Library Name: {args.library_name}")
print(f"  Asset Directory: {args.asset_directory}")
print(f"  Outer Border Percent: {args.outer_border_percent}")
print(f"  Inner Border Percent: {args.inner_border_percent}")
print(f"  Outer Border Color: {args.outer_border_color}")
print(f"  Inner Border Color: {args.inner_border_color}")
print("")

# Normalize the asset directory path
args.asset_directory = os.path.normpath(args.asset_directory)

# Create asset directory as needed
create_directory(args.asset_directory)

# Connect to Plex server
plex = PlexServer(PLEX_URL, PLEX_TOKEN)

# Get library and collection items
lib = next((s for s in plex.library.sections() if s.title == args.library_name), None)
items = lib.search(libtype="collection")

# Process each collection item
print("Processing collections:")
print('_' * 100)

for collection in items:
    process_collection(collection, args.action, args.asset_directory, args.outer_border_percent, args.inner_border_percent, args.outer_border_color, args.inner_border_color)

# Print total counts
print("")
print('_' * 100)
print("\nTotal Counts:")
print(f"  Collections: {len(items)}")
print(f"    Skipped: {skipped_count}")
print(f"    Modified: {modified_count}")
print(f"      Downloaded: {downloaded_count}")
print(f"      Uploaded: {uploaded_count}")
print(f"    Errors: {error_count}")
print("")
print("Done")
