import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# --- Configuration and Initialization ---

# Set up page configuration
st.set_page_config(
    page_title="Streamlit Schedule Manager",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define the desired order of days for sorting
DAY_ORDER = {
    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
    'Friday': 4, 'Saturday': 5, 'Sunday': 6
}

# Mock User ID (since Streamlit runs server-side, we mock the auth)
MOCK_USER_ID = "stream-user-schedule-40345"

# Initialize schedule data storage in session state
if 'schedule' not in st.session_state:
    st.session_state.schedule = {}
    st.session_state.message = ""

# --- Helper Functions (Database/Sorting Logic) ---

def sort_classes(classes):
    """Sorts classes first by day of week, then by time."""
    
    # Convert the dictionary of classes into a list of dictionaries for sorting
    class_list = list(classes.values())

    def compare_classes(a, b):
        """Custom comparison function for Python's sort method."""
        # 1. Sort by Day of Week
        day_a = DAY_ORDER.get(a.get('classDay'), 99)
        day_b = DAY_ORDER.get(b.get('classDay'), 99)
        if day_a != day_b:
            return day_a - day_b
        
        # 2. Sort by Time (HH:MM format)
        time_a = a.get('classTime', '00:00')
        time_b = b.get('classTime', '00:00')
        if time_a < time_b: return -1
        if time_a > time_b: return 1
        
        return 0

    # Use a lambda function to implement the custom comparison using functools.cmp_to_key
    # (Streamlit environments might not have functools easily available, using standard approach)
    # A cleaner approach in modern Python is often to use multiple keys:
    
    class_list.sort(key=lambda x: (
        DAY_ORDER.get(x.get('classDay', 'Unknown'), 99), 
        x.get('classTime', '00:00')
    ))

    return class_list

def add_class(class_data):
    """Adds a new class to the session state schedule."""
    if not all(class_data.values()):
        st.session_state.message = "Error: All fields are required."
        return

    doc_id = str(uuid.uuid4())
    st.session_state.schedule[doc_id] = {
        'id': doc_id,
        'className': class_data['className'],
        'teacherName': class_data['teacherName'],
        'classDay': class_data['classDay'],
        'classTime': class_data['classTime'],
        'classLocation': class_data['classLocation'],
        'timestamp': datetime.now().isoformat()
    }
    st.session_state.message = f"Class '{class_data['className']}' added successfully!"

def delete_class(doc_id):
    """Deletes a class from the session state schedule."""
    if doc_id in st.session_state.schedule:
        del st.session_state.schedule[doc_id]
        st.session_state.message = "Class deleted successfully."
    else:
        st.session_state.message = "Error: Class not found."

# --- Streamlit UI Layout ---

st.title("📚 Recurring Schedule Manager (Streamlit)")
st.caption(f"User ID (Mocked): `{MOCK_USER_ID}` | Data persists for your current session only.")

# Create the two-column layout
col_form, col_schedule = st.columns([1, 2])

# --- Left Column: Add Class Form ---
with col_form:
    st.header("Add New Class/Period", divider='blue')
    
    with st.form(key='schedule_form'):
        class_name = st.text_input("Class/Subject Name", placeholder="e.g., Advanced Calculus")
        teacher_name = st.text_input("Teacher Name", placeholder="e.g., Ms. Davis")

        day_options = list(DAY_ORDER.keys())
        class_day = st.selectbox("Day of Week", options=['Select Day'] + day_options, index=0)
        
        # Streamlit doesn't have a native 'time' input, but 'text' with careful input works, 
        # or use a slider for simplicity. Using text input to force HH:MM format consistency.
        class_time = st.text_input("Start Time (HH:MM 24hr format)", placeholder="e.g., 09:30")
        
        class_location = st.text_input("Room/Location", placeholder="e.g., Room 301")

        submit_button = st.form_submit_button(label='Add Class to Schedule')

        if submit_button:
            # Validate day selection
            if class_day == 'Select Day':
                st.session_state.message = "Error: Please select a Day of Week."
            else:
                try:
                    # Minimal time format validation (check if parsable)
                    datetime.strptime(class_time, '%H:%M')
                    class_data = {
                        'className': class_name,
                        'teacherName': teacher_name,
                        'classDay': class_day,
                        'classTime': class_time,
                        'classLocation': class_location
                    }
                    add_class(class_data)
                except ValueError:
                    st.session_state.message = "Error: Time must be in HH:MM format (e.g., 09:30)."
                
# Display success/error message in the form column
if st.session_state.message:
    if "Error" in st.session_state.message:
        st.error(st.session_state.message)
    else:
        st.success(st.session_state.message)
    # Clear the message after display
    # st.session_state.message = "" # Disabled clearing to make message persistent until next action

# --- Right Column: Schedule View ---
with col_schedule:
    st.header("Current Weekly Schedule", divider='orange')

    sorted_classes = sort_classes(st.session_state.schedule)

    if not sorted_classes:
        st.info("Your schedule is currently empty. Add a class using the form on the left!")
    else:
        # Prepare data for display
        display_data = []
        for cls in sorted_classes:
            display_data.append({
                'Subject': cls['className'],
                'Teacher': cls['teacherName'],
                'Day': cls['classDay'],
                'Time': cls['classTime'],
                'Location': cls['classLocation'],
                'Action': f"Delete_{cls['id']}" # Placeholder for button
            })
        
        df = pd.DataFrame(display_data)

        # Render the table using st.dataframe or st.data_editor for interactive delete buttons
        st.markdown("<p style='font-size: 0.9em; color: gray;'>Click the 'Delete' button in the table to remove a class.</p>", unsafe_allow_html=True)
        
        # Use st.data_editor to render a table with interactive buttons
        edited_df = st.data_editor(
            df,
            column_config={
                "Action": st.column_config.ButtonColumn(
                    "Actions",
                    help="Click to delete the class",
                    key="delete_button_key",
                    on_click=delete_class,
                    args=["<st_delete_id>"] # Placeholder to be replaced below
                )
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # Reconstruct the delete logic using the standard button column approach
        # Note: Streamlit's ButtonColumn requires a stable key and direct function call.
        # Since the column config is static, we'll revert to generating buttons outside the editor
        # which is often more straightforward for simple actions like delete.

        # Re-render the schedule with explicit delete buttons if the previous method fails
        st.subheader("Schedule Details", divider='gray')
        
        # Data preparation for the manual table display
        table_columns = st.columns([3, 2, 2, 2, 2, 1])
        headers = ["Subject", "Teacher", "Day", "Time", "Location", ""]
        for i, header in enumerate(headers):
            table_columns[i].markdown(f"**{header}**")

        st.divider()

        # Display rows with an interactive button
        for cls in sorted_classes:
            row_cols = st.columns([3, 2, 2, 2, 2, 1])
            row_cols[0].write(cls['className'])
            row_cols[1].write(cls['teacherName'])
            row_cols[2].write(cls['classDay'])
            row_cols[3].write(cls['classTime'])
            row_cols[4].write(cls['classLocation'])
            
            # Use a unique key for each button tied to the document ID
            row_cols[5].button(
                "Delete", 
                key=f"delete_{cls['id']}", 
                on_click=delete_class, 
                args=[cls['id']],
                type="primary"
            )

# This is necessary to clear the message display on a clean rerun (not triggered by a button)
st.session_state.message = ""
