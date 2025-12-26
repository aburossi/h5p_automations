# ================================================
# FILE: JR/utils_image_gen.py
# ================================================
import os
import requests
import cv2
import numpy as np
import json
import textwrap
import re
import logging
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional: German Hyphenation
try:
    import pyphen
    dic = pyphen.Pyphen(lang='de')
    HAS_PYPHEN = True
except ImportError:
    HAS_PYPHEN = False

# --- Configuration Constants ---
IMAGE_SIZE = 1080
MAX_FONT_SIZE = 140
MIN_FONT_SIZE = 60
PADDING = 40

# --- Utilities ---
def clean_html(raw_html):
    if not raw_html: return "Unknown"
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', str(raw_html)).strip()

def extract_year(date_str):
    if not date_str: return "Unknown"
    match = re.search(r'\d{4}', str(date_str))
    return match.group(0) if match else "Unknown"

def extract_version(license_text):
    if not license_text: return ""
    match = re.search(r'\d\.\d', str(license_text))
    return match.group(0) if match else ""

def ensure_directory(file_path):
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

# --- Wikimedia & Image Logic ---
def get_wikimedia_data(search_term, num_results=1):
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrnamespace": "6", "gsrlimit": str(num_results + 3),
        "gsrsearch": f"{search_term} filetype:bitmap",
        "prop": "imageinfo", "iiprop": "url|extmetadata"
    }
    results = []
    try:
        response = requests.get(url, params=params, headers={"User-Agent": "MyBot/1.0"}, timeout=10)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        
        for _, page in pages.items():
            image_info = page.get("imageinfo", [])
            if image_info:
                info = image_info[0]
                meta = info.get("extmetadata", {})
                results.append({
                    "url": info.get("url"),
                    "title": clean_html(meta.get("ObjectName", {}).get("value", page.get("title", "Unknown"))),
                    "author": clean_html(meta.get("Artist", {}).get("value", "Unknown")),
                    "year": extract_year(meta.get("DateTime", {}).get("value", "Unknown")),
                    "license": meta.get("LicenseShortName", {}).get("value", "Unknown"),
                    "version": extract_version(meta.get("LicenseShortName", {}).get("value", "Unknown")),
                    "source": info.get("descriptionurl", info.get("url"))
                })
    except Exception as e:
        logger.error(f"Error searching Wikimedia for {search_term}: {e}")
    return results[:num_results]

