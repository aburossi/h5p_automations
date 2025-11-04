import streamlit as st
import json
from pathlib import Path
import booklet_generator_iframe as booklet_generator # Renamed for clarity
import utils_booklet_iframe as utils_booklet   # Renamed for clarity


# Define paths (assuming this script is in the same directory as templates/)
PROJECT_ROOT = Path(__file__).parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
TEMPLATE_ZIP_PATH = TEMPLATES_DIR / "template.zip"
SOURCE_COVER_IMAGE_PATH = TEMPLATES_DIR / "img_1.png"

# Target paths within the H5P package (relative to content/)
H5P_INTERNAL_COVER_IMAGE_PATH = "images/img_1.png"

st.set_page_config(page_title="H5P InteractiveBook Generator (IFrame)", page_icon="📚")

def main():
    st.title("H5P InteractiveBook Generator (IFrame Version)")
    st.markdown("""
        This tool generates H5P interactive book packages with an IFrame embed, summary, and questions.
        An optional fifth chapter can be added by providing assignment content in the final text area.
    """)

    with st.expander("How to Use"):
        st.markdown(f"""
            0. **Generate JSON Content (if needed) with a helper tool or manually, following the examples.**
            1.  **IFrame URL:** Enter the URL for the IFrame in Chapter 2.
            2.  **JSON Content (Chapters):** Paste JSON data for the first four chapters in the corresponding text areas.
            3.  **(Optional) Chapter 5 Assignment:** To add a final assignment chapter, paste the specific assignment JSON into the fifth text area. If you leave this empty, a standard 4-chapter booklet will be generated. The tool will automatically convert this JSON into a special IFrame URL.
            4.  **Package Generation:** Click the "Generate H5P Booklet" button.
            5.  **Download:** Download the generated `.h5p` file.

            **About Fixed Images:**
            - `{SOURCE_COVER_IMAGE_PATH.name}` is used for the cover image. This image must be placed in the `{TEMPLATES_DIR.name}/` folder.
            
            **H5P Template ZIP:**
            - `{TEMPLATE_ZIP_PATH.name}` is used as the template. It must be placed in the `{TEMPLATES_DIR.name}/` folder.
        """)

    iframe_url_input = st.text_input("👉 1. Enter IFrame URL (for Chapter 2)", placeholder="Example: https://www.srf.ch/play/embed?urn=urn:srf:video:...")
    
    st.subheader("👉 2. Paste JSON Content (Sections)")

    # Default JSON inputs
    default_json_intro = """{
  "book": {
    "title": "POLECO - Mein Beitrag",
    "coverPage": {
      "title": "<h1 style=\\"text-align:center\\">ABUnews</h1>",
      "subtitle": "<h3 style=\\"text-align:center\\">Titel meines Beitrags</h3>"
    },
    "showCoverPage": true
  },
  "chapter1_introduction": {
    "titleForChapter": "Einleitung",
    "introductionContent": {
      "title": "<h2>Das Wichtigste in Kürze</h2>",
      "bulletPoints": [
        "<li>Punkt 1</li>",
        "<li>Punkt 2</li>"
      ],
      "guidanceText": "<hr /><p>Lesen Sie die Definitionen.</p>"
    },
    "accordion": {
      "titleForElement": "Begriffe",
      "definitions": [
        {
          "term": "Begriff A",
          "definition": "<p>Definition A.</p>"
        }
      ]
    }
  }
}"""
    default_json_iframe = """{
  "chapter2_iframe": {
    "titleForChapter": "Beitrag",
    "iframeSectionIntro": {
      "title": "<h2>Externer Beitrag</h2>",
      "instruction": "<p>Sehen Sie sich den Beitrag an.</p>"
    },
    "iframeEmbed": {
      "width": "700",
      "minWidth": "400",
      "height": "500",
      "titleForElement": "Beitrag via Iframe"
    }
  }
}"""
    default_json_summary = """{
  "chapter3_summary": {
    "titleForChapter": "Zusammenfassung",
    "summarySectionIntro":{
        "title": "<h2>Zusammenfassung</h2>",
        "instruction": "<p>Wählen Sie die korrekten Aussagen.</p>"
    },
    "summaryElement": {
      "titleForElement": "Inhaltszusammenfassung",
      "introText": "<p>Wählen Sie die korrekte Aussage.</p>",
      "summaries": [
        {
          "choices": [
            "Korrekte Aussage.",
            "Falsche Aussage."
          ],
          "tip": ""
        }
      ]
    }
  }
}"""
    default_json_questions = """{
  "chapter4_questions": {
    "titleForChapter": "Verständnisfragen",
    "questionSectionIntro": {
      "title": "<h2>Fragen zum Beitrag</h2>",
      "instruction": "<p>Beantworten Sie die Fragen.</p>"
    },
    "questionSet": {
      "titleForElement": "Quiz",
      "introPageTitle": "Quiz starten",
      "questions": [
        {
          "type": "MultipleChoice",
          "question": "<p>Frage 1?</p>",
          "options": [
            {"text": "Antwort A", "is_correct": false, "feedback": "Falsch."},
            {"text": "Antwort B", "is_correct": true, "feedback": "Richtig!"}
          ]
        }
      ]
    }
  }
}"""
    default_json_assignment = """{
  "chapter5_assignment": {
    "titleForChapter": "Stellungnahme",
    "assignmentContent": {
      "title": "<h2>Reflexion und Positionierung</h2>",
      "instructions": [
        "<p>Sie haben sich nun intensiv mit dem Beitrag über die Rolle der Literatur in der aktuellen Demokratiekrise auseinandergesetzt, der im Rahmen der Solothurner Literaturtage diskutiert wurde.</p>",
        "<p>Im Beitrag wurde argumentiert, dass die Literatur eine wichtige Funktion hat: Sie bietet Raum für <strong>Zweifel</strong> an eigenen Überzeugungen und fördert <strong>Empathie</strong> – beides wird als essenziell für die Demokratie beschrieben.</p>",
        "<p>Nehmen Sie nun Stellung zur folgenden Aussage, die auf den Diskussionen im Beitrag basiert:</p>",
        "<p><strong>\\\"Der 'gesunde Menschenverstand' allein ist gefährlich; eine Demokratie braucht stattdessen Bürgerinnen und Bürger, die durch Literatur zum Zweifel an den eigenen Überzeugungen und zu Empathie befähigt werden.\\\"</strong></p>",
        "<p><strong>Anleitung für Ihre Stellungnahme:</strong></p>",
        "<p>Verfassen Sie einen zusammenhängenden Text (ca. 250–400 Wörter), der die folgenden Punkte klar strukturiert (Einleitung, Hauptteil, Schluss) beinhaltet:</p>",
        "<p><ul><li><strong>Position beziehen:</strong> Beginnen Sie damit, ob Sie der oben genannten Aussage zustimmen, sie ablehnen oder differenziert betrachten.</li><li><strong>Argumentation (mit Beleg):</strong> Begründen Sie Ihre Haltung mit mindestens zwei Argumenten, die sich direkt auf die Kernaussagen des Beitrags stützen.</li><li><strong>Bezug 1 (Zweifel vs. M.):</strong> Gehen Sie darauf ein, warum der <strong>'gesunde Menschenverstand'</strong> laut dem Beitrag als 'gefährlich' eingestuft wird und welche Rolle der <strong>Zweifel</strong> spielt.</li><li><strong>Bezug 2 (Empathie):</strong> Erläutern Sie, wie Literatur <strong>Empathie</strong> für andere Lebenswelten fördern kann und warum dies für die Demokratie wichtig ist.</li><li><strong>Reflexion (Bürger):</strong> Schliessen Sie Ihre Stellungnahme mit einem kurzen Fazit, das auf die Idee der <strong>'wachsamen und engagierten Bürger'</strong> eingeht.</li></ul></p>",
        "<p><strong>Ziel:</strong> Zeigen Sie, dass Sie die zentralen Konzepte (Zweifel, Empathie, wachsame Bürger) aus dem Beitrag verstanden haben und auf eine aktuelle Debatte anwenden können.</p>"
      ]
    }
  }
}"""

    json_input_intro_area = st.text_area("Allg. Settings, Buchdetails & Kap. 1 (Einleitung) JSON:", value=default_json_intro, height=200)
    json_input_iframe_area = st.text_area("Kapitel 2 (Iframe-Beitrag) JSON:", value=default_json_iframe, height=200)
    json_input_summary_area = st.text_area("Kapitel 3 (Zusammenfassung) JSON:", value=default_json_summary, height=200)
    json_input_questions_area = st.text_area("Kapitel 4 (Fragen) JSON:", value=default_json_questions, height=200)
    
    st.subheader("👉 3. (Optional) Paste Assignment Content for Chapter 5")
    json_input_assignment_area = st.text_area("Kapitel 5 (Text-Auftrag) JSON:", value=default_json_assignment, height=200,
                                              help="Paste JSON for the final assignment. Leave empty to generate a 4-chapter booklet.")

    if st.button("👉 4. Generate H5P Booklet"):
        if not iframe_url_input:
            st.error("IFrame URL for Chapter 2 is not entered.")
            return
        if not all([json_input_intro_area, json_input_iframe_area, json_input_summary_area, json_input_questions_area]):
            st.error("One or more of the first four JSON content fields are empty.")
            return

        try:
            input_data_intro = json.loads(json_input_intro_area)
            input_data_iframe = json.loads(json_input_iframe_area)
            input_data_summary = json.loads(json_input_summary_area)
            input_data_questions = json.loads(json_input_questions_area)
            
            input_data_assignment = None
            if json_input_assignment_area.strip():
                input_data_assignment = json.loads(json_input_assignment_area)

        except json.JSONDecodeError as e:
            st.error(f"JSON format error: {e}")
            return

        # Merge JSON inputs
        final_input_data = {
            "iframeUrl": iframe_url_input,
            "book": input_data_intro.get("book", {}),
            "chapter1_introduction": input_data_intro.get("chapter1_introduction", {}),
            "chapter2_iframe": input_data_iframe.get("chapter2_iframe", {}),
            "chapter3_summary": input_data_summary.get("chapter3_summary", {}),
            "chapter4_questions": input_data_questions.get("chapter4_questions", {}),
            "chapter5_assignment": input_data_assignment.get("chapter5_assignment", {}) if input_data_assignment else None
        }
        
        if not final_input_data["iframeUrl"]:
            st.error("No IFrame URL found in the text field for Chapter 2.")
            return
        
        st.info(f"IFrame URL (Chapter 2): {final_input_data['iframeUrl']} will be used.")
        if final_input_data["chapter5_assignment"]:
            st.info("Content for Chapter 5 provided. A 5-chapter booklet will be generated.")
        else:
            st.info("No content for Chapter 5. A 4-chapter booklet will be generated.")

        try:
            book_overall_title = final_input_data.get("book", {}).get("title", "Generated InteractiveBook")

            st.write("Generating content JSON structure...")
            content_dict = booklet_generator.create_booklet_content_json_structure(
                final_input_data, 
                H5P_INTERNAL_COVER_IMAGE_PATH,
                book_overall_title
            )
            content_json_str = json.dumps(content_dict, ensure_ascii=False, indent=2)

            st.write("Generating h5p.json structure...")
            h5p_json_dict = booklet_generator.generate_h5p_json_dict(book_overall_title)
            h5p_json_str = json.dumps(h5p_json_dict, ensure_ascii=False, indent=2)

            images_to_add = [
                (str(SOURCE_COVER_IMAGE_PATH), H5P_INTERNAL_COVER_IMAGE_PATH)
            ]
            
            if not SOURCE_COVER_IMAGE_PATH.exists():
                st.error(f"Required image file not found: {SOURCE_COVER_IMAGE_PATH}")
                st.error(f"Image must be placed in the `{TEMPLATES_DIR}` folder.")
                return

            if not TEMPLATE_ZIP_PATH.exists():
                st.error(f"H5P Template ZIP file not found: {TEMPLATE_ZIP_PATH}")
                st.error(f"Template ZIP must be placed in the `{TEMPLATES_DIR}` folder.")
                return

            st.write("Creating H5P package...")
            h5p_package_bytes = utils_booklet.create_h5p_package(
                content_json_str,
                h5p_json_str,
                str(TEMPLATE_ZIP_PATH),
                images_to_add
            )

            if h5p_package_bytes:
                st.success("H5P Booklet successfully generated!")
                
                clean_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in book_overall_title)
                clean_title = "_".join(clean_title.split()) 
                if not clean_title: clean_title = "InteractiveBook_IFrame"
                download_filename = f"{clean_title}.h5p"
                
                st.download_button(
                    label="💾 Download H5P Booklet",
                    data=h5p_package_bytes,
                    file_name=download_filename,
                    mime="application/zip"
                )
            else:
                st.error("H5P package generation failed. Please check logs.")

        except Exception as e:
            st.error(f"Error during package generation: {e}")
            import traceback
            st.text(traceback.format_exc())

if __name__ == "__main__":
    main()