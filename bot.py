import asyncio
import discord
import os
from src import responses
from src import log
import random
from collections import deque

logger = log.setup_logger(__name__)

config = responses.get_config()

class ThinkingBot(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.all())
        self.tree = discord.app_commands.CommandTree(self)
        self.activity = discord.Activity(type=discord.ActivityType.watching, name="my thoughts")
        self.thought_history = deque(maxlen=100)  # stores the bot's previous thoughts
        self.current_thought = ""  # stores the bot's current thought, initially empty

    async def on_message(self, message):
        if message.author == self.user:  # Ignore messages sent by the bot
            return

        if str(message.channel.id) == config['discord_channel_id']:  # Only listen to messages in the designated channel
            if message.content == "!killswitch":  # Check if the killswitch command is called
                self.current_thought = ""  # Clear the current thought
                self.thought_history.clear()  # Clear the thought history
                await message.channel.send("Memory cleared.")  # Send a confirmation message to the channel
            else:
                self.current_thought = (self.current_thought + " " + message.content).strip()  # Remove leading and trailing whitespace
                self.thought_history.append(message.content)  # Add the message content to the bot's thought history

    async def send_thought(self):
        bot_id = config['bot_id']
        initial_thought = config['initial_thought']

        # convert the deque object to a list before it's passed to the handle_thinking function
        thought_history_list = list(self.thought_history)
        thought_message = await responses.handle_thinking(bot_id, initial_thought, thought_history_list)

        if thought_message and str(config['discord_channel_id']) == config['discord_channel_id']:  # Only send messages to the designated channel
            channel = self.get_channel(int(config['discord_channel_id']))

            # Remove the initial thought from the message before sending it
            thought_to_send = thought_message.replace(initial_thought, "", 1).strip()

            # Check if the thought message exceeds the maximum token length
            if len(thought_to_send) > 2000:
                thought_to_send = thought_to_send[:2000]  # Truncate the thought message to the maximum allowed length

            try:
                await channel.send(thought_to_send)
                logger.info(f"Thought and response: {thought_message}")

            except discord.errors.HTTPException:
                logger.warning("HTTPException encountered. Retrying in 2 seconds.")
                await asyncio.sleep(2)
                await self.send_thought()

            self.current_thought = thought_message  # The bot's new current thought is its most recent thought message

    async def prepare_bot(self):
        await self.send_thought()
        logger.info(f'{self.user} is ready.')

def run_discord_bot():
    client = ThinkingBot()

    @client.event
    async def on_ready():
        await client.prepare_bot()
        while True:  # This loop will keep the bot running
            await asyncio.sleep(5)  # Wait for 5 seconds before generating a new thought
            await client.send_thought()

    TOKEN = config['discord_bot_token']
    client.run(TOKEN)

if __name__ == "__main__":
    run_discord_bot()