
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    """
    Validates and stores the user's answer for the current question to the Django session.
    Returns a tuple indicating whether the recording was successful and an error message if any.
    """

    # Get the current question based on the question ID
    current_question = None
    for question in PYTHON_QUESTION_LIST:
        if question['id'] == current_question_id:
            current_question = question
            break

    if current_question is None:
        return False, "Invalid question ID"

    # Validate the user's answer
    if answer not in current_question['options']:
        return False, "Invalid answer"

    # Store the user's answer in the session
    session['user_answers'] = session.get('user_answers', {})
    session['user_answers'][current_question_id] = answer
    session.save()

    return True, ""


def get_next_question(current_question_id):
    """
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    Returns the next question and its ID.
    """

    # Find the index of the current question
    current_index = None
    for index, question in enumerate(PYTHON_QUESTION_LIST):
        if question['id'] == current_question_id:
            current_index = index
            break

    # If the current question is not found or it's the last question, return None
    if current_index is None or current_index == len(PYTHON_QUESTION_LIST) - 1:
        return None, None

    # Get the next question
    next_question = PYTHON_QUESTION_LIST[current_index + 1]
    next_question_id = next_question['id']

    return next_question, next_question_id



def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    user_answers = session.get('user_answers', {})
    correct_answers = 0

    # Calculate the number of correct answers
    for question in PYTHON_QUESTION_LIST:
        question_id = question['id']
        if question_id in user_answers and user_answers[question_id] == question['answer']:
            correct_answers += 1

    # Calculate the score
    total_questions = len(PYTHON_QUESTION_LIST)
    score = (correct_answers / total_questions) * 100

    # Generate the final response message
    final_response = f"Your quiz score: {score:.2f}% ({correct_answers}/{total_questions} correct answers)."

    return final_response
