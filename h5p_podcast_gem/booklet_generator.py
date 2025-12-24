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
            {"machineName":"H5P.SingleChoiceSet","majorVersion":1,"minorVersion":11},
            {"machineName":"H5P.DragText","majorVersion":1,"minorVersion":10},
            {"machineName":"H5P.InteractiveBook","majorVersion":1,"minorVersion":11}
        ]
    }

# --- Helper functions for creating different interaction types ---

def create_summary_h5p(interaction_data: dict) -> dict:
    """Creates an H5P.Summary interaction dictionary."""
    h5p_summary_tasks = []
    for group in interaction_data.get("statementGroups", []):
        choices = []
        correct_statement = ""
        incorrect_statements = []
        for stmt in group.get("statements", []):
            if stmt.get("isCorrect"):
                correct_statement = stmt.get("text", "")
            else:
                incorrect_statements.append(stmt.get("text", ""))
        
        if correct_statement:
            choices = [correct_statement] + incorrect_statements
        elif incorrect_statements:
            choices = incorrect_statements
        
        h5p_summary_tasks.append({
            "summary": choices,
            "subContentId": utils_booklet.generate_uuid(),
            "tip": group.get("tip", "")
        })

    return {
        "library": "H5P.Summary 1.10",
        "params": {
            "intro": interaction_data.get("introText", "<p>Wähle die korrekten Aussagen.</p>"),
            "overallFeedback": [{"from": 0, "to": 100}],
            "solvedLabel":"Fortschritt:", "scoreLabel":"Falsche Antworten:", "resultLabel":"Dein Ergebnis",
            "labelCorrect":"Richtig.", "labelIncorrect":"Falsch! Bitte versuche es noch einmal.",
            "alternativeIncorrectLabel":"Falsch", "labelCorrectAnswers":"Richtige Antwort(en).",
            "tipButtonLabel":"Tipp anzeigen", "scoreBarLabel":"Du hast :num von :total Punkten erreicht.",
            "progressText":"Fortschritt :num von :total",
            "summaries": h5p_summary_tasks
        },
        "subContentId": utils_booklet.generate_uuid(),
        "metadata": {
            "contentType": "Summary", "license": "U", 
            "title": interaction_data.get("interactionTitle", "Zusammenfassung"),
            "authors": [], "changes": [], "extraTitle": interaction_data.get("interactionTitle", "Zusammenfassung")
        }
    }

def create_single_choice_set_h5p(interaction_data: dict) -> dict:
    """Creates an H5P.SingleChoiceSet interaction dictionary."""
    h5p_choices = []
    for choice_item in interaction_data.get("choices", []):
        h5p_choices.append({
            "question": choice_item.get("question", ""),
            "answers": choice_item.get("answers", []),
            "subContentId": utils_booklet.generate_uuid()
        })

    return {
        "library": "H5P.SingleChoiceSet 1.11",
        "params": {
            "overallFeedback": [{"from": 0, "to": 100}],
            "behaviour": {"autoContinue": True, "timeoutCorrect": 1000, "timeoutWrong": 2000, "soundEffectsEnabled": False, "enableRetry": False, "enableSolutionsButton": False, "passPercentage": 100},
            "l10n": {"nextButtonLabel": "Weiter", "showSolutionButtonLabel": "Lösung anzeigen", "retryButtonLabel": "Wiederholen", "solutionViewTitle": "Lösung", "correctText": "Richtig!", "incorrectText": "Falsch!", "shouldSelect": "Hätte gewählt werden müssen", "shouldNotSelect": "Hätte nicht gewählt werden sollen", "muteButtonLabel": "Stumm schalten", "closeButtonLabel": "Schließen", "slideOfTotal": "Seite :num von :total", "scoreBarLabel": "Du hast :num von :total Punkten erreicht.", "solutionListQuestionNumber": "Frage :num", "a11yShowSolution": "Die Lösung anzeigen. Die richtigen Lösungen werden in der Aufgabe angezeigt.", "a11yRetry": "Die Aufgabe wiederholen. Alle Versuche werden zurückgesetzt und die Aufgabe wird erneut gestartet."},
            "choices": h5p_choices
        },
        "subContentId": utils_booklet.generate_uuid(),
        "metadata": {
            "contentType": "Single Choice Set", "license": "U", 
            "title": interaction_data.get("interactionTitle", "Single Choice"),
            "authors": [], "changes": [], "extraTitle": interaction_data.get("interactionTitle", "Single Choice")
        }
    }

