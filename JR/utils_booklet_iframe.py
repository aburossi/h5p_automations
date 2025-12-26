import uuid
import zipfile
import io
import logging
import json
from pathlib import Path
from PIL import Image  # Requires: pip install Pillow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Constants ---
MAX_IMAGE_SIZE_BYTES = 1 * 1024 * 1024   # Threshold: 1 MB
TARGET_IMAGE_SIZE_BYTES = 500 * 1024     # Target: 500 KB

def generate_uuid():
    return str(uuid.uuid4())

# --- Image Processing ---
def compress_image_if_needed(image_data_bytes: bytes, original_filename: str) -> bytes:
    """
    Checks if image data > 1MB. If so, resizes dimensions iteratively 
    using Pillow until size is approx < 500KB.
    Keeps the original file format (PNG/JPG) to ensure JSON references remain valid.
    """
    # If it's already small enough, just return original data
    if len(image_data_bytes) <= MAX_IMAGE_SIZE_BYTES:
        return image_data_bytes

    logger.info(f"Compressing image {original_filename} (Current: {len(image_data_bytes)/1024:.2f} KB)...")

    try:
        # Load image from bytes
        img = Image.open(io.BytesIO(image_data_bytes))
        
        # Determine format based on filename extension (keep original format)
        ext = Path(original_filename).suffix.lower()
        fmt = 'PNG' if ext == '.png' else 'JPEG'
        
        # Setup for iteration
        current_img = img
        output_buffer = io.BytesIO()
        scale_factor = 0.9 # Reduce dimensions by 10% each step

        iteration = 0
        while True:
            iteration += 1
            output_buffer.seek(0)
            output_buffer.truncate(0)
            
            # Save current version to buffer
            # Optimize=True helps both formats. Quality only affects JPEG.
            kwargs = {'optimize': True}
            if fmt == 'JPEG': kwargs['quality'] = 85
                
            current_img.save(output_buffer, format=fmt, **kwargs)
            
            current_size = output_buffer.tell()
            
            # Check if goal reached
            if current_size <= TARGET_IMAGE_SIZE_BYTES:
                break 

            # Safety break if dimensions get too small or too many iterations
            if current_img.width < 300 or current_img.height < 300 or iteration > 10:
                logger.warning(f"Could not compress {original_filename} fully to target size. Stopping at {current_size/1024:.2f} KB.")
                break

            # Calculate new dimensions for next iteration
            new_width = int(current_img.width * scale_factor)
            new_height = int(current_img.height * scale_factor)
            
            # Resize (LANCZOS is good quality for downscaling)
            current_img = current_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
        compressed_data = output_buffer.getvalue()
        logger.info(f"Finished compressing {original_filename}. New size: {len(compressed_data)/1024:.2f} KB")
        return compressed_data

    except Exception as e:
        logger.error(f"Error compressing image {original_filename}: {e}")
        # Fallback: return original data if compression fails
        return image_data_bytes

