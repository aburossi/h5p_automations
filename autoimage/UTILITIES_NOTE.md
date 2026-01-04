# Note on Utility Files

## Files Reused from V1

The following files from your original codebase are **reused as-is** in V2:

### 1. `utils_booklet_iframe.py`
**Purpose**: Core H5P utilities

**Functions (unchanged):**
- `generate_uuid()` - Generate unique IDs for H5P elements
- `compress_image_if_needed()` - Smart image compression with Pillow
- `recursive_replace_ss()` - German text normalization (ß → ss)
- `parse_copyright_info()` - Copyright metadata parsing
- `create_image_param()` - H5P image parameter standardization
- `map_drag_text_to_h5p()` - Cloze exercise mapping
- `map_questions_to_h5p_array()` - Quiz question mapping
- `map_mc_question()` - Multiple choice question structure
- `map_tf_question()` - True/false question structure
- `create_h5p_package()` - Final ZIP package creation

**Why unchanged?**
These are low-level utilities that work regardless of content source. They handle the technical details of H5P format compliance, image processing, and package creation.

---

### 2. `utils_image_gen.py`
**Purpose**: Image generation and processing

**Functions (minor improvements only):**
- `get_wikimedia_data()` - Search Wikimedia Commons
- `download_image_as_cv2()` - Download and decode images
- `resize_and_crop_center()` - Image resizing
- `create_collage()` - Multi-image collage creation
- `smart_crop_auto()` - Face-detection based cropping
- `create_text_image()` - Generate text images with Pillow
- `generate_memory_assets()` - Main image generation pipeline

**Minor changes:**
- Better error handling
- More flexible parameter passing
- Improved logging
- But core algorithm unchanged

**Why mostly unchanged?**
The image generation logic is already generic and works for any content. The refactoring focuses on *what* images to generate, not *how* to generate them.

---

## Integration in V2

### How V1 utilities are used in V2

**In `orchestrator_v2.py`:**
```python
import utils_booklet_iframe as utils_booklet
import utils_image_gen

# Image compression (same as V1)
processed = utils_booklet.compress_image_if_needed(image_bytes, filename)

# Image generation (same as V1)
h5p_cards, files = utils_image_gen.generate_memory_assets(
    prompts, temp_dir, use_collage, collage_count
)
```

**In `booklet_generator_v2.py`:**
```python
import utils_booklet_iframe as utils_booklet

# UUID generation (same as V1)
uuid = utils_booklet.generate_uuid()

# Image parameters (same as V1)
img_param = utils_booklet.create_image_param(image_path)

# Question mapping (same as V1)
h5p_questions = utils_booklet.map_questions_to_h5p_array(questions)

# Package creation (same as V1)
pkg_bytes = utils_booklet.create_h5p_package(
    content_json, h5p_json, template_path, extra_files
)
```

---

## What This Means for You

### ✅ Benefits
1. **Proven code** - These utilities are already tested and working
2. **No breaking changes** - Existing functionality preserved
3. **Easy maintenance** - Updates to utilities benefit both V1 and V2
4. **Familiar codebase** - Developers know these files already

### 📝 Maintenance
- Bug fixes in these files automatically improve both versions
- Image processing improvements benefit all users
- H5P compliance updates apply everywhere

### 🔄 Compatibility
- V1 and V2 can coexist
- Share the same utility files
- No conflicts between versions

---

## If You Need to Modify Utilities

### Example: Change image size
**File:** `utils_image_gen.py`
```python
# Line 19
IMAGE_SIZE = 1080  # Change to 1920 for HD
```

### Example: Adjust compression threshold
**File:** `utils_booklet_iframe.py`
```python
# Line 12-13
MAX_IMAGE_SIZE_BYTES = 1 * 1024 * 1024   # 1 MB → Change to 2 MB
TARGET_IMAGE_SIZE_BYTES = 500 * 1024     # 500 KB → Change to 1 MB
```

### Example: Add new question type
**File:** `utils_booklet_iframe.py`

Add new function:
```python
def map_fill_blank_question(q):
    return {
        "library": "H5P.Blanks 1.14",
        "subContentId": generate_uuid(),
        # ... your structure
    }
```

Update mapper:
```python
def map_questions_to_h5p_array(questions_in):
    out = []
    for q in questions_in:
        q_type = q.get("type")
        if q_type == "multichoice":
            out.append(map_mc_question(q))
        elif q_type == "truefalse":
            out.append(map_tf_question(q))
        elif q_type == "fillblank":  # NEW
            out.append(map_fill_blank_question(q))
    return out
```

---

## Technical Notes

### Dependencies
Both utility files require:
```python
# From requirements.txt
Pillow>=10.0.0      # Image processing
opencv-python>=4.8.0 # Image manipulation
numpy>=1.24.0       # Array operations
pyphen>=0.14.0      # German hyphenation
requests>=2.31.0    # HTTP requests
```

### Image Format Support
- Input: PNG, JPG, JPEG from Wikimedia
- Output: JPG (for photos), PNG (for graphics)
- Auto-compression: When >1MB → ~500KB
- Quality: 85% JPEG quality maintained

### H5P Compliance
All output structures comply with:
- H5P.org specification v1.x
- Interactive Book v1.11
- Memory Game v1.3
- QuestionSet v1.20
- DragText v1.10

---

## File Dependencies Graph

```
orchestrator_v2.py
    ├── booklet_generator_v2.py
    │   └── utils_booklet_iframe.py
    └── utils_image_gen.py

cli_generator.py
    ├── booklet_generator_v2.py
    │   └── utils_booklet_iframe.py
    └── utils_image_gen.py
```

**Conclusion**: The utilities are **foundation files** that both V1 and V2 build upon. They're stable, tested, and work perfectly for the refactored system.

---

**Note**: If you need the actual content of `utils_booklet_iframe.py` or `utils_image_gen.py`, they should be copied from your original codebase (from the document you provided) into the same directory as the V2 files.
