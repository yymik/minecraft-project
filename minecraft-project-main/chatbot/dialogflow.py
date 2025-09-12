import os
from google.cloud import dialogflow_v2 as dialogflow

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "chatbot/eternal-unity-459818-q2-e6e959835a0a.json"

def get_dialogflow_response(user_input):
    
    project_id = 'eternal-unity-459818-q2'
    session_id = 'unique-session-id'
    language_code = 'ko'

    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=user_input, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return response.query_result.fulfillment_text

#동작O, 응답 정확도X -> intent 인식 정확도 튜닝 필요