# --- Text Processing ---
def recursive_replace_ss(data):
    """
    Recursively traverses a dictionary or list.
    If a string is found, replaces 'ß' with 'ss'.
    """
    if isinstance(data, str):
        return data.replace("ß", "ss")
    elif isinstance(data, dict):
        return {k: recursive_replace_ss(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursive_replace_ss(i) for i in data]
    else:
        return data

# --- H5P Mapping Utils ---
def parse_copyright_info(copyright_input):
    if not copyright_input:
        return {"license": "U"} 

    raw_license = copyright_input.get("license", "U")
    h5p_license = "U"
    h5p_version = copyright_input.get("version", "")

    if "CC BY-SA" in raw_license:
        h5p_license = "CC BY-SA"
        if not h5p_version and "4.0" in raw_license: h5p_version = "4.0"
        if not h5p_version and "3.0" in raw_license: h5p_version = "3.0"
    elif "CC BY" in raw_license or "Attribution" in raw_license:
        h5p_license = "CC BY"
        if not h5p_version: h5p_version = "4.0"
    elif "Public Domain" in raw_license or "CC0" in raw_license:
        h5p_license = "PD"
    elif "Copyright" in raw_license:
        h5p_license = "C"
    
    return {
        "license": h5p_license,
        "title": copyright_input.get("title", ""),
        "author": copyright_input.get("author", ""),
        "year": copyright_input.get("year", ""),
        "source": copyright_input.get("source", ""),
        "version": h5p_version
    }

def create_image_param(image_path_or_data):
    """
    Standardizes image parameter generation.
    """
    if not image_path_or_data:
        return None

    # Default values
    path = ""
    mime = "image/png"
    copyright_obj = {"license": "U"}

    if isinstance(image_path_or_data, str):
        path = image_path_or_data
        # Simple extension check for mime
        if path.lower().endswith('.jpg') or path.lower().endswith('.jpeg'):
            mime = "image/jpeg"
    else:
        path = image_path_or_data.get("path")
        mime = image_path_or_data.get("mime", "image/png")
        copyright_obj = parse_copyright_info(image_path_or_data.get("copyright"))

    if not path:
        return None

    return {
        "path": path,
        "mime": mime,
        "copyright": copyright_obj,
        "width": 50, "height": 50
    }

def map_drag_text_to_h5p(task_data):
    full_text = task_data.get("text_content", "")
    distractors = task_data.get("distractors", "")
    return {
        "library": "H5P.DragText 1.10",
        "subContentId": generate_uuid(),
        "metadata": {"contentType": "Drag the Words", "license": "U", "title": task_data.get("description", "Cloze")},
        "params": {
            "taskDescription": f"<p>{task_data.get('description', '')}</p>",
            "textField": full_text,
            "distractors": distractors,
            "behaviour": {"enableRetry": True, "enableSolutionsButton": False, "enableCheckButton": True, "instantFeedback": False},
            "checkAnswer": "Überprüfen", "submitAnswer": "Absenden", "tryAgain": "Wiederholen", "showSolution": "Lösung anzeigen",
            "scoreBarLabel": "Du hast :num von :total Punkten erreicht."
        }
    }

def map_questions_to_h5p_array(questions_in):
    out = []
    for q in questions_in:
        q_type = q.get("type")
        if q_type == "multichoice":
            out.append(map_mc_question(q))
        elif q_type == "truefalse":
            out.append(map_tf_question(q))
    return out

def map_mc_question(q):
    answers = []
    for a in q.get("answers", []):
        answers.append({
            "text": a.get("text"),
            "correct": a.get("correct"),
            "tipsAndFeedback": {
                "chosenFeedback": f"<div>{a.get('feedback','')}</div>",
                "notChosenFeedback": ""
            }
        })
    return {
        "library": "H5P.MultiChoice 1.16",
        "subContentId": generate_uuid(),
        "metadata": {"contentType": "Multiple Choice", "license": "U", "title": "MC"},
        "params": {
            "question": f"<p>{q.get('question')}</p>",
            "answers": answers,
            "behaviour": {"singleAnswer": True, "enableRetry": False, "enableCheckButton": True},
            "UI": {
                "checkAnswerButton": "Überprüfen", "showSolutionButton": "Lösung anzeigen",
                "tryAgainButton": "Wiederholen", "correctAnswer": "Richtige Antwort", "wrongAnswer": "Falsche Antwort"
            }
        }
    }

def map_tf_question(q):
    return {
        "library": "H5P.TrueFalse 1.8",
        "subContentId": generate_uuid(),
        "metadata": {"contentType": "True/False", "license": "U", "title": "TF"},
        "params": {
            "question": f"<p>{q.get('question')}</p>",
            "correct": "true" if q.get("correct") else "false",
            "behaviour": {
                "feedbackOnCorrect": q.get("feedback_correct", ""),
                "feedbackOnWrong": q.get("feedback_wrong", "")
            },
            "l10n": {"trueText": "Wahr", "falseText": "Falsch"}
        }
    }

# --- Packaging ---
def create_h5p_package(content_json_str: str, h5p_json_str: str, template_zip_path: str, extra_files: list = None):
    """
    extra_files: list of tuples/dicts -> [{"filename": "images/title.png", "data": bytes_obj}, ...]
    """
    if extra_files is None: extra_files = []
    
    try:
        with open(template_zip_path, 'rb') as f_template:
            template_bytes = f_template.read()
        
        in_memory_zip = io.BytesIO()
        
        with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as new_zip:
            # 1. Copy template files (excluding content.json and h5p.json)
            with zipfile.ZipFile(io.BytesIO(template_bytes), 'r') as template_zip_obj:
                for item in template_zip_obj.infolist():
                    if item.filename.lower() in ['content/content.json', 'h5p.json']:
                        continue
                    new_zip.writestr(item, template_zip_obj.read(item.filename))
            
            # 2. Write new JSONs
            new_zip.writestr('content/content.json', content_json_str.encode('utf-8'))
            new_zip.writestr('h5p.json', h5p_json_str.encode('utf-8'))

            # 3. Write extra files (images)
            for file_info in extra_files:
                filename = file_info["filename"]
                data = file_info["data"]
                # Ensure it sits in content/ folder if not specified
                if not filename.startswith("content/"):
                    target_path = f"content/{filename}"
                else:
                    target_path = filename
                
                new_zip.writestr(target_path, data)

        in_memory_zip.seek(0)
        return in_memory_zip.getvalue()
    except Exception as e:
        logger.error(f"Error zipping: {e}")
        return None