# Dashboard User Guide

**Version**: 1.0
**Last Updated**: 2026-02-07

Welcome to the Todo Application Dashboard! This guide will help you understand and make the most of your dashboard features.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Understanding Your Statistics](#understanding-your-statistics)
4. [Real-Time Updates](#real-time-updates)
5. [Dashboard Features](#dashboard-features)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## Overview

The Dashboard provides a real-time overview of your task management activity. It displays key metrics and statistics to help you track your productivity and stay organized.

### Key Features

- **Live Statistics**: View total, pending, and completed tasks at a glance
- **Shared Tasks**: Track tasks shared with you by team members
- **Activity Metrics**: Monitor your daily and weekly task activity
- **Auto-Refresh**: Dashboard updates automatically every 5 seconds
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

---

## Getting Started

### Accessing the Dashboard

1. **Sign In**: Log in to your account at the sign-in page
2. **Navigate**: Click on "Dashboard" in the navigation menu
3. **View**: Your dashboard will load with current statistics

### First Time Setup

When you first access the dashboard:
- You'll see zero statistics if you haven't created any tasks yet
- Create your first task to see the dashboard come to life
- Statistics update automatically as you add, complete, or share tasks

---

## Understanding Your Statistics

### Task Statistics Card

The main statistics card displays four key metrics:

#### 1. Total Tasks
- **What it shows**: The total number of tasks you've created
- **Includes**: Both pending and completed tasks
- **Excludes**: Tasks that have been deleted

#### 2. Pending Tasks
- **What it shows**: Tasks that are not yet completed
- **Status**: Tasks with `status: "pending"`
- **Action**: Click to view your pending tasks list

#### 3. Completed Tasks
- **What it shows**: Tasks you've finished
- **Status**: Tasks with `status: "completed"`
- **Calculation**: Completion rate = (Completed / Total) × 100%

#### 4. Shared Tasks
- **What it shows**: Tasks shared with you by other users
- **Permissions**: May be view-only or editable depending on share settings
- **Access**: Click to view all shared tasks

### Activity Metrics

Additional metrics available on the dashboard:

- **Tasks Created Today**: New tasks added in the last 24 hours
- **Tasks Completed Today**: Tasks finished in the last 24 hours
- **Weekly Activity**: Task creation and completion over the past 7 days
- **Completion Rate**: Percentage of tasks completed vs. total tasks

---

## Real-Time Updates

### How It Works

The dashboard automatically refreshes every 5 seconds to show the latest data:

1. **Automatic Polling**: Dashboard fetches new data every 5 seconds
2. **Smooth Updates**: Statistics update without page reload
3. **Visual Feedback**: Loading indicators show when data is being fetched
4. **Error Recovery**: Automatic retry if connection fails

### Update Indicators

- **Loading State**: Spinner or skeleton screen while fetching data
- **Success**: Statistics update smoothly with new values
- **Error**: Error message with retry button if update fails

### Manual Refresh

You can manually refresh the dashboard:
- Click the refresh icon (if available)
- Reload the page (Ctrl+R or Cmd+R)
- Navigate away and back to the dashboard

---

## Dashboard Features

### 1. Statistics Cards

**Visual Design**:
- Color-coded cards for easy identification
- Large numbers for quick scanning
- Icons representing each metric
- Hover effects for interactivity

**Interaction**:
- Click on a card to view related tasks
- Hover to see additional details
- Responsive layout adapts to screen size

### 2. Task Breakdown

View your tasks by status:
- **Pending**: Tasks awaiting completion
- **Completed**: Finished tasks
- **Total**: All tasks combined

### 3. Shared Tasks Details

Detailed breakdown of shared tasks:
- **Total Shared**: All tasks shared with you
- **View Only**: Tasks you can view but not edit
- **Can Edit**: Tasks you have permission to modify

### 4. Activity Timeline

Track your productivity over time:
- Daily task creation and completion
- Weekly trends and patterns
- Completion rate over time

---

## Troubleshooting

### Dashboard Not Loading

**Problem**: Dashboard page is blank or shows loading indefinitely

**Solutions**:
1. Check your internet connection
2. Verify you're logged in (check for valid session)
3. Clear browser cache and reload
4. Try a different browser
5. Check browser console for errors (F12)

### Statistics Not Updating

**Problem**: Numbers don't change when you create/complete tasks

**Solutions**:
1. Wait 5 seconds for automatic refresh
2. Manually refresh the page
3. Check if tasks are being created successfully
4. Verify you're viewing the correct user's dashboard
5. Check network tab for failed API requests

### Incorrect Statistics

**Problem**: Numbers don't match your actual tasks

**Solutions**:
1. Refresh the page to fetch latest data
2. Verify task status (pending vs. completed)
3. Check if tasks belong to the correct user
4. Ensure shared tasks are properly configured
5. Contact support if issue persists

### Slow Performance

**Problem**: Dashboard takes long to load or update

**Solutions**:
1. Check your internet connection speed
2. Close unnecessary browser tabs
3. Clear browser cache
4. Disable browser extensions temporarily
5. Try accessing during off-peak hours

### Error Messages

#### "Failed to fetch statistics"
- **Cause**: Network error or server unavailable
- **Solution**: Check internet connection, wait a moment, and retry

#### "Unauthorized"
- **Cause**: Session expired or invalid token
- **Solution**: Sign out and sign in again

#### "Internal Server Error"
- **Cause**: Backend issue
- **Solution**: Wait a few minutes and retry, contact support if persistent

---

## FAQ

### How often does the dashboard update?

The dashboard automatically refreshes every 5 seconds to show the latest statistics. You can also manually refresh at any time.

### Can I customize which statistics are shown?

Currently, the dashboard shows a fixed set of statistics. Customization features may be added in future updates.

### Do shared tasks count toward my total?

No, shared tasks are counted separately. Your "Total Tasks" only includes tasks you created. Shared tasks appear in the "Shared Tasks" metric.

### What happens if I delete a task?

Deleted tasks are removed from all statistics immediately. The dashboard will update within 5 seconds to reflect the change.

### Can I see historical data?

The current version shows real-time statistics. Historical trends and analytics features are planned for future releases.

### Why do my statistics differ from the task list?

This can happen if:
- Dashboard is still loading (wait for refresh)
- Tasks are filtered in the task list
- Shared tasks are included/excluded differently
- Cache needs to be cleared

### How do I share my dashboard with others?

The dashboard is personal and shows only your statistics. To collaborate with others, use the Teams feature to share specific tasks.

### Is the dashboard available offline?

No, the dashboard requires an internet connection to fetch real-time statistics from the server.

### Can I export dashboard data?

Export functionality is not currently available but is planned for future releases.

### What browsers are supported?

The dashboard works on all modern browsers:
- Chrome (recommended)
- Firefox
- Safari
- Edge
- Opera

Mobile browsers are also fully supported.

---

## Tips for Best Experience

### 1. Keep Your Browser Updated
Use the latest version of your browser for optimal performance and security.

### 2. Use a Stable Internet Connection
A reliable connection ensures smooth real-time updates.

### 3. Organize Your Tasks
Use clear titles and descriptions to make statistics more meaningful.

### 4. Check Dashboard Regularly
Make it a habit to review your dashboard daily to track progress.

### 5. Use Keyboard Shortcuts
- `Ctrl+R` / `Cmd+R`: Refresh page
- `F5`: Reload dashboard
- `F12`: Open developer tools (for troubleshooting)

### 6. Mobile Usage
- Dashboard is fully responsive
- Swipe to refresh on mobile devices
- Tap cards for detailed views

---

## Getting Help

### Support Resources

- **Documentation**: http://localhost:8000/docs
- **API Reference**: See backend/docs/api.md
- **GitHub Issues**: Report bugs and request features
- **Email Support**: support@example.com

### Reporting Issues

When reporting dashboard issues, please include:
1. Browser name and version
2. Operating system
3. Screenshot of the issue
4. Steps to reproduce
5. Error messages (if any)
6. Browser console logs (F12 → Console)

---

## What's Next?

### Upcoming Features

- **WebSocket Support**: Instant updates without polling
- **Custom Widgets**: Choose which statistics to display
- **Historical Charts**: View trends over time
- **Export Data**: Download statistics as CSV/PDF
- **Dark Mode**: Eye-friendly theme for night work
- **Notifications**: Alerts for important milestones

### Stay Updated

Check the changelog and release notes for new features and improvements.

---

## Conclusion

The Dashboard is your command center for task management. Use it to:
- Monitor your productivity
- Track task completion
- Stay organized
- Collaborate with teams

For more information, visit the [API Documentation](http://localhost:8000/docs) or contact support.

**Happy task managing!** 🚀