def create_drag_the_words_h5p(interaction_data: dict) -> dict:
    """Creates an H5P.DragText interaction dictionary."""
    distractors_input = interaction_data.get("distractors", "")
    distractors_h5p = ""
    if distractors_input:
        # Convert "word1, word2" to "*word1* *word2*"
        distractors_list = [f"*{word.strip()}*" for word in distractors_input.split(',') if word.strip()]
        distractors_h5p = " ".join(distractors_list)

    return {
        "library": "H5P.DragText 1.10",
        "params": {
            "media": {"disableImageZooming": False},
            "taskDescription": interaction_data.get("taskDescription", "Ziehe die Wörter in die richtigen Felder!"),
            "textField": interaction_data.get("textField", "Lückentext hier. *Lücke*."),
            "distractors": distractors_h5p,
            "overallFeedback": [{"from": 0, "to": 100}],
            "checkAnswer": "Überprüfen", "tryAgain": "Wiederholen", "showSolution": "Lösung anzeigen",
            "correctText": "Richtig!", "incorrectText": "Falsch!",
            "behaviour": {"enableRetry": True, "enableSolutionsButton": True, "enableCheckButton": True, "instantFeedback": False},
            "scoreBarLabel": "Du hast :num von :total Punkten erreicht."
        },
        "subContentId": utils_booklet.generate_uuid(),
        "metadata": {
            "contentType": "Drag the Words", "license": "U", 
            "title": interaction_data.get("interactionTitle", "Drag the Words"),
            "authors": [], "changes": [], "extraTitle": interaction_data.get("interactionTitle", "Drag the Words")
        }
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
    
    # NEW: Loop through the generic 'interactions' array
    for interaction_item in interactive_video_section_data.get("interactions", []):
        interaction_type = interaction_item.get("type")
        h5p_action = None

        if interaction_type == "Summary":
            h5p_action = create_summary_h5p(interaction_item)
        elif interaction_type == "SingleChoiceSet":
            h5p_action = create_single_choice_set_h5p(interaction_item)
        elif interaction_type == "DragTheWords":
            h5p_action = create_drag_the_words_h5p(interaction_item)
        else:
            utils_booklet.logger.warning(f"Unknown interaction type '{interaction_type}' found. Skipping.")
            continue

        if h5p_action:
            iv_interactions.append({
                "x": 3, "y": 5, "width": 40, "height": 20, # Generic position
                "duration": {
                    "from": interaction_item.get("startTime", 0),
                    "to": interaction_item.get("startTime", 0) + 1
                },
                "action": h5p_action,
                "pause": True,
                "displayType": "poster",
                "buttonOnMobile": False,
                "adaptivity": {"correct": {"allowOptOut": False, "message": ""}, "wrong": {"allowOptOut": False, "message": ""}},
                "label": ""
            })

    # NEW: Build the final summary task for the end of the video
    final_summary_data = interactive_video_section_data.get("finalSummary")
    final_summary_task = None
    if final_summary_data:
        # Re-use the summary creation helper, as the structure is identical
        final_summary_task = create_summary_h5p(final_summary_data)

    # Fallback to a default empty summary if none is provided in the JSON
    if not final_summary_task:
        final_summary_task = {
            "library":"H5P.Summary 1.10",
            "params": {
                "intro":"Wähle die korrekte Aussage.", "overallFeedback":[{"from":0,"to":100}],
                "summaries":[{"subContentId": utils_booklet.generate_uuid(),"tip":""}]
            },
            "subContentId": utils_booklet.generate_uuid(),
            "metadata":{"contentType":"Summary","license":"U","title":"Video End-Summary"}
        }

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
                                   {"time": video_endscreen_time,"label":f"{video_endscreen_time//60}:{video_endscreen_time%60:02d} Antwortübermittlung"}
                                ]
                              },
                    "summary": { 
                        "task": final_summary_task, # Use the generated or fallback final summary
                        "displayAt": 3 
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
                "backgroundImage": qs_background_file_params,
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