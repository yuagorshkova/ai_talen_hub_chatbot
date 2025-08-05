import logging
import os

from langchain_core.messages import HumanMessage
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src.graph import workflow

# Setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, _):
    user_id = update.effective_user.id
    logger.info(f"New session started for user {user_id}")
    await update.message.reply_text(
        "Привет! Я бот-помощник по вопросам о программах магистратуры AI Talent Hub :) Чем могу помочь?"
    )


async def handle_message(update: Update, _):
    user_id = update.effective_user.id
    user_message = update.message.text
    logger.info(
        f"Message from user {user_id}: {user_message[:50]}..."
    )  # Log first 50 chars

    try:
        logger.info("Invoking LangGraph...")
        response = await workflow.ainvoke(
            {"messages": [HumanMessage(content=user_message)]},
            {"configurable": {"thread_id": str(user_id)}},
        )

        ai_response = response["messages"][-1].content
        logger.debug(f"Generated response: {ai_response[:50]}...")
        await update.message.reply_text(ai_response)

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        await update.message.reply_text("Error occurred. Restarting...")
        await start(update, None)


def main():
    logger.info("Starting bot application...")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    logger.info("Bot is running and polling...")
    application.run_polling()


if __name__ == "__main__":
    main()
