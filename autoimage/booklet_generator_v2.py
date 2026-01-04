import json
import logging
import utils_booklet_iframe as utils_booklet

# --- Constants & L10N ---
DEFAULT_BEHAVIOUR = {
    "baseColor": "#002f6c", 
    "defaultTableOfContents": False, 
    "progressIndicators": True,
    "progressAuto": True, 
    "displaySummary": True, 
    "enableRetry": True
}

BOOK_L10N = {
    "read": "Öffnen", "displayTOC": "Inhaltsverzeichnis anzeigen", "hideTOC": "Inhaltsverzeichnis ausblenden",
    "nextPage": "Nächste Seite", "previousPage": "Vorherige Seite", "chapterCompleted": "Seite abgeschlossen!",
    "partCompleted": "@pages von @total Seiten abgeschlossen", "incompleteChapter": "Unvollständige Seite",
    "navigateToTop": "Nach oben springen", "markAsFinished": "Ich habe diese Seite abgeschlossen",
    "fullscreen": "Vollbild", "exitFullscreen": "Vollbild beenden", "bookProgressSubtext": "@count von @total Seiten",
    "interactionsProgressSubtext": "@count von @total Interaktionen", "submitReport": "Report absenden",
    "restartLabel": "Neustart", "summaryHeader": "Zusammenfassung", "allInteractions": "Alle Interaktionen",
    "unansweredInteractions": "Unbeantwortete Interaktionen", "scoreText": "@score / @maxscore",
    "leftOutOfTotalCompleted": "@left von @max Interaktionen abgeschlossen", "noInteractions": "Keine Interaktionen",
    "score": "Punkte", "summaryAndSubmit": "Zusammenfassung und Einsenden",
    "noChapterInteractionBoldText": "Du hast noch keine Seiten bearbeitet.",
    "noChapterInteractionText": "Du musst wenigstens eine Seite bearbeiten, um die Zusammenfassung zu sehen.",
    "yourAnswersAreSubmittedForReview": "Deine Antworten wurden zur Begutachtung versendet!",
    "bookProgress": "Buchfortschritt", "interactionsProgress": "Interaktionsfortschritt",
    "totalScoreLabel": "Gesamtpunktzahl",
    "a11y": {"progress": "Seite @page von @total.", "menu": "Inhaltsverzeichnis ein- bzw. ausschalten"}
}

# --- H5P.json Generation ---
def generate_h5p_json_dict(title: str):
    return {
        "embedTypes": ["iframe"],
        "language": "en",
        "defaultLanguage": "de",
        "license": "U",
        "title": title,
        "mainLibrary": "H5P.InteractiveBook",
        "preloadedDependencies": [
            {"machineName": "H5P.Image", "majorVersion": 1, "minorVersion": 1},
            {"machineName": "H5P.AdvancedText", "majorVersion": 1, "minorVersion": 1},
            {"machineName": "H5P.Accordion", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "FontAwesome", "majorVersion": 4, "minorVersion": 5},
            {"machineName": "H5P.Column", "majorVersion": 1, "minorVersion": 18},
            {"machineName": "H5P.IFrameEmbed", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "H5P.MemoryGame", "majorVersion": 1, "minorVersion": 3},
            {"machineName": "H5P.QuestionSet", "majorVersion": 1, "minorVersion": 20},
            {"machineName": "H5P.MultiChoice", "majorVersion": 1, "minorVersion": 16},
            {"machineName": "H5P.TrueFalse", "majorVersion": 1, "minorVersion": 8},
            {"machineName": "H5P.DragText", "majorVersion": 1, "minorVersion": 10},
            {"machineName": "H5P.JoubelUI", "majorVersion": 1, "minorVersion": 3},
            {"machineName": "H5P.Transition", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "H5P.FontIcons", "majorVersion": 1, "minorVersion": 0},
            {"machineName": "H5P.Question", "majorVersion": 1, "minorVersion": 5},
            {"machineName": "H5P.InteractiveBook", "majorVersion": 1, "minorVersion": 11}
        ]
    }

# --- Content Generators ---

def create_custom_introduction(intro_data: dict):
    """
    Create a customized introduction based on AI-generated content
    
    intro_data should contain:
    - title: str
    - welcome_text: str
    - learning_objectives: list[str]
    - workflow: list[str]
    """
    
    # Build learning objectives HTML
    objectives_html = "<ul>"
    for obj in intro_data.get("learning_objectives", []):
        objectives_html += f"<li>{obj}</li>"
    objectives_html += "</ul>"
    
    # Build workflow HTML
    workflow_html = "<ol>"
    for step in intro_data.get("workflow", []):
        workflow_html += f"<li>{step}</li>"
    workflow_html += "</ol>"
    
    intro_html = f"""<h2><strong>{intro_data.get('title', 'Willkommen')}</strong></h2>
<p>{intro_data.get('welcome_text', '')}</p>
<h3>Lernziele</h3>
{objectives_html}
<h3>Ablauf</h3>
{workflow_html}"""

    return {
        "subContentId": utils_booklet.generate_uuid(),
        "library": "H5P.Column 1.18",
        "metadata": {"contentType": "Column", "license": "U", "title": "Einführung"},
        "params": {
            "content": [{
                "useSeparator": "auto",
                "content": {
                    "subContentId": utils_booklet.generate_uuid(),
                    "library": "H5P.AdvancedText 1.1",
                    "metadata": {"contentType": "Text", "license": "U", "title": "Einführungstext"},
                    "params": {"text": intro_html}
                }
            }]
        }
    }

