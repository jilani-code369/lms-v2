# 1. User

## default fields: 
- id (PK)
- username
- password
- first_name
- last_name
- email
- is_active
- is_staff
- is_superuser
- groups
- user_permissions
- lat_login
- date_joined

## custom fields: 
- role 
- address
- phone_no
- photo
- dob
- gender


# 2. Course
- id (PK)
- instructor (FK → User)
- course_image
- title
- description
- price
- difficulty_level
- syllabus

- created_at
- updated_at


# 3. Enrollment
- id (PK)
- student (FK → User)
- course (FK → Course)
- enrollment_date
- status
- progress

- updated_at


# 4. Assignment
- id (PK)
- course (FK → Course)
- title
- description
- total_marks
- deadline

- created_at
- updated_at


# 5. Submission

## writtable by student: 
- id (PK)
- assignment (FK → Assignment)
- student (FK → User)
- answer_text
- file

## written by instructor only, student can readonly: 
- marks_obtained
- status

- submitted_at
- updated_at


# 6. Sponsorship
- id (PK)
- sponsor (FK → User)
- organization_name
- student (FK → User) (1:1)
- course (FK → Course)
- amount
- status

- funded_at
- updated_at


# 7. Notification
- id (PK)
- sender (FK → User)
- receiver (FK → User)
- message
- type
- is_read

- created_at
- updated_at


# Relationships

## One-to-One: 
- User(Student)            - Sponsorship (1:1)

## One-to-Many: 
- User (Instructor)        -> Course (1:M)
- User (Student)           -> Enrollment (1:M)
- User (Student)           -> Submission (1:M)
- User (Sponsor)           -> Sponsorship (1:M)
- User (Sponsor/Student)   -> Payment (1:M)
- User (Sender)            -> Notification (1:M)
- User (Receiver)          -> Notification (1:M)
- User (Sender)            -> Email_log (1:M)
- User (Receiver)          -> Email_log (1:M)
- Course                   -> Enrollment (1:M)
- Course                   -> Assignment (1:M)
- Course                   -> Sponsorship (1:M)
- Assignment               -> Submission (1:M)

## Many-to-Many: 
- Student                 <-> Course (M:M)
- Student                 <-> Assignment (M:M)
- Sponsor                 <-> Course (M:M)
- Sender (User)           <-> Receiver (User) (M:M) - Notification 
- Sender (User)           <-> Receiver (User) (M:M) - Email_log