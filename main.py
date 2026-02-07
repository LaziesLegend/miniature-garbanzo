import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN, ADMIN_ID, AD_COST, MIN_CAMPAIGN
from database import init_db, add_user, get_user, update_tokens

logging.basicConfig(level=logging.INFO)

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)
    await update.message.reply_text(
        "Welcome! Use /balance to check tokens.\nUse /promote <members> to create campaign."
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if user:
        await update.message.reply_text(f"Your balance: {user[2]} tokens")

async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /promote 5")
        return

    members = int(context.args[0])

    if members < MIN_CAMPAIGN:
        await update.message.reply_text(f"Minimum campaign is {MIN_CAMPAIGN}")
        return

    total_cost = members * AD_COST

    user = get_user(update.effective_user.id)
    if user[2] < total_cost:
        await update.message.reply_text("Not enough tokens.")
        return

    update_tokens(update.effective_user.id, -total_cost)

    await update.message.reply_text(
        f"Campaign created for {members} members.\nTotal cost: {total_cost} tokens."
    )

async def addtokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])
    amount = int(context.args[1])

    update_tokens(user_id, amount)
    await update.message.reply_text("Tokens added.")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("promote", promote))
app.add_handler(CommandHandler("addtokens", addtokens))

app.run_polling()
