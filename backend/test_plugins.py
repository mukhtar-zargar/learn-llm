import os
import asyncio
from dotenv import load_dotenv

from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextCompletion, OpenAIChatCompletion
from semantic_kernel.functions import kernel_function
from semantic_kernel import Kernel
from semantic_kernel.core_plugins.time_plugin import TimePlugin
from semantic_kernel.core_plugins.conversation_summary_plugin import ConversationSummaryPlugin
from semantic_kernel.prompt_template import PromptTemplateConfig, InputVariable
from semantic_kernel.functions import KernelArguments
from semantic_kernel.functions.kernel_plugin import KernelPlugin

load_dotenv()


api_key = os.getenv("AZURE_OPENAI_API_KEY")
base_url = os.getenv("AZURE_OPENAI_API_ENDPOINT")
ai_model_id = os.getenv("DEPLOYMENT_NAME")


kernel = Kernel()

kernel.remove_all_services()

chat_completion_service = AzureChatCompletion(
    service_id="azure-gpt35",
    deployment_name=ai_model_id,
    api_key=api_key,
    endpoint=base_url,
)

kernel.add_service(chat_completion_service)

# chat_completion_service = OpenAIChatCompletion(
#     service_id="openai-gpt35",
#     ai_model_id="gpt-3.5-turbo",  # or "gpt-4"
#     api_key=api_key,
# )

# kernel.add_service(chat_completion_service)

# text_completion_service = AzureTextCompletion(
#     service_id="azure-gpt35-text", 
#     deployment_name=ai_model_id,
#     api_key=api_key,
#     endpoint=base_url,
# )

# kernel.add_service(text_completion_service)


async def main():
    from native_plugins.career_history.career_tracker_plugin import CareerTrackerPlugin

    career_tracker_plugin = CareerTrackerPlugin()

    kernel.add_plugin(career_tracker_plugin, plugin_name="career_tracker")
    ct = kernel.plugins["career_tracker"]
    print(f"Plugin loaded: {ct.name} - {ct.model_dump()}")

    history = await kernel.invoke(plugin_name="career_tracker", function_name="get_career_history")
    # result = career_tracker_plugin.get_career_history()
    print(f"Result {history}")

    # prompt = """This is a list of the user's career history:
    #     {{career_tracker.get_career_history}}
    #     Based on their career history, suggest a job role for them to pursue next and explain why. But first list down the ranks as well.
    # """

    prompt_template_config = PromptTemplateConfig(
        name="SummarizeConversation",
        template="Summarize the following conversation:\n{{$input}}",
        description="Summarize a conversation into a few key points.",
            input_variables=[InputVariable(name="input", description="The conversation text", type="string")]
    )
        
    conversation_summary_plugin = ConversationSummaryPlugin(prompt_template_config=prompt_template_config)
    kernel.add_plugin(conversation_summary_plugin, plugin_name="conversation_summary")


    prompt = """User's career history:
        {{conversation_summary.SummarizeConversation $history}}
        Based on their career history, suggest a job role for them to pursue next and explain why. But first list down the ranks as well.
    """
    args = KernelArguments(history=history)


    history = await kernel.invoke_prompt(prompt=prompt, arguments=args,)
    print(f"Result from prompt: {history}")

    

asyncio.run(main())