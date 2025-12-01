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
# Map hex color back to name for radio button initialization
COLOR_TO_NAME = {v: k for k, v in COLORS.items()}

# --- Session State Initialization ---
def initialize_state():
    """Initializes the classes list and edit_id in session state."""
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

# --- Utility Functions ---
def get_class_duration(start_time, end_time):
    """Calculates duration in minutes, handling wrap-around for safety."""
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
    """Sets the class ID to be edited."""
    st.session_state.edit_id = class_id
    # We don't call rerun here; it's handled by the caller/data_editor logic for better state management.

def delete_class(class_id):
    """Deletes a class by ID."""
    st.session_state.classes = [c for c in st.session_state.classes if c['id'] != class_id]
    st.success("Class deleted successfully!")
    st.session_state.edit_id = None 
    st.experimental_rerun()

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

    # Get initial values for the form (Ensuring defaults exist for all types)
    initial_day = initial_data.get('day', 'Monday')
    
    # Use fallback values that are guaranteed to be of type time (important for st.time_input)
    initial_start_time = initial_data.get('startTime', time(9, 0))
    initial_end_time = initial_data.get('endTime', time(10, 0))

    initial_color = initial_data.get('color', COLORS['Blue'])
    initial_color_name = COLOR_TO_NAME.get(initial_color, 'Blue')
    initial_color_index = list(COLORS.keys()).index(initial_color_name)

    with st.sidebar.form("class_form_inputs", clear_on_submit=True):
        subject = st.text_input("Subject", value=initial_data.get('subject', ''))
        teacher = st.text_input("Teacher", value=initial_data.get('teacher', ''))
        room = st.text_input("Room", value=initial_data.get('room', ''))
        day = st.selectbox("Day", DAYS, index=DAYS.index(initial_day))

        col1, col2 = st.columns(2)
        with col1:
            # Ensure time inputs receive time objects
            start_time = st.time_input("Start Time", value=initial_start_time, step=300) 
        with col2:
            end_time = st.time_input("End Time", value=initial_end_time, step=300)

        # Color Selection with radio buttons
        color_name = st.radio("Color", list(COLORS.keys()), 
                              index=initial_color_index,
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

    classes_by_day = {day: [c for c in st.session_state.classes if c['day'] == day] for day in DAYS}
    
    SLOT_HEIGHT_PX = 96
    MIN_TO_PX_RATIO = SLOT_HEIGHT_PX / 60
    
    for i, t in enumerate(TIME_SLOTS):
        # Time Label Column
        cols[0].markdown(f"<div style='background-color:#F9FAFB; padding: 8px; height: {SLOT_HEIGHT_PX}px; border-bottom: 1px solid #E5E7EB; display:flex; align-items:flex-start;'>{time_to_str(t)}</div>", unsafe_allow_html=True)

        # Day Columns
        for j, day in enumerate(DAYS):
            
            with cols[j+1]:
                # The container provides the background/border for the hour slot
                st.markdown(f"<div id='slot-{day}-{i}' style='height: {SLOT_HEIGHT_PX}px; border-bottom: 1px solid #F3F4F6; position: relative;'></div>", unsafe_allow_html=True)
                
                for cls in classes_by_day[day]:
                    slot_start_dt = datetime.combine(datetime.today(), t)
                    slot_end_dt = slot_start_dt + timedelta(hours=1)
                    class_start_dt = datetime.combine(datetime.today(), cls['startTime'])
                    
                    # Check if class starts within the slot's time range
                    if slot_start_dt <= class_start_dt < slot_end_dt:
                        
                        duration_minutes = get_class_duration(cls['startTime'], cls['endTime'])
                        
                        minute_offset = cls['startTime'].minute
                        minute_offset_px = minute_offset * MIN_TO_PX_RATIO
                        height_px = duration_minutes * MIN_TO_PX_RATIO
                        
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
                            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                            z-index: 10; 
                            overflow: hidden;
                            display: flex;
                            flex-direction: column;
                            border: 1px solid rgba(255, 255, 255, 0.5);
                            ">
                            <div style="font-weight: 700; margin-bottom: 4px; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{cls['subject']}</div>
                            <div style="font-size: 11px; opacity: 0.9; line-height: 1.3;">
                                👤 {cls['teacher']}<br>
                                📍 {cls['room']}<br>
                                {time_to_str(cls['startTime'])} - {time_to_str(cls['endTime'])}
                            </div>
                        </div>
                        """
                        st.markdown(class_block_html, unsafe_allow_html=True)

def render_data_editor():
    """Renders a data editor for easy class management (Edit/Delete)."""
    st.markdown("## ⚙️ Class Management")

    # 1. Create DataFrame for display
    data = []
    for cls in st.session_state.classes:
        # Calculate duration for display only
        duration = pd.to_datetime(time_to_str(cls['endTime']), format='%H:%M') - pd.to_datetime(time_to_str(cls['startTime']), format='%H:%M')
        # Handle negative duration from end time < start time
        if duration.total_seconds() < 0:
            duration += timedelta(days=1)
        
        total_minutes = int(duration.total_seconds() / 60)
        duration_str = f"{total_minutes // 60}h {total_minutes % 60}m"
        
        data.append({
            'ID': cls['id'],
            'Subject': cls['subject'],
            'Teacher': cls['teacher'],
            'Room': cls['room'],
            'Day': cls['day'],
            'Start': time_to_str(cls['startTime']),
            'End': time_to_str(cls['endTime']),
            'Color': cls['color'],
            'Duration': duration_str,
            'Edit': False, 
            'Delete': False
        })
    df = pd.DataFrame(data)

    # 2. Render Data Editor
    edited_df = st.data_editor(
        df.drop(columns=['ID', 'Color']), # Drop internal columns for display
        column_order=('Subject', 'Teacher', 'Room', 'Day', 'Start', 'End', 'Duration', 'Edit', 'Delete'),
        column_config={
            "Edit": st.column_config.ButtonColumn("Edit", help="Click to edit class in sidebar.", default=False, width="small"),
            "Delete": st.column_config.ButtonColumn("Delete", help="Click to permanently delete class.", default=False, width="small"),
            "Day": st.column_config.SelectboxColumn("Day", options=DAYS, required=True),
            "Start": st.column_config.TextColumn("Start (HH:MM)"), # Using TextColumn to prevent implicit Time parsing errors
            "End": st.column_config.TextColumn("End (HH:MM)"),
            "Duration": st.column_config.TextColumn("Duration", disabled=True),
        },
        hide_index=True,
        key='class_data_editor'
    )
    
    # 3. Process Edits/Deletes from the Data Editor
    
    # Use the original DataFrame to find the ID corresponding to the clicked row index
    
    # Find the row where 'Edit' was clicked
    edit_clicked_row = edited_df[edited_df['Edit'] == True]
    if not edit_clicked_row.empty:
        # Get the original index from the data editor row
        original_index = edit_clicked_row.index[0]
        class_id_to_edit = df.iloc[original_index]['ID']
        # Set edit_id and rerun
        st.session_state.edit_id = class_id_to_edit
        st.experimental_rerun()

    # Find the row where 'Delete' was clicked
    delete_clicked_row = edited_df[edited_df['Delete'] == True]
    if not delete_clicked_row.empty:
        # Get the original index from the data editor row
        original_index = delete_clicked_row.index[0]
        class_id_to_delete = df.iloc[original_index]['ID']
        delete_class(class_id_to_delete) # This calls rerun internally
        
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
    /* Hide the default index header column in data_editor */
    .st-emotion-cache-10qj05 { visibility: hidden; }
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
# Use a column layout for the main content and management table
col_main, col_management = st.columns([2, 1])

# Render the form in the sidebar
class_form()

# Render the Schedule Grid in the main area
with col_main:
    # Use a custom div to mimic the schedule-container styling
    st.markdown("<div class='schedule-card'>", unsafe_allow_html=True)
    render_schedule_grid()
    st.markdown("</div>", unsafe_allow_html=True)

# Render the data editor for management
with col_management:
    render_data_editor()

# --- Next Step ---
st.markdown("---")
st.info("Tip: Use the **sidebar form** to **Add** or **Edit** classes. Use the **Class Management** table's 'Edit' and 'Delete' buttons to trigger actions.")
