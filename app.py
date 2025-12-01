import streamlit as st
import pandas as pd
from datetime import time, datetime, timedelta
import uuid

# --- Configuration & Constants ---
st.set_page_config(layout="wide", page_title="School Scheduler")

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
# Define time slots from 8:00 to 17:00 (5 PM) with one-hour increments
TIME_SLOTS = [time(h, 0) for h in range(8, 18)] 
COLORS = {
    'Blue': '#3B82F6',
    'Purple': '#8B5CF6',
    'Pink': '#EC4899',
    'Green': '#10B981',
    'Orange': '#F59E0B',
    'Red': '#EF4444',
    'Teal': '#14B8A6',
    'Indigo': '#6366F1'
}

# --- Session State Initialization ---
def initialize_state():
    """Initializes the classes list in session state."""
    if 'classes' not in st.session_state:
        # Load sample data 
        st.session_state.classes = [
            {'id': '1', 'subject': 'Mathematics', 'teacher': 'Mr. Smith', 'room': 'Room 101', 'day': 'Monday', 'startTime': time(9, 0), 'endTime': time(10, 30), 'color': '#3B82F6'},
            {'id': '2', 'subject': 'History', 'teacher': 'Ms. Jones', 'room': 'Auditorium', 'day': 'Tuesday', 'startTime': time(11, 0), 'endTime': time(13, 0), 'color': '#8B5CF6'},
            {'id': '3', 'subject': 'Science Lab', 'teacher': 'Dr. White', 'room': 'Lab 3', 'day': 'Thursday', 'startTime': time(14, 0), 'endTime': time(15, 30), 'color': '#10B981'},
        ]
    if 'edit_id' not in st.session_state:
        st.session_state.edit_id = None

initialize_state()

# --- Utility Functions (Unchanged) ---
def get_class_duration(start_time, end_time):
    """Calculates duration in minutes."""
    dt_start = datetime.combine(datetime.today(), start_time)
    dt_end = datetime.combine(datetime.today(), end_time)
    
    if dt_end <= dt_start:
        dt_end += timedelta(days=1)
        
    duration = dt_end - dt_start
    return duration.total_seconds() / 60

def time_to_str(t: time) -> str:
    """Converts a time object to a 'HH:MM' string."""
    return t.strftime("%H:%M")

def set_edit_id(class_id):
    """Sets the class ID to be edited and opens the form."""
    st.session_state.edit_id = class_id
    st.experimental_rerun()

# --- CRUD Operations (Unchanged) ---
def add_or_update_class(data):
    """Adds a new class or updates an existing one."""
    
    if data['startTime'] >= data['endTime']:
        st.error("End time must be after start time.")
        return

    if st.session_state.edit_id:
        for i, cls in enumerate(st.session_state.classes):
            if cls['id'] == st.session_state.edit_id:
                st.session_state.classes[i] = {**data, 'id': st.session_state.edit_id}
                break
        st.session_state.edit_id = None
        st.success("Class updated successfully!")
    else:
        new_id = str(uuid.uuid4())
        st.session_state.classes.append({**data, 'id': new_id})
        st.success("Class added successfully!")

    st.experimental_rerun()

def delete_class(class_id):
    """Deletes a class by ID."""
    st.session_state.classes = [c for c in st.session_state.classes if c['id'] != class_id]
    st.success("Class deleted successfully!")
    st.experimental_rerun()

