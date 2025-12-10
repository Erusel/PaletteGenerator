"""
Streamlit Web Application for PNG Recoloring.
Upload PNG images and generate recolored versions with custom palettes.
"""

import streamlit as st
from PIL import Image
import io
import zipfile
from pathlib import Path

from palettes import (
    get_source_palettes, get_target_palettes, get_palette_groups,
    add_source_palette, add_target_palette, delete_source_palette, delete_target_palette,
    add_palette_group, update_palette_group, delete_palette_group,
    export_palettes_json, import_palettes_json,
    rgb_to_hex, hex_to_rgb
)
from recolor import recolor_image, load_image_from_bytes, image_to_bytes


# Page configuration
st.set_page_config(
    page_title="PNG Recoloring Tool",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .color-box {
        display: inline-block;
        width: 30px;
        height: 30px;
        border: 2px solid #333;
        border-radius: 4px;
        margin: 2px;
    }
    .palette-preview {
        display: flex;
        gap: 4px;
        margin:  8px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .delete-btn {
        color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)


def display_color_palette(palette: list, show_hex: bool = True):
    """Display a color palette with visual color boxes."""
    cols = st.columns(len(palette))
    for i, (col, color) in enumerate(zip(cols, palette)):
        if isinstance(color, tuple):
            hex_color = rgb_to_hex(color)
        else:
            hex_color = color if color. startswith('#') else f'#{color}'
        with col:
            st.markdown(
                f'<div style="background-color: {hex_color}; width: 100%; height: 40px; '
                f'border-radius: 4px; border: 2px solid #333;"></div>',
                unsafe_allow_html=True
            )
            if show_hex:
                st. caption(hex_color)


def display_color_palette_inline(palette: list) -> str:
    """Generate inline HTML for palette preview."""
    html = '<div style="display: flex; gap: 4px;">'
    for color in palette:
        if isinstance(color, tuple):
            hex_color = rgb_to_hex(color)
        else:
            hex_color = color if color. startswith('#') else f'#{color}'
        html += f'<div style="background-color:  {hex_color}; width:  24px; height: 24px; border-radius: 4px; border: 1px solid #333;"></div>'
    html += '</div>'
    return html


def create_zip_file(images_dict: dict) -> bytes:
    """Create a ZIP file containing all recolored images."""
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, palettes in images_dict.items():
            basename = Path(filename).stem
            for palette_name, img_bytes in palettes.items():
                zip_path = f"{basename}/{palette_name}.png"
                zip_file.writestr(zip_path, img_bytes)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def palette_manager_page():
    """Palette and group management interface."""
    st.header("🎨 Palette Manager")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 Source Palettes",
        "🎯 Target Palettes",
        "📁 Palette Groups",
        "💾 Import/Export"
    ])

    # ============ SOURCE PALETTES TAB ============
    with tab1:
        st.subheader("Source Palettes")
        st.caption("Define which colors will be detected and replaced in your images.")

        source_palettes = get_source_palettes()

        # Display existing source palettes
        if source_palettes:
            for name, colors in source_palettes.items():
                with st.expander(f"🎨 {name}", expanded=False):
                    display_color_palette(colors)
                    col1, col2 = st. columns([3, 1])
                    with col2:
                        if name != "Default":
                            if st.button("🗑️ Delete", key=f"del_src_{name}", type="secondary"):
                                delete_source_palette(name)
                                st.rerun()
                        else:
                            st.caption("(Default)")

        st.divider()

        # Add new source palette
        st.subheader("➕ Add New Source Palette")

        with st.form("new_source_palette"):
            new_src_name = st.text_input("Palette Name", placeholder="My Source Palette")

            st.caption("Enter 4 colors (hex format):")
            src_cols = st.columns(4)
            new_src_colors = []
            for i, col in enumerate(src_cols):
                with col:
                    color = st.color_picker(f"Color {i+1}", value="#FFFFFF", key=f"src_color_{i}")
                    new_src_colors.append(color)

            if st. form_submit_button("Add Source Palette", type="primary"):
                if new_src_name and len(new_src_name. strip()) > 0:
                    add_source_palette(new_src_name.strip(), new_src_colors)
                    st. success(f"Source palette '{new_src_name}' added!")
                    st. rerun()
                else:
                    st.error("Please enter a palette name.")

    # ============ TARGET PALETTES TAB ============
    with tab2:
        st. subheader("Target Palettes")
        st.caption("Define the replacement color schemes for your images.")

        target_palettes = get_target_palettes()

        # Display existing target palettes
        if target_palettes:
            for name, colors in target_palettes. items():
                with st.expander(f"🎯 {name}", expanded=False):
                    display_color_palette(colors)
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_tgt_{name}", type="secondary"):
                            delete_target_palette(name)
                            st.rerun()

        st.divider()

        # Add new target palette
        st.subheader("➕ Add New Target Palette")

        with st. form("new_target_palette"):
            new_tgt_name = st.text_input("Palette Name", placeholder="My Target Palette")

            st. caption("Enter 4 colors (hex format):")
            tgt_cols = st.columns(4)
            new_tgt_colors = []
            for i, col in enumerate(tgt_cols):
                with col:
                    color = st.color_picker(f"Color {i+1}", value="#FF0000", key=f"tgt_color_{i}")
                    new_tgt_colors. append(color)

            if st.form_submit_button("Add Target Palette", type="primary"):
                if new_tgt_name and len(new_tgt_name.strip()) > 0:
                    add_target_palette(new_tgt_name.strip(), new_tgt_colors)
                    st.success(f"Target palette '{new_tgt_name}' added!")
                    st.rerun()
                else:
                    st.error("Please enter a palette name.")

    # ============ PALETTE GROUPS TAB ============
    with tab3:
        st.subheader("Palette Groups")
        st.caption("Organize target palettes into groups for batch processing.")

        palette_groups = get_palette_groups()
        target_palettes = get_target_palettes()
        available_palette_names = list(target_palettes.keys())

        # Display existing groups
        if palette_groups:
            for group_name, palette_names in palette_groups.items():
                with st.expander(f"📁 {group_name} ({len(palette_names)} palettes)", expanded=False):
                    # Show palettes in this group with previews
                    for pname in palette_names:
                        if pname in target_palettes:
                            st.markdown(f"**{pname}**")
                            st.markdown(display_color_palette_inline(target_palettes[pname]), unsafe_allow_html=True)

                    st.divider()

                    # Edit group
                    st.caption("Edit group palettes:")
                    updated_palettes = st.multiselect(
                        "Palettes in group",
                        options=available_palette_names,
                        default=[p for p in palette_names if p in available_palette_names],
                        key=f"edit_group_{group_name}"
                    )

                    col1, col2 = st. columns(2)
                    with col1:
                        if st.button("💾 Update", key=f"update_group_{group_name}"):
                            update_palette_group(group_name, updated_palettes)
                            st. success(f"Group '{group_name}' updated!")
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_group_{group_name}", type="secondary"):
                            delete_palette_group(group_name)
                            st.rerun()

        st.divider()

        # Add new group
        st.subheader("➕ Add New Palette Group")

        with st.form("new_palette_group"):
            new_group_name = st.text_input("Group Name", placeholder="My Palette Group")

            selected_palettes = st.multiselect(
                "Select palettes for this group",
                options=available_palette_names,
                default=[]
            )

            if st.form_submit_button("Create Group", type="primary"):
                if new_group_name and len(new_group_name.strip()) > 0:
                    if selected_palettes:
                        add_palette_group(new_group_name.strip(), selected_palettes)
                        st.success(f"Group '{new_group_name}' created!")
                        st.rerun()
                    else:
                        st.error("Please select at least one palette.")
                else:
                    st.error("Please enter a group name.")

    # ============ IMPORT/EXPORT TAB ============
    with tab4:
        st.subheader("Import/Export Palettes")

        col1, col2 = st. columns(2)

        with col1:
            st. markdown("### 📤 Export")
            st.caption("Download all your palettes and groups as JSON.")

            json_data = export_palettes_json()
            st.download_button(
                label="⬇️ Download Palettes JSON",
                data=json_data,
                file_name="palettes_export.json",
                mime="application/json",
                use_container_width=True
            )

            with st.expander("Preview JSON"):
                st.code(json_data, language="json")

        with col2:
            st.markdown("### 📥 Import")
            st.caption("Upload a JSON file to import palettes and groups.")

            uploaded_json = st.file_uploader(
                "Choose JSON file",
                type=["json"],
                key="import_json"
            )

            if uploaded_json:
                json_content = uploaded_json.read().decode('utf-8')

                with st.expander("Preview Import"):
                    st.code(json_content, language="json")

                if st.button("📥 Import Palettes", type="primary", use_container_width=True):
                    if import_palettes_json(json_content):
                        st.success("Palettes imported successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to import.  Please check the JSON format.")


