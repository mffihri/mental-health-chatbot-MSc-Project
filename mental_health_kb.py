"""
Mental Health Knowledge Base for RAG System

This file contains sample mental health information to be used with the RAG system.
You can replace or extend this content with your own mental health resources.
"""

# Sample mental health knowledge base
MENTAL_HEALTH_DOCUMENTS = [
    {
        "content": """Depression is a mood disorder that causes a persistent feeling of sadness and loss of interest.
It affects how you feel, think, and behave and can lead to a variety of emotional and physical problems.
Common symptoms include persistent sadness, loss of interest in activities once enjoyed, sleep disturbances,
fatigue, feelings of worthlessness, difficulty concentrating, and thoughts of death or suicide.
Depression is treatable with therapy, medication, lifestyle changes, or a combination of these approaches.""",
        "metadata": {"source": "mental_health_guide", "topic": "depression", "type": "informational"}
    },
    {
        "content": """Anxiety disorders involve excessive worry, fear, or nervousness that interferes with daily activities.
Common symptoms include restlessness, feeling on edge, fatigue, difficulty concentrating, irritability,
muscle tension, and sleep problems. Types of anxiety disorders include generalized anxiety disorder,
panic disorder, social anxiety disorder, and specific phobias. Treatment options include therapy,
medication, stress management techniques, and lifestyle changes.""",
        "metadata": {"source": "mental_health_guide", "topic": "anxiety", "type": "informational"}
    },
    {
        "content": """Cognitive Behavioral Therapy (CBT) is a type of psychotherapy that helps people identify
and change negative thinking patterns and behaviors. It focuses on challenging distorted thoughts
and replacing them with more realistic and positive ones. CBT is highly effective for treating
depression, anxiety disorders, PTSD, OCD, and many other mental health conditions. It typically
involves working with a therapist for 12-20 sessions and practicing new skills between sessions.""",
        "metadata": {"source": "therapy_guide", "topic": "CBT", "type": "therapeutic"}
    },
    {
        "content": """Mindfulness meditation is a practice that involves focusing on the present moment without judgment.
Regular mindfulness practice can reduce stress, anxiety, and depression symptoms by helping you:
1. Become more aware of your thoughts without being ruled by them
2. Respond thoughtfully rather than reacting automatically
3. Develop a greater sense of calm and balance
4. Improve concentration and sleep quality
Start with just 5 minutes daily, focusing on your breath, and gradually increase the duration.""",
        "metadata": {"source": "coping_strategies", "topic": "mindfulness", "type": "self_help"}
    },
    {
        "content": """These grounding techniques can help during moments of anxiety or overwhelming emotions:
1. 5-4-3-2-1 Technique: Identify 5 things you can see, 4 things you can touch, 3 things you can hear,
   2 things you can smell, and 1 thing you can taste.
2. Deep breathing: Breathe in slowly for 4 counts, hold for 4, exhale for 6.
3. Body scan: Progressively focus attention from head to toe, noticing sensations without judgment.
4. Physical grounding: Feel your feet on the ground, press your palms together, or hold a cold or textured object.
5. Mental categories: Name items within categories (e.g., types of dogs, cities, or foods).""",
        "metadata": {"source": "coping_strategies", "topic": "grounding", "type": "crisis_support"}
    },
    {
        "content": """Physical activity is a powerful tool for improving mental health. Regular exercise:
- Releases endorphins and other neurotransmitters that reduce pain and enhance mood
- Reduces levels of stress hormones like cortisol and adrenaline
- Improves sleep quality
- Increases self-confidence and sense of control
- Provides distraction from worries and negative thoughts
Even 30 minutes of moderate activity 3-5 times per week can significantly improve symptoms of depression and anxiety.""",
        "metadata": {"source": "lifestyle_strategies", "topic": "exercise", "type": "self_help"}
    },
    {
        "content": """Creating and maintaining a strong support system is essential for mental health.
Here are ways to build your support network:
1. Reach out to trusted friends and family members
2. Join support groups related to your specific challenges
3. Consider therapy or counseling for professional support
4. Connect with community organizations or religious/spiritual groups
5. Use online communities and forums responsibly
Remember that seeking help is a sign of strength, not weakness.""",
        "metadata": {"source": "support_resources", "topic": "social_support", "type": "informational"}
    },
    {
        "content": """Trauma-Informed Care (TIC) is an approach that recognizes the widespread impact of trauma
and understands potential paths for recovery. It recognizes the signs and symptoms of trauma in clients,
families, staff, and others. TIC responds by fully integrating knowledge about trauma into policies,
procedures, and practices, and seeks to actively resist re-traumatization. The key principles include:
safety, trustworthiness and transparency, peer support, collaboration, empowerment, and cultural sensitivity.""",
        "metadata": {"source": "professional_guide", "topic": "trauma_informed_care", "type": "professional"}
    },
    {
        "content": """If you're experiencing thoughts of suicide, please know that you're not alone and help is available.
Please contact a crisis helpline immediately:
- National Suicide Prevention Lifeline (US): 1-800-273-8255 (Available 24/7)
- Crisis Text Line: Text HOME to 741741 (US & UK)
- Samaritans (UK): 116 123
These services provide free, confidential support 24/7. You can also go to your nearest emergency room
or call emergency services (911 in US, 999 in UK).""",
        "metadata": {"source": "crisis_resources", "topic": "suicide_prevention", "type": "crisis_support"}
    },
    {
        "content": """Setting boundaries is essential for mental health and healthy relationships.
Healthy boundaries involve:
1. Knowing your limits (physical, emotional, mental)
2. Communicating these limits clearly to others
3. Being consistent with your boundaries
4. Respecting others' boundaries as well
5. Understanding that it's okay to say "no"
Remember that setting boundaries isn't selfish—it's necessary for your wellbeing and for developing
respectful, balanced relationships.""",
        "metadata": {"source": "relationship_guide", "topic": "boundaries", "type": "self_help"}
    }
]

# Function to get the knowledge base
def get_mental_health_kb():
    """Return the mental health knowledge base documents."""
    return MENTAL_HEALTH_DOCUMENTS

# Function to load the knowledge base into the RAG system
def load_mental_health_kb_into_rag():
    """Load the mental health knowledge base into the RAG system."""
    from ollama_handler import load_rag_documents
    return load_rag_documents(MENTAL_HEALTH_DOCUMENTS)

# Example usage
if __name__ == "__main__":
    print(f"Mental Health Knowledge Base contains {len(MENTAL_HEALTH_DOCUMENTS)} documents")
    print("Sample topics:", ", ".join(set(doc["metadata"]["topic"] for doc in MENTAL_HEALTH_DOCUMENTS)))
