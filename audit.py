import os
import glob
import zipfile
from datetime import datetime, timedelta, time
from telegram import Update, Document
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue
import asyncio
import threading
import time as t

TOKEN = "7889731518:AAHZCHcFs7gWO1D56C5ptKjx1mvh8UbF1Fg"
PDF_DIRECTORY = "/volume1/audit_temp"

# Get scheduler time from environment variables (default to 23:00)
SCHEDULE_HOUR = int(os.getenv("SCHEDULE_HOUR", 23))
SCHEDULE_MINUTE = int(os.getenv("SCHEDULE_MINUTE", 00))

# Ensure the directory exists
if not os.path.exists(PDF_DIRECTORY):
    os.makedirs(PDF_DIRECTORY)

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
            now = datetime.utcnow() + timedelta(hours=8)
            date_str = now.strftime("%d%m%y")
            time_str = now.strftime("%H%M%S")

            # Extract the value from the caption (fetching only the first line after mentioning the bot)
            lines = caption.split("\n")
            first_line = lines[0].strip()
            value = lines[-1].strip().replace('.', '_') if lines[-1] else "unknown"

            # Generate the new file name
            new_file_name = f"W-{date_str}-{time_str}-{value}.pdf"
            new_file_path = os.path.join(PDF_DIRECTORY, new_file_name)

            # Download the document and save it with the new file name
            file_path = await document.get_file()
            await file_path.download_to_drive(new_file_path)

            # Send the renamed file back to the user
            with open(new_file_path, 'rb') as pdf_file:
                await message.reply_document(pdf_file)
        except Exception as e:
            await message.reply_text(f"An error occurred: {str(e)}")

# Define a function to compile all PDFs for the day into a ZIP file and send back to the chat
async def compile_pdfs(bot, chat_id) -> None:
    try:
        # Get today's date
        today = datetime.utcnow() + timedelta(hours=8)
        today_str = today.strftime("%d%m%y")

        # Find all PDF files for today in the specified directory
        pdf_files = glob.glob(os.path.join(PDF_DIRECTORY, f"W-{today_str}-*.pdf"))

        if pdf_files:
            print(f"Found PDF files for today: {pdf_files}")  # Debugging log
            # Create a ZIP file with all today's PDFs
            zip_file_name = f"Compiled-{today_str}.zip"
            zip_file_path = os.path.join(PDF_DIRECTORY, zip_file_name)
            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                for pdf in pdf_files:
                    zipf.write(pdf, os.path.basename(pdf))

            # Send the ZIP file back to the chat
            with open(zip_file_path, 'rb') as zip_file:
                await bot.send_document(chat_id=chat_id, document=zip_file, caption=f"Compiled ZIP for {today_str}")

            # Delete all the individual PDF files
            for pdf in pdf_files:
                os.remove(pdf)
        else:
            print("No PDF files found for today to compile.")  # Debugging log
            await bot.send_message(chat_id=chat_id, text="No PDFs found for today to compile.")
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"An error occurred while compiling PDFs: {str(e)}")
        print(f"Error in compile_pdfs: {str(e)}")  # Debugging log

# Scheduler function to run compile_pdfs at the specified time every day
async def compile_pdfs_task(context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = context.job.data['chat_id']
    try:
        print(f"Running compile_pdfs_task at {datetime.utcnow()}")  # Debugging log
        await compile_pdfs(bot, chat_id)
    except Exception as e:
        print(f"Error in compile_pdfs_task: {str(e)}")

def schedule_compile_pdfs(application, chat_id):
    job_queue = application.job_queue
    job_queue.run_daily(
        compile_pdfs_task,
        time=time(hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE),
        days=(0, 1, 2, 3, 4, 5, 6),  # Every day of the week
        name=f'compile_pdfs_{chat_id}',
        data={'chat_id': chat_id}
    )

# Create the application and add handlers
def main() -> None:
    application = ApplicationBuilder().token(TOKEN).post_init(lambda app: app.job_queue.start()).build()

    # Add a handler to handle messages with PDF documents
    application.add_handler(MessageHandler(filters.Document.PDF, handle_document))

    # Add a command handler to manually trigger the compilation (for testing purposes)
    async def manual_compile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await compile_pdfs(context.bot, update.effective_chat.id)

    application.add_handler(CommandHandler("compile", manual_compile_command))

    # Set up a scheduler to compile PDFs every day at the specified time
    chat_id = -1002365935364  # Replace with the chat ID where you want to send the compiled ZIP
    schedule_compile_pdfs(application, chat_id)

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
