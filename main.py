import os
import telebot
from pytube import YouTube
from sendpulse import SendpulseAPI  # Import the module we created

# Telegram bot token
TELEGRAM_TOKEN = '6785472621:AAGZwkKYmBmHx1c3g60KxFVQs7JDegIloU0'

# SendPulse API credentials
API_USER_ID = '6d9c68847d0b41374b6b1b6495803f58'
API_SECRET = 'bfbd1d7a6264229ff90789c44eb1d561'
TOKEN_STORAGE = os.path.join(os.path.dirname(__file__), 'tokens.json')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
sp_api = SendpulseAPI(API_USER_ID, API_SECRET, TOKEN_STORAGE)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the YouTube Downloader Bot! Send me a YouTube link to get started.")

@bot.message_handler(func=lambda message: True)
def provide_quality_options(message):
    try:
        url = message.text
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True, file_extension='mp4')
        
        quality_options = []
        for stream in streams:
            quality = f"{stream.resolution} - {stream.mime_type.split('/')[1]}"
            quality_options.append((stream.itag, quality))
        
        options_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(quality_options)])
        bot.reply_to(message, f"Choose a quality option by sending the number:\n{options_text}")

        bot.register_next_step_handler(message, lambda m: send_download_link(m, yt, quality_options))
    except Exception as e:
        bot.reply_to(message, "An error occurred: " + str(e))

def send_download_link(message, yt, quality_options):
    try:
        choice = int(message.text) - 1
        if 0 <= choice < len(quality_options):
            itag = quality_options[choice][0]
            stream = yt.streams.get_by_itag(itag)
            download_url = stream.url

            bot.reply_to(message, f"Click the link below to download the video:\n{download_url}")
        else:
            bot.reply_to(message, "Invalid choice. Please try again.")
    except ValueError:
        bot.reply_to(message, "Please send a valid number.")
    except Exception as e:
        bot.reply_to(message, "An error occurred: " + str(e))

def notify_admin(subject, message):
    sp_api.smtp_send_mail({
        "html": message,
        "text": message,
        "subject": subject,
        "from": {"name": "YouTube Downloader Bot", "email": "your_email"},
        "to": [{"name": "Admin", "email": "admin_email"}]
    })

@bot.message_handler(commands=['notify'])
def send_notification(message):
    try:
        subject = "Bot Notification"
        msg = "Bot is running and handling requests"
        notify_admin(subject, msg)
        bot.reply_to(message, "Notification sent to admin.")
    except Exception as e:
        bot.reply_to(message, "Failed to send notification: " + str(e))

if __name__ == '__main__':
    bot.polling()
