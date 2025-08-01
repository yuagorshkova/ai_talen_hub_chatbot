import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from graph import app
from langchain_core.messages import HumanMessage

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context):
    """Start a new conversation with fresh context"""
    user_id = str(update.effective_user.id)
    # Clear any existing conversation
    await app.acheckpointer.adelete_thread({"configurable": {"thread_id": user_id}})
    await update.message.reply_text("Hello! I'm your AI assistant. How can I help you today?")

async def handle_message(update: Update, context):
    """Process user messages with conversation context"""
    user_message = update.message.text
    user_id = str(update.effective_user.id)
    
    # Prepare the conversation thread
    thread = {"configurable": {"thread_id": user_id}}
    
    try:
        # Get current conversation state if exists
        current_state = await app.acheckpointer.aget(thread)
        
        # Prepare input with history
        inputs = {
            "messages": [
                *([] if not current_state else current_state["values"]["messages"]),
                HumanMessage(content=user_message)
            ]
        }
        
        # Process through LangGraph
        result = await app.ainvoke(inputs, thread)
        
        # Get the last AI response
        ai_response = result["messages"][-1].content
        
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        await update.message.reply_text("Sorry, I encountered an error. Let's start fresh.")
        await start(update, context)  # Reset conversation

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    
    application.run_polling()

if __name__ == '__main__':
    main()