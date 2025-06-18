import json
from pathlib import Path
import re
import traceback
import booklet_generator  # Requires booklet_generator.py to be accessible
import utils_booklet    # Requires utils_booklet.py to be accessible

# --- Path Definitions ---
# This script's location is the base for finding the 'templates' folder.
# Assumes 'templates/' is a subdirectory of this script's location OR in the same directory.
# If your 'templates' folder is elsewhere, adjust 'TEMPLATES_DIR' accordingly.
# For example, if 'process_md_folder.py' is in your project root, and 'templates' is also in the root:
# SCRIPT_DIR = Path(__file__).resolve().parent
# TEMPLATES_DIR = SCRIPT_DIR / "templates"
# If 'process_md_folder.py' is inside a 'scripts' folder, and 'templates' is in the project root:
# SCRIPT_DIR = Path(__file__).resolve().parent # This is scripts/
# PROJECT_ROOT = SCRIPT_DIR.parent # This is project_root/
# TEMPLATES_DIR = PROJECT_ROOT / "templates"

# Assuming 'templates' folder is in the same directory as this script or a subdirectory
# For the common case where this script is in the project root alongside the 'templates' folder:
SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR / "templates"

# Ensure the templates directory exists (basic check for common setup)
if not TEMPLATES_DIR.is_dir():
    # Fallback: if the script is in a subfolder (e.g. 'src') and templates is in the parent
    PROJECT_ROOT_GUESS = Path(__file__).resolve().parent.parent
    TEMPLATES_DIR_GUESS = PROJECT_ROOT_GUESS / "templates"
    if TEMPLATES_DIR_GUESS.is_dir():
        TEMPLATES_DIR = TEMPLATES_DIR_GUESS
        print(f"Info: Adjusted TEMPLATES_DIR to: {TEMPLATES_DIR}")
    else:
        # If still not found, the user might need to configure paths manually if structure is very different
        print(f"Warning: Could not automatically determine TEMPLATES_DIR. Using default: {TEMPLATES_DIR}")
        print("Please ensure your 'templates' directory (with template.zip, img_1.png, img_2.png) is correctly located.")


TEMPLATE_ZIP_PATH = TEMPLATES_DIR / "template.zip"
SOURCE_COVER_IMAGE_PATH = TEMPLATES_DIR / "img_1.png"
SOURCE_QS_BG_IMAGE_PATH = TEMPLATES_DIR / "img_2.png"

# Target paths within the H5P package (relative to content/) - these are constants
H5P_INTERNAL_COVER_IMAGE_PATH = "images/img_1.png"
H5P_INTERNAL_QS_BG_IMAGE_PATH = "images/img_2.png"


def parse_md_file_content(md_content: str) -> tuple[str | None, str | None, str | None, str | None]:
    """
    Parses the MD file content to extract the YouTube URL and the three JSON strings.
    Looks for ```markdown code blocks.
    Returns (youtube_url, json_intro_str, json_video_str, json_questions_str)
    """
    youtube_url = None
    json_intro_str = None
    json_video_str = None
    json_questions_str = None

    pattern = re.compile(r"## Response Block (\d)\s*```markdown\s*([\s\S]*?)\s*```", re.MULTILINE)
    matches = pattern.findall(md_content)
    
    parsed_blocks = {int(num_str): data_str for num_str, data_str in matches}

    json_intro_str = parsed_blocks.get(1)
    json_video_str = parsed_blocks.get(2)
    json_questions_str = parsed_blocks.get(3)

    if json_intro_str:
        try:
            temp_data = json.loads(json_intro_str)
            youtube_url = temp_data.get("youtubeUrl")
        except json.JSONDecodeError as e:
            # This warning will print to the console during CLI execution
            print(f"Warning: Could not parse JSON from Block 1 in MD (for youtubeUrl extraction): {e}")
            
    return youtube_url, json_intro_str, json_video_str, json_questions_str

