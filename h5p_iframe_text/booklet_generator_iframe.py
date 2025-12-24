import json
import utils_booklet_iframe as utils_booklet # Renamed for clarity

# --- H5P Structure Default Values ---
DEFAULT_H5P_IMAGE_PARAMS_BASE = {
    "mime": "image/png", "copyright": {"license": "U"}, "width": 52, "height": 52
}
DEFAULT_H5P_IMAGE_WRAPPER_PARAMS = {
    "decorative": False, "contentName": "Bild", "expandImage": "Bild vergrößern",
    "minimizeImage": "Bild verkleinern"
}
DEFAULT_H5P_IMAGE_METADATA = {
    "contentType": "Image", "license": "U", "title": "Bild",
    "authors": [], "changes": []
}
DEFAULT_H5P_ADVANCED_TEXT_METADATA = {
    "contentType": "Text", "license": "U", "title": "Textblock",
    "authors": [], "changes": []
}

# --- h5p.json generation ---
def generate_h5p_json_dict(book_overall_title: str):
    """Generates the Python dictionary for h5p.json for the IFrame version."""
    return {
        "embedTypes": ["iframe"],
        "language": "en",
        "defaultLanguage": "de",
        "license": "U",
        "extraTitle": book_overall_title, # As per new h5p.json (e.g. POLECO)
        "title": book_overall_title,     # As per new h5p.json
        "mainLibrary": "H5P.InteractiveBook",
        "preloadedDependencies": [
            {"machineName":"H5P.Image","majorVersion":1,"minorVersion":1},
            {"machineName":"H5P.AdvancedText","majorVersion":1,"minorVersion":1},
            {"machineName":"H5P.Accordion","majorVersion":1,"minorVersion":0},
            {"machineName":"FontAwesome","majorVersion":4,"minorVersion":5}, # Commonly used
            {"machineName":"H5P.Column","majorVersion":1,"minorVersion":18},
            {"machineName":"H5P.IFrameEmbed","majorVersion":1,"minorVersion":0}, # ADDED
            {"machineName":"H5P.Summary","majorVersion":1,"minorVersion":10},
            {"machineName":"H5P.JoubelUI","majorVersion":1,"minorVersion":3},
            {"machineName":"H5P.Transition","majorVersion":1,"minorVersion":0},
            {"machineName":"H5P.FontIcons","majorVersion":1,"minorVersion":0},
            {"machineName":"H5P.Question","majorVersion":1,"minorVersion":5},
            {"machineName":"H5P.MultiChoice","majorVersion":1,"minorVersion":16},
            {"machineName":"H5P.TrueFalse","majorVersion":1,"minorVersion":8},
            {"machineName":"H5P.QuestionSet","majorVersion":1,"minorVersion":20},
            {"machineName":"H5P.Video","majorVersion":1,"minorVersion":6},
            {"machineName":"H5P.InteractiveBook","majorVersion":1,"minorVersion":11}
        ]
    }

