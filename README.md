# Enhanced Learning Management System (LMS)

This is a web-based learning platform built using Python and Django. It connects teachers, students, and financial sponsors in one place. The system allows teachers to share courses, students to learn, and sponsors to fund students who need financial help.

---

## 👥 User Roles

The project has four different types of users, and each has its own permissions and dashboard:

1. **Admin (Manager)**
   * Manages all accounts on the platform.
   * Sees total numbers like total users, active courses, and how many students are enrolled.

2. **Instructor (Teacher)**
   * Creates, updates, and deletes courses.
   * Gives out assignments and grades student work.
   * Sees alerts about how well students are keeping up with the course.

3. **Student**
   * Searches for courses they want.
   * Enrolls in courses, enroll in it and submits assignments.
   * Receives email alerts about due dates and grades.

4. **Sponsor (Funder)**
   * Fund the students
   * See the dashboard and analytics about fund untilization.
   * See the progress of fund utilization. 

---

## 🚀 Key Features Included

* **Full CRUD Operations:** You can Create, Read, Update, and Delete courses, assignments, and user records easily.
* **Search & Filters:** Students can quickly search for courses. Sponsors can filter students by their progress or status.
* **Pagination:** Long lists (like pages of courses or student records) are broken down into small, numbered pages so the app loads fast.
* **Role-Based Login:** Users can only see the pages meant for their specific role using secure login groups.
* **Emails & Alerts:** The system sends emails for deadlines and scores, plus in-app notifications for new tasks.

---

## 🛠️ Tools Used

* **Language:** Python
* **Web Framework:** Django and Django REST Framework
* **Documentation Tool:** DRF Spectacular (creates a test page for the backend links)
* **Database:** PostgreSQL

---