def do_h5p_generation(
    youtube_url_override: str | None, 
    json_input_intro_area_str: str | None,
    json_input_video_area_str: str | None,
    json_input_questions_area_str: str | None
):
    """
    Core H5P generation logic.
    Returns a tuple: (h5p_package_bytes, internal_h5p_title_filename, error_message)
    error_message is None on success.
    internal_h5p_title_filename is the filename suggested by H5P content title.
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
        "youtubeUrl": youtube_url_override,
        "book": input_data_intro.get("book", {}),
        "chapter1_introduction": input_data_intro.get("chapter1_introduction", {}),
        "chapter2_video": input_data_video.get("chapter2_video", {}),
        "chapter3_questions": input_data_questions.get("chapter3_questions", {})
    }
    
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
            H5P_INTERNAL_COVER_IMAGE_PATH,
            H5P_INTERNAL_QS_BG_IMAGE_PATH
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
            if not clean_title: clean_title = "InteractiveBook"
            internal_h5p_filename = f"{clean_title}.h5p" # This is for the H5P metadata title consistency
            return h5p_package_bytes, internal_h5p_filename, None # Success
        else:
            return None, None, "H5P package generation failed (create_h5p_package returned None without exception)."

    except Exception as e:
        print(f"Error during package generation internals: {e}\n{traceback.format_exc()}") # Full traceback to console
        return None, None, f"Error during package generation: {e}"

def run_batch_processor():
    """
    Main function to drive the batch processing of .md files from a specified folder.
    """
    folder_path_str = input("👉 Enter the path to the folder containing your .md files: ").strip()
    
    target_folder = Path(folder_path_str)
    if not target_folder.is_dir():
        print(f"❌ Error: Folder not found or is not a directory: {target_folder.resolve()}")
        return

    # Check for essential template files once at the start
    essential_files_missing = []
    if not TEMPLATE_ZIP_PATH.exists():
        essential_files_missing.append(f"- H5P Template ZIP: `{TEMPLATE_ZIP_PATH}` (Expected at {TEMPLATE_ZIP_PATH.resolve()})")
    if not SOURCE_COVER_IMAGE_PATH.exists():
        essential_files_missing.append(f"- Cover Image: `{SOURCE_COVER_IMAGE_PATH}` (Expected at {SOURCE_COVER_IMAGE_PATH.resolve()})")
    if not SOURCE_QS_BG_IMAGE_PATH.exists():
        essential_files_missing.append(f"- Question Set BG Image: `{SOURCE_QS_BG_IMAGE_PATH}` (Expected at {SOURCE_QS_BG_IMAGE_PATH.resolve()})")
    
    if essential_files_missing:
        print(f"❌ Critical Setup Error: The following essential file(s) are missing. Please ensure they exist at the expected paths and try again:\n" + "\n".join(essential_files_missing))
        return

    print(f"⚙️ Processing .md files in folder: {target_folder.resolve()}")
    
    md_files = list(target_folder.glob('*.md'))
    if not md_files:
        print(f"ℹ️ No .md files found in {target_folder.resolve()}.")
        return

    processed_count = 0
    success_count = 0

    for md_file_path in md_files:
        processed_count += 1
        print(f"\n--- [{processed_count}/{len(md_files)}] Processing: {md_file_path.name} ---")
        
        try:
            md_content_str = md_file_path.read_text(encoding="utf-8")
            
            md_youtube_url, md_json_intro, md_json_video, md_json_questions = parse_md_file_content(md_content_str)

            if not md_json_intro or not md_json_video or not md_json_questions:
                print(f"⚠️ Skipping `{md_file_path.name}`: Could not parse all required JSON blocks (Intro, Video, Questions). Please check MD file structure.")
                print(f"   Ensure the file contains `## Response Block 1`, `## Response Block 2`, and `## Response Block 3` headers, each followed by a valid ```markdown ... ``` code block.")
                continue
            
            h5p_bytes, internal_h5p_metadata_filename, error_msg = do_h5p_generation(
                md_youtube_url, 
                md_json_intro,
                md_json_video,
                md_json_questions
            )

            if error_msg:
                print(f"❌ Error generating H5P for `{md_file_path.name}`: {error_msg}")
            else:
                # Save the H5P file with the same name as the .md file, but .h5p extension, in the same folder
                output_h5p_filename = md_file_path.stem + '.h5p'
                output_h5p_filepath = md_file_path.parent / output_h5p_filename # md_file_path.parent is the target_folder
                
                with open(output_h5p_filepath, 'wb') as f_out:
                    f_out.write(h5p_bytes)
                print(f"✅ Successfully generated: {output_h5p_filepath.name} (H5P internal title based on: {internal_h5p_metadata_filename})")
                success_count += 1
        
        except Exception as e:
            print(f"❌ An unexpected error occurred while processing `{md_file_path.name}`: {e}")
            print(traceback.format_exc()) # Full traceback for unexpected errors

    print("\n--- Batch Processing Complete ---")
    print(f"Total .md files found: {len(md_files)}")
    print(f"Successfully generated .h5p files: {success_count}")
    print(f"Failed or skipped files: {len(md_files) - success_count}")

if __name__ == "__main__":
    # Initialize logging for utils_booklet if it uses it and you want to see its output
    # import logging
    # logging.basicConfig(level=logging.INFO) # Or logging.WARNING
    
    run_batch_processor()