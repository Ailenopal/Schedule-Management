import streamlit as st
import streamlit.components.v1 as components
import json
import os
import uuid
from datetime import datetime

# --- Configuration Section ---
# IMPORTANT: Replace these with your actual Firebase configuration details.
# This app is designed to run in a controlled environment where these values are provided.
# If running locally, you must fill these in.
FIREBASE_CONFIG = {
    "apiKey": "YOUR_FIREBASE_API_KEY", 
    "authDomain": "YOUR_PROJECT_ID.firebaseapp.com",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_PROJECT_ID.appspot.com",
    "messagingSenderId": "YOUR_SENDER_ID",
    "appId": "YOUR_APP_ID"
}
APP_ID = FIREBASE_CONFIG.get("appId", f"sch-builder-{uuid.uuid4().hex[:8]}")

# Use the current date for the default date input
today_date = datetime.now().strftime('%Y-%m-%d')

# --- HTML/JavaScript Content (The Web App) ---
# We inject the configuration and demo logic directly into the script.
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>School Schedule Builder</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Custom styles for a cleaner look */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #f7f9fc; /* Light background */
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            padding: 2rem;
        }}
        .main-container {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
            max-width: 1200px; /* Increased max width for the new column */
            width: 100%;
        }}
        @media (min-width: 1024px) {{
            .main-container {{
                grid-template-columns: 1fr 2fr;
            }}
        }}
        .form-card, .schedule-card {{
            background-color: white;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            border-radius: 0.75rem; /* rounded-xl */
        }}
        .input-group label {{
            font-weight: 500;
            color: #374151;
            margin-bottom: 0.25rem;
            display: block;
        }}
        .input-style {{
            padding: 0.6rem 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            width: 100%;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }}
        .input-style:focus {{
            border-color: #3b82f6;
            outline: none;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
        }}
        .schedule-table th, .schedule-table td {{
            padding: 0.75rem 1rem;
            text-align: left;
        }}
    </style>
