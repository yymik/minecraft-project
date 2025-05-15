import os
from google.cloud import dialogflow_v2 as dialogflow

# JSON 경로 지정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "chatbot/eternal-unity-459818-q2-e6e959835a0a.json"

def get_dialogflow_response(user_input):
    print("🟢 [DEBUG] get_dialogflow_response() 호출됨")

    project_id = 'eternal-unity-459818-q2'
    session_id = 'unique-session-id'
    language_code = 'ko'
    #set endpoint start

    session_client = dialogflow.SessionsClient(
        client_options={"api_endpoint": "asia-northeast1-dialogflow.googleapis.com"}
    )
    #set endpoint
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=user_input, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    #user input
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    #response

    return response.query_result.fulfillment_text
