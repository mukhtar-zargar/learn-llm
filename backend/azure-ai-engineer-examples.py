from dotenv import load_dotenv
import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.inference.models import SystemMessage, UserMessage


def main():
    load_dotenv()

    # Get the Azure Text Analytics endpoint and key from environment variables
    endpoint = os.getenv("AZURE_AI_SERVICE_ENDPOINT")
    key = os.getenv("AZURE_AI_SERVICE_API_KEY")

    client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Example text to analyze
    documents = ["The food and service were unacceptable. While the host was nice, the waiter was rude and food was cold.!"]

    response = client.analyze_sentiment(documents=documents)

    for doc in response:
        print(f"Document sentiment: {doc.sentiment} with confidence scores {doc.confidence_scores}")

    response = client.detect_language(documents=documents)

    for doc in response:
        print(f"Document language: {doc.primary_language.name} with confidence score {doc.primary_language.confidence_score}")

# if __name__ == "__main__":
#     main()


project = AIProjectClient(
    endpoint=os.getenv("AZURE_AI_SERVICE_PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
)

connections = project.connections
gen_ai = connections.get('GenAISetup01')

# print(gen_ai)
print("List all connections:")
for connection in connections.list():
    print(f"{connection.name} ({connection.type})")


#   ## Get a chat client
# chat_client = project.inference.get_chat_completions_client()

# # Get a chat completion based on a user-provided prompt
# # print(chat_client.get_model_info())
# user_prompt = input("Enter a question:")

# response = chat_client.complete(
#     model="gpt-35-turbo",
#     messages=[
#         SystemMessage("You are a helpful AI assistant that answers questions."),
#         UserMessage(user_prompt)
#     ],
# )
# print(response.choices[0].message.content)

## Get an Azure OpenAI chat client
openai_client = project.inference.get_azure_openai_client(api_version="2024-05-01-preview")

# Get a chat completion based on a user-provided prompt
user_prompt = input("Enter a question:")
response = openai_client.chat.completions.create(
    model="gpt-4o-model",
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant that answers questions."},
        {"role": "user", "content": user_prompt},
    ]
)
print(response.choices[0].message.content)
