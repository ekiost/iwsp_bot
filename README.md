# IWSP Bot
This is a bot for telegram that can be used to get the latest IWSP listing from the Ready Talent. It is written in Python and uses the `python-telegram-bot` library.

## Installation
1. Clone the repository
2. Install the required packages using `pip install -r requirements.txt`
3. Create a `.env` file in the root directory and add the following
   ```shell
   export USER_NAME=<YOUR_READY_TALENT_USERNAME>
   export PASSWORD=<YOUR_READY_TALENT_PASSWORD>
   export API_TOKEN=<YOUR_TELEGRAM_BOT_API_TOKEN>
   ```
4. Source the `.env` file using `source .env` or use tools like `autoenv` to automatically source the file when you enter the directory
5. Replace the chat_id in `main.py` with your chat_id
   ```python
   # Replace chat_id with your own chat_id
   await context.bot.send_message(chat_id=<YOUR_CHAT_ID>, text=reply)
   ```
6. Run the bot using `python main.py`