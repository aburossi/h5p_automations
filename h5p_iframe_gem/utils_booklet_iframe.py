import json
import uuid
import zipfile
import io
import logging
# from urllib.parse import urlparse, parse_qs # No longer needed for YouTube ID
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_uuid():
    """Generates a unique UUID."""
    return str(uuid.uuid4())

# extract_youtube_id function is REMOVED

def map_mc_question_to_h5p(q_data):
    """Maps a MultipleChoice question from input JSON to H5P format."""
    answers_h5p = []
    for opt in q_data.get("options", []):
        answers_h5p.append({
            "text": opt.get("text", ""),
            "correct": opt.get("is_correct", False),
            "tipsAndFeedback": { # From example
                "tip": opt.get("tip", ""), # Allow tip per option if provided
                "chosenFeedback": opt.get("feedback", ""), # Renamed from chosenFeedback to feedback in input
                "notChosenFeedback": "" # Can be extended if needed
            }
        })

    # Using UI texts from the new example content.json
    ui_texts = {
        "checkAnswerButton": "Überprüfen", "submitAnswerButton": "Absenden",
        "showSolutionButton": "Lösung anzeigen", "tryAgainButton": "Wiederholen",
        "tipsLabel": "Hinweis anzeigen", "scoreBarLabel": "Du hast :num von :total Punkten erreicht.",
        "tipAvailable": "Hinweis verfügbar", "feedbackAvailable": "Rückmeldung verfügbar",
        "readFeedback": "Rückmeldung vorlesen", "wrongAnswer": "Falsche Antwort",
        "correctAnswer": "Richtige Antwort", "shouldCheck": "Hätte gewählt werden müssen",
        "shouldNotCheck": "Hätte nicht gewählt werden sollen",
        "noInput": "Bitte antworte, bevor du die Lösung ansiehst",
        "a11yCheck": "Die Antworten überprüfen. Die Auswahlen werden als richtig, falsch oder fehlend markiert.",
        "a11yShowSolution": "Die Lösung anzeigen. Die richtigen Lösungen werden in der Aufgabe angezeigt.",
        "a11yRetry": "Die Aufgabe wiederholen. Alle Versuche werden zurückgesetzt und die Aufgabe wird erneut gestartet."
    }
    confirm_check_dialog = {"header": "Beenden?", "body": "Ganz sicher beenden?", "cancelLabel": "Abbrechen", "confirmLabel": "Beenden"}
    confirm_retry_dialog = {"header": "Wiederholen?", "body": "Ganz sicher wiederholen?", "cancelLabel": "Abbrechen", "confirmLabel": "Bestätigen"}


    return {
        "library": "H5P.MultiChoice 1.16",
        "params": {
            "question": q_data.get("question", "N/A"),
            "answers": answers_h5p,
            "behaviour": { # From example
                "singleAnswer": True, "enableRetry": False, "enableSolutionsButton": False,
                "enableCheckButton": True, "type": "auto", "singlePoint": False,
                "randomAnswers": True, "showSolutionsRequiresInput": True,
                "confirmCheckDialog": False, "confirmRetryDialog": False,
                "autoCheck": False, "passPercentage": 100, "showScorePoints": True
            },
            "media": {"disableImageZooming": False}, # Default from example
            "overallFeedback": [{"from": 0, "to": 100}], # Default
            "UI": ui_texts, # from example
            "confirmCheck": confirm_check_dialog, # from example
            "confirmRetry": confirm_retry_dialog  # from example
        },
        "subContentId": generate_uuid(),
        "metadata": { # From example
            "contentType": "Multiple Choice", "license": "U", "title": "Multiple Choice",
            "authors": [], "changes": [], "extraTitle": "Multiple Choice"
        }
    }

def map_tf_question_to_h5p(q_data):
    """Maps a TrueFalse question from input JSON to H5P format."""
    # Using UI texts from the new example content.json
    l10n_texts = {
        "trueText": "Wahr", "falseText": "Falsch",
        "score": "Du hast @score von @total Punkten erreicht.",
        "checkAnswer": "Überprüfen", "submitAnswer": "Absenden",
        "showSolutionButton": "Lösung anzeigen", "tryAgain": "Wiederholen",
        "wrongAnswerMessage": "Falsche Antwort", "correctAnswerMessage": "Richtige Antwort", # Added from example
        "scoreBarLabel": "Du hast :num von :total Punkten erreicht.",
        "a11yCheck": "Die Antworten überprüfen. Die Antwort wird als richtig, falsch oder unbeantwortet markiert.", # unbeantwortet vs fehlend
        "a11yShowSolution": "Die Lösung anzeigen. Die richtige Lösung wird in der Aufgabe angezeigt.",
        "a11yRetry": "Die Aufgabe wiederholen. Alle Versuche werden zurückgesetzt, und die Aufgabe wird erneut gestartet."
    }
    confirm_check_dialog = {"header": "Beenden?", "body": "Ganz sicher beenden?", "cancelLabel": "Abbrechen", "confirmLabel": "Beenden"}
    confirm_retry_dialog = {"header": "Wiederholen?", "body": "Ganz sicher wiederholen?", "cancelLabel": "Abbrechen", "confirmLabel": "Bestätigen"}

    return {
        "library": "H5P.TrueFalse 1.8",
        "params": {
            "question": q_data.get("question", "N/A"),
            "correct": "true" if q_data.get("correct_answer") else "false",
            "behaviour": { # From example
                "enableRetry": False, "enableSolutionsButton": False, "enableCheckButton": True,
                "confirmCheckDialog": False, "confirmRetryDialog": False, "autoCheck": False,
                "feedbackOnCorrect": q_data.get("feedback_correct", ""),
                "feedbackOnWrong": q_data.get("feedback_incorrect", "")
            },
            "media": {"disableImageZooming": False}, # Default
            "l10n": l10n_texts, # from example
            "confirmCheck": confirm_check_dialog, # from example
            "confirmRetry": confirm_retry_dialog # from example
        },
        "subContentId": generate_uuid(),
        "metadata": { # From example
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
                        # Ensure paths are compared correctly, especially if one has 'content/' prefix and other doesn't
                        normalized_item_filename = item.filename.lower().removeprefix('content/')
                        normalized_target_path = target_img_path_in_zip.lower().removeprefix('content/')
                        if item.filename.lower() == f'content/{target_img_path_in_zip.lower()}' or \
                           normalized_item_filename == normalized_target_path :
                            is_image_to_be_replaced = True
                            break
                    if is_image_to_be_replaced:
                        logger.info(f"Skipping '{item.filename}' from template, will be replaced by image: {target_img_path_in_zip}")
                        continue
                    
                    new_zip.writestr(item, template_zip_obj.read(item.filename))

            # Write new content.json and h5p.json
            new_zip.writestr('content/content.json', content_json_str.encode('utf-8'))
            new_zip.writestr('h5p.json', h5p_json_str.encode('utf-8'))

            # Add/overwrite specified images
            for source_disk_path_str, target_path_in_zip in images_to_add:
                source_disk_path = Path(source_disk_path_str)
                # Ensure target path within zip is correctly prefixed with 'content/'
                full_target_path_in_zip = target_path_in_zip
                if not target_path_in_zip.lower().startswith('content/'):
                    full_target_path_in_zip = f'content/{target_path_in_zip}'
                
                if source_disk_path.exists():
                    with open(source_disk_path, 'rb') as f_img:
                        new_zip.writestr(full_target_path_in_zip, f_img.read())
                        logger.info(f"Added/Replaced image: '{source_disk_path_str}' as '{full_target_path_in_zip}'")
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