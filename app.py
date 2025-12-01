import { useState } from 'react';



interface Class {

  id: string;

  subject: string;

  teacher: string;

  room: string;

  day: string;

  startTime: string;

  endTime: string;

  color: string;

}



export default function App() {

  const [classes, setClasses] = useState<Class[]>([

    { id: '1', subject: 'Math', teacher: 'Mr. Smith', room: '101', day: 'Monday', startTime: '09:00', endTime: '10:00', color: '#3B82F6' },

    { id: '2', subject: 'English', teacher: 'Ms. Johnson', room: '205', day: 'Monday', startTime: '10:00', endTime: '11:00', color: '#8B5CF6' },

    { id: '3', subject: 'Science', teacher: 'Dr. Brown', room: '302', day: 'Tuesday', startTime: '09:00', endTime: '10:00', color: '#10B981' },

  ]);



  const [showModal, setShowModal] = useState(false);

  const [editingClass, setEditingClass] = useState<Class | null>(null);

  

  // Form states

  const [subject, setSubject] = useState('');

  const [teacher, setTeacher] = useState('');

  const [room, setRoom] = useState('');

  const [day, setDay] = useState('Monday');

  const [startTime, setStartTime] = useState('09:00');

  const [endTime, setEndTime] = useState('10:00');

  const [color, setColor] = useState('#3B82F6');



  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

  const times = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00'];

  const colors = ['#3B82F6', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B', '#EF4444', '#14B8A6', '#6366F1'];



  // JavaScript function: Open modal for adding

  const openAddModal = () => {

    setEditingClass(null);

    setSubject('');

    setTeacher('');

    setRoom('');

    setDay('Monday');

    setStartTime('09:00');

    setEndTime('10:00');

    setColor('#3B82F6');

    setShowModal(true);

  };



  // JavaScript function: Open modal for editing

  const openEditModal = (cls: Class) => {

    setEditingClass(cls);

    setSubject(cls.subject);

    setTeacher(cls.teacher);

    setRoom(cls.room);

    setDay(cls.day);

    setStartTime(cls.startTime);

    setEndTime(cls.endTime);

    setColor(cls.color);

    setShowModal(true);

  };



  // JavaScript function: Close modal

  const closeModal = () => {

    setShowModal(false);

    setEditingClass(null);

  };



  // JavaScript function: Submit form

  const handleSubmit = (e: React.FormEvent) => {

    e.preventDefault();

    

    if (editingClass) {

      // Update existing class

      setClasses(classes.map(cls => 

        cls.id === editingClass.id 

          ? { ...cls, subject, teacher, room, day, startTime, endTime, color }

          : cls

      ));

    } else {

      // Add new class

      const newClass: Class = {

        id: Date.now().toString(),

        subject,

        teacher,

        room,

        day,

        startTime,

        endTime,

        color

      };

      setClasses([...classes, newClass]);

    }

    

    closeModal();

  };



  // JavaScript function: Delete class

  const deleteClass = (id: string) => {

    if (window.confirm('Are you sure you want to delete this class?')) {

      setClasses(classes.filter(cls => cls.id !== id));

    }

  };



  // JavaScript function: Get classes for a specific day and time

  const getClassForSlot = (day: string, time: string) => {

    return classes.find(cls => cls.day === day && cls.startTime === time);

  };



  return (

    <div>

      {/* CSS Styles */}

      <style>{`

        * {

          margin: 0;

          padding: 0;

          box-sizing: border-box;

        }



        body {

          font-family: Arial, sans-serif;

          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

          min-height: 100vh;

        }



        .app-container {

          padding: 40px 20px;

          max-width: 1400px;

          margin: 0 auto;

        }



        .header {

          display: flex;

          justify-content: space-between;

          align-items: center;

          margin-bottom: 30px;

          flex-wrap: wrap;

          gap: 20px;

        }



        .header-title {

          display: flex;

          align-items: center;

          gap: 15px;

          color: white;

        }



        .logo {

          width: 56px;

          height: 56px;

          background: #4F46E5;

          border-radius: 12px;

          display: flex;

          align-items: center;

          justify-content: center;

          font-size: 28px;

        }



        h1 {

          font-size: 32px;

          color: white;

        }



        .subtitle {

          color: rgba(255, 255, 255, 0.9);

          font-size: 14px;

          margin-top: 5px;

        }



        .btn {

          background: #4F46E5;

          color: white;

          border: none;

          padding: 12px 24px;

          border-radius: 8px;

          cursor: pointer;

          font-size: 16px;

          transition: all 0.3s;

        }



        .btn:hover {

          background: #4338CA;

          transform: translateY(-2px);

        }



        .schedule-grid {

          background: white;

          border-radius: 12px;

          overflow: hidden;

          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);

        }



        .table-wrapper {

          overflow-x: auto;

        }



        table {

          width: 100%;

          border-collapse: collapse;

          min-width: 800px;

        }



        thead {

          background: #4F46E5;

        }



        th {

          padding: 16px;

          color: white;

          text-align: center;

          border-right: 1px solid rgba(255, 255, 255, 0.2);

        }



        th:first-child {

          text-align: left;

        }



        tbody tr {

          border-bottom: 1px solid #E5E7EB;

        }



        tbody tr:hover {

          background: #F9FAFB;

        }



        td {

          padding: 12px;

          text-align: center;

          border-right: 1px solid #E5E7EB;

          vertical-align: top;

          min-height: 80px;

        }



        td:first-child {

          font-weight: bold;

          color: #4F46E5;

          text-align: left;

          background: #F9FAFB;

        }



        .class-block {

          padding: 12px;

          border-radius: 8px;

          color: white;

          cursor: pointer;

          transition: all 0.3s;

          position: relative;

        }



        .class-block:hover {

          transform: scale(1.05);

          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);

        }



        .class-subject {

          font-weight: bold;

          margin-bottom: 5px;

        }



        .class-details {

          font-size: 12px;

          opacity: 0.95;

        }



        .class-actions {

          display: flex;

          gap: 5px;

          margin-top: 8px;

        }



        .btn-small {

          background: rgba(255, 255, 255, 0.3);

          border: none;

          padding: 4px 8px;

          border-radius: 4px;

          color: white;

          cursor: pointer;

          font-size: 11px;

        }



        .btn-small:hover {

          background: rgba(255, 255, 255, 0.5);

        }



        .empty-slot {

          color: #9CA3AF;

          font-size: 14px;

          padding: 20px;

        }



        /* Modal Styles */

        .modal {

          position: fixed;

          top: 0;

          left: 0;

          width: 100%;

          height: 100%;

          background: rgba(0, 0, 0, 0.5);

          display: flex;

          align-items: center;

          justify-content: center;

          z-index: 1000;

        }



        .modal-content {

          background: white;

          border-radius: 12px;

          width: 90%;

          max-width: 500px;

          max-height: 90vh;

          overflow-y: auto;

        }



        .modal-header {

          padding: 20px;

          border-bottom: 1px solid #E5E7EB;

          display: flex;

          justify-content: space-between;

          align-items: center;

        }



        .modal-title {

          font-size: 20px;

          color: #111827;

        }



        .close-btn {

          background: none;

          border: none;

          font-size: 24px;

          cursor: pointer;

          color: #6B7280;

          width: 32px;

          height: 32px;

          display: flex;

          align-items: center;

          justify-content: center;

          border-radius: 6px;

        }



        .close-btn:hover {

          background: #F3F4F6;

        }



        .modal-body {

          padding: 20px;

        }



        .form-group {

          margin-bottom: 16px;

        }



        .form-label {

          display: block;

          margin-bottom: 6px;

          color: #374151;

          font-weight: 500;

        }



        .form-input,

        .form-select {

          width: 100%;

          padding: 10px;

          border: 1px solid #D1D5DB;

          border-radius: 6px;

          font-size: 14px;

        }



        .form-input:focus,

        .form-select:focus {

          outline: none;

          border-color: #4F46E5;

          box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);

        }



        .form-row {

          display: grid;

          grid-template-columns: 1fr 1fr;

          gap: 12px;

        }



        .color-options {

          display: grid;

          grid-template-columns: repeat(4, 1fr);

          gap: 8px;

        }



        .color-option {

          height: 40px;

          border-radius: 6px;

          border: 3px solid transparent;

          cursor: pointer;

          transition: all 0.3s;

        }



        .color-option:hover {

          transform: scale(1.1);

        }



        .color-option.selected {

          border-color: #111827;

          box-shadow: 0 0 0 2px white, 0 0 0 4px #111827;

        }



        .form-actions {

          display: flex;

          gap: 10px;

          margin-top: 20px;

        }



        .btn-secondary {

          background: #E5E7EB;

          color: #374151;

        }



        .btn-secondary:hover {

          background: #D1D5DB;

        }



        .form-actions button {

          flex: 1;

        }



        @media (max-width: 768px) {

          h1 {

            font-size: 24px;

          }



          .header {

            flex-direction: column;

            align-items: stretch;

          }



          table {

            font-size: 12px;

          }

        }

      `}</style>



      {/* HTML Structure */}

      <div className="app-container">

        {/* Header */}

        <header className="header">

          <div className="header-title">

            <div className="logo">🎓</div>

            <div>

              <h1>School Scheduler</h1>

              <div className="subtitle">Organize your weekly classes</div>

            </div>

          </div>

          <button className="btn" onClick={openAddModal}>

            + Add Class

          </button>

        </header>



        {/* Schedule Grid */}

        <div className="schedule-grid">

          <div className="table-wrapper">

            <table>

              <thead>

                <tr>

                  <th>Time</th>

                  {days.map(day => (

                    <th key={day}>{day}</th>

                  ))}

                </tr>

              </thead>

              <tbody>

                {times.map(time => (

                  <tr key={time}>

                    <td>{time}</td>

                    {days.map(day => {

                      const cls = getClassForSlot(day, time);

                      return (

                        <td key={day}>

                          {cls ? (

                            <div 

                              className="class-block" 

                              style={{ backgroundColor: cls.color }}

                            >

                              <div className="class-subject">{cls.subject}</div>

                              <div className="class-details">

                                👤 {cls.teacher}<br />

                                📍 {cls.room}<br />

                                ⏰ {cls.startTime} - {cls.endTime}

                              </div>

                              <div className="class-actions">

                                <button 

                                  className="btn-small"

                                  onClick={() => openEditModal(cls)}

                                >

                                  ✏️ Edit

                                </button>

                                <button 

                                  className="btn-small"

                                  onClick={() => deleteClass(cls.id)}

                                >

                                  🗑️ Delete

                                </button>

                              </div>

                            </div>

                          ) : (

                            <div className="empty-slot">-</div>

                          )}

                        </td>

                      );

                    })}

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

        </div>

      </div>



      {/* Modal */}

      {showModal && (

        <div className="modal" onClick={closeModal}>

          <div className="modal-content" onClick={(e) => e.stopPropagation()}>

            <div className="modal-header">

              <h2 className="modal-title">

                {editingClass ? 'Edit Class' : 'Add New Class'}

              </h2>

              <button className="close-btn" onClick={closeModal}>×</button>

            </div>

            

            <div className="modal-body">

              <form onSubmit={handleSubmit}>

                <div className="form-group">

                  <label className="form-label">Subject</label>

                  <input

                    type="text"

                    className="form-input"

                    value={subject}

                    onChange={(e) => setSubject(e.target.value)}

                    placeholder="e.g., Mathematics"

                    required

                  />

                </div>



                <div className="form-group">

                  <label className="form-label">Teacher</label>

                  <input

                    type="text"

                    className="form-input"

                    value={teacher}

                    onChange={(e) => setTeacher(e.target.value)}

                    placeholder="e.g., Mr. Smith"

                    required

                  />

                </div>



                <div className="form-group">

                  <label className="form-label">Room</label>

                  <input

                    type="text"

                    className="form-input"

                    value={room}

                    onChange={(e) => setRoom(e.target.value)}

                    placeholder="e.g., Room 101"

                    required

                  />

                </div>



                <div className="form-group">

                  <label className="form-label">Day</label>

                  <select

                    className="form-select"

                    value={day}

                    onChange={(e) => setDay(e.target.value)}

                    required

                  >

                    {days.map(d => (

                      <option key={d} value={d}>{d}</option>

                    ))}

                  </select>

                </div>



                <div className="form-row">

                  <div className="form-group">

                    <label className="form-label">Start Time</label>

                    <input

                      type="time"

                      className="form-input"

                      value={startTime}

                      onChange={(e) => setStartTime(e.target.value)}

                      required

                    />

                  </div>



                  <div className="form-group">

                    <label className="form-label">End Time</label>

                    <input

                      type="time"

                      className="form-input"

                      value={endTime}

                      onChange={(e) => setEndTime(e.target.value)}

                      required

                    />

                  </div>

                </div>



                <div className="form-group">

                  <label className="form-label">Color</label>

                  <div className="color-options">

                    {colors.map(c => (

                      <div

                        key={c}

                        className={`color-option ${color === c ? 'selected' : ''}`}

                        style={{ backgroundColor: c }}

                        onClick={() => setColor(c)}

                      />

                    ))}

                  </div>

                </div>



                <div className="form-actions">

                  <button type="button" className="btn btn-secondary" onClick={closeModal}>

                    Cancel

                  </button>

                  <button type="submit" className="btn">

                    {editingClass ? 'Update Class' : 'Add Class'}

                  </button>

                </div>

              </form>

            </div>

          </div>

        </div>

      )}

    </div>

  );

}
