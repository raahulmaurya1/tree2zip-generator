import os
import zipfile
from pathlib import Path
import streamlit as st
import time

# Page config
st.set_page_config(page_title="📦 ZIP Generator", layout="centered")

# Inject custom CSS
st.markdown("""
    <style>
    body {
        font-family: 'Segoe UI', sans-serif;
    }
    textarea {
        font-family: 'Courier New', monospace !important;
        background-color:rgb(17, 31, 46) !important;
        border: 1px solid #ddd !important;
    }
    .stButton button {
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #45a049 !important;
    }
    .download-btn {
        font-size: 16px;
        padding: 0.6em 1.2em;
        border-radius: 10px;
        background-color: #3498db;
        color: white;
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.title("📦 TREE2ZIP GENERATOR")
st.markdown("Turn your folder/file structure text into a real ZIP file with one click!")

# Expandable example section
with st.expander("📄 Click to see an example format"):
    st.code("""my-app/
├── src/
│   └── App.jsx
└── package.json""")

# Text area for input
structure_input = st.text_area(
    "📂 Paste Folder Structure Below:",
    placeholder="Example:\nmy-app/\n├── src/\n│   └── App.jsx\n└── package.json",
    height=300,
    help="Use a tree-like format to define folder/file structure.",
)

# Generate button
generate_btn = st.button("🚀 Generate ZIP")

# Function to extract the root folder name
def get_root_folder_name(structure_text):
    lines = structure_text.strip().splitlines()
    for line in lines:
        stripped = line.strip("│├└─ ").rstrip("/")
        if stripped:
            return stripped
    return "project"

# Function to build structure and ZIP it
def create_structure(structure_text, folder_name):
    base_dir = Path(folder_name)
    if base_dir.exists():
        for root, dirs, files in os.walk(base_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(base_dir)

    base_dir.mkdir(parents=True, exist_ok=True)
    lines = structure_text.strip().splitlines()
    stack = [base_dir]

    for line in lines:
        stripped = line.lstrip("│├└─ ").rstrip()
        indent = len(line) - len(stripped) - line.count("─")
        level = indent // 4
        current_path = stack[level] / stripped

        if '.' in Path(stripped).name:
            current_path.parent.mkdir(parents=True, exist_ok=True)
            current_path.touch()
        else:
            current_path.mkdir(parents=True, exist_ok=True)
            if len(stack) <= level + 1:
                stack.append(current_path)
            else:
                stack[level + 1] = current_path

    zip_filename = f"{folder_name}.zip"
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for foldername, _, filenames in os.walk(base_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, base_dir)
                zipf.write(file_path, arcname)

    return zip_filename

# Button logic with animation
if generate_btn:
    if not structure_input.strip():
        st.warning("⚠️ Please enter a valid folder/file structure.")
    else:
        with st.spinner("⏳ Generating ZIP file..."):
            time.sleep(1.2)  # simulate processing time
            folder_name = get_root_folder_name(structure_input)
            zip_file_path = create_structure(structure_input, folder_name)
            st.success(f"✅ `{folder_name}.zip` created successfully!")

            with open(zip_file_path, "rb") as f:
                st.download_button(
                    label="📁 Download ZIP",
                    data=f,
                    file_name=f"{folder_name}.zip",
                    mime="application/zip",
                )