# --- content.json generation ---
def create_booklet_content_json_structure(data: dict, h5p_cover_image_path: str, book_overall_title: str) -> dict:
    """
    Creates the Python dictionary for the H5P.InteractiveBook content.json (IFrame version).
    """
    # --- Data Extraction ---
    book_data = data.get("book", {})
    ch1_data = data.get("chapter1_introduction", {})
    ch2_data = data.get("chapter2_iframe", {})
    ch3_data = data.get("chapter3_summary", {})
    ch4_data = data.get("chapter4_questions", {})
    ch5_assignment_data = data.get("chapter5_assignment") # Can be None
    
    iframe_url = data.get("iframeUrl", "")

    # --- Cover Page ---
    cover_page_data = book_data.get("coverPage", {})
    cover_description_html = f"{cover_page_data.get('title', '<h1>Cover Title</h1>')}{cover_page_data.get('subtitle', '')}"
    
    cover_image_file_params = {**DEFAULT_H5P_IMAGE_PARAMS_BASE, "path": h5p_cover_image_path}
    cover_image_full_params = {**DEFAULT_H5P_IMAGE_WRAPPER_PARAMS, "file": cover_image_file_params}
    cover_image_metadata = {**DEFAULT_H5P_IMAGE_METADATA, "title": "Cover Bild"}

    book_cover = {
        "coverDescription": cover_description_html,
        "coverMedium": {
            "params": cover_image_full_params,
            "library": "H5P.Image 1.1",
            "metadata": cover_image_metadata,
            "subContentId": utils_booklet.generate_uuid()
        }
    }

    # --- Chapter 1: Introduction ---
    intro_content_data = ch1_data.get("introductionContent", {})
    bullet_points_list = intro_content_data.get("bulletPoints", [])
    bullet_points_html = "".join(bullet_points_list)
    
    if bullet_points_html and not bullet_points_html.strip().lower().startswith("<ul>") and bullet_points_list:
        bullet_points_html_complete = f"<ul>{bullet_points_html}</ul>"
    else:
        bullet_points_html_complete = bullet_points_html

    intro_text_html = (
        f"{intro_content_data.get('title', '')}"
        f"{bullet_points_html_complete}"
        f"{intro_content_data.get('guidanceText', '')}"
    )
    
    chapter1_text = {
        "content": {
            "params": {"text": intro_text_html},
            "library": "H5P.AdvancedText 1.1",
            "metadata": {**DEFAULT_H5P_ADVANCED_TEXT_METADATA, "title": "Einleitungstext"},
            "subContentId": utils_booklet.generate_uuid()
        },
        "useSeparator": "auto"
    }

    accordion_section_data = ch1_data.get("accordion", {})
    accordion_panels = []
    for definition_item in accordion_section_data.get("definitions", []):
        accordion_panels.append({
            "title": definition_item.get("term", "N/A"),
            "content": {
                "params": {"text": definition_item.get("definition", "")},
                "library": "H5P.AdvancedText 1.1",
                "subContentId": utils_booklet.generate_uuid(),
                "metadata": {**DEFAULT_H5P_ADVANCED_TEXT_METADATA, "title": f"Definition: {definition_item.get('term', 'N/A')}"}
            }
        })
    
    chapter1_accordion = {
        "content": {
            "params": {"panels": accordion_panels, "hTag": "h2"},
            "library": "H5P.Accordion 1.0",
            "metadata": {
                "contentType": "Accordion", "license": "U", 
                "title": accordion_section_data.get("titleForElement", "Begriffe"),
                "authors": [], "changes": [], "extraTitle": accordion_section_data.get("titleForElement", "Begriffe")
            },
            "subContentId": utils_booklet.generate_uuid()
        },
        "useSeparator": "auto"
    }
    
    chapter1_column = {
        "params": {"content": [chapter1_text, chapter1_accordion]},
        "library": "H5P.Column 1.18",
        "subContentId": utils_booklet.generate_uuid(),
        "metadata": {
            "contentType": "Column", "license": "U", 
            "title": ch1_data.get("titleForChapter", "Einleitung"),
            "authors": [], "changes": [], "extraTitle": ch1_data.get("titleForChapter", "Einleitung")
        }
    }

    # --- Chapter 2: IFrame ---
    iframe_section_intro_data = ch2_data.get("iframeSectionIntro", {})
    chapter2_intro_text_html = f"{iframe_section_intro_data.get('title', '')}{iframe_section_intro_data.get('instruction', '')}"
    chapter2_intro_text = {
        "content": {
            "params": {"text": chapter2_intro_text_html},
            "library": "H5P.AdvancedText 1.1",
            "metadata": {**DEFAULT_H5P_ADVANCED_TEXT_METADATA, "title": "Iframe Einleitung"},
            "subContentId": utils_booklet.generate_uuid()
        },
        "useSeparator": "auto"
    }

    iframe_embed_data = ch2_data.get("iframeEmbed", {})
    chapter2_iframe_embed = {
        "content": {
            "params": {
                "source": iframe_url,
                "width": iframe_embed_data.get("width", "700"),
                "minWidth": iframe_embed_data.get("minWidth", "400"),
                "height": iframe_embed_data.get("height", "500"),
                "resizeSupported": True
            },
            "library": "H5P.IFrameEmbed 1.0",
            "metadata": {
                "contentType": "Iframe Embedder", "license": "U",
                "title": iframe_embed_data.get("titleForElement", "Externer Inhalt"),
                "authors": [], "changes": [], "extraTitle": iframe_embed_data.get("titleForElement", "Externer Inhalt")
            },
            "subContentId": utils_booklet.generate_uuid()
        },
        "useSeparator": "auto"
    }

    chapter2_iframe_column = {
        "params": {"content": [chapter2_intro_text, chapter2_iframe_embed]},
        "library": "H5P.Column 1.18",
        "subContentId": utils_booklet.generate_uuid(),
        "metadata": {
            "contentType": "Column", "license": "U", 
            "title": ch2_data.get("titleForChapter", "Beitrag"),
            "authors": [], "changes": [], "extraTitle": ch2_data.get("titleForChapter", "Beitrag")
        }
    }

    # --- Chapter 3: Summary ---
    summary_section_intro_data = ch3_data.get("summarySectionIntro", {})
    chapter3_intro_text_html = f"{summary_section_intro_data.get('title', '')}{summary_section_intro_data.get('instruction', '')}"
    chapter3_intro_text = {
        "content": {
            "params": {"text": chapter3_intro_text_html},
            "library": "H5P.AdvancedText 1.1",
            "metadata": {**DEFAULT_H5P_ADVANCED_TEXT_METADATA, "title": "Zusammenfassung Einleitung"},
            "subContentId": utils_booklet.generate_uuid()
        },
        "useSeparator": "auto"
    }
    
    summary_element_data = ch3_data.get("summaryElement", {})
    h5p_summary_tasks = []
    for task_item in summary_element_data.get("summaries", []):
        h5p_summary_tasks.append({
            "summary": task_item.get("choices", ["Placeholder - no choices provided"]),
            "subContentId": utils_booklet.generate_uuid(),
            "tip": task_item.get("tip", "")
        })
    
    if not h5p_summary_tasks:
         utils_booklet.logger.warning(f"No summary tasks found. Adding a placeholder.")
         h5p_summary_tasks.append({
            "summary": ["Placeholder - no statements provided"],
            "subContentId": utils_booklet.generate_uuid(),
            "tip": "Input JSON had no summary tasks."
        })

    chapter3_summary_element = {
        "content": {
            "params": {
                "intro": summary_element_data.get("introText", "<p>Wähle die korrekte Aussage.</p>"),
                "overallFeedback": [{"from": 0, "to": 100}],
                "solvedLabel":"Fortschritt:", "scoreLabel":"Falsche Antworten:", "resultLabel":"Dein Ergebnis",
                "labelCorrect":"Richtig.", "labelIncorrect":"Falsch! Bitte versuche es noch einmal.",
                "alternativeIncorrectLabel":"Falsch", "labelCorrectAnswers":"Richtige Antwort(en).",
                "tipButtonLabel":"Tipp anzeigen", "scoreBarLabel":"Du hast :num von :total Punkten erreicht.",
                "progressText":"Fortschritt :num von :total",
                "summaries": h5p_summary_tasks
            },
            "library": "H5P.Summary 1.10",
            "metadata": {
                "contentType": "Summary", "license": "U",
                "title": summary_element_data.get("titleForElement", "Zusammenfassung"),
                "authors": [], "changes": [], "extraTitle": summary_element_data.get("titleForElement", "Zusammenfassung")
            },
            "subContentId": utils_booklet.generate_uuid()
        },
        "useSeparator": "auto"
    }

    chapter3_summary_column = {
        "params": {"content": [chapter3_intro_text, chapter3_summary_element]},
        "library": "H5P.Column 1.18",
        "subContentId": utils_booklet.generate_uuid(),
        "metadata": {
            "contentType": "Column", "license": "U", 
            "title": ch3_data.get("titleForChapter", "Zusammenfassung"),
            "authors": [], "changes": [], "extraTitle": ch3_data.get("titleForChapter", "Zusammenfassung")
        }
    }

    # --- Chapter 4: Question Set ---
    qs_intro_data = ch4_data.get("questionSectionIntro", {})
    chapter4_intro_text_html = f"{qs_intro_data.get('title', '')}{qs_intro_data.get('instruction', '')}"
    chapter4_intro_text = {
        "content": {
            "params": {"text": chapter4_intro_text_html},
            "library": "H5P.AdvancedText 1.1",
            "metadata": {**DEFAULT_H5P_ADVANCED_TEXT_METADATA, "title": "Fragen Einleitung"},
            "subContentId": utils_booklet.generate_uuid()
        },
        "useSeparator": "auto"
    }

    qs_section_data = ch4_data.get("questionSet", {})
    mapped_questions = utils_booklet.map_questions_to_h5p_array(qs_section_data.get("questions", []))
    
    chapter4_question_set = {
        "content": {
            "params": {
                "introPage": { 
                    "showIntroPage": True, "startButtonText": "Quiz starten",
                    "title": qs_section_data.get("introPageTitle", "Verständnisfragen Quiz"),
                    "introduction": qs_section_data.get("introPageIntroduction", "")
                },
                "progressType": "dots", "passPercentage": 50, "disableBackwardsNavigation": False,
                "randomQuestions": True, 
                "poolSize": qs_section_data.get("poolSize", 10),
                "questions": mapped_questions,
                "endGame": {
                    "showResultPage":True,"showSolutionButton":True,"showRetryButton":True,
                    "noResultMessage":"Quiz beendet","message":"Dein Ergebnis:",
                    "scoreBarLabel":"Du hast @score von @total Punkten erreicht.","overallFeedback":[{"from":0,"to":100}],
                    "solutionButtonText":"Lösung anzeigen","retryButtonText":"Wiederholen","finishButtonText":"Beenden",
                    "submitButtonText":"Absenden","showAnimations":False,"skippable":False,"skipButtonText":"Video überspringen"
                },
                "texts": {
                    "prevButton":"Zurück","nextButton":"Weiter","finishButton":"Beenden","submitButton":"Absenden",
                    "textualProgress":"Aktuelle Frage: @current von @total Fragen","jumpToQuestion":"Frage %d von %total",
                    "questionLabel":"Frage","readSpeakerProgress":"Frage @current von @total",
                    "unansweredText":"Unbeantwortet","answeredText":"Beantwortet","currentQuestionText":"Aktuelle Frage",
                    "navigationLabel":"Fragen"
                },
                "override":{"checkButton":True,"showSolutionButton":"off","retryButton":"off"}
            },
            "library": "H5P.QuestionSet 1.20",
            "metadata": {
                "contentType": "Question Set", "license": "U", 
                "title": qs_section_data.get("titleForElement", "Fragenset"),
                "authors": [], "changes": [], "extraTitle": qs_section_data.get("titleForElement", "Fragenset")
            },
            "subContentId": utils_booklet.generate_uuid()
        },
        "useSeparator": "auto"
    }

    chapter4_qs_column = {
        "params": {"content": [chapter4_intro_text, chapter4_question_set]},
        "library": "H5P.Column 1.18",
        "subContentId": utils_booklet.generate_uuid(),
        "metadata": {
            "contentType": "Column", "license": "U", 
            "title": ch4_data.get("titleForChapter", "Verständnisfragen"),
            "authors": [], "changes": [], "extraTitle": ch4_data.get("titleForChapter", "Verständnisfragen")
        }
    }

    # --- Assemble Chapters List ---
    chapters_list = [chapter1_column, chapter2_iframe_column, chapter3_summary_column, chapter4_qs_column]

    # --- Chapter 5: Assignment IFrame (Conditional) ---
    if ch5_assignment_data:
        assignment_url = utils_booklet.generate_assignment_iframe_url(ch5_assignment_data, book_overall_title)
        
        chapter5_assignment_iframe_embed = {
            "content": {
                "params": {
                    "source": assignment_url,
                    "width": "720", # Default width for this type of assignment
                    "height": "1600", # Default height
                    "resizeSupported": True
                },
                "library": "H5P.IFrameEmbed 1.0",
                "metadata": {
                    "contentType": "Iframe Embedder", "license": "U",
                    "title": ch5_assignment_data.get("titleForChapter", "Aufgabe"),
                    "authors": [], "changes": [], "extraTitle": ch5_assignment_data.get("titleForChapter", "Aufgabe")
                },
                "subContentId": utils_booklet.generate_uuid()
            },
            "useSeparator": "auto"
        }

        chapter5_assignment_column = {
            "params": {"content": [chapter5_assignment_iframe_embed]},
            "library": "H5P.Column 1.18",
            "subContentId": utils_booklet.generate_uuid(),
            "metadata": {
                "contentType": "Column", "license": "U", 
                "title": ch5_assignment_data.get("titleForChapter", "Aufgabe"),
                "authors": [], "changes": [], "extraTitle": ch5_assignment_data.get("titleForChapter", "Aufgabe")
            }
        }
        chapters_list.append(chapter5_assignment_column)


    # --- Final Content Structure ---
    content_structure = {
        "showCoverPage": book_data.get("showCoverPage", True),
        "bookCover": book_cover,
        "chapters": chapters_list, # Use the dynamic list
        "behaviour": {
            "baseColor":"#002f6c","defaultTableOfContents":True,"progressIndicators":True,
            "progressAuto":True,"displaySummary":True,"enableRetry":True
        },
        "read":"Öffnen","displayTOC":"Inhaltsverzeichnis anzeigen","hideTOC":"Inhaltsverzeichnis ausblenden",
        "nextPage":"Nächste Seite","previousPage":"Vorherige Seite","chapterCompleted":"Seite abgeschlossen!",
        "partCompleted":"@pages von @total Seiten abgeschlossen","incompleteChapter":"Unvollständige Seite",
        "navigateToTop":"Nach oben springen","markAsFinished":"Ich habe diese Seite abgeschlossen",
        "fullscreen":"Vollbild","exitFullscreen":"Vollbild beenden","bookProgressSubtext":"@count von @total Seiten",
        "interactionsProgressSubtext":"@count von @total Interaktionen","submitReport":"Report absenden",
        "restartLabel":"Neustart","summaryHeader":"Zusammenfassung","allInteractions":"Alle Interaktionen",
        "unansweredInteractions":"Unbeantwortete Interaktionen","scoreText":"@score / @maxscore",
        "leftOutOfTotalCompleted":"@left von @max Interaktionen abgeschlossen","noInteractions":"Keine Interaktionen",
        "score":"Punkte","summaryAndSubmit":"Zusammenfassung und Einsenden",
        "noChapterInteractionBoldText":"Du hast noch keine Seiten bearbeitet.",
        "noChapterInteractionText":"Du musst wenigstens eine Seite bearbeiten, um die Zusammenfassung zu sehen.",
        "yourAnswersAreSubmittedForReview":"Deine Antworten wurden zur Begutachtung versendet!",
        "bookProgress":"Buchfortschritt","interactionsProgress":"Interaktionsfortschritt",
        "totalScoreLabel":"Gesamtpunktzahl",
        "a11y":{"progress":"Seite @page von @total.","menu":"Inhaltsverzeichnis ein- bzw. ausschalten"}
    }
    return content_structure