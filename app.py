"""
Streamlit Web Application for PNG Recoloring.
Beautiful and intuitive interface for image recoloring with custom palettes.
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
)
from recolor import recolor_image, load_image_from_bytes, image_to_bytes


# Page configuration
st.set_page_config(
    page_title="Recolor Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main container */
    .main . block-container {
        padding-top: 2rem;
        padding-bottom:  2rem;
        max-width: 1400px;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2. 5rem;
        border-radius: 16px;
        margin-bottom:  2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    . main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Cards */
    .custom-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #f0f0f0;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .custom-card:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom:  1rem;
        padding-bottom: 0.75rem;
        border-bottom:  2px solid #f5f5f5;
    }
    
    .card-header h3 {
        margin: 0;
        font-size: 1.2rem;
        font-weight: 600;
        color: #1a1a2e;
    }
    
    .card-icon {
        font-size: 1.5rem;
    }
    
    /* Color palette display */
    .palette-row {
        display: flex;
        gap: 8px;
        align-items: center;
        padding: 12px;
        background: #f8f9fa;
        border-radius: 12px;
        margin:  8px 0;
        transition: all 0.2s ease;
    }
    
    .palette-row:hover {
        background: #f0f1f3;
    }
    
    .color-swatch {
        width: 36px;
        height: 36px;
        border-radius:  8px;
        border: 2px solid rgba(0, 0, 0, 0.1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .color-swatch:hover {
        transform: scale(1.1);
    }
    
    . color-swatch-small {
        width: 28px;
        height: 28px;
        border-radius: 6px;
        border: 2px solid rgba(0, 0, 0, 0.1);
        display: inline-block;
    }
    
    .palette-name {
        font-weight: 600;
        color:  #333;
        flex-grow: 1;
        font-size: 0.95rem;
    }
    
    /* Group card */
    .group-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom:  1rem;
        border-left: 4px solid #667eea;
    }
    
    .group-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap:  8px;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow:  0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Upload area */
    .upload-area {
        border: 3px dashed #667eea;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #f0f4ff 0%, #e8ecff 100%);
    }
    
    .upload-icon {
        font-size: 4rem;
        margin-bottom:  1rem;
    }
    
    /* Stats badge */
    .stats-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4px 12px;
        border-radius:  20px;
        font-size: 0.85rem;
        font-weight:  600;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color:  #888;
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom:  1rem;
        opacity: 0.5;
    }
    
    .empty-state h4 {
        color: #555;
        margin-bottom: 0.5rem;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f5f7fa;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Image preview grid */
    .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 1rem;
    }
    
    .image-card {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .image-card:hover {
        transform: translateY(-4px);
        box-shadow:  0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Success message */
    .success-banner {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding:  1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
        border-left: 4px solid #00bcd4;
        padding: 1rem 1.25rem;
        border-radius:  0 12px 12px 0;
        margin: 1rem 0;
    }
    
    /* Warning box */
    .warning-box {
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
        border-left: 4px solid #ffc107;
        padding: 1rem 1.25rem;
        border-radius: 0 12px 12px 0;
        margin: 1rem 0;
    }
    
    /* Divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
        margin: 1. 5rem 0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)


def render_header():
    """Render the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Recolor Studio</h1>
        <p>Transform your images with beautiful color palettes</p>
    </div>
    """, unsafe_allow_html=True)


def render_color_swatches(colors: list, size: str = "normal") -> str:
    """Generate HTML for color swatches."""
    swatch_class = "color-swatch" if size == "normal" else "color-swatch-small"
    html = '<div style="display: flex; gap: 6px;">'
    for color in colors:
        if isinstance(color, tuple):
            hex_color = rgb_to_hex(color)
        else:
            hex_color = color if color.startswith('#') else f'#{color}'
        html += f'<div class="{swatch_class}" style="background-color: {hex_color};" title="{hex_color}"></div>'
    html += '</div>'
    return html


def render_palette_row(palette_name: str, colors: list, show_actions: bool = False) -> str:
    """Render a palette row with name and colors."""
    swatches = render_color_swatches(colors)
    return f"""
    <div class="palette-row">
        <span class="palette-name">{palette_name}</span>
        {swatches}
    </div>
    """


def render_empty_state(icon: str, title: str, message: str):
    """Render an empty state message."""
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <h4>{title}</h4>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)


def render_info_box(message: str):
    """Render an info box."""
    st.markdown(f"""
    <div class="info-box">
        💡 {message}
    </div>
    """, unsafe_allow_html=True)


def render_warning_box(message: str):
    """Render a warning box."""
    st.markdown(f"""
    <div class="warning-box">
        ⚠️ {message}
    </div>
    """, unsafe_allow_html=True)


def create_zip_file(images_dict: dict) -> bytes:
    """Create a ZIP file containing all recolored images."""
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, palettes in images_dict.items():
            basename = Path(filename).stem
            for palette_name, img_bytes in palettes.items():
                zip_path = f"{basename}_{palette_name}. png"
                zip_file. writestr(zip_path, img_bytes)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def recolor_page():
    """Main recoloring interface."""

    # Load data
    source_palettes = get_source_palettes()
    palette_groups = get_palette_groups()
    group_names = get_group_names()

    # Check if setup is complete
    has_source = len(source_palettes) > 0
    has_targets = any(len(palettes) > 0 for palettes in palette_groups.values())

    if not has_source or not has_targets:
        st.markdown("""
        <div class="custom-card">
            <div class="card-header">
                <span class="card-icon">⚙️</span>
                <h3>Setup Required</h3>
            </div>
        """, unsafe_allow_html=True)

        if not has_source:
            render_warning_box("Please create a <b>Source Palette</b> first.  This defines which colors will be detected in your images.")

        if not has_targets:
            render_warning_box("Please create at least one <b>Target Palette</b> in a group. These are the colors that will replace the source colors.")

        st. markdown("</div>", unsafe_allow_html=True)

        render_info_box("Go to the <b>Palette Manager</b> tab to set up your palettes.")
        return

    # Main layout
    col1, col2 = st. columns([1, 1], gap="large")

    with col1:
        # Upload Section
        st.markdown("""
        <div class="custom-card">
            <div class="card-header">
                <span class="card-icon">📤</span>
                <h3>Upload Images</h3>
            </div>
        """, unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Drop your PNG files here",
            type=["png"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

        if not uploaded_files:
            st. markdown("""
            <div class="upload-area">
                <div class="upload-icon">🖼️</div>
                <p style="font-size: 1.1rem; color: #555; margin: 0;">
                    Drag & drop PNG files here<br>
                    <span style="font-size: 0.9rem; color: #888;">or click to browse</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="stats-badge">📎 {len(uploaded_files)} file(s) selected</span>', unsafe_allow_html=True)

            # Preview grid
            preview_cols = st.columns(min(len(uploaded_files), 4))
            for i, uploaded_file in enumerate(uploaded_files):
                with preview_cols[i % 4]:
                    image = Image.open(uploaded_file)
                    st.image(image, caption=uploaded_file.name[: 15] + "..." if len(uploaded_file.name) > 15 else uploaded_file.name, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Settings Section
        st.markdown("""
        <div class="custom-card">
            <div class="card-header">
                <span class="card-icon">⚙️</span>
                <h3>Settings</h3>
            </div>
        """, unsafe_allow_html=True)

        # Source palette selection
        st.markdown("**Source Palette** <span style='color: #888; font-size: 0.85rem;'>(colors to detect)</span>", unsafe_allow_html=True)
        selected_source = st.selectbox(
            "Source Palette",
            options=list(source_palettes.keys()),
            label_visibility="collapsed"
        )

        if selected_source:
            st. markdown(render_color_swatches(source_palettes[selected_source]), unsafe_allow_html=True)

        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

        # Target selection
        st.markdown("**Target Palettes** <span style='color:  #888; font-size: 0.85rem;'>(replacement colors)</span>", unsafe_allow_html=True)

        selection_mode = st.radio(
            "Selection mode",
            options=["📁 By Group", "🎯 Individual"],
            horizontal=True,
            label_visibility="collapsed"
        )

        selected_palettes = []

        if selection_mode == "📁 By Group":
            for group_name in group_names:
                group_palettes = palette_groups.get(group_name, {})
                if group_palettes:
                    if st.checkbox(f"📁 {group_name} ({len(group_palettes)} palettes)", value=True, key=f"grp_{group_name}"):
                        for palette_name, colors in group_palettes.items():
                            selected_palettes. append((group_name, palette_name, colors))
        else:
            for group_name in group_names:
                group_palettes = palette_groups.get(group_name, {})
                if group_palettes:
                    with st.expander(f"📁 {group_name}", expanded=True):
                        for palette_name, colors in group_palettes.items():
                            col_a, col_b = st.columns([1, 2])
                            with col_a:
                                if st.checkbox(palette_name, key=f"sel_{group_name}_{palette_name}"):
                                    selected_palettes.append((group_name, palette_name, colors))
                            with col_b:
                                st.markdown(render_color_swatches(colors, "small"), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Process button
        can_process = uploaded_files and selected_palettes and selected_source

        if st.button(
            "🚀 Generate Recolored Images",
            type="primary",
            use_container_width=True,
            disabled=not can_process
        ):
            if can_process:
                all_results = {}
                source_palette = source_palettes[selected_source]

                progress_bar = st.progress(0)
                status = st.empty()

                total = len(uploaded_files) * len(selected_palettes)
                current = 0

                for uploaded_file in uploaded_files:
                    filename = uploaded_file.name
                    all_results[filename] = {}

                    uploaded_file.seek(0)
                    source_image = load_image_from_bytes(uploaded_file. read())

                    for group_name, palette_name, target_palette in selected_palettes:
                        status.markdown(f"⏳ Processing **{filename}** with **{palette_name}**...")

                        recolored = recolor_image(source_image, source_palette, target_palette)
                        img_bytes = image_to_bytes(recolored)

                        all_results[filename][palette_name] = {
                            "image": recolored,
                            "bytes": img_bytes,
                            "group": group_name
                        }

                        current += 1
                        progress_bar.progress(current / total)

                progress_bar.empty()
                status.empty()

                st.session_state['results'] = all_results
                st.rerun()

    with col2:
        # Results Section
        st.markdown("""
        <div class="custom-card">
            <div class="card-header">
                <span class="card-icon">✨</span>
                <h3>Results</h3>
            </div>
        """, unsafe_allow_html=True)

        if 'results' in st.session_state and st.session_state['results']:
            results = st.session_state['results']

            # Stats
            total_images = sum(len(palettes) for palettes in results. values())
            st.markdown(f"""
            <div class="success-banner">
                ✅ Generated <b>{total_images}</b> recolored images! 
            </div>
            """, unsafe_allow_html=True)

            # Download all button
            zip_data = {
                filename: {pname: data["bytes"] for pname, data in palettes.items()}
                for filename, palettes in results.items()
            }
            zip_bytes = create_zip_file(zip_data)

            st.download_button(
                "📦 Download All (ZIP)",
                data=zip_bytes,
                file_name="recolored_images.zip",
                mime="application/zip",
                use_container_width=True
            )

            st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

            # Individual results
            for filename, palettes in results.items():
                basename = Path(filename).stem
                st.markdown(f"**📄 {filename}**")

                cols = st.columns(min(len(palettes), 3))
                for idx, (palette_name, data) in enumerate(palettes.items()):
                    with cols[idx % 3]:
                        st. image(data["image"], caption=palette_name, use_container_width=True)
                        st. download_button(
                            f"⬇️ Download",
                            data=data["bytes"],
                            file_name=f"{basename}_{palette_name}.png",
                            mime="image/png",
                            use_container_width=True,
                            key=f"dl_{filename}_{palette_name}"
                        )

                st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

            # Clear results button
            if st.button("🗑️ Clear Results", use_container_width=True):
                del st.session_state['results']
                st.rerun()

        else:
            render_empty_state(
                "🖼️",
                "No results yet",
                "Upload images and click 'Generate' to see your recolored images here."
            )

        st.markdown("</div>", unsafe_allow_html=True)


def palette_manager_page():
    """Palette management interface."""

    tab1, tab2, tab3 = st.tabs(["📥 Source Palettes", "🎨 Target Palettes", "💾 Import/Export"])

    # ============ SOURCE PALETTES TAB ============
    with tab1:
        col1, col2 = st. columns([1, 1], gap="large")

        with col1:
            st.markdown("""
            <div class="custom-card">
                <div class="card-header">
                    <span class="card-icon">📥</span>
                    <h3>Source Palettes</h3>
                </div>
            """, unsafe_allow_html=True)

            render_info_box("Source palettes define which colors will be <b>detected and replaced</b> in your images.")

            source_palettes = get_source_palettes()

            if source_palettes:
                for name, colors in source_palettes. items():
                    st.markdown(f"""
                    <div class="palette-row">
                        <span class="palette-name">{name}</span>
                        {render_color_swatches(colors)}
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🗑️ Delete", key=f"del_src_{name}", use_container_width=True):
                        delete_source_palette(name)
                        st.rerun()

                    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
            else:
                render_empty_state("📥", "No source palettes", "Create one to get started!")

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="custom-card">
                <div class="card-header">
                    <span class="card-icon">➕</span>
                    <h3>Create Source Palette</h3>
                </div>
            """, unsafe_allow_html=True)

            with st.form("new_source_palette", clear_on_submit=True):
                new_name = st.text_input("Palette Name", placeholder="e.g., My Grayscale")

                st.markdown("**Pick 4 colors:**")
                color_cols = st.columns(4)
                colors = []
                default_colors = ["#FBFBFB", "#CAC1D1", "#9788A2", "#6A5976"]
                for i, col in enumerate(color_cols):
                    with col:
                        color = st.color_picker(f"#{i+1}", value=default_colors[i], key=f"src_new_{i}")
                        colors.append(color)

                if st.form_submit_button("✨ Create Palette", type="primary", use_container_width=True):
                    if new_name and new_name.strip():
                        add_source_palette(new_name.strip(), colors)
                        st.success(f"Created '{new_name}'!")
                        st.rerun()
                    else:
                        st.error("Please enter a name.")

            st.markdown("</div>", unsafe_allow_html=True)

    # ============ TARGET PALETTES TAB ============
    with tab2:
        col1, col2 = st.columns([2, 1], gap="large")

        with col1:
            st.markdown("""
            <div class="custom-card">
                <div class="card-header">
                    <span class="card-icon">🎨</span>
                    <h3>Palette Groups</h3>
                </div>
            """, unsafe_allow_html=True)

            render_info_box("Organize palettes into groups.  The <b>same palette name</b> can exist in different groups with different colors!")

            palette_groups = get_palette_groups_hex()
            group_names = get_group_names()

            if group_names:
                for group_name in group_names:
                    palettes = palette_groups.get(group_name, {})

                    st.markdown(f"""
                    <div class="group-card">
                        <div class="group-title">📁 {group_name} <span class="stats-badge">{len(palettes)} palettes</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Group actions
                    gcol1, gcol2 = st.columns([3, 1])
                    with gcol2:
                        if st.button("🗑️ Delete Group", key=f"del_grp_{group_name}", use_container_width=True):
                            delete_palette_group(group_name)
                            st. rerun()

                    # Palettes in group
                    if palettes:
                        for palette_name, colors in palettes. items():
                            pcol1, pcol2, pcol3 = st.columns([3, 2, 1])
                            with pcol1:
                                st.markdown(f"**{palette_name}**")
                            with pcol2:
                                st.markdown(render_color_swatches(colors, "small"), unsafe_allow_html=True)
                            with pcol3:
                                if st.button("🗑️", key=f"del_pal_{group_name}_{palette_name}", help="Delete palette"):
                                    delete_palette_from_group(group_name, palette_name)
                                    st.rerun()
                    else:
                        st.caption("No palettes in this group yet.")

                    # Add palette to group form
                    with st.expander(f"➕ Add palette to {group_name}"):
                        with st.form(f"add_to_{group_name}", clear_on_submit=True):
                            pal_name = st.text_input("Palette Name", placeholder="e.g., ocean_blue", key=f"pname_{group_name}")

                            pcols = st.columns(4)
                            pal_colors = []
                            for i, pc in enumerate(pcols):
                                with pc:
                                    c = st.color_picker(f"#{i+1}", value="#FF5733", key=f"pc_{group_name}_{i}")
                                    pal_colors.append(c)

                            if st.form_submit_button("Add Palette", use_container_width=True):
                                if pal_name and pal_name.strip():
                                    add_palette_to_group(group_name, pal_name.strip(), pal_colors)
                                    st.rerun()

                    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
            else:
                render_empty_state("📁", "No groups yet", "Create a group to start organizing your palettes!")

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="custom-card">
                <div class="card-header">
                    <span class="card-icon">➕</span>
                    <h3>Create Group</h3>
                </div>
            """, unsafe_allow_html=True)

            with st.form("new_group", clear_on_submit=True):
                group_name = st.text_input("Group Name", placeholder="e. g., Tropical, Neon...")

                if st.form_submit_button("✨ Create Group", type="primary", use_container_width=True):
                    if group_name and group_name.strip():
                        if add_palette_group(group_name.strip()):
                            st.success(f"Created '{group_name}'!")
                            st.rerun()
                        else:
                            st.error("Group already exists.")
                    else:
                        st.error("Please enter a name.")

            st.markdown("</div>", unsafe_allow_html=True)

            # Quick stats
            st.markdown("""
            <div class="custom-card">
                <div class="card-header">
                    <span class="card-icon">📊</span>
                    <h3>Stats</h3>
                </div>
            """, unsafe_allow_html=True)

            total_palettes = sum(len(p) for p in palette_groups. values())
            st.metric("Groups", len(group_names))
            st.metric("Total Palettes", total_palettes)

            st.markdown("</div>", unsafe_allow_html=True)

    # ============ IMPORT/EXPORT TAB ============
    with tab3:
        col1, col2 = st. columns([1, 1], gap="large")

        with col1:
            st.markdown("""
            <div class="custom-card">
                <div class="card-header">
                    <span class="card-icon">📤</span>
                    <h3>Export</h3>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("Download all your palettes as a JSON file to back up or share.")

            json_data = export_palettes_json()

            st.download_button(
                "📥 Download Palettes JSON",
                data=json_data,
                file_name="palettes_export.json",
                mime="application/json",
                use_container_width=True
            )

            with st.expander("👁️ Preview JSON"):
                st.code(json_data, language="json")

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="custom-card">
                <div class="card-header">
                    <span class="card-icon">📥</span>
                    <h3>Import</h3>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("Upload a JSON file to import palettes.")

            merge = st.checkbox("Merge with existing palettes", value=True)

            uploaded = st.file_uploader("Choose JSON file", type=["json"], label_visibility="collapsed")

            if uploaded:
                content = uploaded.read().decode('utf-8')

                with st.expander("👁️ Preview"):
                    st.code(content, language="json")

                if st.button("📥 Import", type="primary", use_container_width=True):
                    if import_palettes_json(content, merge=merge):
                        st.success("Imported successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid JSON format.")

            st.markdown("</div>", unsafe_allow_html=True)


def main():
    """Main application."""
    render_header()

    tab1, tab2 = st.tabs(["🖼️ Recolor Images", "🎨 Palette Manager"])

    with tab1:
        recolor_page()

    with tab2:
        palette_manager_page()


if __name__ == "__main__":
    main()