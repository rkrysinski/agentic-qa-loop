import chainlit as cl
from app.utils import extract_text_from_file
from app.orchestrator import Orchestrator

@cl.on_chat_start
async def start():
    files = None
    
    # Wait for the user to upload a file
    while files == None:
        files = await cl.AskFileMessage(
            content="Please upload a text file to begin processing.", 
            accept=["text/plain", "application/pdf", "text/markdown"],
            max_size_mb=20,
            timeout=180
        ).send()

    file = files[0]
    
    # Extract text (mock impl for now in utils, supports text read)
    # Spec mentioned "text extraction" but utils only does open().read().
    # Assuming user uploads .md or .txt for now as per "reqirements.md" context.
    
    msg = cl.Message(content=f"Processing `{file.name}`...")
    await msg.send()

    # Read file content
    try:
        text_content = extract_text_from_file(file)
    except Exception as e:
        await cl.Message(content=f"Error reading file: {str(e)}").send()
        return

    # Store the document in the user session
    cl.user_session.set("document_content", text_content)
    
    msg.content = f"`{file.name}` processed. You can now ask questions about it."
    await msg.update()

@cl.on_message
async def main(message: cl.Message):
    document_content = cl.user_session.get("document_content")
    
    if not document_content:
        await cl.Message(content="No document found. Please restart the chat and upload a file.").send()
        return

    orchestrator = Orchestrator(document_content, message.content)
    
    final_answer = await orchestrator.run()
    
    await cl.Message(content=final_answer).send()
