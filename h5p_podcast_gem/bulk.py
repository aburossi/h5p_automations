import streamlit as st
import json
from pathlib import Path
import booklet_generator  # Direct import
import utils_booklet    # Direct import
import re               # For Markdown parsing
import io               # For zipping files
import zipfile          # For zipping files
import traceback        # For detailed error logging

# Define paths (assuming this script is in the same directory as templates/)
PROJECT_ROOT = Path(__file__).parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
TEMPLATE_ZIP_PATH = TEMPLATES_DIR / "template.zip"
SOURCE_COVER_IMAGE_PATH = TEMPLATES_DIR / "img_1.png"
SOURCE_QS_BG_IMAGE_PATH = TEMPLATES_DIR / "img_2.png"

# Target paths within the H5P package (relative to content/)
H5P_INTERNAL_COVER_IMAGE_PATH = "images/img_1.png"
H5P_INTERNAL_QS_BG_IMAGE_PATH = "images/img_2.png"

def parse_md_file_content(md_content: str) -> tuple[str | None, str | None, str | None, str | None]:
    """
    Parses the MD file content to extract the YouTube URL and the three JSON strings.
    Now looks for ```markdown code blocks.
    Returns (youtube_url, json_intro_str, json_video_str, json_questions_str)
    """
    youtube_url = None
    json_intro_str = None
    json_video_str = None
    json_questions_str = None

    # MODIFIED Regex: Changed from ```json to ```markdown
    pattern = re.compile(r"## Response Block (\d)\s*```markdown\s*([\s\S]*?)\s*```", re.MULTILINE)
    matches = pattern.findall(md_content)
    
    parsed_blocks = {int(num_str): data_str for num_str, data_str in matches}

    json_intro_str = parsed_blocks.get(1)
    json_video_str = parsed_blocks.get(2)
    json_questions_str = parsed_blocks.get(3)

    if json_intro_str:
        try:
            # Extract youtubeUrl from the first block's JSON content
            temp_data = json.loads(json_intro_str)
            youtube_url = temp_data.get("youtubeUrl")
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON from Block 1 in MD (for youtubeUrl extraction): {json.JSONDecodeError}")
            
    return youtube_url, json_intro_str, json_video_str, json_questions_str

