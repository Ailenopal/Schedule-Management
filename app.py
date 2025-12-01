import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

# --- Configuration ---
# Set the page configuration for a wide layout
st.set_page_config(layout="wide", page_title="Streamlit School Schedule")

# --- Session State Initialization ---
# Initialize the list to hold schedule data if it doesn't exist
if 'schedule' not in st.session_state:
    st.session_state.schedule = []
# Initialize a unique ID to simulate the user context (like the Firebase User ID)
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4()) 

# --- Helper Functions ---

def add_class(subject, teacher, date, time, location):
    """
    Adds a new class entry to the session state schedule.
    This function is called when the form is submitted.
    """
    # Create a unique ID for the class (used for deletion)
    class_id = str(uuid.uuid4()) 

    new_entry = {
        'id': class_id,
        'Subject': subject,
        'Teacher': teacher,
        # Store Date and Time as native Python objects for sorting
        'Date': date,
        'Time': time,
        'Location': location
    }
    st.session_state.schedule.append(new_entry)
    st.toast(f"Class '{subject}' with {teacher} added successfully!", icon='✅')

def delete_class(class_id):
    """Deletes a class entry by ID from the session state schedule."""
    # Filter out the class with the matching ID
    st.session_state.schedule = [
        cls for cls in st.session_state.schedule if cls['id'] != class_id
    ]
    st.toast("Class deleted successfully.", icon='🗑️')


# --- UI Layout ---

st.title("📚 Streamlit School Schedule Manager")

# Display Simulated User ID
st.markdown(
    f'<p style="font-size: 14px; color: grey; margin-top: -10px;">Session ID (Simulated User ID): {st.session_state.user_id}</p>',
    unsafe_allow_html=True
)

# Use columns for a two-column layout (Form on left, Schedule on right)
col1, col2 = st.columns([1, 2])

# --- Column 1: Add Class Form ---
with col1:
    st.header("Add New Class/Period")
    
    # Use st.form for grouping inputs and handling submission cleanly
    with st.form("schedule_form", clear_on_submit=True):
        
        # 1. Class/Subject Name
        subject = st.text_input(
            "Class/Subject Name", 
            placeholder="e.g., Advanced Calculus, World History",
            key="className"
        )

        # 2. Teacher Name
        teacher = st.text_input(
            "Teacher Name", 
            placeholder="e.g., Ms. Davis, Mr. Smith",
            key="teacherName"
        )
        
        # 3. Date and Time
        date_col, time_col = st.columns(2)
        with date_col:
            # Default to today's date
            date = st.date_input("Date", datetime.now().date(), key="classDate")
        with time_col:
            # Default to current time
            time = st.time_input("Time", datetime.now().time(), key="classTime")

        # 4. Room/Location
        location = st.text_input(
            "Room/Location", 
            placeholder="e.g., Room 301, Library Annex",
            key="classLocation"
        )
        
        # Submit Button
        submitted = st.form_submit_button("➕ Add Class to Schedule", 
                                          type="primary")

        if submitted:
            # Basic validation
            if subject and teacher and location:
                add_class(subject, teacher, date, time, location)
            else:
                st.error("Please fill in all fields.")

# --- Column 2: Schedule View ---
with col2:
    st.header("Current Schedule")
    
    if st.session_state.schedule:
        
        # 1. Prepare data for display and sorting using Pandas
        df_full = pd.DataFrame(st.session_state.schedule)
        
        # 2. Combine date and time for correct temporal sorting
        df_full['combined_datetime'] = df_full.apply(
            lambda row: datetime.combine(row['Date'], row['Time']), axis=1
        )
        df_full = df_full.sort_values(by='combined_datetime', ascending=True)

        # 3. Apply custom CSS for the Delete button style
        st.markdown("""
        <style>
        .stButton>button {
            padding: 4px 10px;
            font-size: 12px;
            border-radius: 9999px; /* Rounded pill shape */
            background-color: #ef4444; /* red-500 */
            color: white;
            transition: background-color 0.15s;
            border: none !important;
        }
        .stButton>button:hover {
            background-color: #dc2626; /* red-700 */
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 4. Manually create the table row by row using Streamlit columns 
        #    to place a 'Delete' button in each row.
        
        # Define column widths for the table layout
        col_widths = [2, 1.5, 1, 1, 1.5, 0.8]
        
        # Display the header row
        header_cols = st.columns(col_widths)
        header_cols[0].subheader("Subject")
        header_cols[1].subheader("Teacher")
        header_cols[2].subheader("Date")
        header_cols[3].subheader("Time")
        header_cols[4].subheader("Location")
        header_cols[5].subheader("Actions")
        st.markdown("---") # Horizontal separator below header

        # Display data rows with Delete button
        for index, row in df_full.iterrows():
            # Format date/time strings for better display
            display_date = row['Date'].strftime('%Y-%m-%d')
            display_time = row['Time'].strftime('%H:%M')
            
            row_cols = st.columns(col_widths)
            
            # Display data in columns
            row_cols[0].text(row['Subject'])
            row_cols[1].text(row['Teacher'])
            row_cols[2].text(display_date)
            row_cols[3].text(display_time)
            row_cols[4].text(row['Location'])
            
            # Place the Delete button in the last column
            with row_cols[5]:
                st.button(
                    "Delete", 
                    key=f"delete_{row['id']}", 
                    on_click=delete_class, 
                    args=(row['id'],) # Pass the class ID to the delete function
                )
            
        st.markdown("---") # Separator line
        
    else:
        st.info("Your schedule is currently empty. Add a class using the form on the left!")
