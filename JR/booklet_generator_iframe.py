import json
import logging
import utils_booklet_iframe as utils_booklet

# --- Constants & L10N ---
DEFAULT_BEHAVIOUR = {
    "baseColor": "#002f6c", 
    "defaultTableOfContents": False, # Disabled as requested
    "progressIndicators": True,
    "progressAuto": True, 
    "displaySummary": True, 
    "enableRetry": True
}

BOOK_L10N = {
    "read": "Starten", "displayTOC": "Inhaltsverzeichnis anzeigen", "hideTOC": "Inhaltsverzeichnis ausblenden",
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

def create_hardcoded_introduction(roman_number: str):
    intro_html = f"""<h2><strong>Willkommen zum Jahresrückblick 2025, Teil {roman_number}</strong></h2><p>Gemeinsam blicken wir zurück auf bewegende, spannende und teils tragische Ereignisse aus Politik, Gesellschaft und Kultur, die das Jahr 2025 geprägt haben.&nbsp;</p><h3>Lernziele</h3><p>Sie können …</p><ul><li><strong>zentrale Ereignisse des Jahres 2025 beschreiben</strong> und deren Bedeutung erklären.</li><li><strong>Zusammenhänge zwischen verschiedenen Entwicklungen erkennen</strong> und reflektieren.</li><li>eigene Meinungen zu den Geschehnissen formulieren und begründen.</li></ul><h3>Ablauf</h3><ol><li><strong>Memory-Spiel:</strong> Spielen Sie eine Runde Memory, in der Sie Gesichter und Beschreibungen von Personen, die das Jahr 2025 geprägt haben, zuordnen.</li><li><strong>SRF-Beitrag:</strong> Schauen Sie den SRF-Rückblick auf die Ereignisse des Jahres und beantworten Sie die Verständnisfragen.</li><li><strong>Reflexion:</strong> Nutzen Sie Mentimeter, um Ihre Gedanken zu den Geschehnissen zu teilen und mögliche Schlagzeilen für 2026 zu formulieren.</li></ol>"""

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
                    "metadata": {"contentType": "Text", "license": "U", "title": "Unbenannt: Text"},
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
            "behaviour": {"useGrid": False, "allowRetry": False},
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
            "params": {"text": f"<p>❗ Falls die Meldung 'Ihr Webbrowser wird nicht unterstützt' kommt, 👉 Seite neu laden löst meistens das Problem.</p><p>Link zum Video 👉 <a href='{vid_data.get('url')}' target='_blank'>SRF</a></p>"}
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

    # --- POOL SIZE LOGIC ---
    # Default: Use all questions
    pool_size = len(questions_h5p)
    
    # If forced by orchestrator (e.g. for Quiz)
    if forced_pool_size is not None:
        pool_size = forced_pool_size
    # -----------------------

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

def create_iframe_page(data, reused_accordion=None):
    column_content = []

    if data.get("top_text"):
        column_content.append({
            "useSeparator": "auto",
            "content": {
                "subContentId": utils_booklet.generate_uuid(),
                "library": "H5P.AdvancedText 1.1",
                "metadata": {"contentType": "Text", "license": "U", "title": "Intro"},
                "params": {"text": data.get("top_text")}
            }
        })

    if data.get("include_accordion_ref") and reused_accordion:
        import copy
        acc_clone = copy.deepcopy(reused_accordion)
        acc_clone["subContentId"] = utils_booklet.generate_uuid()
        column_content.append({"useSeparator": "auto", "content": acc_clone})
        
        column_content.append({
            "useSeparator": "auto",
            "content": {
                "subContentId": utils_booklet.generate_uuid(),
                "library": "H5P.AdvancedText 1.1",
                "metadata": {"contentType": "Text", "license": "U", "title": "Link"},
                "params": {"text": f"<p><a href='{data.get('embed', {}).get('source')}' target='_blank'>Direkter Link</a></p>"}
            }
        })

    embed_data = data.get("embed", {})
    column_content.append({
        "useSeparator": "enabled",
        "content": {
            "subContentId": utils_booklet.generate_uuid(),
            "library": "H5P.IFrameEmbed 1.0",
            "metadata": {"contentType": "Iframe Embedder", "license": "U", "title": data.get("title")},
            "params": {
                "source": embed_data.get("source"),
                "width": str(embed_data.get("width", "100%")),
                "height": str(embed_data.get("height", "600")),
                "resizeSupported": True,
                "minWidth": str(embed_data.get("minWidth", "300"))
            }
        }
    })

    return {
        "subContentId": utils_booklet.generate_uuid(),
        "library": "H5P.Column 1.18",
        "metadata": {"contentType": "Column", "license": "U", "title": data.get("title")},
        "params": {"content": column_content}
    }

def create_mentimeter_page(url: str, title: str, top_text: str = "", accordion: dict = None, height: str = "600", min_width: str = "300"):
    """
    Simpler helper to create steps 6 and 7 without full JSON
    """
    data = {
        "title": title,
        "type": "iframe_page",
        "top_text": top_text,
        "embed": {
            "source": url, 
            "width": "800", 
            "height": height,
            "minWidth": min_width
        },
        "include_accordion_ref": True if accordion else False
    }
    return create_iframe_page(data, reused_accordion=accordion)


def create_booklet_content_json_structure(user_input_list: list, roman_number: str, months_text: str, 
                                            cover_image_name: str = "images/title_2025.png",
                                            mentimeter_urls: tuple = (None, None)) -> dict:
    
    # 1. Start with Introduction
    chapters = [create_hardcoded_introduction(roman_number)]
    reusable_accordion = None

    # 2. Process User Input List (Memory, Video, Questions, Cloze)
    for chapter_data in user_input_list:
        if not isinstance(chapter_data, dict):
            logging.warning(f"Skipping invalid chapter data: {chapter_data}")
            continue

        c_type = chapter_data.get("type")
        
        if c_type == "memory_game":
            chapters.append(create_memory_game(chapter_data))
            
        elif c_type == "video_page":
            result = create_video_page(chapter_data)
            reusable_accordion = result.pop("_reusable_accordion", None)
            chapters.append(result)
            
        elif c_type == "question_set":
            # --- FIX: Set forced_pool_size=5 for the Quiz ---
            chapters.append(create_question_set(chapter_data, is_drag_text=False, forced_pool_size=5))
            
        elif c_type == "cloze_set":
            chapters.append(create_question_set(chapter_data, is_drag_text=True))

    # 3. Add Steps 6 and 7 (Mentimeters)
    url_1, url_2 = mentimeter_urls
    
    # Step 6: The Survey / Reflection
    if url_1:
        chap_6 = create_mentimeter_page(
            url_1, 
            title="Reflexion", 
            top_text="<p>Nehmen Sie sich einen Moment Zeit für die Reflexion.</p>",
            accordion=reusable_accordion,
            height="2000",
            min_width="500"
        )
        chapters.append(chap_6)
    
    # Step 7: The Results (Ergebnisse)
    if url_2:
        chap_7 = create_mentimeter_page(
            url_2, 
            title="Ergebnisse", 
            top_text="<p>Hier sehen Sie die Ergebnisse der Umfrage:</p>", 
            accordion=None,
            height="500",
            min_width="800"
        )
        chapters.append(chap_7)

    # 4. Define Cover Image
    cover_image_file = utils_booklet.create_image_param(cover_image_name)
    
    content_structure = {
        "showCoverPage": True,
        "bookCover": {
            "coverDescription": f"<h2 style='text-align:center'>{months_text}</h2>",
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
    
    # 5. Global text replacement for German 'ß' -> 'ss'
    final_structure = utils_booklet.recursive_replace_ss(content_structure)

    return final_structure