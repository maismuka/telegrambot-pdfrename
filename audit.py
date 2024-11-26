import os
import glob
import zipfile
from datetime import datetime, timedelta
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import threading
import time

TOKEN = "7889731518:AAHZCHcFs7gWO1D56C5ptKjx1mvh8UbF1Fg"

# Define a function to handle PDF documents
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Extract message and document information
    message = update.message
    document: Document = message.document
    caption = message.caption

    # Check if the document is a PDF
    if document.mime_type == 'application/pdf' and caption:
        try:
            # Extract current date and time
            now = datetime.now()
            date_str = now.strftime("%d%m%y")
            time_str = now.strftime("%H%M%S")

            # Extract the value from the caption (fetching only the first line after mentioning the bot)
            lines = caption.split("\n")
            first_line = lines[0].strip()
            value = lines[-1].strip().replace('.', '_') if lines[-1] else "unknown"

            # Generate the new file name
            new_file_name = f"W-{date_str}-{time_str}-{value}.pdf"

            # Download the document and save it with the new file name
            file_path = await document.get_file()
            await file_path.download_to_drive(new_file_name)

            # Send the renamed file back to the user
            with open(new_file_name, 'rb') as pdf_file:
                await message.reply_document(pdf_file, caption=f"File saved as: {new_file_name}\nCaption: {first_line}")
        except Exception as e:
            await message.reply_text(f"An error occurred: {str(e)}")

# Define a function to compile all PDFs for the day into a ZIP file and send back to the chat
async def compile_pdfs(bot, chat_id) -> None:
    try:
        # Get today's date
        today = datetime.now().strftime("%d%m%y")

        # Find all PDF files for today
        pdf_files = glob.glob(f"W-{today}-*.pdf")

        if pdf_files:
            # Create a ZIP file with all today's PDFs
            zip_file_name = f"Compiled-{today}.zip"
            with zipfile.ZipFile(zip_file_name, 'w') as zipf:
                for pdf in pdf_files:
                    zipf.write(pdf)

            # Send the ZIP file back to the chat
            with open(zip_file_name, 'rb') as zip_file:
                await bot.send_document(chat_id=chat_id, document=zip_file, caption=f"Compiled ZIP for {today}")

            # Delete all the individual PDF files
            for pdf in pdf_files:
                os.remove(pdf)
        else:
            # No PDFs found for today
            await bot.send_message(chat_id=chat_id, text="No PDFs found for today to compile.")
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"An error occurred while compiling PDFs: {str(e)}")

# Scheduler function to run compile_pdfs at 23:50 every day
def schedule_compile_pdfs(application, chat_id):
    async def scheduled_task():
        while True:
            now = datetime.now()
            target_time = now.replace(hour=23, minute=50, second=0, microsecond=0)
            if now > target_time:
                target_time += timedelta(days=1)
            wait_time = (target_time - now).total_seconds()
            await asyncio.sleep(wait_time)
            await compile_pdfs(application.bot, chat_id)

    threading.Thread(target=lambda: asyncio.run(scheduled_task()), daemon=True).start()

# Create the application and add handlers
def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    # Add a handler to handle messages with PDF documents
    application.add_handler(MessageHandler(filters.Document.PDF, handle_document))

    # Set up a scheduler to compile PDFs every day at 23:50
    chat_id = -1002145390528  # Replace with the chat ID where you want to send the compiled ZIP
    schedule_compile_pdfs(application, chat_id)

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