def do_h5p_generation(
    youtube_url_override: str | None, 
    json_input_intro_area_str: str | None,
    json_input_video_area_str: str | None,
    json_input_questions_area_str: str | None
):
    """
    Core H5P generation logic.
    Returns a tuple: (h5p_package_bytes, download_filename, error_message)
    error_message is None on success.
    """
    if not json_input_intro_area_str or not json_input_video_area_str or not json_input_questions_area_str:
        return None, None, "One or more JSON content fields are empty or missing from the MD file."

    input_data_intro = None
    input_data_video = None
    input_data_questions = None
    
    try:
        input_data_intro = json.loads(json_input_intro_area_str)
    except json.JSONDecodeError as e:
        return None, None, f"JSON format error in Intro JSON (Block 1): {e}"
    try:
        input_data_video = json.loads(json_input_video_area_str)
    except json.JSONDecodeError as e:
        return None, None, f"JSON format error in Video JSON (Block 2): {e}"
    try:
        input_data_questions = json.loads(json_input_questions_area_str)
    except json.JSONDecodeError as e:
        return None, None, f"JSON format error in Questions JSON (Block 3): {e}"

    final_input_data = {
        "youtubeUrl": youtube_url_override, # Prioritize URL from MD (passed as youtube_url_override)
        "book": input_data_intro.get("book", {}),
        "chapter1_introduction": input_data_intro.get("chapter1_introduction", {}),
        "chapter2_video": input_data_video.get("chapter2_video", {}), # Expects "chapter2_video" key in JSON from Block 2
        "chapter3_questions": input_data_questions.get("chapter3_questions", {}) # Expects "chapter3_questions" key in JSON from Block 3
    }
    
    # Fallback for youtubeUrl if not provided by youtube_url_override (already extracted from Block 1's JSON)
    # and also if the key was missing in Block 1's JSON.
    if not final_input_data["youtubeUrl"]:
        final_input_data["youtubeUrl"] = input_data_intro.get("youtubeUrl") 
    
    if not final_input_data["youtubeUrl"]:
        return None, None, "No YouTube URL found (neither as override nor in Intro JSON's 'youtubeUrl' field)."
    
    video_id = utils_booklet.extract_youtube_id(final_input_data["youtubeUrl"])
    if not video_id:
        return None, None, f"Valid YouTube Video ID could not be extracted from the URL: {final_input_data['youtubeUrl']}. Please check the URL."
    
    try:
        content_dict = booklet_generator.create_booklet_content_json_structure(
            final_input_data, 
            video_id,
            H5P_INTERNAL_COVER_IMAGE_PATH, # Uses global constant
            H5P_INTERNAL_QS_BG_IMAGE_PATH  # Uses global constant
        )
        content_json_str = json.dumps(content_dict, ensure_ascii=False, indent=2)

        book_overall_title = final_input_data.get("book", {}).get("title", "Generated InteractiveBook")
        h5p_json_dict = booklet_generator.generate_h5p_json_dict(book_overall_title)
        h5p_json_str = json.dumps(h5p_json_dict, ensure_ascii=False, indent=2)

        images_to_add = [
            (str(SOURCE_COVER_IMAGE_PATH), H5P_INTERNAL_COVER_IMAGE_PATH),
            (str(SOURCE_QS_BG_IMAGE_PATH), H5P_INTERNAL_QS_BG_IMAGE_PATH)
        ]
        
        missing_source_images_messages = []
        for src_path_str, _ in images_to_add:
            if not Path(src_path_str).exists():
                missing_source_images_messages.append(f"Required image file not found: {src_path_str}")
        if missing_source_images_messages:
            error_msg = "\n".join(missing_source_images_messages) + f"\nImages must be placed in the `{TEMPLATES_DIR}` folder."
            return None, None, error_msg

        if not TEMPLATE_ZIP_PATH.exists():
            return None, None, f"H5P Template ZIP file not found: {TEMPLATE_ZIP_PATH}. It must be placed in the `{TEMPLATES_DIR}` folder."

        h5p_package_bytes = utils_booklet.create_h5p_package(
            content_json_str,
            h5p_json_str,
            str(TEMPLATE_ZIP_PATH),
            images_to_add
        )

        if h5p_package_bytes:
            clean_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in book_overall_title)
            clean_title = "_".join(clean_title.split()) 
            if not clean_title: clean_title = "InteractiveBook" # Default filename if title is empty or all special chars
            download_filename = f"{clean_title}.h5p"
            return h5p_package_bytes, download_filename, None # Success
        else:
            # This case might be hard to reach if create_h5p_package raises exceptions for its failures.
            return None, None, "H5P package generation failed (create_h5p_package returned None without exception)."

    except Exception as e:
        # Log the full traceback for server-side debugging if needed
        print(f"Error during package generation: {e}\n{traceback.format_exc()}")
        return None, None, f"Error during package generation: {e}"


