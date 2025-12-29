import chainlit as cl
from app.utils import extract_text_from_file
from app.orchestrator import Orchestrator
from app.config import config


@cl.on_chat_start
async def on_chat_start():
    """
    Initialize chat session with settings.
    """
    # Define chat settings
    settings = await cl.ChatSettings(
        [
            cl.input_widget.Slider(
                id="max_iterations",
                label="Maximum Iterations",
                initial=config.max_iterations,
                min=1,
                max=10,
                step=1,
                description="Maximum number of Producer-Critic refinement loops",
            ),
        ]
    ).send()
    
    # Store settings in user session
    cl.user_session.set("settings", settings)
    
    await cl.Message(
        content="👋 Welcome to the Agentic Q&A Loop!\n\n"
                "**How it works:**\n"
                "1. Upload a document (text file)\n"
                "2. Ask a question about it\n"
                "3. The Producer agent will generate an answer\n"
                "4. The Critic agent will evaluate and provide feedback\n"
                "5. The loop continues until the answer passes or max iterations is reached\n\n"
                f"**Current settings:** Max iterations = {settings['max_iterations']}\n\n"
                "📎 Please upload a document to begin."
    ).send()


@cl.on_settings_update
async def on_settings_update(settings):
    """
    Handle settings updates from the UI.
    """
    cl.user_session.set("settings", settings)
    await cl.Message(
        content=f"⚙️ Settings updated: Max iterations = {settings['max_iterations']}"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    # Get uploaded files
    files = message.elements
    
    # Initialize variables
    document_content = None
    
    if files:
        # Extract text from the first file
        file_path = files[0].path
        document_content = extract_text_from_file(file_path)
        
        if not document_content:
            await cl.Message(content="❌ Could not extract text from the file.").send()
            return

        # Clear previous final answer when new file is uploaded
        cl.user_session.set("final_answer", None)
        
    else:
        # Check if we have a previous final answer to iterate on
        previous_answer = cl.user_session.get("final_answer")
        if previous_answer:
            document_content = previous_answer
            # Notify user we are iterating
            await cl.Message(content="🔄 Iterating on previous answer...").send()
        else:
            await cl.Message(content="⚠️ Please upload a document first.").send()
            return
    
    # Get current settings
    settings = cl.user_session.get("settings", {"max_iterations": config.max_iterations})
    max_iterations = settings.get("max_iterations", config.max_iterations)
    
    # Create orchestrator with user-configured max_iterations
    orchestrator = Orchestrator(
        document_content, 
        message.content,
        max_iterations=max_iterations
    )
    
    # Run the Q&A loop
    final_answer = await orchestrator.run()
    
    # Store final answer for potential iteration
    cl.user_session.set("final_answer", final_answer)
    
    # Send final result
    await cl.Message(
        content=f"## ✅ Final Answer\n\n{final_answer}"
    ).send()