def create_memory_game(data):
    raw_cards_list = data.get("cards", [])
    cards_h5p = []

    for i in range(0, len(raw_cards_list), 2):
        if i + 1 >= len(raw_cards_list):
            break 

        item_a = raw_cards_list[i].get("image", {})
        item_b = raw_cards_list[i+1].get("image", {})

        # --- Handle String vs Dict inputs ---
        if isinstance(item_a, str):
            image_alt = ""
            description = ""
        else:
            image_alt = item_a.get("imageAlt", "")
            description = item_a.get("description", "")

        if isinstance(item_b, str):
            match_alt = ""
        else:
            match_alt = item_b.get("matchAlt", "")
        # ------------------------------------

        pair = {
            "image": utils_booklet.create_image_param(item_a),
            "match": utils_booklet.create_image_param(item_b),
            "imageAlt": image_alt,
            "matchAlt": match_alt,
            "description": description
        }
        cards_h5p.append(pair)

    memory_content = {
        "subContentId": utils_booklet.generate_uuid(),
        "library": "H5P.MemoryGame 1.3",
        "metadata": {"contentType": "Memory Game", "license": "U", "title": data.get("title", "Memory")},
        "params": {
            "cards": cards_h5p,
            "behaviour": {
                "useGrid": False, 
                "allowRetry": False,
                "numCardsToUse": 4  # Show only 4 cards (2 pairs)
            },
            "lookNFeel": {
                "themeColor": data.get("themeColor", "#002f6c"),
                "cardBack": utils_booklet.create_image_param(data.get("card_back_image", "images/card_back.png"))
            },
            "l10n": {
                "cardTurns": "Züge", "timeSpent": "Benötigte Zeit", "feedback": "Gut gemacht!",
                "tryAgain": "Nochmal spielen?", "closeLabel": "Schließen", "label": "Memory",
                "done": "Du hast alle Kartenpaare gefunden!", "cardPrefix": "Karte %num:",
                "cardUnturned": "Zugedeckt.", "cardMatched": "Paar gefunden.",
                "cardTurned": "Umgedreht.", "cardMatchedA11y": "Match found", "cardNotMatchedA11y": "No match"
            }
        }
    }

    instruction_text = {
        "useSeparator": "auto",
        "content": {
            "subContentId": utils_booklet.generate_uuid(),
            "library": "H5P.AdvancedText 1.1",
            "params": {"text": f"<p><strong>{data.get('instruction', '')}</strong></p>"},
            "metadata": {"contentType": "Text", "license": "U", "title": "Instruction"}
        }
    }

    return {
        "subContentId": utils_booklet.generate_uuid(),
        "library": "H5P.Column 1.18",
        "metadata": {"contentType": "Column", "license": "U", "title": data.get("title")},
        "params": {"content": [instruction_text, {"useSeparator": "auto", "content": memory_content}]}
    }

def create_accordion(accordion_data):
    panels = []
    for item in accordion_data:
        panels.append({
            "title": item.get("title", ""),
            "content": {
                "subContentId": utils_booklet.generate_uuid(),
                "library": "H5P.AdvancedText 1.1",
                "metadata": {"contentType": "Text", "license": "U", "title": "Text"},
                "params": {"text": item.get("text", "")}
            }
        })

    return {
        "subContentId": utils_booklet.generate_uuid(),
        "library": "H5P.Accordion 1.0",
        "metadata": {"contentType": "Accordion", "license": "U", "title": "Zusammenfassung"},
        "params": {"panels": panels, "hTag": "h2"}
    }

def create_video_page(data):
    title_text = {
        "useSeparator": "auto",
        "content": {
            "subContentId": utils_booklet.generate_uuid(),
            "library": "H5P.AdvancedText 1.1",
            "metadata": {"contentType": "Text", "license": "U", "title": "Title"},
            "params": {"text": f"<h2>{data.get('title', '')}</h2>"}
        }
    }

    vid_data = data.get("video", {})
    iframe_obj = {
        "useSeparator": "auto",
        "content": {
            "subContentId": utils_booklet.generate_uuid(),
            "library": "H5P.IFrameEmbed 1.0",
            "metadata": {"contentType": "Iframe Embedder", "license": "U", "title": "Video"},
            "params": {
                "source": vid_data.get("url"),
                "width": str(vid_data.get("width", 800)),
                "height": str(vid_data.get("height", 400)),
                "resizeSupported": True,
                "minWidth": "300"
            }
        }
    }

    warning_text = {
        "useSeparator": "auto",
        "content": {
            "subContentId": utils_booklet.generate_uuid(),
            "library": "H5P.AdvancedText 1.1",
            "metadata": {"contentType": "Text", "license": "U", "title": "Link"},
            "params": {"text": f"<p>❗ Falls das Video nicht lädt, versuchen Sie die Seite neu zu laden.</p><p>Link zum Video 👉 <a href='{vid_data.get('url')}' target='_blank'>Video öffnen</a></p>"}
        }
    }

    accordion_obj = create_accordion(data.get("summary_accordion", []))
    accordion_wrapper = {"useSeparator": "auto", "content": accordion_obj}

    return {
        "subContentId": utils_booklet.generate_uuid(),
        "library": "H5P.Column 1.18",
        "metadata": {"contentType": "Column", "license": "U", "title": data.get("title")},
        "params": {"content": [title_text, iframe_obj, warning_text, accordion_wrapper]},
        "_reusable_accordion": accordion_obj
    }

