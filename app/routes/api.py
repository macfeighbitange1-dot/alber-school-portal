from flask import Blueprint, request
from app.services.ai_tutor import get_ai_explanation

# Define the blueprint here
api = Blueprint('api', __name__)

@api.route('/ai-tutor', methods=['POST'])
def handle_ai_query():
    student_query = request.form.get('student_query')
    explanation = get_ai_explanation(student_query, grade_level=4)
    
    return f"""
    <div class="mt-6 p-6 bg-white rounded-xl border-l-4 border-blue-600 shadow-sm">
        <h4 class="text-blue-800 font-bold mb-2">Teacher's Explanation:</h4>
        <p class="text-gray-700 leading-relaxed">{explanation}</p>
    </div>
    """