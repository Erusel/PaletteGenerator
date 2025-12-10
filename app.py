
"""
Streamlit Web Application for PNG Recoloring. 
Upload PNG images and generate recolored versions with custom palettes. 
Palettes are organized by groups - same palette name can exist in different groups.
"""

import streamlit as st
from PIL import Image
import io
import zipfile
from pathlib import Path

from palettes import (
    get_source_palettes, get_palette_groups, get_palette_groups_hex,
    get_group_names, get_palettes_in_group,
    add_source_palette, delete_source_palette,
    add_palette_group, delete_palette_group, rename_palette_group,
    add_palette_to_group, update_palette_in_group, delete_palette_from_group,
    copy_palette_to_group,
    export_palettes_json, import_palettes_json,
    rgb_to_hex, hex_to_rgb,
    get_unique_palette_identifier
)
from recolor import recolor_image, create_emissive_texture, load_image_from_bytes, image_to_bytes


# Page configuration
st.set_page_config(
    page_title="PNG Recoloring Tool",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
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
    .group-header {
        background:  linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 10px 15px;
        border-radius:  8px;
        color: white;
        margin-bottom: 10px;
    }
    . emissive-badge {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2px 8px;
        border-radius:  4px;
        font-size: 0.8em;
        font-weight: bold;
        display: inline-block;
        margin-left: 8px;
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
                f'border-radius:  4px; border: 2px solid #333;"></div>',
                unsafe_allow_html=True
            )
            if show_hex:
                st.caption(hex_color)


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


def create_zip_file(images_dict: dict, include_emissive: bool = False) -> bytes:
    """
    Create a ZIP file containing all recolored images. 
    Output format: filename_palettename.png
    If include_emissive is True, also includes filename_palettename_emissive.png
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, palettes in images_dict.items():
            basename = Path(filename).stem
            for palette_name, data in palettes.items():
                # Regular recolored image
                zip_path = f"{basename}_{palette_name}.png"
                zip_file. writestr(zip_path, data['bytes'])
                
                # Emissive texture if requested and available
                if include_emissive and 'emissive_bytes' in data:
                    emissive_path = f"{basename}_{palette_name}_emissive.png"
                    zip_file.writestr(emissive_path, data['emissive_bytes'])

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def palette_manager_page():
    """Palette and group management interface."""
    st.header("🎨 Palette Manager")

    tab1, tab2, tab3 = st.tabs([
        "📥 Source Palettes",
        "📁 Palette Groups & Palettes",
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

            if st.form_submit_button("Add Source Palette", type="primary"):
                if new_src_name and len(new_src_name. strip()) > 0:
                    add_source_palette(new_src_name.strip(), new_src_colors)
                    st.success(f"Source palette '{new_src_name}' added!")
                    st. rerun()
                else:
                    st. error("Please enter a palette name.")

    # ============ PALETTE GROUPS TAB ============
    with tab2:
        st.subheader("Palette Groups & Palettes")
        st.caption("Organize palettes into groups. Same palette name can exist in different groups with different colors.")

        # Info box
        st.info("💡 **Example:** You can have 'light_gray' in both 'Tropimon' and 'Saturated' groups with different colors!")

        palette_groups = get_palette_groups_hex()
        group_names = get_group_names()

        # ---- Create New Group ----
        st.subheader("➕ Create New Group")
        with st.form("new_group"):
            new_group_name = st.text_input("Group Name", placeholder="e.g., Tropimon, Saturated, Neon...")
            if st.form_submit_button("Create Group", type="primary"):
                if new_group_name and len(new_group_name. strip()) > 0:
                    if add_palette_group(new_group_name.strip()):
                        st.success(f"Group '{new_group_name}' created!")
                        st.rerun()
                    else:
                        st.error("Group already exists.")
                else:
                    st.error("Please enter a group name.")

        st.divider()

        # ---- Display Groups and Palettes ----
        if group_names:
            for group_name in group_names: 
                palettes_in_group = palette_groups.get(group_name, {})

                with st.expander(f"📁 **{group_name}** ({len(palettes_in_group)} palettes)", expanded=True):

                    # Group actions
                    gcol1, gcol2, gcol3 = st.columns([2, 1, 1])
                    with gcol2:
                        if st.button("✏️ Rename", key=f"rename_grp_{group_name}"):
                            st.session_state[f"renaming_group_{group_name}"] = True
                    with gcol3:
                        if st.button("🗑️ Delete Group", key=f"del_grp_{group_name}", type="secondary"):
                            delete_palette_group(group_name)
                            st.rerun()

                    # Rename group form
                    if st.session_state.get(f"renaming_group_{group_name}", False):
                        with st.form(f"rename_group_form_{group_name}"):
                            new_name = st. text_input("New group name", value=group_name)
                            col1, col2 = st. columns(2)
                            with col1:
                                if st.form_submit_button("Save"):
                                    if rename_palette_group(group_name, new_name):
                                        st.session_state[f"renaming_group_{group_name}"] = False
                                        st.rerun()
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st. session_state[f"renaming_group_{group_name}"] = False
                                    st. rerun()

                    st.divider()

                    # Display palettes in this group
                    if palettes_in_group:
                        for palette_name, colors in palettes_in_group.items():
                            st.markdown(f"**🎯 {palette_name}**")

                            pcol1, pcol2 = st.columns([3, 1])
                            with pcol1:
                                st.markdown(display_color_palette_inline(colors), unsafe_allow_html=True)
                            with pcol2:
                                btn_col1, btn_col2, btn_col3 = st. columns(3)
                                with btn_col1:
                                    if st.button("✏️", key=f"edit_{group_name}_{palette_name}", help="Edit"):
                                        st.session_state[f"editing_{group_name}_{palette_name}"] = True
                                with btn_col2:
                                    if st.button("📋", key=f"copy_{group_name}_{palette_name}", help="Copy to another group"):
                                        st. session_state[f"copying_{group_name}_{palette_name}"] = True
                                with btn_col3:
                                    if st.button("🗑️", key=f"del_{group_name}_{palette_name}", help="Delete"):
                                        delete_palette_from_group(group_name, palette_name)
                                        st.rerun()

                            # Edit palette form
                            if st.session_state.get(f"editing_{group_name}_{palette_name}", False):
                                with st.form(f"edit_palette_{group_name}_{palette_name}"):
                                    st.caption("Edit colors:")
                                    edit_cols = st.columns(4)
                                    edited_colors = []
                                    for i, col in enumerate(edit_cols):
                                        with col:
                                            current_color = colors[i] if i < len(colors) else "#FFFFFF"
                                            if not current_color.startswith('#'):
                                                current_color = f"#{current_color}"
                                            new_color = st.color_picker(
                                                f"Color {i+1}",
                                                value=current_color,
                                                key=f"edit_color_{group_name}_{palette_name}_{i}"
                                            )
                                            edited_colors.append(new_color)

                                    ecol1, ecol2 = st.columns(2)
                                    with ecol1:
                                        if st.form_submit_button("💾 Save", type="primary"):
                                            update_palette_in_group(group_name, palette_name, edited_colors)
                                            st.session_state[f"editing_{group_name}_{palette_name}"] = False
                                            st.rerun()
                                    with ecol2:
                                        if st.form_submit_button("Cancel"):
                                            st.session_state[f"editing_{group_name}_{palette_name}"] = False
                                            st. rerun()

                            # Copy palette form
                            if st.session_state.get(f"copying_{group_name}_{palette_name}", False):
                                with st.form(f"copy_palette_{group_name}_{palette_name}"):
                                    other_groups = [g for g in group_names if g != group_name]
                                    if other_groups: 
                                        target_group = st.selectbox("Copy to group:", other_groups)
                                        new_palette_name = st.text_input("New name (optional):", value=palette_name)

                                        ccol1, ccol2 = st.columns(2)
                                        with ccol1:
                                            if st.form_submit_button("📋 Copy", type="primary"):
                                                copy_palette_to_group(group_name, palette_name, target_group, new_palette_name)
                                                st. session_state[f"copying_{group_name}_{palette_name}"] = False
                                                st.success(f"Copied to {target_group}!")
                                                st.rerun()
                                        with ccol2:
                                            if st.form_submit_button("Cancel"):
                                                st.session_state[f"copying_{group_name}_{palette_name}"] = False
                                                st.rerun()
                                    else:
                                        st.warning("Create another group first to copy palettes.")
                                        if st.form_submit_button("Cancel"):
                                            st.session_state[f"copying_{group_name}_{palette_name}"] = False
                                            st.rerun()

                            st.markdown("---")
                    else:
                        st.caption("No palettes in this group yet.")

                    # Add palette to this group
                    st.markdown("**➕ Add Palette to this Group**")
                    with st.form(f"add_palette_to_{group_name}"):
                        new_palette_name = st.text_input(
                            "Palette Name",
                            placeholder="e.g., light_gray, ocean_blue.. .",
                            key=f"new_pal_name_{group_name}"
                        )

                        st.caption("Pick 4 colors:")
                        pal_cols = st.columns(4)
                        new_pal_colors = []
                        for i, col in enumerate(pal_cols):
                            with col:
                                color = st.color_picker(
                                    f"Color {i+1}",
                                    value="#FF0000",
                                    key=f"new_pal_color_{group_name}_{i}"
                                )
                                new_pal_colors.append(color)

                        if st. form_submit_button("Add Palette", type="primary"):
                            if new_palette_name and len(new_palette_name. strip()) > 0:
                                add_palette_to_group(group_name, new_palette_name.strip(), new_pal_colors)
                                st.success(f"Palette '{new_palette_name}' added to {group_name}!")
                                st.rerun()
                            else:
                                st.error("Please enter a palette name.")
        else:
            st.info("No groups yet. Create a group to start adding palettes!")

    # ============ IMPORT/EXPORT TAB ============
    with tab3:
        st.subheader("Import/Export Palettes")

        col1, col2 = st. columns(2)

        with col1:
            st.markdown("### 📤 Export")
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

            merge_mode = st.checkbox("Merge with existing (uncheck to replace all)", value=True)

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
                    if import_palettes_json(json_content, merge=merge_mode):
                        st.success("Palettes imported successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to import.  Please check the JSON format.")


def recolor_page():
    """Main recoloring interface."""
    st.header("🖼️ Recolor Images")

    # Load palettes and groups
    source_palettes = get_source_palettes()
    palette_groups = get_palette_groups()
    group_names = get_group_names()

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

        # Target palette selection
        st.subheader("🎯 Target Palettes")

        selection_mode = st.radio(
            "Selection mode",
            options=["Select by Group", "Select Individual Palettes"],
            horizontal=False
        )

        selected_palettes = []  # List of (group_name, palette_name, colors)

        if selection_mode == "Select by Group":
            # Select entire groups
            st.caption("Select groups to process:")
            for group_name in group_names:
                if st.checkbox(f"📁 {group_name}", value=True, key=f"grp_{group_name}"):
                    for palette_name, colors in palette_groups.get(group_name, {}).items():
                        selected_palettes.append((group_name, palette_name, colors))

        else: 
            # Select individual palettes from any group
            st.caption("Select individual palettes:")
            for group_name in group_names:
                st.markdown(f"**📁 {group_name}**")
                for palette_name, colors in palette_groups.get(group_name, {}).items():
                    # Show color preview inline
                    col1, col2 = st. columns([1, 3])
                    with col1:
                        if st.checkbox(
                            palette_name,
                            value=False,
                            key=f"sel_{group_name}_{palette_name}"
                        ):
                            selected_palettes.append((group_name, palette_name, colors))
                    with col2:
                        st.markdown(
                            display_color_palette_inline(colors),
                            unsafe_allow_html=True
                        )

        st.divider()

        # Emissive texture option
        st.subheader("✨ Emissive Textures")
        generate_emissive = st.checkbox(
            "Generate emissive textures",
            value=False,
            help="Create additional textures showing only the recolored pixels (rest transparent)"
        )
        
        if generate_emissive: 
            st.info("💡 Emissive textures will be saved as:\n`filename_palettename_emissive.png`")

        st.divider()

        # Show selected count
        st.metric("Selected Palettes", len(selected_palettes))

        # Output format info
        st.subheader("📄 Output Format")
        st.info("Files are saved as:\n`filename_palettename.png`")

    # Main content
    col1, col2 = st.columns([1, 1])

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
            disabled=not uploaded_files or not selected_palettes or not selected_source
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
        st. subheader("📥 Results")

        if process_button and uploaded_files and selected_palettes and selected_source:
            all_results = {}
            source_palette = source_palettes[selected_source]

            progress_bar = st.progress(0)
            status_text = st.empty()

            total_operations = len(uploaded_files) * len(selected_palettes)
            current_operation = 0

            for uploaded_file in uploaded_files: 
                filename = uploaded_file.name
                all_results[filename] = {}

                uploaded_file.seek(0)
                source_image = load_image_from_bytes(uploaded_file.read())

                for group_name, palette_name, target_palette in selected_palettes:
                    status_text.text(f"Processing {filename} with {group_name}/{palette_name}...")

                    recolored = recolor_image(source_image, source_palette, target_palette)
                    img_bytes = image_to_bytes(recolored)

                    result_data = {
                        "image":  recolored,
                        "bytes": img_bytes,
                        "group": group_name
                    }

                    # Generate emissive texture if requested
                    if generate_emissive: 
                        emissive = create_emissive_texture(source_image, source_palette, target_palette)
                        emissive_bytes = image_to_bytes(emissive)
                        result_data["emissive_image"] = emissive
                        result_data["emissive_bytes"] = emissive_bytes

                    all_results[filename][palette_name] = result_data

                    current_operation += 1
                    progress_bar.progress(current_operation / total_operations)

            status_text.text("✅ Processing complete!")
            progress_bar.empty()

            st.session_state['results'] = all_results
            st.session_state['has_emissive'] = generate_emissive

        # Display results
        if 'results' in st.session_state and st.session_state['results']: 
            results = st.session_state['results']
            has_emissive = st.session_state.get('has_emissive', False)

            # Download all as ZIP
            zip_data = {}
            for filename, palettes in results.items():
                zip_data[filename] = {
                    palette_name: {
                        'bytes': data["bytes"],
                        'emissive_bytes': data. get("emissive_bytes")
                    }
                    for palette_name, data in palettes.items()
                }

            # Flatten for create_zip_file
            zip_data_flat = {}
            for filename, palettes in results.items():
                zip_data_flat[filename] = palettes

            zip_bytes = create_zip_file(zip_data_flat, include_emissive=has_emissive)

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
                basename = Path(filename).stem
                st. subheader(f"📄 {filename}")

                for palette_name, data in palettes.items():
                    st.markdown(f"**🎨 {palette_name}** ({data. get('group', '')})")
                    
                    # Display regular and emissive side by side if available
                    if has_emissive and 'emissive_image' in data:
                        img_col1, img_col2 = st.columns(2)
                        
                        with img_col1:
                            st.markdown("**Regular**")
                            st.image(data["image"], use_container_width=True)
                            output_filename = f"{basename}_{palette_name}.png"
                            st.download_button(
                                label=f"⬇️ Download Regular",
                                data=data["bytes"],
                                file_name=output_filename,
                                mime="image/png",
                                use_container_width=True,
                                key=f"download_{filename}_{palette_name}_regular"
                            )
                        
                        with img_col2:
                            st.markdown('**Emissive** <span class="emissive-badge">✨ GLOW</span>', unsafe_allow_html=True)
                            st.image(data["emissive_image"], use_container_width=True)
                            emissive_filename = f"{basename}_{palette_name}_emissive.png"
                            st.download_button(
                                label=f"⬇️ Download Emissive",
                                data=data["emissive_bytes"],
                                file_name=emissive_filename,
                                mime="image/png",
                                use_container_width=True,
                                key=f"download_{filename}_{palette_name}_emissive"
                            )
                    else:
                        # Just show regular
                        st.image(data["image"], use_container_width=True)
                        output_filename = f"{basename}_{palette_name}.png"
                        st.download_button(
                            label=f"⬇️ Download",
                            data=data["bytes"],
                            file_name=output_filename,
                            mime="image/png",
                            use_container_width=True,
                            key=f"download_{filename}_{palette_name}"
                        )
                    
                    st.markdown("---")

                st.divider()

        elif not process_button:
            st.info("👆 Upload images and click 'Process Images' to see results here.")


def main():
    """Main Streamlit application."""

    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state['page'] = 'recolor'

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