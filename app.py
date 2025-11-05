"""Yomitoku OCR Web UI with Streamlit"""

import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import streamlit as st
from PIL import Image
from streamlit_paste_button import paste_image_button


# Configuration
TEMP_DIR = Path("./temp")
SUPPORTED_FORMATS = ["png", "jpg", "jpeg", "pdf", "tiff", "bmp"]
OUTPUT_FORMATS = {
    "Markdown": "md",
    "JSON": "json",
    "HTML": "html",
    "CSV": "csv",
}


def ensure_temp_dir():
    """Create temp directory if it doesn't exist"""
    TEMP_DIR.mkdir(exist_ok=True)


def cleanup_temp_files(temp_path: Path):
    """Remove temporary files after processing"""
    try:
        if temp_path.exists():
            if temp_path.is_dir():
                for file in temp_path.iterdir():
                    file.unlink()
                temp_path.rmdir()
            else:
                temp_path.unlink()
    except Exception as e:
        st.warning(f"Failed to cleanup temp files: {e}")


def save_uploaded_file(uploaded_file) -> Optional[Path]:
    """Save uploaded file to temp directory"""
    ensure_temp_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = TEMP_DIR / f"{timestamp}_{uploaded_file.name}"

    try:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Failed to save file: {e}")
        return None


def save_pasted_image(image: Image.Image) -> Optional[Path]:
    """Save pasted image to temp directory"""
    ensure_temp_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = TEMP_DIR / f"{timestamp}_pasted.png"

    try:
        image.save(file_path)
        return file_path
    except Exception as e:
        st.error(f"Failed to save pasted image: {e}")
        return None


def validate_file_format(file_path: Path) -> bool:
    """Check if file format is supported"""
    suffix = file_path.suffix.lower().lstrip(".")
    return suffix in SUPPORTED_FORMATS


def run_yomitoku(
    input_path: Path, output_format: str, progress_callback=None
) -> Tuple[bool, Optional[Path], Optional[Path], Optional[str]]:
    """
    Run yomitoku command

    Returns:
        Tuple of (success, output_file_path, output_dir, error_message)
    """
    ensure_temp_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = TEMP_DIR / f"output_{timestamp}"
    output_dir.mkdir(exist_ok=True)

    # Build command
    cmd = [
        "yomitoku",
        str(input_path),
        "-f", output_format,
        "-o", str(output_dir),
        "--figure_letter",
    ]

    try:
        if progress_callback:
            progress_callback(0.2, "Running yomitoku...")

        # Run command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
        )

        if progress_callback:
            progress_callback(0.8, "Processing results...")

        if result.returncode != 0:
            error_msg = result.stderr or "Unknown error occurred"
            return False, None, None, error_msg

        # Find output file
        output_files = list(output_dir.glob(f"*.{output_format}"))
        if not output_files:
            return False, None, None, "No output file generated"

        if progress_callback:
            progress_callback(1.0, "Complete!")

        return True, output_files[0], output_dir, None

    except subprocess.TimeoutExpired:
        return False, None, None, "Processing timeout (exceeded 5 minutes)"
    except Exception as e:
        return False, None, None, f"Error: {str(e)}"


def generate_download_filename(original_name: str, format_ext: str) -> str:
    """Generate download filename with timestamp"""
    date_str = datetime.now().strftime("%Y%m%d")
    # Remove extension from original name
    name_without_ext = Path(original_name).stem
    return f"{name_without_ext}_{date_str}_ocr.{format_ext}"


def main():
    st.set_page_config(
        page_title="Yomitoku OCR Web UI",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Initialize session state
    if "processed_result" not in st.session_state:
        st.session_state.processed_result = None
    if "input_image_path" not in st.session_state:
        st.session_state.input_image_path = None
    if "original_filename" not in st.session_state:
        st.session_state.original_filename = None
    if "output_format" not in st.session_state:
        st.session_state.output_format = "md"

    # Create two columns
    left_col, right_col = st.columns([1, 1])

    # Left column - Input
    with left_col:
        st.title("Yomitoku OCR Web UI")

        st.subheader("1. Select Image")

        # File upload
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=SUPPORTED_FORMATS,
            label_visibility="collapsed",
        )

        # Clipboard paste button
        st.write("Or paste from clipboard:")
        paste_result = paste_image_button(
            label="📋 Paste Image",
            background_color="#FF4B4B",
            hover_background_color="#FF6B6B",
        )

        # Handle input
        current_image_path = None
        current_filename = None

        if uploaded_file is not None:
            current_image_path = save_uploaded_file(uploaded_file)
            current_filename = uploaded_file.name
        elif paste_result.image_data is not None:
            current_image_path = save_pasted_image(paste_result.image_data)
            current_filename = "pasted_image.png"

        # Update session state
        if current_image_path:
            st.session_state.input_image_path = current_image_path
            st.session_state.original_filename = current_filename

        # Image preview
        if st.session_state.input_image_path and st.session_state.input_image_path.exists():
            st.subheader("2. Image Preview")
            try:
                # Validate file format
                if not validate_file_format(st.session_state.input_image_path):
                    st.error(f"非対応のファイル形式です。サポート形式: {', '.join(SUPPORTED_FORMATS)}")
                else:
                    image = Image.open(st.session_state.input_image_path)
                    st.image(image, use_container_width=True)
            except Exception as e:
                st.error(f"Failed to load image: {e}")

        # Output format selection
        st.subheader("3. Select Output Format")
        selected_format = st.radio(
            "Format",
            options=list(OUTPUT_FORMATS.keys()),
            index=0,
            label_visibility="collapsed",
            horizontal=True,
        )
        st.session_state.output_format = OUTPUT_FORMATS[selected_format]

        # Execute button
        st.subheader("4. Run OCR")
        can_execute = (
            st.session_state.input_image_path is not None
            and st.session_state.input_image_path.exists()
            and validate_file_format(st.session_state.input_image_path)
        )

        if st.button("🚀 Execute Yomitoku", disabled=not can_execute, use_container_width=True):
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(value, text):
                progress_bar.progress(value)
                status_text.text(text)

            # Run yomitoku
            success, output_file, output_dir, error_msg = run_yomitoku(
                st.session_state.input_image_path,
                st.session_state.output_format,
                progress_callback=update_progress,
            )

            if success:
                # Read result file
                try:
                    with open(output_file, "r", encoding="utf-8") as f:
                        result_content = f.read()
                    st.session_state.processed_result = result_content

                    # Cleanup temporary files
                    cleanup_temp_files(st.session_state.input_image_path)
                    cleanup_temp_files(output_dir)

                    st.success("処理が完了しました！")
                except Exception as e:
                    st.error(f"Failed to read result: {e}")
                    st.session_state.processed_result = None
            else:
                st.error(f"処理に失敗しました。再度実行してください\n\nError: {error_msg}")
                st.session_state.processed_result = None

            # Clear progress
            progress_bar.empty()
            status_text.empty()

    # Right column - Results
    with right_col:
        st.title("Results")

        if st.session_state.processed_result:
            # Download button
            download_filename = generate_download_filename(
                st.session_state.original_filename,
                st.session_state.output_format,
            )

            st.download_button(
                label=f"⬇️ Download {st.session_state.output_format.upper()}",
                data=st.session_state.processed_result,
                file_name=download_filename,
                mime="text/plain",
                use_container_width=True,
            )

            # Display result in expander with code block
            with st.expander("読み取り結果を確認", expanded=True):
                st.code(st.session_state.processed_result, language=st.session_state.output_format, height=500)
        else:
            st.info("処理を実行すると、ここに結果が表示されます")


if __name__ == "__main__":
    main()
