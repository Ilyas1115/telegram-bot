import logging
import os
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# ✅ Enable Logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Your API Token & Channel Username
TOKEN = "7804153317:AAGyhmcnsYWJMC36AIuoWvlOwmR2fl1KTxs"  # Replace with your actual token
CHANNEL_USERNAME = "@hackspherexy"  # Replace with your actual channel username

# ✅ Store user data temporarily
users = {}

# ✅ Function to Check If a User Has Joined the Channel
def is_user_in_channel(user_id):
    url = f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}"
    response = requests.get(url).json()
    status = response.get("result", {}).get("status", "")
    return status in ["member", "administrator", "creator"]

# ✅ Start Command
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id

    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0}

    # ✅ Check if the user has joined the channel
    if not is_user_in_channel(user_id):
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/hackspherexy")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("⚠️ You must join our channel to use this bot!", reply_markup=reply_markup)
        return

    # ✅ Main Menu
    keyboard = [
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance")],
        [InlineKeyboardButton("🔗 Get Referral Link", callback_data="referral")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("🎁 Claim Daily Bonus", callback_data="daily_bonus")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome! Earn ₹5 per referral. Choose an option:", reply_markup=reply_markup
    )

# ✅ Handle Button Clicks
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.message.chat_id
    await query.answer()

    if query.data == "balance":
        balance = users[user_id]["balance"]
        await query.message.reply_text(f"💰 Your balance: ₹{balance}")

    elif query.data == "referral":
        await query.message.reply_text(f"🔗 Share this link: \n\n👉 https://t.me/YOUR_BOT_USERNAME?start={user_id}")

    elif query.data == "withdraw":
        if users[user_id]["balance"] >= 50:
            await query.message.reply_text("✅ Withdrawal request sent! Processing...")
            users[user_id]["balance"] = 0  
        else:
            await query.message.reply_text("❌ Minimum withdrawal amount is ₹50.")

    elif query.data == "daily_bonus":
        users[user_id]["balance"] += 2  
        await query.message.reply_text("🎁 Daily bonus claimed! ₹2 added to your balance.")

    elif query.data == "back":
        await start(update, context)

# ✅ Handle New Users with Referral System
async def new_user(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat_id
    args = context.args  

    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0}

        if args:
            referrer_id = int(args[0])
            if referrer_id in users:
                users[referrer_id]["balance"] += 5  
                users[referrer_id]["referrals"] += 1
                await context.bot.send_message(referrer_id, "🎉 You earned ₹5 from a referral!")

    await start(update, context)  

# ✅ Main Function to Run the Bot
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", new_user))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == "__main__":
    main()
