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
        # Load sample data (optional, remove for empty start)
        st.session_state.classes = [
            {'id': '1', 'subject': 'Mathematics', 'teacher': 'Mr. Smith', 'room': 'Room 101', 'day': 'Monday', 'startTime': time(9, 0), 'endTime': time(10, 30), 'color': '#3B82F6'},
            {'id': '2', 'subject': 'History', 'teacher': 'Ms. Jones', 'room': 'Auditorium', 'day': 'Tuesday', 'startTime': time(11, 0), 'endTime': time(13, 0), 'color': '#8B5CF6'},
            {'id': '3', 'subject': 'Science Lab', 'teacher': 'Dr. White', 'room': 'Lab 3', 'day': 'Thursday', 'startTime': time(14, 0), 'endTime': time(15, 30), 'color': '#10B981'},
        ]
    if 'edit_id' not in st.session_state:
        st.session_state.edit_id = None

initialize_state()

# --- Utility Functions ---
def get_class_duration(start_time, end_time):
    """Calculates duration in minutes."""
    dt_start = datetime.combine(datetime.today(), start_time)
    dt_end = datetime.combine(datetime.today(), end_time)
    
    # Handle end time on the next day (if applicable, though usually not for classes)
    if dt_end <= dt_start:
        dt_end += timedelta(days=1)
        
    duration = dt_end - dt_start
    return duration.total_seconds() / 60

def time_to_str(t: time) -> str:
    """Converts a time object to a 'HH:MM' string."""
    return t.strftime("%H:%M")

def get_slot_index(start_time: time) -> int:
    """Gets the index of the hour slot (0-indexed based on TIME_SLOTS)."""
    # Find the hour slot that this class starts closest to (or at)
    try:
        return TIME_SLOTS.index(start_time)
    except ValueError:
        # If the start time isn't exactly on the hour, find the preceding hour slot
        start_hour = start_time.hour
        for i, t in enumerate(TIME_SLOTS):
            if t.hour == start_hour:
                return i
        return 0 # Fallback to the first slot

# --- CRUD Operations ---
def add_or_update_class(data):
    """Adds a new class or updates an existing one."""
    
    # Simple validation for time order
    if data['startTime'] >= data['endTime']:
        st.error("End time must be after start time.")
        return

    if st.session_state.edit_id:
        # Update
        for i, cls in enumerate(st.session_state.classes):
            if cls['id'] == st.session_state.edit_id:
                st.session_state.classes[i] = {**data, 'id': st.session_state.edit_id}
                break
        st.session_state.edit_id = None
        st.success("Class updated successfully!")
    else:
        # Add new
        new_id = str(uuid.uuid4())
        st.session_state.classes.append({**data, 'id': new_id})
        st.success("Class added successfully!")

    # Rerun to clear form and redraw schedule
    st.experimental_rerun()

def delete_class(class_id):
    """Deletes a class by ID."""
    st.session_state.classes = [c for c in st.session_state.classes if c['id'] != class_id]
    st.success("Class deleted successfully!")
    st.experimental_rerun()

# --- UI Components ---
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
            # Fallback if ID is invalid
            st.session_state.edit_id = None
            is_editing = False

    with st.sidebar.form("class_form_inputs", clear_on_submit=True):
        subject = st.text_input("Subject", value=initial_data.get('subject', ''))
        teacher = st.text_input("Teacher", value=initial_data.get('teacher', ''))
        room = st.text_input("Room", value=initial_data.get('room', ''))
        day = st.selectbox("Day", DAYS, index=DAYS.index(initial_data.get('day', 'Monday')))

        col1, col2 = st.columns(2)
        with col1:
            start_time = st.time_input("Start Time", value=initial_data.get('startTime', time(9, 0)), step=300) # 5 min step
        with col2:
            end_time = st.time_input("End Time", value=initial_data.get('endTime', time(10, 0)), step=300)

        # Color Selection with radio buttons (more Streamlit-friendly)
        color_name = st.radio("Color", list(COLORS.keys()), 
                              index=list(COLORS.keys()).index(next(name for name, val in COLORS.items() if val == initial_data.get('color', COLORS['Blue'])), 0),
                              key='color_radio')

        submitted = st.form_submit_button(f"{'Update' if is_editing else 'Add'} Class")
        
        if submitted:
            # Prepare data for add/update function
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
            
    # Allow user to cancel edit
    if is_editing:
        if st.sidebar.button("Cancel Edit"):
            st.session_state.edit_id = None
            st.experimental_rerun()


