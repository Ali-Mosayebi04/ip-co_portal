no# Meeting Room Management System

## Overview
A comprehensive meeting room management system has been added to the portal where admins can create meetings, select employees, and automatically send email notifications. Regular users can only view their own upcoming meetings.

## Features

### For Admins (Superuser Only)
1. **Create Meetings** - `/meetings/manage/create/`
   - Set meeting title, agenda, date, and time
   - Select meeting room from available rooms
   - Choose multiple employees to attend
   - Automatic email invitations sent to selected employees

2. **View All Meetings** - `/meetings/manage/`
   - List of all meetings with pagination
   - See meeting details, attendees count, and status
   - Quick access to edit or cancel meetings

3. **Edit Meetings** - `/meetings/manage/<id>/edit/`
   - Update meeting details
   - Add or remove attendees
   - Only newly added attendees receive invitation emails

4. **View Meeting Details** - `/meetings/manage/<id>/`
   - Complete meeting information
   - Full list of attendees with their details
   - Email delivery status for each attendee

5. **Cancel Meetings** - `/meetings/manage/<id>/delete/`
   - Cancel a meeting and notify all attendees
   - Automatic cancellation emails sent

### For Regular Users (Employees)
- **View Upcoming Meetings** - `/meetings/upcoming/`
  - See ONLY meetings they've been invited to
  - Shows meeting time, room, agenda, and organizer
  - Cannot create, edit, or delete meetings

## Email Notifications

The system automatically sends emails in these scenarios:
1. **Meeting Created** - All selected attendees receive invitation emails
2. **Meeting Updated** - Only newly added attendees receive invitations
3. **Meeting Cancelled** - All attendees who received invitations get cancellation notices

## Access Control
- **Admin Only**: Meeting management features (create, edit, delete) require superuser permissions (`is_superuser=True`)
- **Regular Users**: Can only view their own upcoming meetings at `/meetings/upcoming/`
- **Access Denied**: Non-admin users trying to access management pages get redirected to their upcoming meetings with an error message
- **Employee Link Required**: Users must be linked to an Employee record to see their meetings

## Email Templates
The system uses these templates (already created):
- `templates/emails/meeting_invitation.txt` - Invitation email content
- `templates/emails/meeting_cancellation.txt` - Cancellation email content

## Configuration

### Email Settings
Configure in `.env` file or environment variables:
```
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=پورتال ایران خودرو <no-reply@ipco.local>
```

For development, emails are printed to console by default.

## Database Models

### MeetingRoom
- Physical meeting rooms that can be booked
- Fields: name, location, capacity, is_active

### Meeting
- A booking of a room for a specific time
- Fields: room, organizer, title, agenda, date, start_time, end_time, attendees, is_cancelled

### MeetingInvitation
- Tracks individual attendee invitations
- Records email delivery status and errors
- Prevents duplicate email sending

## URLs

### Admin URLs (Superuser Only)
- `/meetings/manage/` - List all meetings
- `/meetings/manage/create/` - Create new meeting
- `/meetings/manage/<id>/` - View meeting details
- `/meetings/manage/<id>/edit/` - Edit meeting
- `/meetings/manage/<id>/delete/` - Cancel meeting

### Employee URLs (All Users)
- `/meetings/upcoming/` - View their own upcoming meetings

## Usage Example

1. Admin logs into the portal (must have superuser permissions)
2. Navigates to `/meetings/manage/`
3. Clicks "ایجاد جلسه جدید" (Create New Meeting)
4. Fills in meeting details:
   - Title: "Sprint Planning Meeting"
   - Agenda: "Discuss Q3 objectives and milestones"
   - Room: "Conference Room A"
   - Date: 2026-08-05
   - Time: 09:00 to 11:00
5. Selects employees from checkbox list
6. Clicks "ایجاد جلسه" (Create Meeting)
7. System saves meeting and sends email to all selected employees
8. Success message shows how many emails were sent

**For Regular Users:**
1. User logs into the portal
2. Navigates to `/meetings/upcoming/`
3. Sees only meetings where they are invited
4. Cannot create, edit, or manage meetings

## Notes

- Meeting room conflicts are automatically validated
- Start time must be before end time
- Employees without email addresses are skipped (no error)
- Email delivery status is tracked per attendee
- Failed emails don't block the meeting creation
- Cancelled meetings cannot be edited or deleted again
