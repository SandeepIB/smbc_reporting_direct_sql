# Admin Interface Access Guide

## How to Access Admin Interface

### Method 1: Direct Admin Page (Recommended)
1. Start the application: `bash start_fullstack.sh`
2. Open http://localhost:3000
3. Click the **⚙️** (gear) icon on the home page
4. Login with admin credentials:
   - **Username**: admin
   - **Password**: admin123
5. Access the full Admin Dashboard for feedback management

### Method 2: Direct Database Access
The feedback data is stored in MySQL database `org_insights` with tables:
- `feedback` - User feedback submissions
- `training_data` - Approved training data

## Admin Credentials

**Default Login:**
- Username: `admin`
- Password: `admin123`

*Note: These are hardcoded credentials for demo purposes. In production, implement proper authentication.*

### Admin Interface Features

#### Feedback Management
- **View Pending Feedback**: See all negative feedback waiting for review
- **Approve Feedback**: Add feedback to training data for future improvements
- **Reject Feedback**: Dismiss feedback that's not useful

#### Training Data Management
- **View Training Data**: See all approved training examples
- **Add Manual Training**: Add custom question-answer pairs
- **Context Management**: Add contextual information for better responses

### Database Schema

#### Feedback Table
```sql
CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id VARCHAR(255),
    type VARCHAR(50),
    feedback TEXT,
    original_query TEXT,
    sql_query TEXT,
    response TEXT,
    session_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Training Data Table
```sql
CREATE TABLE training_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT,
    answer TEXT,
    context TEXT,
    source VARCHAR(50) DEFAULT 'manual',
    approved_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Workflow
1. **User gives thumbs down** → Feedback stored in database
2. **Admin reviews feedback** → Approves/rejects via admin interface
3. **Approved feedback** → Added to training data
4. **Future queries** → Enhanced with semantic context from training data

### API Endpoints
- `POST /admin/login` - Admin authentication
- `GET /admin/feedbacks` - Get pending feedback
- `POST /admin/feedbacks/{id}/approve` - Approve feedback
- `POST /admin/feedbacks/{id}/reject` - Reject feedback
- `GET /admin/training-data` - Get training data
- `POST /admin/training-data` - Add training data

### Security Features
- **Login Required**: All admin functions require authentication
- **Session Management**: Admin sessions are managed securely
- **Separate Interface**: Admin panel is completely separate from user chat
- **Access Control**: Only authenticated admins can access feedback data