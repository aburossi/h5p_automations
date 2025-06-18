import json
import uuid
import zipfile
import io
import logging
from urllib.parse import urlparse, parse_qs
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_uuid():
    """Generates a unique UUID."""
    return str(uuid.uuid4())

def extract_youtube_id(url: str) -> str | None:
    """
    Extracts YouTube video ID from various URL formats.
    Handles standard, short, and embed URLs.
    """
    if not url:
        return None
    try:
        parsed_url = urlparse(url)
        if "youtube.com" in parsed_url.hostname:
            if "v" in parse_qs(parsed_url.query):
                return parse_qs(parsed_url.query)["v"][0]
            if parsed_url.path.startswith("/embed/"):
                return parsed_url.path.split("/embed/")[1].split("?")[0]
            if parsed_url.path.startswith("/live/"): # Handle live URLs
                return parsed_url.path.split("/live/")[1].split("?")[0]
            if parsed_url.path.startswith("/shorts/"):
                return parsed_url.path.split("/shorts/")[1].split("?")[0]
        elif "youtu.be" in parsed_url.hostname:
            return parsed_url.path[1:].split("?")[0]
        elif "googleusercontent.com/youtube.com/" in url: # From previous version, might be useful
             # e.g. https://youtu.be/HoHLxjTOa5E{VIDEO_ID}
            if "/youtube.com/6" in url:
                return url.split("/youtube.com/6")[-1].split("?")[0]
            # Add other googleusercontent patterns if necessary
    except Exception as e:
        logger.error(f"Error parsing YouTube URL '{url}': {e}")
    logger.warning(f"Could not extract YouTube ID from URL: {url}")
    return None


def map_mc_question_to_h5p(q_data):
    """Maps a MultipleChoice question from input JSON to H5P format."""
    answers_h5p = []
    for opt in q_data.get("options", []):
        answers_h5p.append({
            "text": opt.get("text", ""),
            "correct": opt.get("is_correct", False),
            "tipsAndFeedback": {
                "tip": "", # Tips are not in this simple MC structure
                "chosenFeedback": opt.get("feedback", ""),
                "notChosenFeedback": ""
            }
        })

    return {
        "library": "H5P.MultiChoice 1.16",
        "params": {
            "question": q_data.get("question", "N/A"),
            "answers": answers_h5p,
            "behaviour": {
                "singleAnswer": True,
                "enableRetry": False, # As per dummy
                "enableSolutionsButton": False, # As per dummy
                "enableCheckButton": True, # As per dummy
                "type": "auto",
                "singlePoint": False,
                "randomAnswers": True,
                "showSolutionsRequiresInput": True,
                "confirmCheckDialog": False,
                "confirmRetryDialog": False,
                "autoCheck": False,
                "passPercentage": 100,
                "showScorePoints": True
            },
            "media": {"disableImageZooming": False}, # Default from dummy
            "overallFeedback": [{"from": 0, "to": 100}], # Default
            "UI": { # Standard UI texts, mostly German from dummy
                "checkAnswerButton": "Überprüfen",
                "submitAnswerButton": "Absenden",
                "showSolutionButton": "Lösung anzeigen",
                "tryAgainButton": "Wiederholen",
                "tipsLabel": "Hinweis anzeigen",
                "scoreBarLabel": "Du hast :num von :total Punkten erreicht.",
                "tipAvailable": "Hinweis verfügbar",
                "feedbackAvailable": "Rückmeldung verfügbar",
                "readFeedback": "Rückmeldung vorlesen",
                "wrongAnswer": "Falsche Antwort",
                "correctAnswer": "Richtige Antwort",
                "shouldCheck": "Hätte gewählt werden müssen",
                "shouldNotCheck": "Hätte nicht gewählt werden sollen",
                "noInput": "Bitte antworte, bevor du die Lösung ansiehst",
                "a11yCheck": "Die Antworten überprüfen. Die Auswahlen werden als richtig, falsch oder fehlend markiert.",
                "a11yShowSolution": "Die Lösung anzeigen. Die richtigen Lösungen werden in der Aufgabe angezeigt.",
                "a11yRetry": "Die Aufgabe wiederholen. Alle Versuche werden zurückgesetzt und die Aufgabe wird erneut gestartet."
            },
            "confirmCheck": {"header": "Beenden?", "body": "Ganz sicher beenden?", "cancelLabel": "Abbrechen", "confirmLabel": "Beenden"},
            "confirmRetry": {"header": "Wiederholen?", "body": "Ganz sicher wiederholen?", "cancelLabel": "Abbrechen", "confirmLabel": "Bestätigen"}
        },
        "subContentId": generate_uuid(),
        "metadata": {
            "contentType": "Multiple Choice", "license": "U", "title": "Multiple Choice",
            "authors": [], "changes": [], "extraTitle": "Multiple Choice"
        }
    }