def recolor_page():
    """Main recoloring interface."""
    st.header("🖼️ Recolor Images")

    # Load palettes and groups
    source_palettes = get_source_palettes()
    target_palettes = get_target_palettes()
    palette_groups = get_palette_groups()

    # Sidebar configuration
    with st.sidebar:
        st. header("⚙️ Settings")

        # Source palette selection
        st.subheader("📥 Source Palette")
        selected_source = st.selectbox(
            "Select source palette",
            options=list(source_palettes.keys()),
            index=0
        )
        if selected_source:
            display_color_palette(source_palettes[selected_source], show_hex=False)

        st.divider()

        # Target palette/group selection
        st.subheader("🎯 Target Selection")

        selection_mode = st.radio(
            "Selection mode",
            options=["Individual Palettes", "Palette Group"],
            horizontal=True
        )

        selected_target_palettes = []

        if selection_mode == "Individual Palettes":
            for palette_name in target_palettes. keys():
                if st.checkbox(palette_name, value=True, key=f"sel_{palette_name}"):
                    selected_target_palettes.append(palette_name)
        else:
            if palette_groups:
                selected_group = st.selectbox(
                    "Select palette group",
                    options=list(palette_groups.keys())
                )
                if selected_group:
                    selected_target_palettes = [
                        p for p in palette_groups[selected_group]
                        if p in target_palettes
                    ]
                    st.caption(f"Palettes in group:  {', '.join(selected_target_palettes)}")
            else:
                st.warning("No palette groups defined.  Create one in Palette Manager.")

        st.divider()

        # Quick links
        st.subheader("🔗 Quick Links")
        if st.button("🎨 Open Palette Manager", use_container_width=True):
            st.session_state['page'] = 'manager'
            st.rerun()

    # Main content
    col1, col2 = st. columns([1, 1])

    with col1:
        st.subheader("📤 Upload Images")

        uploaded_files = st.file_uploader(
            "Choose PNG files",
            type=["png"],
            accept_multiple_files=True,
            help="Upload one or more PNG files to recolor"
        )

        # Process button
        process_button = st.button(
            "🚀 Process Images",
            type="primary",
            use_container_width=True,
            disabled=not uploaded_files or not selected_target_palettes or not selected_source
        )

        # Display uploaded images preview
        if uploaded_files:
            st.subheader("📷 Uploaded Images Preview")
            preview_cols = st.columns(min(len(uploaded_files), 3))
            for i, uploaded_file in enumerate(uploaded_files):
                with preview_cols[i % 3]:
                    image = Image.open(uploaded_file)
                    st.image(image, caption=uploaded_file.name, use_container_width=True)
                    st.caption(f"Size: {image.size[0]}x{image.size[1]}")

    with col2:
        st.subheader("📥 Results")

        if process_button and uploaded_files and selected_target_palettes and selected_source:
            all_results = {}
            source_palette = source_palettes[selected_source]

            progress_bar = st.progress(0)
            status_text = st.empty()

            total_operations = len(uploaded_files) * len(selected_target_palettes)
            current_operation = 0

            for uploaded_file in uploaded_files:
                filename = uploaded_file.name
                all_results[filename] = {}

                uploaded_file.seek(0)
                source_image = load_image_from_bytes(uploaded_file. read())

                for palette_name in selected_target_palettes:
                    status_text.text(f"Processing {filename} with {palette_name}...")

                    target_palette = target_palettes[palette_name]
                    recolored = recolor_image(source_image, source_palette, target_palette)

                    img_bytes = image_to_bytes(recolored)
                    all_results[filename][palette_name] = {
                        "image":  recolored,
                        "bytes": img_bytes
                    }

                    current_operation += 1
                    progress_bar. progress(current_operation / total_operations)

            status_text.text("✅ Processing complete!")
            progress_bar.empty()

            st.session_state['results'] = all_results

        # Display results
        if 'results' in st.session_state and st.session_state['results']:
            results = st.session_state['results']

            # Download all as ZIP
            zip_data = {}
            for filename, palettes in results.items():
                zip_data[filename] = {
                    palette_name: data["bytes"]
                    for palette_name, data in palettes.items()
                }

            zip_bytes = create_zip_file(zip_data)

            st.download_button(
                label="📦 Download All (ZIP)",
                data=zip_bytes,
                file_name="recolored_images.zip",
                mime="application/zip",
                use_container_width=True
            )

            st.divider()

            # Display individual results
            for filename, palettes in results.items():
                st.subheader(f"📄 {filename}")

                num_cols = min(len(palettes), 3)
                result_cols = st.columns(num_cols)

                for idx, (palette_name, data) in enumerate(palettes.items()):
                    with result_cols[idx % num_cols]:
                        st.image(
                            data["image"],
                            caption=f"{palette_name}",
                            use_container_width=True
                        )

                        basename = Path(filename).stem
                        st.download_button(
                            label=f"⬇️ {palette_name}",
                            data=data["bytes"],
                            file_name=f"{basename}_{palette_name}.png",
                            mime="image/png",
                            use_container_width=True,
                            key=f"download_{filename}_{palette_name}"
                        )

                st.divider()

        elif not process_button:
            st.info("👆 Upload images and click 'Process Images' to see results here.")


def main():
    """Main Streamlit application."""

    # Initialize session state
    if 'page' not in st. session_state:
        st. session_state['page'] = 'recolor'

    # Header with navigation
    st.title("🎨 PNG Recoloring Tool")

    # Navigation tabs
    tab1, tab2 = st.tabs(["🖼️ Recolor Images", "🎨 Palette Manager"])

    with tab1:
        recolor_page()

    with tab2:
        palette_manager_page()


if __name__ == "__main__":
    main()