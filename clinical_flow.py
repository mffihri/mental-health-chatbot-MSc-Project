"""
Clinical Conversational Flow Module for Mental Health Chatbot
"""

# Structured conversation flow for clinical assessment
CLINICAL_QUESTIONS = [
    {
        "id": "presenting_issue",
        "question": "What brings you in today, and what are the main challenges you're experiencing?",
        "tag": "presenting_issue",
        "category": "current_concerns"
    },
    {
        "id": "mood_changes",
        "question": "Have you noticed changes in your mood, energy, or sleep patterns recently—such as feeling very down, anxious, or unusually energetic?",
        "tag": "mood",
        "category": "symptoms"
    },
    {
        "id": "unusual_experiences",
        "question": "Have you ever experienced things like hearing voices, seeing things others don't, or feeling that your thoughts are disorganized?",
        "tag": "unusual_experiences",
        "category": "symptoms"
    },
    {
        "id": "functional_impact",
        "question": "How are these issues affecting your daily life, relationships, and work or school?",
        "tag": "impact",
        "category": "functioning"
    },
    {
        "id": "past_events",
        "question": "Can you share any significant past events or stressors (like trauma or major life changes) that might be contributing to your current feelings?",
        "tag": "trauma",
        "category": "history"
    },
    {
        "id": "strengths",
        "question": "What personal strengths or support systems do you rely on when things get tough?",
        "tag": "strengths",
        "category": "resources"
    },
    {
        "id": "goals",
        "question": "What would you like to achieve from our work together?",
        "tag": "goals",
        "category": "treatment_planning"
    }
]

# Introduction text for the clinical conversation
INTRODUCTION_TEXT = """
Hello, I'm here to support you on your mental health journey. I'd like to understand your experiences better by asking some questions that will help create a timeline of your concerns and strengths.

This conversation will help us identify patterns and develop strategies tailored to your needs. Feel free to share as much or as little as you're comfortable with, and know that everything you share is confidential.

Let's start with understanding what brings you here today.
"""

# Function to get the next question based on conversation state
def get_next_question(conversation_state):
    """
    Returns the appropriate next question based on the current conversation state.
    
    Args:
        conversation_state (dict): Contains information about the current state of the conversation
        
    Returns:
        dict: The next question to ask
    """
    current_question_index = conversation_state.get('current_question_index', -1)
    
    # If we're just starting, return the introduction
    if current_question_index == -1:
        return {
            "id": "introduction",
            "text": INTRODUCTION_TEXT,
            "is_question": False
        }
    
    # If we've gone through all questions, return a closing message
    if current_question_index >= len(CLINICAL_QUESTIONS):
        return {
            "id": "closing",
            "text": "Thank you for sharing your experiences with me. Based on what you've shared, I can now offer more personalized support. Is there anything specific you'd like to focus on today?",
            "is_question": True
        }
    
    # Return the next question in the sequence
    return {
        "id": CLINICAL_QUESTIONS[current_question_index]["id"],
        "text": CLINICAL_QUESTIONS[current_question_index]["question"],
        "is_question": True,
        "tag": CLINICAL_QUESTIONS[current_question_index]["tag"],
        "category": CLINICAL_QUESTIONS[current_question_index]["category"]
    }

# Function to process user response and update timeline
def process_response(user_response, question_data, timeline_data):
    """
    Processes the user's response to a clinical question and updates the timeline.
    
    Args:
        user_response (str): The user's response to the question
        question_data (dict): Data about the question that was asked
        timeline_data (dict): The current timeline data
        
    Returns:
        dict: Updated timeline data
    """
    # Skip processing for non-questions (like the introduction)
    if not question_data.get('is_question', True):
        return timeline_data
    
    # Extract timestamp
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    
    # Create a new entry for the timeline
    entry = {
        "timestamp": timestamp,
        "question_id": question_data.get('id'),
        "question": question_data.get('text'),
        "response": user_response,
        "tag": question_data.get('tag'),
        "category": question_data.get('category')
    }
    
    # Add the entry to the timeline
    if 'entries' not in timeline_data:
        timeline_data['entries'] = []
    
    timeline_data['entries'].append(entry)
    
    return timeline_data

# Function to generate a clinical summary from the timeline
def generate_clinical_summary(timeline_data):
    """
    Generates a clinical summary from the timeline data.
    
    Args:
        timeline_data (dict): The timeline data collected during the conversation
        
    Returns:
        str: A clinical summary of the user's responses
    """
    if not timeline_data or 'entries' not in timeline_data or not timeline_data['entries']:
        return "Insufficient data to generate a clinical summary."
    
    # Organize entries by category
    categories = {}
    for entry in timeline_data['entries']:
        category = entry.get('category')
        if category not in categories:
            categories[category] = []
        categories[category].append(entry)
    
    # Generate the summary
    summary = "CLINICAL ASSESSMENT SUMMARY\n\n"
    
    # Add each category to the summary
    for category_name, entries in categories.items():
        if entries:
            # Format the category name for display
            formatted_category = category_name.replace('_', ' ').title()
            summary += f"{formatted_category}:\n"
            
            # Add each entry in the category
            for entry in entries:
                summary += f"- Question: {entry.get('question')}\n"
                summary += f"  Response: {entry.get('response')}\n\n"
    
    # Add a conclusion
    summary += "CLINICAL IMPRESSIONS:\n"
    summary += "Based on the information provided, consider the following areas for further exploration:\n"
    
    # Add suggestions based on the categories present
    if 'symptoms' in categories:
        summary += "- Assess severity and duration of reported symptoms\n"
    if 'trauma' in categories or 'history' in categories:
        summary += "- Explore trauma history and its connection to current symptoms\n"
    if 'functioning' in categories:
        summary += "- Evaluate functional impairment across domains\n"
    if 'resources' in categories:
        summary += "- Leverage identified strengths in treatment planning\n"
    
    return summary