# --- UI Components (Unchanged) ---
def class_form():
    """Displays the Add/Edit class form in a sidebar."""
    
    is_editing = st.session_state.edit_id is not None
    st.sidebar.title(f"{'Edit' if is_editing else 'Add New'} Class")
    
    initial_data = {}
    if is_editing:
        cls_to_edit = next((c for c in st.session_state.classes if c['id'] == st.session_state.edit_id), None)
        if cls_to_edit:
            initial_data = cls_to_edit
        else:
            st.session_state.edit_id = None
            is_editing = False

    # Find the correct color name for the initial radio selection
    initial_color_value = initial_data.get('color', COLORS['Blue'])
    initial_color_key = next((name for name, val in COLORS.items() if val == initial_color_value), 'Blue')
    
    with st.sidebar.form("class_form_inputs", clear_on_submit=True):
        subject = st.text_input("Subject", value=initial_data.get('subject', ''))
        teacher = st.text_input("Teacher", value=initial_data.get('teacher', ''))
        room = st.text_input("Room", value=initial_data.get('room', ''))
        day = st.selectbox("Day", DAYS, index=DAYS.index(initial_data.get('day', 'Monday')))

        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("Start Time", value=initial_data.get('startTime', time(9, 0)), step=300) 
        with col2:
            end_time = st.time_input("End Time", value=initial_data.get('endTime', time(10, 0)), step=300)

        color_name = st.radio("Color", list(COLORS.keys()), 
                              index=list(COLORS.keys()).index(initial_color_key),
                              key='color_radio')

        submitted = st.form_submit_button(f"{'Update' if is_editing else 'Add'} Class")
        
        if submitted:
            new_data = {
                'subject': subject,
                'teacher': teacher,
                'room': room,
                'day': day,
                'startTime': start_time,
                'endTime': end_time,
                'color': COLORS[color_name]
            }
            add_or_update_class(new_data)
            
    if is_editing:
        if st.sidebar.button("Cancel Edit"):
            st.session_state.edit_id = None
            st.experimental_rerun()


# --- FIX APPLIED HERE: Render Schedule Grid ---
def render_schedule_grid():
    """Renders the main weekly schedule grid with embedded buttons."""
    
    st.markdown("## 📅 Weekly Schedule")

    # Define the 6 columns: Time + 5 Days
    cols = st.columns([0.5] + [1] * len(DAYS))

    # --- Header Row ---
    # Use inline styles for headers
    cols[0].markdown(f"<div style='background-color:#EEF2FF; padding: 16px; border-radius: 8px 0 0 0; text-align:center;'>**Time**</div>", unsafe_allow_html=True)
    for i, day in enumerate(DAYS):
        cols[i+1].markdown(f"<div style='background-color:#EEF2FF; padding: 16px; text-align:center;'>**{day}**</div>", unsafe_allow_html=True)

    # Group classes by day for easier lookup
    classes_by_day = {day: [c for c in st.session_state.classes if c['day'] == day] for day in DAYS}
    
    for i, t in enumerate(TIME_SLOTS):
        # Time Label Column
        # NOTE: Height 96px for 1 hour slot.
        cols[0].markdown(f"<div style='background-color:#F9FAFB; padding: 8px; height: 96px; border-bottom: 1px solid #E5E7EB; display:flex; align-items:flex-start;'>{time_to_str(t)}</div>", unsafe_allow_html=True)

        # Day Columns
        for j, day in enumerate(DAYS):
            
            # Create a placeholder for the entire hour slot
            with cols[j+1]:
                
                # Use a temporary container for the slot background and relative positioning
                st.markdown(f"<div id='slot-{day}-{i}' style='height: 96px; border-bottom: 1px solid #F3F4F6; position: relative;'>", unsafe_allow_html=True)
                
                # Filter for classes starting in this slot (8:00 class starts in 8:00 slot, 9:30 starts in 9:00 slot)
                for cls in classes_by_day[day]:
                    slot_start_dt = datetime.combine(datetime.today(), t)
                    slot_end_dt = slot_start_dt + timedelta(hours=1)
                    class_start_dt = datetime.combine(datetime.today(), cls['startTime'])

                    # Check if class starts within the slot's time range [slot_start, slot_end)
                    if slot_start_dt <= class_start_dt < slot_end_dt:
                        
                        duration_minutes = get_class_duration(cls['startTime'], cls['endTime'])
                        
                        # Calculate position and height (96px per 60 minutes)
                        minute_offset_px = cls['startTime'].minute * (96 / 60)
                        height_px = duration_minutes * (96 / 60)
                        
                        # Class Block HTML structure
                        class_block_html = f"""
                        <div style="
                            position: absolute;
                            left: 4px;
                            right: 4px;
                            top: {minute_offset_px}px;
                            height: {height_px}px;
                            background-color: {cls['color']};
                            border-radius: 8px;
                            padding: 8px;
                            color: white;
                            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                            z-index: 10; 
                            overflow: hidden;
                            display: flex;
                            flex-direction: column;"
                        >
                            <div style="font-weight: 600; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{cls['subject']}</div>
                            <div style="font-size: 12px; opacity: 0.9; line-height: 1.4;">
                                👤 {cls['teacher']}<br>
                                📍 {cls['room']}<br>
                                {time_to_str(cls['startTime'])} - {time_to_str(cls['endTime'])}
                            </div>
                        </div>
                        """
                        st.markdown(class_block_html, unsafe_allow_html=True)
                        
                        # --- FIX: Embed Streamlit Buttons inside the main column's markdown context ---
                        
                        # Render two micro-columns *inside* the main column to contain the buttons
                        btn_cols = st.columns([1, 1, 100]) # 100 is large to push actions to the top-right
                        
                        with btn_cols[0]:
                            st.button("✏️", key=f"edit_btn_{cls['id']}", help="Edit Class", 
                                     on_click=set_edit_id, args=(cls['id'],))
                        
                        with btn_cols[1]:
                            st.button("🗑️", key=f"delete_btn_{cls['id']}", help="Delete Class", 
                                     on_click=delete_class, args=(cls['id'],))

                # Close the temporary slot container
                st.markdown("</div>", unsafe_allow_html=True)


