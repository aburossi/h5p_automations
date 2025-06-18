import json
import utils_booklet # Direct import

# --- H5P Structure Default Values (mostly from dummy content.json) ---
DEFAULT_H5P_IMAGE_PARAMS_BASE = { # Base for file part, path will be set
    "mime": "image/png", "copyright": {"license": "U"}, "width": 52, "height": 52
}
DEFAULT_H5P_IMAGE_WRAPPER_PARAMS = { # Params for H5P.Image itself
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
    """Generates the Python dictionary for h5p.json."""
    return {
        "embedTypes": ["iframe"],
        "language": "en",
        "defaultLanguage": "de",
        "license": "U",
        "extraTitle": book_overall_title,
        "title": book_overall_title,
        "mainLibrary": "H5P.InteractiveBook",
        "preloadedDependencies": [
            {"machineName":"H5P.Image","majorVersion":1,"minorVersion":1},
            {"machineName":"H5P.AdvancedText","majorVersion":1,"minorVersion":1},
            {"machineName":"H5P.Accordion","majorVersion":1,"minorVersion":0},
            {"machineName":"FontAwesome","majorVersion":4,"minorVersion":5},
            {"machineName":"H5P.Column","majorVersion":1,"minorVersion":18},
            {"machineName":"H5P.Summary","majorVersion":1,"minorVersion":10},
            {"machineName":"H5P.JoubelUI","majorVersion":1,"minorVersion":3},
            {"machineName":"H5P.Transition","majorVersion":1,"minorVersion":0},
            {"machineName":"H5P.FontIcons","majorVersion":1,"minorVersion":0},
            {"machineName":"H5P.Question","majorVersion":1,"minorVersion":5},
            {"machineName":"H5P.InteractiveVideo","majorVersion":1,"minorVersion":27},
            {"machineName":"jQuery.ui","majorVersion":1,"minorVersion":10},
            {"machineName":"H5P.Video","majorVersion":1,"minorVersion":6},
            {"machineName":"H5P.DragNBar","majorVersion":1,"minorVersion":5},
            {"machineName":"H5P.DragNDrop","majorVersion":1,"minorVersion":1},
            {"machineName":"H5P.DragNResize","majorVersion":1,"minorVersion":2},
            {"machineName":"H5P.MultiChoice","majorVersion":1,"minorVersion":16},
            {"machineName":"H5P.TrueFalse","majorVersion":1,"minorVersion":8},
            {"machineName":"H5P.QuestionSet","majorVersion":1,"minorVersion":20},
            {"machineName":"H5P.InteractiveBook","majorVersion":1,"minorVersion":11}
        ]
    }

# --- content.json generation ---
def create_booklet_content_json_structure(data: dict, video_id: str | None, 
                                          h5p_cover_image_path: str, 
                                          h5p_qs_image_path: str) -> dict:
    """
    Creates the Python dictionary for the H5P.InteractiveBook content.json.
    """
    book_data = data.get("book", {})
    ch1_data = data.get("chapter1_introduction", {})
    ch2_data = data.get("chapter2_video", {})
    ch3_data = data.get("chapter3_questions", {})

    cover_page_data = book_data.get("coverPage", {})
    cover_description_html = f"{cover_page_data.get('title', '<h1>Cover Title</h1>')}{cover_page_data.get('subtitle', '')}"
    
    cover_image_file_params = {**DEFAULT_H5P_IMAGE_PARAMS_BASE, "path": h5p_cover_image_path}
    cover_image_full_params = {**DEFAULT_H5P_IMAGE_WRAPPER_PARAMS, "file": cover_image_file_params}

    book_cover = {
        "coverDescription": cover_description_html,
        "coverMedium": {
            "params": cover_image_full_params,
            "library": "H5P.Image 1.1",
            "metadata": {**DEFAULT_H5P_IMAGE_METADATA, "title": "Cover Bild"},
            "subContentId": utils_booklet.generate_uuid()
        }
    }

    intro_content_data = ch1_data.get("introductionContent", {})
    learning_objectives_list = intro_content_data.get("learningObjectives", [])
    learning_objectives_html = "".join(learning_objectives_list)
    
    if learning_objectives_html and not learning_objectives_html.strip().lower().startswith("<ul>") and learning_objectives_list:
        learning_objectives_html_complete = f"<ul>{learning_objectives_html}</ul>"
    else:
        learning_objectives_html_complete = learning_objectives_html

    intro_text_html = (
        f"{intro_content_data.get('title', '')}"
        f"{intro_content_data.get('guidanceText', '')}"
        f"{learning_objectives_html_complete}"
        "<hr /><p>Lesen Sie zuerst die Definitionen der Begriffen hier unten. Sie werden im Video weiter vertieft.</p>"
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
                "metadata": {**DEFAULT_H5P_ADVANCED_TEXT_METADATA, "title": f"Definition: {definition_item.get('term', '')}"}
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

    video_section_intro_data = ch2_data.get("videoSectionIntro", {})
    chapter2_text_html = f"{video_section_intro_data.get('title', '')}{video_section_intro_data.get('instruction', '')}"
    chapter2_text = {
        "content": {
            "params": {"text": chapter2_text_html},
            "library": "H5P.AdvancedText 1.1",
            "metadata": {**DEFAULT_H5P_ADVANCED_TEXT_METADATA, "title": "Videoeinleitung"},
            "subContentId": utils_booklet.generate_uuid()
        },
        "useSeparator": "auto"
    }

    interactive_video_section_data = ch2_data.get("interactiveVideo", {})
    iv_interactions = []
    # Loop through each summary interaction pop-up defined in the input JSON
    for summary_interaction_item in interactive_video_section_data.get("summaries", []):
        h5p_summary_tasks = [] # This will hold the tasks for *this specific* pop-up

        # NEW: Loop through each statementGroup within this summary interaction item
        for group in summary_interaction_item.get("statementGroups", []):
            h5p_statement_choices = []
            correct_statement_text = ""
            incorrect_statement_texts = []

            for stmt_obj in group.get("statements", []):
                if stmt_obj.get("isCorrect"):
                    correct_statement_text = stmt_obj.get("text", "")
                else:
                    incorrect_statement_texts.append(stmt_obj.get("text", ""))
            
            if correct_statement_text:
                h5p_statement_choices = [correct_statement_text] + incorrect_statement_texts
            elif incorrect_statement_texts: 
                 h5p_statement_choices = incorrect_statement_texts
            
            # Each group becomes one task in H5P.Summary's "summaries" array
            h5p_summary_tasks.append({
                "summary": h5p_statement_choices, # Array of choice strings for this task
                "subContentId": utils_booklet.generate_uuid(),
                "tip": group.get("tip", "") # Tip specific to this group
            })

        # If no statementGroups were processed, h5p_summary_tasks will be empty.
        # H5P.Summary might require at least one task, so consider a fallback or log a warning.
        if not h5p_summary_tasks:
            # Add a default placeholder task if none were generated to avoid H5P errors
            # Or, you might choose to skip this interaction entirely if no valid groups.
             utils_booklet.logger.warning(f"No statement groups found for interaction '{summary_interaction_item.get('interactionTitle', 'N/A')}'. Adding a placeholder task.")
             h5p_summary_tasks.append({
                 "summary": ["Placeholder - no statements provided"],
                 "subContentId": utils_booklet.generate_uuid(),
                 "tip": "Input JSON had no statement groups for this summary."
             })


        iv_interactions.append({
            "x": 3.149, "y": 5.594, "width": 37.5, "height": 20,
            # MODIFIED PART STARTS HERE
            "duration": {
                "from": summary_interaction_item.get("startTime", 0) + 3, 
                "to": summary_interaction_item.get("startTime", 0) + 3 + 1 # Or (summary_interaction_item.get("startTime", 0) + 2)
            },
            "libraryTitle": "Statements", # Corresponds to H5P.Summary in the editor UI
            "action": {
                "library": "H5P.Summary 1.10",
                "params": {
                    "intro": summary_interaction_item.get("introText", "<p>Wähle die korrekten Aussagen.</p>"),
                    "overallFeedback": [{"from": 0, "to": 100}],
                    "solvedLabel":"Fortschritt:", "scoreLabel":"Falsche Antworten:", "resultLabel":"Dein Ergebnis",
                    "labelCorrect":"Richtig.", "labelIncorrect":"Falsch! Bitte versuche es noch einmal.",
                    "alternativeIncorrectLabel":"Falsch", "labelCorrectAnswers":"Richtige Antwort(en).",
                    "tipButtonLabel":"Tipp anzeigen", "scoreBarLabel":"Du hast :num von :total Punkten erreicht.",
                    "progressText":"Fortschritt :num von :total",
                    "summaries": h5p_summary_tasks # MODIFIED: This is now an array of tasks
                },
                "subContentId": utils_booklet.generate_uuid(),
                "metadata": {
                    "contentType": "Summary", "license": "U", 
                    "title": summary_interaction_item.get("interactionTitle", "Zusammenfassung"),
                    "authors": [], "changes": [], "extraTitle": summary_interaction_item.get("interactionTitle", "Zusammenfassung")
                }
            },
            "pause": True, "displayType": "poster", "buttonOnMobile": False,
            "adaptivity": {"correct": {"allowOptOut": False, "message": ""}, "wrong": {"allowOptOut": False, "message": ""}},
            "label": ""
        })
    
    youtube_path = f"https://www.youtube.com/watch?v={video_id}" if video_id else ""
    
    video_endscreen_time = 432 
    if interactive_video_section_data.get("videoDurationForEndscreen"):
        video_endscreen_time = interactive_video_section_data.get("videoDurationForEndscreen")

    chapter2_interactive_video = {
        "content": {
            "params": {
                "interactiveVideo": {
                    "video": {
                        "startScreenOptions": {"title": "Interaktives Video", "hideStartTitle": False},
                        "textTracks": {"videoTrack": [{"label":"Untertitel","kind":"subtitles","srcLang":"en"}]},
                        "files": [{"path": youtube_path, "mime": "video/YouTube", "copyright": {"license": "U"}, "aspectRatio":"16:9"}]
                    },
                    "assets": {"interactions": iv_interactions, "bookmarks": [], 
                               "endscreens": [
                                   {"time":0,"label":"0:00 Antwortübermittlung"},
                                   {"time": video_endscreen_time,"label":f"{video_endscreen_time//60}:{video_endscreen_time%60:02d} Antwortübermittlung"}
                                ]
                              },
                    "summary": { 
                        "task": {
                            "library":"H5P.Summary 1.10",
                            "params": {
                                "intro":"Wähle die korrekte Aussage.", "overallFeedback":[{"from":0,"to":100}],
                                "solvedLabel":"Fortschritt:", "scoreLabel":"Falsche Antworten:", "resultLabel":"Dein Ergebnis",
                                "labelCorrect":"Richtig.", "labelIncorrect":"Falsch! Bitte versuche es noch einmal.",
                                "alternativeIncorrectLabel":"Falsch", "labelCorrectAnswers":"Richtige Antwort(en).",
                                "tipButtonLabel":"Tipp anzeigen", "scoreBarLabel":"Du hast :num von :total Punkten erreicht.",
                                "progressText":"Fortschritt :num von :total",
                                "summaries":[{"subContentId": utils_booklet.generate_uuid(),"tip":""}]
                            },
                            "subContentId": utils_booklet.generate_uuid(),
                            "metadata":{"contentType":"Summary","license":"U","title":"Video End-Summary"}
                        },
                        "displayAt":3 
                    }
                },
                "override": { 
                    "autoplay":False,"loop":False,"showBookmarksmenuOnLoad":False,"showRewind10":True,
                    "preventSkippingMode":"none","deactivateSound":False,"showSolutionButton":"off","retryButton":"off"
                },
                "l10n": { 
                    "interaction":"Interaktion", "play":"Abspielen", "pause":"Pause", "mute":"Stummschalten, derzeit nicht laut geschaltet",
                    "unmute":"Laut schalten, derzeit stumm geschaltet", "quality":"Videoqualität", "captions":"Untertitel",
                    "close":"Schließen", "fullscreen":"Vollbild", "exitFullscreen":"Vollbild beenden",
                    "summary":"Zusammenfassung öffnen", "bookmarks":"Lesezeichen", "endscreen":"Einsendebildschirm",
                    "defaultAdaptivitySeekLabel":"Fortfahren", "continueWithVideo":"Video fortsetzen",
                    "more":"Mehr Abspieloptionen", "playbackRate":"Abspielgeschwindigkeit", "rewind10":"10 Sekunden zurückspulen",
                    "navDisabled":"Vor- und Zurückspulen ist deaktiviert", "navForwardDisabled":"Navigation vorwärts ist deaktiviert",
                    "sndDisabled":"Ton ist deaktiviert",
                    "requiresCompletionWarning":"Es müssen alle Fragen richtig beantwortet werden, um weitermachen zu können.",
                    "back":"Zurück", "hours":"Stunden", "minutes":"Minuten", "seconds":"Sekunden",
                    "currentTime":"Aktuelle Zeit:", "totalTime":"Gesamtzeit:",
                    "singleInteractionAnnouncement":"Interaktion ist erschienen:",
                    "multipleInteractionsAnnouncement":"Mehrere Interaktionen sind erschienen.",
                    "videoPausedAnnouncement":"Video ist angehalten", "content":"Inhalt", "answered":"@answered beantwortet",
                    "endcardTitle":"@answered Frage(n) beantwortet",
                    "endcardInformation":"Du hast @answered Fragen beantwortet.",
                    "endcardInformationOnSubmitButtonDisabled":"Du hast @answered Fragen beantwortet. Klicke unten, um deine Ergebnisse abzusenden.",
                    "endcardInformationNoAnswers":"Du hast noch keine Fragen beantwortet.",
                    "endcardInformationMustHaveAnswer":"Du musst mindestens eine Frage beantworten, um deine Antworten absenden zu können.",
                    "endcardSubmitButton":"Antworten absenden", "endcardSubmitMessage":"Deine Antworten wurden abgeschickt!",
                    "endcardTableRowAnswered":"Beantwortete Fragen", "endcardTableRowScore":"Punkte",
                    "endcardAnsweredScore":"beantwortet",
                    "endCardTableRowSummaryWithScore":"Du hast @score von @total Punkten für die @question erhalten, die bei @minutes Minuten und @seconds Sekunden erschienen ist.",
                    "endCardTableRowSummaryWithoutScore":"Du hast die @question beantwortet, die bei @minutes Minuten und @seconds Sekunden erschienen ist.",
                    "videoProgressBar":"Video-Fortschritt",
                    "howToCreateInteractions":"Spiele das Video ab, um mit dem Erstellen von Interaktionen zu beginnen"
                }
            },
            "library": "H5P.InteractiveVideo 1.27",
            "metadata": {
                "contentType": "Interactive Video", "license": "U", 
                "title": interactive_video_section_data.get("titleForElement", "Interaktives Video"),
                "authors": [], "changes": [], "extraTitle": interactive_video_section_data.get("titleForElement", "Interaktives Video")
            },
            "subContentId": utils_booklet.generate_uuid()
        },
        "useSeparator": "auto"
    }

    chapter2_column = {
        "params": {"content": [chapter2_text, chapter2_interactive_video]},
        "library": "H5P.Column 1.18",
        "subContentId": utils_booklet.generate_uuid(),
        "metadata": {
            "contentType": "Column", "license": "U", "title": ch2_data.get("titleForChapter", "Video"),
            "authors": [], "changes": [], "extraTitle": ch2_data.get("titleForChapter", "Video")
        }
    }
    
    qs_intro_data = ch3_data.get("questionSectionIntro", {})
    chapter3_text_html = f"{qs_intro_data.get('title', '')}{qs_intro_data.get('instruction', '')}"
    chapter3_text = {
        "content": {
            "params": {"text": chapter3_text_html},
            "library": "H5P.AdvancedText 1.1",
            "metadata": {**DEFAULT_H5P_ADVANCED_TEXT_METADATA, "title": "Fragen Einleitung"},
            "subContentId": utils_booklet.generate_uuid()
        },
        "useSeparator": "auto"
    }

    qs_section_data = ch3_data.get("questionSet", {})
    mapped_questions = utils_booklet.map_questions_to_h5p_array(qs_section_data.get("questions", []))
    
    qs_background_file_params = {**DEFAULT_H5P_IMAGE_PARAMS_BASE, "path": h5p_qs_image_path}
    
    chapter3_question_set = {
        "content": {
            "params": {
                "introPage": { 
                    "showIntroPage": True, "startButtonText": "Quiz starten",
                    "title": qs_section_data.get("titleForElement", "Verständnisfragen"), 
                    "introduction": "" 
                },
                "progressType": "dots", "passPercentage": 50, "disableBackwardsNavigation": False,
                "randomQuestions": True, 
                "poolSize": 10,
                "questions": mapped_questions,
                "backgroundImage": qs_background_file_params, # This should be just the file object, not the wrapper
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

    chapter3_column = {
        "params": {"content": [chapter3_text, chapter3_question_set]},
        "library": "H5P.Column 1.18",
        "subContentId": utils_booklet.generate_uuid(),
        "metadata": {
            "contentType": "Column", "license": "U", "title": ch3_data.get("titleForChapter", "Verständnisfragen"),
            "authors": [], "changes": [], "extraTitle": ch3_data.get("titleForChapter", "Verständnisfragen")
        }
    }

    content_structure = {
        "showCoverPage": book_data.get("showCoverPage", True),
        "bookCover": book_cover,
        "chapters": [chapter1_column, chapter2_column, chapter3_column],
        "behaviour": { 
            "baseColor":"#1768c4","defaultTableOfContents":True,"progressIndicators":True,
            "progressAuto":True,"displaySummary":True,"enableRetry":True
        },
        # Full list of l10n strings from the dummy H5P.InteractiveBook content.json
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