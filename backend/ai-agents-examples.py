import os
from dotenv import load_dotenv
from pathlib import Path  


from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FilePurpose, CodeInterpreterTool, ListSortOrder, MessageRole

load_dotenv()

def main():
    project_endpoint = os.getenv("AGENT_PROJECT_ENDPOINT")
    model_name = os.getenv("AGENT_MODEL_NAME")

    data_file = Path(__file__).parent / "data" / "agent-data.txt"

    with data_file.open("r") as file:
        data = file.read() + "\n" 
        print(f"Data loaded from {data_file}: {data}")

    agent_client = AgentsClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(exclude_environment_credential=True, exclude_managed_identity_credential=True)    
    ) 
    
    with agent_client:
        file = agent_client.files.upload_and_poll(
            file_path=data_file,
            purpose=FilePurpose.AGENTS,
        )

        print(f"File uploaded: {file.filename}")

        code_interpreter_tool = CodeInterpreterTool(
            file_ids=[file.id],
        )

        agent = agent_client.create_agent(
            name="DataAgent",
            model=model_name,
            tools=code_interpreter_tool.definitions,
            tool_resources=code_interpreter_tool.resources,
            instructions="You are an AI agent that analyzes the data in the file that has been uploaded. If the user requests a chart, create it and save it as a .png file."
        )
        print(f"Using agent: {agent.name}")

        thread = agent_client.threads.create()

        while True:
            # Get input text
            user_prompt = input("Enter a prompt (or type 'quit' to exit): ")
            if user_prompt.lower() == "quit":
                break
            if len(user_prompt) == 0:
                print("Please enter a prompt.")
                continue

            message = agent_client.messages.create(
                thread_id=thread.id,
                role=MessageRole.USER,
                content=user_prompt,
            )

            run = agent_client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id,
            )

            if run.status == "failed":
                print(f"Run failed: {run.last_error}")

            last_msg = agent_client.messages.get_last_message_text_by_role(
                thread_id=thread.id,
                role=MessageRole.AGENT,
            )

            if last_msg:
                print(f"Agent response: {last_msg.text.value}")
        
        # Get the conversation history
        messages = agent_client.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING,
        )

        for message in messages:
            if message.text_messages:
                last_msg = message.text_messages[-1]
                print(f"{message.role}: {last_msg.text.value}")  
            print("message.image_contents: " + str(len(message.image_contents))) 
            for img in message.image_contents:
                print(f"Image file ID: {img.image_file.file_id}")
                file_id = img.image_file.file_id
                file_name = f"{file_id}_image_file.png"
                agent_client.files.save(file_id=file_id, file_name=file_name)
                print(f"Saved image file to: {Path.cwd() / file_name}")
 


        agent_client.delete_agent(agent.id)
        agent_client.threads.delete(thread.id)
if __name__ == "__main__":
    main()