def render_schedule_grid():
    """Renders the main weekly schedule grid."""
    
    st.markdown("## 📅 Weekly Schedule")

    # Define the 6 columns: Time + 5 Days
    cols = st.columns([0.5] + [1] * len(DAYS))

    # --- Header Row ---
    cols[0].markdown(f"<div style='background-color:#EEF2FF; padding: 16px; border-radius: 8px 0 0 0; text-align:center;'>**Time**</div>", unsafe_allow_html=True)
    for i, day in enumerate(DAYS):
        cols[i+1].markdown(f"<div style='background-color:#EEF2FF; padding: 16px; border-radius: {0 if i < len(DAYS) - 1 else 8}px {0 if i < len(DAYS) - 1 else 8}px 0 0; text-align:center;'>**{day}**</div>", unsafe_allow_html=True)

    # --- Time Slots & Classes ---
    
    # Group classes by day for easier lookup
    classes_by_day = {day: [c for c in st.session_state.classes if c['day'] == day] for day in DAYS}
    
    for i, t in enumerate(TIME_SLOTS):
        # Time Label Column
        cols[0].markdown(f"<div style='background-color:#F9FAFB; padding: 8px; height: 96px; border-bottom: 1px solid #E5E7EB; display:flex; align-items:flex-start;'>{time_to_str(t)}</div>", unsafe_allow_html=True)

        # Day Columns
        for j, day in enumerate(DAYS):
            
            # Create a placeholder for the entire hour slot
            with cols[j+1]:
                
                # Container for classes in this hour slot
                st.markdown(f"<div id='slot-{day}-{i}' style='height: 96px; border-bottom: 1px solid #F3F4F6; position: relative;'></div>", unsafe_allow_html=True)
                
                # Check for classes starting in this slot (or overlapping significantly)
                for cls in classes_by_day[day]:
                    slot_start_dt = datetime.combine(datetime.today(), t)
                    slot_end_dt = slot_start_dt + timedelta(hours=1)
                    class_start_dt = datetime.combine(datetime.today(), cls['startTime'])
                    class_end_dt = datetime.combine(datetime.today(), cls['endTime'])

                    # Check if class starts within the slot's time range
                    if slot_start_dt <= class_start_dt < slot_end_dt:
                        
                        duration_minutes = get_class_duration(cls['startTime'], cls['endTime'])
                        
                        # Calculate position and height relative to the 96px slot
                        minute_offset = cls['startTime'].minute
                        # Scale factor: 96px is 1 hour (60 minutes) -> 96/60 = 1.6 px/minute
                        minute_offset_px = minute_offset * (96 / 60)
                        
                        # Note: This is a simplification. The full duration is relative to the start time,
                        # not just the 96px slot. We need to handle multi-slot classes.
                        
                        # Height is duration_minutes * (96 / 60)
                        height_px = duration_minutes * (96 / 60)
                        
                        # Class Block HTML
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
                            flex-direction: column;
                            cursor: pointer;"
                            onclick="
                                document.getElementById('edit_button_{cls['id']}').click(); 
                                return false;"
                        >
                            <div style="font-weight: 600; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{cls['subject']}</div>
                            <div style="font-size: 12px; opacity: 0.9; line-height: 1.4;">
                                👤 {cls['teacher']}<br>
                                📍 {cls['room']}<br>
                                {time_to_str(cls['startTime'])} - {time_to_str(cls['endTime'])}
                            </div>
                            <div style="position: absolute; top: 8px; right: 8px;">
                                <button id="edit_button_{cls['id']}" style="display: none;" onclick="window.parent.postMessage('edit_{cls['id']}', '*')" title="Edit">✏️</button>
                                <button id="delete_button_{cls['id']}" style="display: none;" onclick="window.parent.postMessage('delete_{cls['id']}', '*')" title="Delete">🗑️</button>
                            </div>
                        </div>
                        """
                        # Streamlit is designed to prevent direct JS injection like the original HTML
                        # For interaction, we use Streamlit buttons/callbacks *outside* the main HTML block, 
                        # but we can render the block visually using markdown.
                        st.markdown(class_block_html, unsafe_allow_html=True)
                        
                        # Add Streamlit buttons for actual functionality
                        # These are placed outside the grid but use the key for association
                        col_action = st.columns([1,1,10])[0] # Use a small column to hide them better
                        with col_action:
                            st.button("✏️", key=f"edit_{cls['id']}", help="Edit Class", on_click=lambda c=cls['id']: set_edit_id(c))
                        
                        col_action_del = st.columns([1,1,10])[1]
                        with col_action_del:
                            st.button("🗑️", key=f"delete_{cls['id']}", help="Delete Class", on_click=delete_class, args=(cls['id'],))
                        

def set_edit_id(class_id):
    """Sets the class ID to be edited and opens the form."""
    st.session_state.edit_id = class_id
    st.experimental_rerun()

# --- Main App Execution ---

# Header Section
st.markdown("""
<style>
    /* Custom Streamlit Styles to mimic the look and feel */
    .st-emotion-cache-18ni7ap { /* Header block */
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .st-emotion-cache-zt5igj.e1f1d6gn4 { /* Sidebar container */
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
    # Button to open the Add form by resetting edit_id
    if st.button("➕ Add Class", key='add_btn'):
        st.session_state.edit_id = None 
        # Rerunning is necessary to clear the form fields if they had old data
        st.experimental_rerun() 

# Render the form in the sidebar
class_form()

# Render the Schedule Grid in the main area
with col_main:
    # Use a custom div to mimic the schedule-container styling
    st.markdown("<div class='schedule-card'>", unsafe_allow_html=True)
    render_schedule_grid()
    st.markdown("</div>", unsafe_allow_html=True)

# --- Next Step ---
st.markdown("---")
st.info("Tip: You can add, edit, or delete classes. Use the sidebar form to manage your schedule.")

