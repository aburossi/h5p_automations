import json
import uuid
import zipfile
import io
import logging
import re
from urllib.parse import quote
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_uuid():
    """Generates a unique UUID."""
    return str(uuid.uuid4())

def strip_html_tags(html_string):
    """Removes HTML tags from a string."""
    return re.sub('<[^<]+?>', '', html_string)

def generate_assignment_iframe_url(assignment_data: dict, book_title: str) -> str:
    """
    Generates a URL for the hep-impuls textbox IFrame, applying special formatting
    to bullet points (smaller font and a bullet character).

    :param assignment_data: The dictionary for "chapter5_assignment".
    :param book_title: The overall title of the book for the assignmentId.
    :return: A fully constructed and encoded URL string.
    """
    base_url = "https://hep-impuls.github.io/textbox/answers.html"
    
    content_data = assignment_data.get("assignmentContent", {})
    title_html = content_data.get("title", "")
    instructions_list = content_data.get("instructions", [])
    
    # 1. Sanitize chapter title for a specific assignmentId
    assignment_id_raw = assignment_data.get("titleForChapter", book_title)
    sanitized_id = re.sub(r'[^a-zA-Z0-9_-]', '', assignment_id_raw.replace(' ', '_'))
    assignment_id_param = f"assignmentId={sanitized_id}"

    # 2. Derive subIds from the title only
    title_text = strip_html_tags(title_html)
    sub_id_terms = [term for term in re.split(r'[\sund,]+', title_text) if term]
    sub_ids_param = f"subIds={'_'.join(sub_id_terms)}" if sub_id_terms else "subIds="

    # 3. Create a structured list of all content parts to track list items
    # Each item is a tuple: (html_content, is_list_item)
    structured_content = [(title_html, False)]  # Start with the title
    for instruction_html in instructions_list:
        if '<li>' in instruction_html:
            list_items = re.findall(r'<li>(.*?)</li>', instruction_html)
            for item_html in list_items:
                structured_content.append((item_html, True))  # Mark as a list item
        else:
            structured_content.append((instruction_html, False)) # Mark as a regular paragraph

    # 4. Process each content part based on its type and create p-parameters
    params = []
    for i, (content_html, is_list_item) in enumerate(structured_content):
        
        # Convert <strong> tags to markdown bold, then strip any other HTML
        content_md = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content_html)
        content_clean_text = strip_html_tags(content_md)
        
        final_content_for_url = ""
        if is_list_item:
            # Apply special formatting for bullet points
            # Prepend bullet and wrap in a styled span. The target app must support this HTML.
            final_content_for_url = f'<span style="font-size: smaller;">• {content_clean_text}</span>'
        else:
            # For regular paragraphs and titles, just use the cleaned text
            final_content_for_url = content_clean_text
            
        # URL-encode the final processed content
        encoded_content = quote(final_content_for_url)
        params.append(f"p{i+1}={encoded_content}")

    # 5. Assemble the final URL
    params_string = "&".join(params)
    final_url = f"{base_url}?{assignment_id_param}&{sub_ids_param}&{params_string}"
    
    logger.info(f"Generated assignment URL with {len(params)} parameters and bullet formatting. Length: {len(final_url)}")
    return final_url


def map_mc_question_to_h5p(q_data):
    """Maps a MultipleChoice question from input JSON to H5P format."""
    answers_h5p = []
    for opt in q_data.get("options", []):
        answers_h5p.append({
            "text": opt.get("text", ""),
            "correct": opt.get("is_correct", False),
            "tipsAndFeedback": {
                "tip": opt.get("tip", ""),
                "chosenFeedback": opt.get("feedback", ""),
                "notChosenFeedback": ""
            }
        })

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
            "behaviour": {
                "singleAnswer": True, "enableRetry": False, "enableSolutionsButton": False,
                "enableCheckButton": True, "type": "auto", "singlePoint": False,
                "randomAnswers": True, "showSolutionsRequiresInput": True,
                "confirmCheckDialog": False, "confirmRetryDialog": False,
                "autoCheck": False, "passPercentage": 100, "showScorePoints": True
            },
            "media": {"disableImageZooming": False},
            "overallFeedback": [{"from": 0, "to": 100}],
            "UI": ui_texts,
            "confirmCheck": confirm_check_dialog,
            "confirmRetry": confirm_retry_dialog
        },
        "subContentId": generate_uuid(),
        "metadata": {
            "contentType": "Multiple Choice", "license": "U", "title": "Multiple Choice",
            "authors": [], "changes": [], "extraTitle": "Multiple Choice"
        }
    }

def map_tf_question_to_h5p(q_data):
    """Maps a TrueFalse question from input JSON to H5P format."""
    l10n_texts = {
        "trueText": "Wahr", "falseText": "Falsch",
        "score": "Du hast @score von @total Punkten erreicht.",
        "checkAnswer": "Überprüfen", "submitAnswer": "Absenden",
        "showSolutionButton": "Lösung anzeigen", "tryAgain": "Wiederholen",
        "wrongAnswerMessage": "Falsche Antwort", "correctAnswerMessage": "Richtige Antwort",
        "scoreBarLabel": "Du hast :num von :total Punkten erreicht.",
        "a11yCheck": "Die Antworten überprüfen. Die Antwort wird als richtig, falsch oder unbeantwortet markiert.",
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
            "behaviour": {
                "enableRetry": False, "enableSolutionsButton": False, "enableCheckButton": True,
                "confirmCheckDialog": False, "confirmRetryDialog": False, "autoCheck": False,
                "feedbackOnCorrect": q_data.get("feedback_correct", ""),
                "feedbackOnWrong": q_data.get("feedback_incorrect", "")
            },
            "media": {"disableImageZooming": False},
            "l10n": l10n_texts,
            "confirmCheck": confirm_check_dialog,
            "confirmRetry": confirm_retry_dialog
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
    """
    if images_to_add is None:
        images_to_add = []

    try:
        with open(template_zip_path, 'rb') as f_template:
            template_bytes = f_template.read()

        in_memory_zip = io.BytesIO()
        with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as new_zip:
            with zipfile.ZipFile(io.BytesIO(template_bytes), 'r') as template_zip_obj:
                for item in template_zip_obj.infolist():
                    if item.filename.lower() in ['content/content.json', 'h5p.json']:
                        continue
                    
                    is_image_to_be_replaced = any(
                        item.filename.lower().endswith(target_path.lower())
                        for _, target_path in images_to_add
                    )
                    if is_image_to_be_replaced:
                        logger.info(f"Skipping '{item.filename}' from template, will be replaced.")
                        continue
                    
                    new_zip.writestr(item, template_zip_obj.read(item.filename))

            new_zip.writestr('content/content.json', content_json_str.encode('utf-8'))
            new_zip.writestr('h5p.json', h5p_json_str.encode('utf-8'))

            for source_disk_path_str, target_path_in_zip in images_to_add:
                source_disk_path = Path(source_disk_path_str)
                full_target_path_in_zip = f'content/{target_path_in_zip}' if not target_path_in_zip.lower().startswith('content/') else target_path_in_zip
                
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