</head>
<body>

    <div class="main-container">

        <div id="add-class-form" class="form-card">
            <header class="p-6 border-b border-gray-100">
                <h1 class="text-3xl font-bold text-gray-800">Schedule Manager</h1>
                <p id="userIdDisplay" class="text-sm mt-1 text-gray-500 truncate">User ID: Loading...</p>
            </header>

            <div class="p-6">
                <h2 class="text-xl font-semibold mb-6 text-gray-700">Add New Class/Period</h2>
                
                <form id="scheduleForm">

                    <div class="mb-5 input-group">
                        <label for="className">Class/Subject Name</label>
                        <input type="text" id="className" placeholder="e.g., Advanced Calculus, World History" required class="input-style">
                    </div>

                    <div class="mb-5 input-group">
                        <label for="teacherName">Teacher Name</label>
                        <input type="text" id="teacherName" placeholder="e.g., Ms. Davis, Mr. Smith" required class="input-style">
                    </div>

                    <div class="flex flex-col sm:flex-row gap-4 mb-5">
                        <div class="flex-1 input-group">
                            <label for="classDate">Date</label>
                            <input type="date" id="classDate" required class="input-style">
                        </div>
                        <div class="flex-1 input-group">
                            <label for="classTime">Time</label>
                            <input type="time" id="classTime" required class="input-style">
                        </div>
                    </div>

                    <div class="mb-8 input-group">
                        <label for="classLocation">Room/Location</label>
                        <input type="text" id="classLocation" placeholder="e.g., Room 301, Library Annex" required class="input-style">
                    </div>
                    
                    <div id="messageBox" class="p-3 text-center rounded-lg mb-6 hidden transition duration-300 text-sm"></div>

                    <button type="submit" id="submitButton" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl shadow-lg transition duration-300 ease-in-out transform hover:scale-[1.01]" disabled>
                        Loading...
                    </button>
                </form>

            </div>
        </div>
        
        <div class="schedule-card">
            <div class="p-6 border-b border-gray-100">
                <h2 class="text-2xl font-bold text-gray-800">Current Schedule</h2>
            </div>
            <div class="p-6 overflow-x-auto">
                <div id="scheduleContainer">
                    <p class="text-gray-500">Awaiting schedule data...</p>
                </div>
            </div>
        </div>

    </div>

    <script type="module">
        // Injecting Python variables into JavaScript
        const __app_id = "{APP_ID}";
        const __firebase_config = '{FIREBASE_CONFIG}';
        const __initial_auth_token = null; // Assuming anonymous or custom token handled outside

        import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
        import {{ getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged }} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
        import {{ getFirestore, collection, addDoc, onSnapshot, deleteDoc, doc, Timestamp, query, orderBy, setLogLevel }} from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

        // Set log level for debugging
        setLogLevel('Debug');

        // --- Firebase Setup & Initialization ---
        const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';
        const firebaseConfig = JSON.parse(typeof __firebase_config !== 'undefined' ? __firebase_config : '{{}}');
        const initialAuthToken = typeof __initial_auth_token !== 'undefined' ? __initial_auth_token : null;

        let db, auth, userId;
        const app = initializeApp(firebaseConfig);
        db = getFirestore(app);
        auth = getAuth(app);
        
        const scheduleForm = document.getElementById('scheduleForm');
        const submitButton = document.getElementById('submitButton');
        const scheduleContainer = document.getElementById('scheduleContainer');
        const messageBox = document.getElementById('messageBox');
        const userIdDisplay = document.getElementById('userIdDisplay');

        function displayMessage(message, isError = false) {{
            messageBox.classList.remove('hidden', 'bg-green-100', 'text-green-700', 'bg-red-100', 'text-red-700');
            messageBox.classList.add(isError ? 'bg-red-100' : 'bg-green-100', isError ? 'text-red-700' : 'text-green-700');
            messageBox.innerHTML = message;
            messageBox.scrollIntoView({{ behavior: 'smooth', block: 'start' }});

            setTimeout(() => {{
                messageBox.classList.add('hidden');
            }}, 5000);
        }}

        // Function to get the path to the user's classes collection
        function getClassesCollectionRef() {{
            if (!userId) {{
                console.error("User ID not available.");
                return null;
            }}
            // Private data path: /artifacts/{{appId}}/users/{{userId}}/classes
            return collection(db, `artifacts/${{appId}}/users/${{userId}}/classes`);
        }}
        
        // --- Demo Data Insertion Function (NEW) ---
        async function addDemoClass() {{
            // Use a flag to ensure the demo class is only added once per session/user.
            if (!userId || window.demoClassAdded) {{
                return;
            }}

            const classesRef = getClassesCollectionRef();
            if (!classesRef) return;

            // Define the class data
            const demoClass = {{
                className: 'Advanced Calculus',
                teacherName: 'Ms. Davis',
                classDate: '2025-12-02', // Tuesday, December 2, 2025
                classTime: '10:00',
                classLocation: 'Room 301',
            }};

            const dateTimeString = `${{demoClass.classDate}}T${{demoClass.classTime}}:00`;
            const classTimestamp = new Date(dateTimeString);

            try {{
                // Check if a document with this className already exists before adding,
                // but for simplicity, we'll just add it and rely on the flag.
                await addDoc(classesRef, {{
                    ...demoClass,
                    createdAt: Timestamp.fromDate(classTimestamp) // Use combined date/time for sorting
                }});
                console.log('Demo class added successfully.');
                window.demoClassAdded = true; // Set flag
            }} catch (error) {{
                console.error("Error adding demo class: ", error);
            }}
        }}

        // --- Authentication & Initialization Flow (MODIFIED) ---
        onAuthStateChanged(auth, async (user) => {{
            if (user) {{
                userId = user.uid;
                userIdDisplay.textContent = `User ID: ${{userId}}`;
                submitButton.textContent = 'Add Class to Schedule';
                submitButton.disabled = false;
                setupScheduleListener();
                await addDemoClass(); // <-- ADDED: Insert the demo class after successful auth
            }} else {{
                try {{
                    if (initialAuthToken) {{
                        await signInWithCustomToken(auth, initialAuthToken);
                    }} else {{
                        await signInAnonymously(auth);
                    }}
                }} catch (error) {{
                    console.error("Auth error:", error);
                    displayMessage('Failed to authenticate. Please try reloading the page.', true);
                    submitButton.textContent = 'Auth Error';
                }}
            }}
        }});

        // --- Add Class Functionality (Write to Firestore) ---
        scheduleForm.addEventListener('submit', async (e) => {{
            e.preventDefault();

            if (!userId) {{
                displayMessage('Schedule manager is still authenticating. Please wait.', true);
                return;
            }}

            const classesRef = getClassesCollectionRef();
            if (!classesRef) return;

            const className = document.getElementById('className').value;
            const teacherName = document.getElementById('teacherName').value; // Get new field value
            const classDate = document.getElementById('classDate').value;
            const classTime = document.getElementById('classTime').value;
            const classLocation = document.getElementById('classLocation').value;

            // Combine date and time to create a single timestamp for sorting
            const dateTimeString = `${{classDate}}T${{classTime}}:00`;
            const classTimestamp = new Date(dateTimeString);

            if (isNaN(classTimestamp)) {{
                displayMessage('Invalid Date or Time entered.', true);
                return;
            }}

            try {{
                // Add the new class document to Firestore, including teacherName
                await addDoc(classesRef, {{
                    className,
                    teacherName, // Store teacher name
                    classDate,
                    classTime,
                    classLocation,
                    createdAt: Timestamp.fromDate(classTimestamp) // Use combined date/time for sorting
                }});

                displayMessage(`Class "${{className}}" with ${{teacherName}} added successfully!`);
                scheduleForm.reset();
            }} catch (error) {{
                console.error("Error adding document: ", error);
                displayMessage('Error saving class. Check the console for details.', true);
            }}
        }});

        // --- Delete Class Functionality (Delete from Firestore) ---
        window.deleteClass = async (docId) => {{
            if (!userId) {{
                displayMessage('Authentication not complete. Cannot delete.', true);
                return;
            }}
            
            try {{
                // Document path: /artifacts/{{appId}}/users/{{userId}}/classes/{{docId}}
                const classDocRef = doc(db, `artifacts/${{appId}}/users/${{userId}}/classes`, docId);
                await deleteDoc(classDocRef);
                displayMessage('Class deleted successfully.');
            }} catch (error) {{
                console.error("Error deleting document: ", error);
                displayMessage('Error deleting class. Check the console for details.', true);
            }}
        }};

        // --- Schedule Listener (Read from Firestore) ---
        function setupScheduleListener() {{
            const classesRef = getClassesCollectionRef();
            if (!classesRef) return;

            // Query the classes, ordered by the timestamp
            const q = query(classesRef, orderBy("createdAt", "asc"));

            // Set up real-time listener
            onSnapshot(q, (snapshot) => {{
                const classes = [];
                snapshot.forEach((doc) => {{
                    classes.push({{ id: doc.id, ...doc.data() }});
                }});

                renderSchedule(classes);
            }}, (error) => {{
                console.error("Error listening to schedule: ", error);
                scheduleContainer.innerHTML = '<p class="text-red-500">Error loading schedule.</p>';
            }});
        }}

        // --- Render Schedule to UI ---
        function renderSchedule(classes) {{
            if (classes.length === 0) {{
                scheduleContainer.innerHTML = '<p class="text-gray-500 p-4">Your schedule is currently empty. Add a class using the form on the left!</p>';
                return;
            }}

            let tableHtml = `
                <table class="schedule-table w-full border-collapse">
                    <thead>
                        <tr class="bg-blue-50 text-blue-800">
                            <th class="rounded-tl-lg">Subject</th>
                            <th>Teacher</th>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Location</th>
                            <th class="rounded-tr-lg">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            classes.forEach(cls => {{
                tableHtml += `
                    <tr class="border-t border-gray-200 hover:bg-gray-50">
                        <td>${{cls.className}}</td>
                        <td>${{cls.teacherName || 'N/A'}}</td>
                        <td>${{cls.classDate}}</td>
                        <td>${{cls.classTime}}</td>
                        <td>${{cls.classLocation}}</td>
                        <td>
                            <button onclick="deleteClass('${{cls.id}}')" 
                                class="text-sm bg-red-500 hover:bg-red-600 text-white font-medium py-1 px-3 rounded-full transition duration-150">
                                Delete
                            </button>
                        </td>
                    </tr>
                `;
            }});

            tableHtml += `
                    </tbody>
                </table>
            `;

            scheduleContainer.innerHTML = tableHtml;
        }}

        // Ensure the date input is initialized with today's date if not set by default value
        window.onload = () => {{
             const dateInput = document.getElementById('classDate');
             dateInput.value = "{today_date}"; // Set default date using Python variable
        }};

    </script>
</body>
</html>
"""

# --- Streamlit App Initialization ---

# Set Streamlit page configuration (optional but good practice)
st.set_page_config(layout="wide", page_title="Firebase Schedule Builder")

st.markdown("# 🗓️ Firebase Schedule Builder")
st.markdown("This application is powered by **Streamlit** (Python) and uses an embedded component to run **Firebase Firestore** (JavaScript) for real-time schedule management.")
st.markdown("---")

# Render the HTML component
components.html(
    html_content.replace("{APP_ID}", APP_ID)
                .replace("{FIREBASE_CONFIG}", json.dumps(FIREBASE_CONFIG))
                .replace("{today_date}", today_date),
    height=800,  # Set an appropriate height for the app
    scrolling=True
)

st.markdown("---")
st.markdown("### Deployment Notes")
st.markdown("To run this app and connect to **Firebase**, make sure you:")
st.markdown(f"* **Replace the placeholder values** in the `FIREBASE_CONFIG` dictionary above with your actual project details.")
st.markdown("* **Enable Anonymous Authentication** in your Firebase project settings (Authentication -> Sign-in method).")
st.markdown("* **Set up Firestore Rules** to allow read/write access for authenticated users to the path `/artifacts/{appId}/users/{userId}/classes/{documentId}`.")
