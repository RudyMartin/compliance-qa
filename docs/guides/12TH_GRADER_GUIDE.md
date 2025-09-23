# 12th Grader Guide: Using the MLflow Recent Activity Viewer

## What is This?
This is a tool that shows you the last 5 things that happened in our AI system. Think of it like looking at your recent text messages - you can see what the AI has been doing lately.

## How to Use It

### Step 1: Open Your Web Browser
Go to: **http://localhost:8520** (or whichever port number we gave you)

### Step 2: Look for "MLflow Recent Activity" Section
You'll see a button or section that says something like:
- "Show Recent Activity"
- "Last 5 MLflow Records"
- "Recent AI Activity"

### Step 3: Click the Button
When you click it, you'll see information like:
- **When**: What time did each AI task happen?
- **User**: Who asked the AI to do something?
- **Task Type**: What kind of work did the AI do? (like "answer a question" or "analyze data")
- **Tokens**: How much "thinking" did the AI do? (higher numbers = more complex tasks)
- **Success**: Did it work correctly?

## What You're Looking At

### Example of What You Might See:
```
RECORD #1 - MLflow Run
========================
When: 2025-09-20 10:30:15
User: student_test_user
Task: Answer question about homework
Tokens Used: 1,250
Status: SUCCESS
Model: claude-3-sonnet
```

### What This Means:
- **When**: The exact time this happened
- **User**: The person who used the AI
- **Task**: What they asked the AI to do
- **Tokens**: How much work the AI did (like counting words)
- **Status**: Whether it worked or failed
- **Model**: Which AI brain was used

## Why This is Useful

1. **Track Usage**: See who's using the AI and how much
2. **Debug Problems**: If something goes wrong, you can see what happened
3. **Monitor Performance**: Check if the AI is working fast enough
4. **Study Patterns**: Learn what tasks people do most often

## Simple Test to Try

1. Go to the chat section of the app
2. Ask the AI a simple question like "What is 2+2?"
3. Wait a few seconds
4. Go back to the "Recent Activity" viewer
5. You should see your question appear as the newest record!

## Common Issues and Solutions

### "No records found"
- **Problem**: The AI hasn't been used yet today
- **Solution**: Try asking the AI a question first, then check again

### "Connection error"
- **Problem**: The database isn't working
- **Solution**: Ask a teacher or admin to check the settings

### "Shows localhost errors"
- **Problem**: It's trying to connect to the wrong database
- **Solution**: This is a technical issue - tell an admin you see "localhost connection refused"

## Questions to Ask Yourself

1. Can I easily find the "Recent Activity" button?
2. Do I understand what each piece of information means?
3. Can I tell if the AI is working properly?
4. Would my classmates be able to use this without help?

## Success Criteria for 12th Grader Test

✅ **Easy to Find**: The recent activity feature should be clearly labeled
✅ **Easy to Read**: Information should be in plain English, not technical jargon
✅ **Fast to Load**: Should show results in under 5 seconds
✅ **Clear Status**: Should clearly show if something worked or failed
✅ **Useful Info**: Should answer "Who did what, when, and did it work?"

If any of these aren't working, the interface needs to be improved!