def map_tf_question_to_h5p(q_data):
    """Maps a TrueFalse question from input JSON to H5P format."""
    return {
        "library": "H5P.TrueFalse 1.8",
        "params": {
            "question": q_data.get("question", "N/A"),
            "correct": "true" if q_data.get("correct_answer") else "false",
            "behaviour": {
                "enableRetry": False, # As per dummy
                "enableSolutionsButton": False, # As per dummy
                "enableCheckButton": True, # As per dummy
                "confirmCheckDialog": False,
                "confirmRetryDialog": False,
                "autoCheck": False,
                "feedbackOnCorrect": q_data.get("feedback_correct", ""),
                "feedbackOnWrong": q_data.get("feedback_incorrect", "")
            },
            "media": {"disableImageZooming": False}, # Default
            "l10n": { # Standard UI texts, German from dummy
                "trueText": "Wahr", "falseText": "Falsch",
                "score": "Du hast @score von @total Punkten erreicht.",
                "checkAnswer": "Überprüfen", "submitAnswer": "Absenden",
                "showSolutionButton": "Lösung anzeigen", "tryAgain": "Wiederholen",
                "wrongAnswerMessage": "Falsche Antwort", "correctAnswerMessage": "Richtige Antwort",
                "scoreBarLabel": "Du hast :num von :total Punkten erreicht.",
                "a11yCheck": "Die Antworten überprüfen. Die Antwort wird als richtig, falsch oder unbeantwortet markiert.",
                "a11yShowSolution": "Die Lösung anzeigen. Die richtige Lösung wird in der Aufgabe angezeigt.",
                "a11yRetry": "Die Aufgabe wiederholen. Alle Versuche werden zurückgesetzt, und die Aufgabe wird erneut gestartet."
            },
            "confirmCheck": {"header": "Beenden?", "body": "Ganz sicher beenden?", "cancelLabel": "Abbrechen", "confirmLabel": "Beenden"},
            "confirmRetry": {"header": "Wiederholen?", "body": "Ganz sicher wiederholen?", "cancelLabel": "Abbrechen", "confirmLabel": "Bestätigen"}
        },
        "subContentId": generate_uuid(),
        "metadata": {
            "contentType": "True/False Question", "license": "U", "title": "Richtig Falsch",
            "authors": [], "changes": [], "extraTitle": "Richtig Falsch"
        }
    }

def map_questions_to_h5p_array(questions_from_input):
    """Maps an array of questions from input JSON to an array of H5P question objects."""
    h5p_questions = []
    if not isinstance(questions_from_input, list):
        logger.warning("Questions data is not a list.")
        return []
        
    for q_data in questions_from_input:
        q_type = q_data.get("type", "").strip()
        if q_type == "MultipleChoice":
            h5p_questions.append(map_mc_question_to_h5p(q_data))
        elif q_type == "TrueFalse":
            h5p_questions.append(map_tf_question_to_h5p(q_data))
        else:
            logger.warning(f"Unsupported question type '{q_type}'. Skipping.")
    return h5p_questions


def create_h5p_package(content_json_str: str, h5p_json_str: str, template_zip_path: str, images_to_add: list = None):
    """
    Creates an H5P package (ZIP file in memory).

    :param content_json_str: JSON string for content/content.json.
    :param h5p_json_str: JSON string for h5p.json.
    :param template_zip_path: Path to the template .zip file.
    :param images_to_add: A list of tuples: [(source_disk_path, target_path_in_zip), ...].
                          Example: [('templates/img_1.png', 'images/img_1.png')]
                          Target path is relative to the 'content/' folder in the H5P zip.
    :return: Bytes of the H5P package or None if an error occurs.
    """
    if images_to_add is None:
        images_to_add = []

    try:
        with open(template_zip_path, 'rb') as f_template:
            template_bytes = f_template.read()

        in_memory_zip = io.BytesIO()
        with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as new_zip:
            # Copy contents from template zip
            with zipfile.ZipFile(io.BytesIO(template_bytes), 'r') as template_zip_obj:
                for item in template_zip_obj.infolist():
                    # Skip existing content.json or h5p.json from template, we're overwriting
                    if item.filename.lower() == 'content/content.json' or \
                       item.filename.lower() == 'h5p.json':
                        continue
                    # Skip images that we might be replacing by name
                    is_image_to_be_replaced = False
                    for _, target_img_path_in_zip in images_to_add:
                        if item.filename.lower() == f'content/{target_img_path_in_zip.lower()}':
                            is_image_to_be_replaced = True
                            break
                    if is_image_to_be_replaced:
                        continue
                    
                    new_zip.writestr(item, template_zip_obj.read(item.filename))

            # Write new content.json and h5p.json
            new_zip.writestr('content/content.json', content_json_str.encode('utf-8'))
            new_zip.writestr('h5p.json', h5p_json_str.encode('utf-8'))

            # Add/overwrite specified images
            for source_disk_path_str, target_path_in_zip in images_to_add:
                source_disk_path = Path(source_disk_path_str)
                if source_disk_path.exists():
                    with open(source_disk_path, 'rb') as f_img:
                        new_zip.writestr(f'content/{target_path_in_zip}', f_img.read())
                else:
                    logger.warning(f"Image file not found at source: {source_disk_path_str}. Skipping.")
        
        in_memory_zip.seek(0)
        return in_memory_zip.getvalue()

    except FileNotFoundError:
        logger.error(f"Template H5P file not found at '{template_zip_path}'.")
        return None
    except Exception as e:
        logger.error(f"Error creating H5P package: {e}")
        import traceback
        traceback.print_exc()
        return None