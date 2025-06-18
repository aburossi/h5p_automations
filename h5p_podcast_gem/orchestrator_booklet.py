import streamlit as st
import json
from pathlib import Path
import booklet_generator # Direct import
import utils_booklet   # Direct import

# Define paths (assuming this script is in the same directory as templates/)
PROJECT_ROOT = Path(__file__).parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
TEMPLATE_ZIP_PATH = TEMPLATES_DIR / "template.zip"
SOURCE_COVER_IMAGE_PATH = TEMPLATES_DIR / "img_1.png"
SOURCE_QS_BG_IMAGE_PATH = TEMPLATES_DIR / "img_2.png"

# Target paths within the H5P package (relative to content/)
H5P_INTERNAL_COVER_IMAGE_PATH = "images/img_1.png"
H5P_INTERNAL_QS_BG_IMAGE_PATH = "images/img_2.png"


st.set_page_config(page_title="H5P InteractiveBook Generator", page_icon="📚")

def main():
    st.title("H5P InteractiveBook Generator Utility")
    st.markdown("""
        This tool generates H5P interactive book packages from YouTube links and JSON content.
        Please follow the instructions below.
    """)

    with st.expander("How to Use"):
        st.markdown(f"""
            0. **Generate JSON Content with this [CustomGPT]()
            1.  **YouTube URL:** Enter the URL of the YouTube video to embed in the generated booklet. (This takes precedence over URLs in chapter JSONs)
            2.  **JSON Content (Chapters):** Paste JSON data that defines the structure and content of the corresponding chapter in each text area.
                -   **General Settings and Chapter 1 (Introduction):** Overall book title, cover page information, and introduction chapter content.
                -   **Chapter 2 (Video):** Video chapter content.
                -   **Chapter 3 (Question Set):** Question set chapter content.
                For JSON format, refer to the provided examples or documentation.
                Text fields can include basic HTML formatting like bold (`<strong>`) or headings (`<h2>`).
            3.  **Package Generation:** Click the "Generate H5P Booklet" button.
            4.  **Download:** Download the generated `.h5p` file.

            **About Fixed Images:**
            - `{SOURCE_COVER_IMAGE_PATH.name}` is used for the cover image.
            - `{SOURCE_QS_BG_IMAGE_PATH.name}` is used for the question set background image.
            These images must be placed in the `{TEMPLATES_DIR.name}/` folder.
            
            **H5P Template ZIP:**
            - `{TEMPLATE_ZIP_PATH.name}` is used as the template for the H5P InteractiveBook. It must be placed in the `{TEMPLATES_DIR.name}/` folder.
        """)

    youtube_url_input = st.text_input("👉 1. Enter YouTube URL", placeholder="Example: https://www.youtube.com/watch?v=your_video_id")
    
    st.subheader("👉 2. Paste JSON Content (Chapters)")

    # Default JSON inputs
    default_json_intro = """"""
    default_json_video = """"""
    default_json_questions = """"""

    json_input_intro_area = st.text_area("Kapitel 1: Einleitung & Buchdetails JSON:", value=default_json_intro, height=68, 
                                         help="JSON für Buchtitel, Cover und Einleitungskapitel.")
    json_input_video_area = st.text_area("Kapitel 2: Video JSON:", value=default_json_video, height=68, 
                                         help="JSON für das Videokapitel.")
    json_input_questions_area = st.text_area("Kapitel 3: Fragen JSON:", value=default_json_questions, height=68, 
                                             help="JSON für das Fragenkapitel.")

    if st.button("👉 3. Generate H5P Booklet"):
        if not youtube_url_input:
            st.error("YouTube URL is not entered.")
            return
        if not json_input_intro_area or not json_input_video_area or not json_input_questions_area:
            st.error("One or more JSON content fields are empty.")
            return

        input_data_intro = None
        input_data_video = None
        input_data_questions = None
        
        try:
            input_data_intro = json.loads(json_input_intro_area)
        except json.JSONDecodeError as e:
            st.error(f"JSON format error in Intro JSON: {e}")
            return
        try:
            input_data_video = json.loads(json_input_video_area)
        except json.JSONDecodeError as e:
            st.error(f"JSON format error in Video JSON: {e}")
            return
        try:
            input_data_questions = json.loads(json_input_questions_area)
        except json.JSONDecodeError as e:
            st.error(f"JSON format error in Questions JSON: {e}")
            return

        # Merge JSON inputs
        # The youtube_url_input from the text field takes precedence.
        # Book details are taken from the intro JSON.
        final_input_data = {
            "youtubeUrl": youtube_url_input, # Prioritize text input
            "book": input_data_intro.get("book", {}),
            "chapter1_introduction": input_data_intro.get("chapter1_introduction", {}),
            "chapter2_video": input_data_video.get("chapter2_video", {}),
            "chapter3_questions": input_data_questions.get("chapter3_questions", {})
        }
        
        # If youtube_url_input was empty, try to get it from the intro JSON as a fallback
        if not final_input_data["youtubeUrl"]:
            final_input_data["youtubeUrl"] = input_data_intro.get("youtubeUrl") # Fallback to intro JSON's URL
        
        if not final_input_data["youtubeUrl"]:
             st.error("No YouTube URL found in the text field or in the Intro JSON.")
             return
        
        video_id = utils_booklet.extract_youtube_id(final_input_data["youtubeUrl"])
        if not video_id:
            st.error("Valid YouTube Video ID could not be extracted from the URL. Please check the URL.")
            return
        
        st.info(f"YouTube Video ID: {video_id} has been extracted. ({final_input_data['youtubeUrl']})")

        try:
            st.write("Generating content JSON structure...")
            content_dict = booklet_generator.create_booklet_content_json_structure(
                final_input_data, 
                video_id,
                H5P_INTERNAL_COVER_IMAGE_PATH,
                H5P_INTERNAL_QS_BG_IMAGE_PATH
            )
            content_json_str = json.dumps(content_dict, ensure_ascii=False, indent=2)
            # st.json(content_dict) # For debugging

            st.write("Generating h5p.json structure...")
            book_overall_title = final_input_data.get("book", {}).get("title", "Generated InteractiveBook")
            h5p_json_dict = booklet_generator.generate_h5p_json_dict(book_overall_title)
            h5p_json_str = json.dumps(h5p_json_dict, ensure_ascii=False, indent=2)
            # st.json(h5p_json_dict) # For debugging

            images_to_add = [
                (str(SOURCE_COVER_IMAGE_PATH), H5P_INTERNAL_COVER_IMAGE_PATH),
                (str(SOURCE_QS_BG_IMAGE_PATH), H5P_INTERNAL_QS_BG_IMAGE_PATH)
            ]
            
            missing_source_images = False
            for src_path_str, _ in images_to_add:
                if not Path(src_path_str).exists():
                    st.error(f"Required image file not found: {src_path_str}")
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
                if not clean_title: clean_title = "InteractiveBook"
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