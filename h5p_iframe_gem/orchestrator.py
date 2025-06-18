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
# SOURCE_QS_BG_IMAGE_PATH is removed as per new content.json

# Target paths within the H5P package (relative to content/)
H5P_INTERNAL_COVER_IMAGE_PATH = "images/img_1.png"
# H5P_INTERNAL_QS_BG_IMAGE_PATH is removed

st.set_page_config(page_title="H5P InteractiveBook Generator (IFrame)", page_icon="📚")

def main():
    st.title("H5P InteractiveBook Generator (IFrame Version)")
    st.markdown("""
        This tool generates H5P interactive book packages with an IFrame embed, summary, and questions.
        Please follow the instructions below.
    """)

    with st.expander("How to Use"):
        st.markdown(f"""
            0. **Generate JSON Content (if needed) with a helper tool or manually, following the examples.**
            1.  **IFrame URL:** Enter the URL of the content to embed in the generated booklet (e.g., a news article, a video player page).
            2.  **JSON Content (Chapters):** Paste JSON data that defines the structure and content for each section in the corresponding text areas.
                -   **General Settings, Book Details & Chapter 1 (Introduction):** Overall book title, cover page information, and introduction chapter content.
                -   **Chapter 2 (IFrame Content):** Introductory text and settings for the IFrame embed.
                -   **Chapter 3 (Summary):** Content for the H5P.Summary element.
                -   **Chapter 4 (Question Set):** Question set chapter content.
                For JSON format, refer to the provided examples or documentation.
                Text fields can include basic HTML formatting like bold (`<strong>`) or headings (`<h2>`).
            3.  **Package Generation:** Click the "Generate H5P Booklet" button.
            4.  **Download:** Download the generated `.h5p` file.

            **About Fixed Images:**
            - `{SOURCE_COVER_IMAGE_PATH.name}` is used for the cover image.
            This image must be placed in the `{TEMPLATES_DIR.name}/` folder.
            
            **H5P Template ZIP:**
            - `{TEMPLATE_ZIP_PATH.name}` is used as the template for the H5P InteractiveBook. It must be placed in the `{TEMPLATES_DIR.name}/` folder.
        """)

    iframe_url_input = st.text_input("👉 1. Enter IFrame URL", placeholder="Example: https://www.srf.ch/play/embed?urn=urn:srf:video:...")
    
    st.subheader("👉 2. Paste JSON Content (Sections)")

    # Default JSON inputs (can be populated with example structures)
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

    json_input_intro_area = st.text_area("Allg. Settings, Buchdetails & Kap. 1 (Einleitung) JSON:", value=default_json_intro, height=200,
                                         help="JSON für Buchtitel, Cover und Einleitungskapitel.")
    json_input_iframe_area = st.text_area("Kapitel 2 (Iframe-Beitrag) JSON:", value=default_json_iframe, height=200,
                                           help="JSON für das Iframe-Kapitel.")
    json_input_summary_area = st.text_area("Kapitel 3 (Zusammenfassung) JSON:", value=default_json_summary, height=200,
                                            help="JSON für das Zusammenfassungskapitel (H5P.Summary).")
    json_input_questions_area = st.text_area("Kapitel 4 (Fragen) JSON:", value=default_json_questions, height=200,
                                             help="JSON für das Fragenkapitel (H5P.QuestionSet).")

    if st.button("👉 3. Generate H5P Booklet"):
        if not iframe_url_input:
            st.error("IFrame URL is not entered.")
            return
        if not json_input_intro_area or not json_input_iframe_area or \
           not json_input_summary_area or not json_input_questions_area:
            st.error("One or more JSON content fields are empty.")
            return

        input_data_intro = None
        input_data_iframe = None
        input_data_summary = None
        input_data_questions = None
        
        try:
            input_data_intro = json.loads(json_input_intro_area)
        except json.JSONDecodeError as e:
            st.error(f"JSON format error in Intro JSON: {e}")
            return
        try:
            input_data_iframe = json.loads(json_input_iframe_area)
        except json.JSONDecodeError as e:
            st.error(f"JSON format error in IFrame JSON: {e}")
            return
        try:
            input_data_summary = json.loads(json_input_summary_area)
        except json.JSONDecodeError as e:
            st.error(f"JSON format error in Summary JSON: {e}")
            return
        try:
            input_data_questions = json.loads(json_input_questions_area)
        except json.JSONDecodeError as e:
            st.error(f"JSON format error in Questions JSON: {e}")
            return

        # Merge JSON inputs
        final_input_data = {
            "iframeUrl": iframe_url_input,
            "book": input_data_intro.get("book", {}),
            "chapter1_introduction": input_data_intro.get("chapter1_introduction", {}),
            "chapter2_iframe": input_data_iframe.get("chapter2_iframe", {}),
            "chapter3_summary": input_data_summary.get("chapter3_summary", {}),
            "chapter4_questions": input_data_questions.get("chapter4_questions", {})
        }
        
        # If iframe_url_input was empty, try to get it from the book JSON as a fallback (optional)
        if not final_input_data["iframeUrl"]:
             final_input_data["iframeUrl"] = input_data_intro.get("book", {}).get("iframeUrl") # Example fallback

        if not final_input_data["iframeUrl"]:
            st.error("No IFrame URL found in the text field or in the Intro JSON.")
            return
        
        st.info(f"IFrame URL: {final_input_data['iframeUrl']} will be used.")

        try:
            st.write("Generating content JSON structure...")
            content_dict = booklet_generator.create_booklet_content_json_structure(
                final_input_data, 
                H5P_INTERNAL_COVER_IMAGE_PATH
                # No QS image path needed
            )
            content_json_str = json.dumps(content_dict, ensure_ascii=False, indent=2)
            # st.json(content_dict) # For debugging

            st.write("Generating h5p.json structure...")
            book_overall_title = final_input_data.get("book", {}).get("title", "Generated InteractiveBook")
            h5p_json_dict = booklet_generator.generate_h5p_json_dict(book_overall_title)
            h5p_json_str = json.dumps(h5p_json_dict, ensure_ascii=False, indent=2)
            # st.json(h5p_json_dict) # For debugging

            images_to_add = [
                (str(SOURCE_COVER_IMAGE_PATH), H5P_INTERNAL_COVER_IMAGE_PATH)
                # No QS background image
            ]
            
            missing_source_images = False
            if not SOURCE_COVER_IMAGE_PATH.exists():
                st.error(f"Required image file not found: {SOURCE_COVER_IMAGE_PATH}")
                missing_source_images = True
            
            if missing_source_images:
                st.error(f"Images must be placed in the `{TEMPLATES_DIR}` folder.")
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