def download_image_as_cv2(url):
    try:
        resp = requests.get(url, headers={"User-Agent": "MyBot/1.0"}, timeout=10)
        if resp.status_code == 200:
            image_array = np.asarray(bytearray(resp.content), dtype=np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            if img is not None and img.shape[2] == 3:
                 return img
    except Exception:
        pass
    return None

def resize_and_crop_center(img, target_w, target_h):
    h, w, _ = img.shape
    scale = max(target_w / w, target_h / h)
    resized_w = int(w * scale)
    resized_h = int(h * scale)
    resized = cv2.resize(img, (resized_w, resized_h), interpolation=cv2.INTER_AREA)
    start_x = (resized_w - target_w) // 2
    start_y = (resized_h - target_h) // 2
    return resized[start_y:start_y+target_h, start_x:start_x+target_w]

def create_collage(image_list, target_size, n_grid):
    if not image_list:
        return np.full((target_size, target_size, 3), 200, dtype=np.uint8)
    
    if n_grid == 4: rows, cols = 2, 2
    elif n_grid == 16: rows, cols = 4, 4
    elif n_grid == 8: rows, cols = 2, 4
    else: rows, cols = 2, 2

    cell_w = target_size // cols
    cell_h = target_size // rows
    
    collage_canvas = np.full((rows * cell_h, cols * cell_w, 3), 240, dtype=np.uint8) 

    img_idx = 0
    for r in range(rows):
        for c in range(cols):
            y_start = r * cell_h; y_end = y_start + cell_h
            x_start = c * cell_w; x_end = x_start + cell_w
            
            if img_idx < len(image_list):
                cell_img = resize_and_crop_center(image_list[img_idx], cell_w, cell_h)
                collage_canvas[y_start:y_end, x_start:x_end] = cell_img
                img_idx += 1
            else:
                cv2.rectangle(collage_canvas, (x_start, y_start), (x_end, y_end), (200,200,200), -1)

    return resize_and_crop_center(collage_canvas, target_size, target_size)

def smart_crop_auto(img, target_size):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    h, w, _ = img.shape
    if len(faces) == 0:
        center_x, center_y = w // 2, h // 2
    elif len(faces) == 1:
        x, y, fw, fh = max(faces, key=lambda b: b[2] * b[3])
        center_x, center_y = x + fw // 2, y + fh // 2
    else:
        min_x = min([f[0] for f in faces]); min_y = min([f[1] for f in faces])
        max_x = max([f[0] + f[2] for f in faces]); max_y = max([f[1] + f[3] for f in faces])
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2

    crop_dim = min(h, w)
    half_crop = crop_dim // 2
    
    start_x = max(0, center_x - half_crop)
    start_y = max(0, center_y - half_crop)
    end_x = start_x + crop_dim; end_y = start_y + crop_dim
    
    if end_x > w: end_x, start_x = w, w - crop_dim
    if end_y > h: end_y, start_y = h, h - crop_dim
    if start_x < 0: start_x = 0; start_y = 0
        
    cropped = img[int(start_y):int(end_y), int(start_x):int(end_x)]
    return cv2.resize(cropped, (target_size, target_size), interpolation=cv2.INTER_AREA)

def create_text_image(text, size):
    img = Image.new('RGB', (size, size), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    current_font_size = MAX_FONT_SIZE
    final_lines = []
    final_font = None

    # Phase 1: Try shrinking
    while current_font_size >= MIN_FONT_SIZE:
        try: font = ImageFont.truetype("arial.ttf", current_font_size) 
        except: font = ImageFont.load_default()

        avg_char_width = current_font_size * 0.55 
        available_width = size - (PADDING * 2)
        chars_per_line = int(available_width / avg_char_width)
        lines = textwrap.wrap(text, width=chars_per_line, break_long_words=False)
        
        longest_word_len = max([len(w) for w in text.split()]) if text else 0
        pixel_width_longest = longest_word_len * avg_char_width
        line_height = current_font_size * 1.2
        total_text_height = len(lines) * line_height
        
        if total_text_height <= (size - PADDING * 2) and pixel_width_longest <= available_width:
            final_lines = lines; final_font = font; break
        else:
            current_font_size -= 5
            
    # Phase 2: Hyphenate
    if final_font is None:
        try: final_font = ImageFont.truetype("arial.ttf", MIN_FONT_SIZE)
        except: final_font = ImageFont.load_default()
        
        avg_char_width = MIN_FONT_SIZE * 0.55
        available_width = size - (PADDING * 2)
        chars_per_line = int(available_width / avg_char_width)
        
        if HAS_PYPHEN:
            processed_text_parts = []
            for word in text.split():
                if len(word) * avg_char_width > available_width:
                    processed_text_parts.append(dic.inserted(word, hyphen='-'))
                else:
                    processed_text_parts.append(word)
            processed_text = " ".join(processed_text_parts)
        else:
            processed_text = text
            
        final_lines = textwrap.wrap(processed_text, width=chars_per_line, break_long_words=True)

    line_height = (final_font.size if hasattr(final_font, 'size') else MIN_FONT_SIZE) * 1.2
    total_text_height = len(final_lines) * line_height
    current_y = (size - total_text_height) // 2
    
    for line in final_lines:
        bbox = draw.textbbox((0, 0), line, font=final_font)
        text_width = bbox[2] - bbox[0]
        x_pos = (size - text_width) // 2
        draw.text((x_pos, current_y), line, font=final_font, fill=(0, 0, 0))
        current_y += line_height
        
    return img

# --- Main Generator Function ---
def generate_memory_assets(cards_input, output_dir, use_collage=False, collage_count=4):
    """
    cards_input: list of dicts [{'prompt': 'Paris', 'match_text': 'Hauptstadt'}, ...]
    output_dir: pathlib.Path object where files will be saved
    returns: List of pairs formatted for the H5P generator, and list of file paths created.
    """
    
    generated_h5p_cards = []
    generated_file_paths = []
    
    # Folder setup
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    for idx, card in enumerate(cards_input):
        prompt = card.get('prompt', 'Unknown')
        match_text = card.get('match_text', '')
        
        # Define Filenames
        safe_prompt = "".join([c for c in prompt if c.isalnum()]).lower()
        if not safe_prompt: safe_prompt = f"card_{idx}"
        
        img_filename = f"{safe_prompt}_{idx}_img.jpg"
        txt_filename = f"{safe_prompt}_{idx}_txt.jpg"
        
        img_path = images_dir / img_filename
        txt_path = images_dir / txt_filename

        # --- 1. Image Generation (Wiki + OpenCV) ---
        needed = collage_count if use_collage else 1
        data_list = get_wikimedia_data(prompt, num_results=needed)
        
        valid_images = []
        copyright_info = {"license": "U"} # Default
        
        for item in data_list:
            img_cv = download_image_as_cv2(item['url'])
            if img_cv is not None:
                valid_images.append(img_cv)
                # Take copyright from first valid image
                if len(valid_images) == 1:
                    copyright_info = {
                        "license": item['license'],
                        "title": item['title'],
                        "author": item['author'],
                        "year": item['year'],
                        "source": item['source'],
                        "version": item['version']
                    }

        # Create/Save Image
        if use_collage:
            final_img = create_collage(valid_images, IMAGE_SIZE, collage_count)
            cv2.imwrite(str(img_path), final_img)
        else:
            if valid_images:
                final_img = smart_crop_auto(valid_images[0], IMAGE_SIZE)
                cv2.imwrite(str(img_path), final_img)
            else:
                # Fallback blank
                blank_img = np.full((IMAGE_SIZE, IMAGE_SIZE, 3), 200, dtype=np.uint8)
                cv2.imwrite(str(img_path), blank_img)
                copyright_info = {"license": "U", "author": "Generated"}

        generated_file_paths.append(img_path)

        # --- 2. Text Generation (PIL) ---
        text_img = create_text_image(match_text, IMAGE_SIZE)
        text_img.save(txt_path)
        generated_file_paths.append(txt_path)

        # --- 3. Build Dict for H5P Generator ---
        pair_entry = {
            "image": {
                "path": f"images/{img_filename}", # Relative path for ZIP
                "mime": "image/jpeg",
                "imageAlt": prompt,
                "description": prompt,
                "copyright": copyright_info
            },
            "match": { # "match" key for the second card in the pair (the text card)
                 # In Memory Game H5P, logic usually expects a pair. 
                 # My existing generator handles pairs logic. Here we map it so utils knows it's an image card.
                 "path": f"images/{txt_filename}",
                 "mime": "image/jpeg",
                 "matchAlt": match_text
            }
        }
        
        # IMPORTANT: The current booklet_generator expects a flattened list or pairs?
        # Looking at booklet_generator.py -> create_memory_game iterates cards by step of 2.
        # It expects: item_a = raw_cards_list[i], item_b = raw_cards_list[i+1]
        # So we append TWO entries to the list per loop.
        
        # Entry 1: The Photo
        generated_h5p_cards.append({
            "image": pair_entry["image"]
        })
        # Entry 2: The Text Image
        generated_h5p_cards.append({
            "image": pair_entry["match"]
        })
        
    return generated_h5p_cards, generated_file_paths