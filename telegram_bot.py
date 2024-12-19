import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from openai import OpenAI

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MAX_MESSAGE_LENGTH = 4096  # Telegram's message length limit

# Available models
MODELS = {
    'o1-mini': 'O1 Mini',
    'o1-mini-2024-09-12': 'O1 Mini (Sep 12, 2024)',
    'gpt-4o': 'GPT-4O',
    'gpt-3.5-turbo': 'GPT-3.5 Turbo (Fallback)'
}

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def format_for_telegram(text: str) -> str:
    """Format text for Telegram's basic markdown."""
    # Replace ** with * for bold
    text = text.replace('**', '*')
    # Replace ``` with ` for code blocks
    text = text.replace('```', '`')
    return text

async def send_long_message(update: Update, text: str) -> None:
    """Split and send long messages."""
    # Format the text for Telegram
    text = format_for_telegram(text)
    
    # Split by newlines first to preserve formatting
    paragraphs = text.split('\n')
    current_chunk = ""
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 1 <= MAX_MESSAGE_LENGTH:
            current_chunk += paragraph + '\n'
        else:
            if current_chunk:
                await update.message.reply_text(current_chunk)
            current_chunk = paragraph + '\n'
    
    if current_chunk:
        await update.message.reply_text(current_chunk)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if 'model' not in context.user_data:
        context.user_data['model'] = 'o1-mini'  # Default to O1 Mini
    
    message = f"*Hello!* I am your AI assistant.\nCurrently using *{MODELS[context.user_data['model']]}*.\n\nUse /model to change the AI model."
    await update.message.reply_text(message)

async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show model selection keyboard."""
    keyboard = []
    for model_id, model_name in MODELS.items():
        keyboard.append([InlineKeyboardButton(model_name, callback_data=f"model:{model_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose an AI model:', reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle model selection button press."""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("model:"):
        model = query.data.split(":")[1]
        context.user_data['model'] = model
        message = f"Model changed to *{MODELS[model]}*"
        await query.edit_message_text(message)

async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Answer user's question using selected AI model."""
    if 'model' not in context.user_data:
        context.user_data['model'] = 'o1-mini'
    
    try:
        question = update.message.text
        current_model = context.user_data['model']
        logger.info(f"Sending question to {current_model}: {question}")
        
        # Only use system message for GPT models
        messages = []
        if current_model.startswith('gpt'):
            messages.append({
                "role": "system", 
                "content": "Format responses with simple markdown: *bold* for emphasis, - for lists, and ` for code."
            })
        messages.append({"role": "user", "content": question})
        
        response = client.chat.completions.create(
            model=current_model,
            messages=messages
        )
        answer = response.choices[0].message.content
        logger.info(f"Received response from {current_model}")
        await send_long_message(update, answer)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        error_message = (
            "*Error:* I encountered an error processing your request.\n\n"
            f"Current model: *{MODELS[context.user_data['model']]}*\n\n"
            "Try changing the model with /model or try again later."
        )
        await update.message.reply_text(error_message)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("model", model_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer_question))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()