def main():
    st.set_page_config(page_title="H5P InteractiveBook Generator", page_icon="📚")
    st.title("H5P InteractiveBook Generator Utility")
    st.markdown("""
        This tool generates H5P interactive book packages from YouTube links and JSON content,
        either manually or by bulk uploading specially formatted Markdown files.
    """)

    with st.expander("How to Use"):
        st.markdown(f"""
            **General Requirements (Apply to Both Modes):**
            - Cover Image: `{SOURCE_COVER_IMAGE_PATH.name}` must be in the `{TEMPLATES_DIR.name}/` folder.
            - Question Set Background: `{SOURCE_QS_BG_IMAGE_PATH.name}` must be in the `{TEMPLATES_DIR.name}/` folder.
            - H5P Template: `{TEMPLATE_ZIP_PATH.name}` must be in the `{TEMPLATES_DIR.name}/` folder.

            ---
            **Manual Generation:**
            0. **Generate JSON Content with this [CustomGPT]() (Link placeholder)
            1.  **YouTube URL:** Enter the URL of the YouTube video. (This takes precedence over URLs in the Intro JSON)
            2.  **JSON Content (Chapters):** Paste JSON data for each chapter into the respective text areas.
                -   **General Settings and Chapter 1 (Introduction):** Book title, cover info, intro content.
                -   **Chapter 2 (Video):** Video chapter content.
                -   **Chapter 3 (Question Set):** Question set chapter content.
            3.  **Package Generation:** Click "Generate H5P Booklet (Manual)".
            4.  **Download:** Download the generated `.h5p` file.

            ---
            **Bulk Generation from Markdown Files:**
            1.  **Prepare `.md` files:** Each file must contain three JSON code blocks under specific headings:
                ```markdown
                # Optional: Any title or text before the blocks

                ## Response Block 1
                ```json
                {{
                  "youtubeUrl": "YOUR_YOUTUBE_URL_HERE_OR_LEAVE_NULL_IF_NONE", 
                  "book": {{ ...book details... }}, 
                  "chapter1_introduction": {{ ...chapter 1 content... }}
                }}
                ```

                ---

                ## Response Block 2
                ```json
                {{
                  "chapter2_video": {{ ...chapter 2 content... }}
                }}
                ```

                ---

                ## Response Block 3
                ```json
                {{
                  "chapter3_questions": {{ ...chapter 3 content... }}
                }}
                ```
                *(Note: The `---` separator between blocks is for clarity in the example; the parser primarily looks for `## Response Block X` followed by the JSON code block.)*
            2.  **Upload:** Use the "Upload Markdown Files" section to select your `.md` files.
            3.  **Generate:** Click "⚙️ Generate H5P from Uploaded Files".
            4.  **Download:** Download individual `.h5p` files as they are generated (if many) or a single `.zip` archive containing all successfully generated H5P files.
        """)
    
    # Check for essential template files once at the start
    essential_files_missing = []
    if not TEMPLATE_ZIP_PATH.exists():
        essential_files_missing.append(f"- H5P Template ZIP: `{TEMPLATE_ZIP_PATH}`")
    if not SOURCE_COVER_IMAGE_PATH.exists():
        essential_files_missing.append(f"- Cover Image: `{SOURCE_COVER_IMAGE_PATH}`")
    if not SOURCE_QS_BG_IMAGE_PATH.exists():
        essential_files_missing.append(f"- Question Set BG Image: `{SOURCE_QS_BG_IMAGE_PATH}`")
    
    if essential_files_missing:
        st.error(f"**Critical Setup Error:** The following essential file(s) are missing from the `{TEMPLATES_DIR}` folder. Please add them to proceed:\n" + "\n".join(essential_files_missing))
        return # Stop the app if essential files are missing

    st.header("Manual Generation")
    youtube_url_input_manual = st.text_input("👉 1. Enter YouTube URL (Manual)", placeholder="Example: [https://www.youtube.com/watch?v=your_video_id](https://www.youtube.com/watch?v=your_video_id)", key="manual_yt_url")
    
    st.subheader("👉 2. Paste JSON Content (Chapters - Manual)")
    # Default JSON inputs (can be loaded from example files or kept empty)
    default_json_intro = "{ \n  \"youtubeUrl\": \"\",\n  \"book\": {\n    \"title\": \"My Awesome Book Title\",\n    \"showCoverPage\": true,\n    \"coverPage\": {\n      \"title\": \"<h1>My Awesome Book</h1>\",\n      \"subtitle\": \"<h3>Subtitle here</h3>\"\n    }\n  },\n  \"chapter1_introduction\": {\n    \"titleForChapter\": \"Introduction\",\n    \"introductionContent\": {\n      \"title\": \"<h2>Welcome!</h2>\",\n      \"guidanceText\": \"<p>This is the intro.</p>\",\n      \"learningObjectives\": [\n        \"<li>Objective 1</li>\"\n      ]\n    },\n    \"accordion\": {\n      \"titleForElement\": \"Key Terms\",\n      \"definitions\": [\n        {\n          \"term\": \"Term 1\",\n          \"definition\": \"<p>Definition 1</p>\"\n        }\n      ]\n    }\n  }\n}"
    default_json_video = "{\n  \"chapter2_video\": {\n    \"titleForChapter\": \"Video Chapter\",\n    \"videoSectionIntro\": {\n      \"title\": \"<h2>Watch This!</h2>\",\n      \"instruction\": \"<p>The video content.</p>\"\n    },\n    \"interactiveVideo\": {\n      \"titleForElement\": \"Interactive Video Title\",\n      \"videoDurationForEndscreen\": 300,\n      \"summaries\": [] \n    }\n  }\n}"
    default_json_questions = "{\n  \"chapter3_questions\": {\n    \"titleForChapter\": \"Quiz Time\",\n    \"questionSectionIntro\": {\n      \"title\": \"<h2>Test Your Knowledge</h2>\",\n      \"instruction\": \"<p>Answer the questions.</p>\"\n    },\n    \"questionSet\": {\n      \"titleForElement\": \"Final Quiz\",\n      \"poolSize\": 1,\n      \"questions\": []\n    }\n  }\n}"


    json_input_intro_area_manual = st.text_area("Kapitel 1: Einleitung & Buchdetails JSON (Manual):", value=default_json_intro, height=200, 
                                         help="JSON für Buchtitel, Cover und Einleitungskapitel.", key="manual_json_intro")
    json_input_video_area_manual = st.text_area("Kapitel 2: Video JSON (Manual):", value=default_json_video, height=200, 
                                         help="JSON für das Videokapitel.", key="manual_json_video")
    json_input_questions_area_manual = st.text_area("Kapitel 3: Fragen JSON (Manual):", value=default_json_questions, height=200, 
                                              help="JSON für das Fragenkapitel.", key="manual_json_questions")

    if st.button("👉 3. Generate H5P Booklet (Manual)", key="manual_generate_btn"):
        # Use the youtube_url_input_manual for this specific call
        # If youtube_url_input_manual is empty, do_h5p_generation will try to use the one from Intro JSON
        h5p_bytes, filename, error = do_h5p_generation(
            youtube_url_input_manual,
            json_input_intro_area_manual,
            json_input_video_area_manual,
            json_input_questions_area_manual
        )
        if error:
            st.error(f"Manual Generation Error: {error}")
        else:
            st.success("H5P Booklet (Manual) successfully generated!")
            st.download_button(
                label="💾 Download H5P Booklet (Manual)",
                data=h5p_bytes,
                file_name=filename,
                mime="application/zip",
                key="manual_download_btn"
            )

    st.header("Bulk Generation from Markdown Files")
    uploaded_md_files = st.file_uploader(
        "Upload .md files", 
        type=["md"], 
        accept_multiple_files=True,
        help="Upload one or more Markdown files formatted as per the instructions in 'How to Use'.",
        key="md_uploader"
    )

    if st.button("⚙️ Generate H5P from Uploaded Files", key="bulk_generate_btn") and uploaded_md_files:
        generated_files_data = [] # List to store {"name": h5p_filename, "data": h5p_bytes, "original_md": uploaded_file.name}

        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, uploaded_file in enumerate(uploaded_md_files):
            status_text.text(f"Processing: {uploaded_file.name} ({i+1}/{len(uploaded_md_files)})...")
            try:
                md_content_bytes = uploaded_file.getvalue()
                md_content_str = md_content_bytes.decode("utf-8")
                
                md_youtube_url, md_json_intro, md_json_video, md_json_questions = parse_md_file_content(md_content_str)

                if not md_json_intro or not md_json_video or not md_json_questions:
                    st.error(f"Skipping `{uploaded_file.name}`: Could not parse all required JSON blocks (Intro, Video, Questions). Please check MD file structure.")
                    continue # Skip to the next file
                
                # md_youtube_url might be None if not in Block 1 JSON, do_h5p_generation handles fallback.
                
                h5p_bytes, h5p_filename, error = do_h5p_generation(
                    md_youtube_url, 
                    md_json_intro,
                    md_json_video,
                    md_json_questions
                )

                if error:
                    st.error(f"Failed to generate H5P for `{uploaded_file.name}`: {error}")
                else:
                    st.success(f"Successfully generated `{h5p_filename}` from `{uploaded_file.name}`.")
                    generated_files_data.append({"name": h5p_filename, "data": h5p_bytes, "original_md": uploaded_file.name})
            
            except Exception as e:
                st.error(f"An unexpected error occurred while processing `{uploaded_file.name}`: {e}")
                st.text(traceback.format_exc())
            
            progress_bar.progress((i + 1) / len(uploaded_md_files))
        
        status_text.text("Bulk processing complete.")

        if generated_files_data:
            st.markdown("---")
            st.subheader("Download Generated H5P Files")
            if len(generated_files_data) == 1:
                single_file_info = generated_files_data[0]
                st.download_button(
                    label=f"💾 Download {single_file_info['name']}",
                    data=single_file_info['data'],
                    file_name=single_file_info['name'],
                    mime="application/zip",
                    key=f"single_bulk_download_{single_file_info['original_md'].replace('.', '_')}"
                )
            elif len(generated_files_data) > 1:
                st.write(f"Preparing a ZIP archive for {len(generated_files_data)} generated H5P files...")
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    for file_info in generated_files_data:
                        zf.writestr(file_info["name"], file_info["data"])
                zip_buffer.seek(0)
                
                st.download_button(
                    label=f"💾 Download All {len(generated_files_data)} H5P Files (.zip)",
                    data=zip_buffer,
                    file_name="h5p_bulk_generated_booklets.zip",
                    mime="application/zip",
                    key="bulk_download_zip_btn"
                )
        elif uploaded_md_files : # If files were uploaded but none were generated
             st.warning("No H5P files were successfully generated from the uploaded Markdown files.")
                
    elif st.button("⚙️ Generate H5P from Uploaded Files", key="bulk_generate_btn_no_files") and not uploaded_md_files:
        st.warning("Please upload at least one Markdown file.")

if __name__ == "__main__":
    main()