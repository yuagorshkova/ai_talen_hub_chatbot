import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.graph import app
from langchain_core.messages import HumanMessage

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context):
    """Start a new conversation with fresh context"""
    user_id = str(update.effective_user.id)
    print(f"Starting new conversation for user {user_id}")
    
    # Clear any existing conversation
    try:
        await app.acheckpointer.adelete_thread({"configurable": {"thread_id": user_id}})
        print(f"Cleared previous conversation state for user {user_id}")
    except Exception as e:
        print(f"Error clearing conversation state for user {user_id}: {str(e)}")
    
    await update.message.reply_text("Hello! I'm your AI assistant. How can I help you today?")
    print(f"Sent welcome message to user {user_id}")

async def handle_message(update: Update, context):
    """Process user messages with conversation context"""
    user_message = update.message.text
    user_id = str(update.effective_user.id)
    
    print(f"Received message from user {user_id}: '{user_message}'")
    
    # Prepare the conversation thread
    thread = {"configurable": {"thread_id": user_id}}
    
    try:
        # Get current conversation state if exists
        print(f"Getting conversation state for user {user_id}")
        current_state = await app.acheckpointer.aget(thread)
        
        if current_state:
            print(f"Found existing conversation state with {len(current_state['values']['messages'])} messages")
        else:
            print("No existing conversation state found - starting fresh")
        
        # Prepare input with history
        inputs = {
            "messages": [
                *([] if not current_state else current_state["values"]["messages"]),
                HumanMessage(content=user_message)
            ]
        }
        
        print("Processing message through LangGraph...")
        result = await app.ainvoke(inputs, thread)
        print("Successfully processed message")
        
        # Get the last AI response
        ai_response = result["messages"][-1].content
        print(f"Sending response to user {user_id}: '{ai_response[:50]}...'")
        
        await update.message.reply_text(ai_response)
        print("Response sent successfully")
        
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        await update.message.reply_text("Sorry, I encountered an error. Let's start fresh.")
        await start(update, context)  # Reset conversation

def main():
    print("Initializing Telegram bot application...")
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    
    print("Bot is starting polling...")
    application.run_polling()
    print("Bot is now running")

if __name__ == '__main__':
    print("Starting bot application...")
    try:
        main()
    except Exception as e:
        print(f"Fatal error in bot application: {str(e)}")
        raise