def create_question_set(data, is_drag_text=False, forced_pool_size=None):
    intro_screen = data.get("intro_screen", {})
    
    questions_h5p = []
    if is_drag_text:
        for task in data.get("tasks", []):
            questions_h5p.append(utils_booklet.map_drag_text_to_h5p(task))
    else:
        questions_h5p = utils_booklet.map_questions_to_h5p_array(data.get("questions", []))

    # Pool size logic
    pool_size = len(questions_h5p)
    if forced_pool_size is not None:
        pool_size = min(forced_pool_size, len(questions_h5p))

    qset_params = {
        "introPage": {
            "showIntroPage": True,
            "startButtonText": "Quiz starten",
            "title": intro_screen.get("title", "Quiz"),
            "introduction": f"<p style='text-align:center'>{intro_screen.get('text','')}</p>",
            "backgroundImage": utils_booklet.create_image_param(intro_screen.get("background_image"))
        },
        "progressType": "dots" if is_drag_text else "textual",
        "passPercentage": 50,
        "questions": questions_h5p,
        "poolSize": pool_size,
        "override": {"checkButton": True, "showSolutionButton": "off" if is_drag_text else "on", "retryButton": "on"},
        "texts": {
            "prevButton": "Zurück", "nextButton": "Weiter", "finishButton": "Beenden", "submitButton": "Absenden",
            "textualProgress": "Frage @current von @total", "questionLabel": "Frage"
        },
        "endGame": {
            "showResultPage": True, "showSolutionButton": True, "showRetryButton": True,
            "message": "Dein Ergebnis:", "scoreBarLabel": "Du hast @score von @total Punkten erreicht."
        }
    }

    qset_content = {
        "subContentId": utils_booklet.generate_uuid(),
        "library": "H5P.QuestionSet 1.20",
        "metadata": {"contentType": "Question Set", "license": "U", "title": data.get("title")},
        "params": qset_params
    }

    return {
        "subContentId": utils_booklet.generate_uuid(),
        "library": "H5P.Column 1.18",
        "metadata": {"contentType": "Column", "license": "U", "title": data.get("title")},
        "params": {"content": [{"useSeparator": "auto", "content": qset_content}]}
    }

def create_booklet_content_json_structure(chapters_data: list, video_title: str, 
                                            cover_image_name: str = "images/default_cover.png") -> dict:
    """
    Create the complete H5P Interactive Book structure
    
    chapters_data: list of chapter definitions with type and data
    """
    
    chapters = []
    
    # Process each chapter
    for chapter_info in chapters_data:
        if not isinstance(chapter_info, dict):
            logging.warning(f"Skipping invalid chapter data: {chapter_info}")
            continue

        c_type = chapter_info.get("type")
        
        if c_type == "introduction":
            # Custom introduction
            chapters.append(create_custom_introduction(chapter_info.get("data", {})))
            
        elif c_type == "memory_game":
            chapters.append(create_memory_game(chapter_info))
            
        elif c_type == "video_page":
            result = create_video_page(chapter_info)
            chapters.append(result)
            
        elif c_type == "question_set":
            # For quiz, limit to 5 random questions from pool
            chapters.append(create_question_set(chapter_info, is_drag_text=False, forced_pool_size=5))
            
        elif c_type == "cloze_set":
            chapters.append(create_question_set(chapter_info, is_drag_text=True))

    # Define cover
    cover_image_file = utils_booklet.create_image_param(cover_image_name)
    
    content_structure = {
        "showCoverPage": True,
        "bookCover": {
            "coverDescription": f"<h2 style='text-align:center'>{video_title}</h2>",
            "coverMedium": {
                "library": "H5P.Image 1.1",
                "params": {
                    "contentName": "Bild",
                    "file": cover_image_file,
                    "decorative": True,
                },
                "metadata": {"contentType": "Image", "license": "U", "title": "Cover"}
            }
        },
        "chapters": chapters,
        "behaviour": DEFAULT_BEHAVIOUR,
        **BOOK_L10N
    }
    
    # Global text replacement for German 'ß' -> 'ss'
    final_structure = utils_booklet.recursive_replace_ss(content_structure)

    return final_structure