# --- Main App Execution (Unchanged) ---

# Header Section
st.markdown("""
<style>
    /* Custom Streamlit Styles to mimic the look and feel */
    .st-emotion-cache-18ni7ap { 
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .st-emotion-cache-zt5igj.e1f1d6gn4 { 
        background: linear-gradient(135deg, #EFF6FF 0%, #E0E7FF 100%);
    }
    /* Simple Card/Container for the Schedule */
    .schedule-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }
    
    /* Ensure all column content has consistent border/padding for grid look */
    [data-testid="column"] > div > div {
        border-right: 1px solid #E5E7EB;
        min-height: 96px; /* Base slot height */
    }
    [data-testid="column"]:last-child > div > div {
        border-right: none;
    }

    /* Custom button styling to look better on the grid */
    button[kind="secondaryFormSubmit"] {
        background-color: rgba(255, 255, 255, 0.5);
        border: none;
        margin: 0;
        padding: 4px;
        border-radius: 4px;
        line-height: 1;
    }

    /* Style the main title */
    h1 {
        color: #312E81;
        font-size: 28px;
        font-weight: 700;
    }
    .subtitle {
        color: #6B7280;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Application Header (Streamlit's header)
st.markdown(f"""
<div style='display: flex; align-items: center; gap: 15px; margin-bottom: 30px;'>
    <div style='background: #4F46E5; width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 28px;'>
        🎓
    </div>
    <div>
        <h1>School Scheduler</h1>
        <div class="subtitle">Organize your weekly classes</div>
    </div>
</div>
---
""", unsafe_allow_html=True)

# --- Layout ---
col_main, col_form_trigger = st.columns([1, 0.2])

with col_form_trigger:
    if st.button("➕ Add Class", key='add_btn', use_container_width=True):
        st.session_state.edit_id = None 
        st.experimental_rerun() 

# Render the form in the sidebar
class_form()

# Render the Schedule Grid in the main area
with col_main:
    st.markdown("<div class='schedule-card'>", unsafe_allow_html=True)
    render_schedule_grid()
    st.markdown("</div>", unsafe_allow_html=True)

# --- Next Step ---
st.markdown("---")
st.info("Tip: Use the **sidebar form** to add or edit classes. Look for the **✏️** and **🗑️** buttons *inside* the schedule blocks to quickly manage existing classes.")
