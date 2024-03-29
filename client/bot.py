from config.bot_config import GM_REGEX_TO_ACTION
from discord import Client, File, DMChannel, FFmpegPCMAudio
from discord.errors import ClientException
from gtts import gTTS
import asyncio
from utils.logger import Logger
import re

DEV_CHANNEL_ID = 779211097520865301
class MemeBotClient(Client):
    def __init__(self):
        self.voice_lookup = {}    
        super().__init__()

    async def on_ready(self):
        Logger.log(f'Logged on as {self.user}')

    async def on_voice_state_update(self, member, before, after):
        # don't respond to ourselves
        if member.id == self.user.id:
            return
        Logger.log("voice state update")
        self.voice_lookup[member.id] = after.channel
        return

    async def whisper(self, message):
        payload = message.content[9:]
        tts = gTTS(text=payload, lang="en", slow=False)
        tts.save("clips/_tts.mp3")
        channel = self.voice_lookup.get(message.author.id)
        if not channel:
            await message.channel.send(f'Try rejoining the Discord channel and trying again my neighbor')             
            return
        voice = await channel.connect()
        audio = FFmpegPCMAudio("clips/_tts.mp3")
        voice.play(audio)
        log = f'Playing whisper\nPayload: **{payload}**\nFrom: **{message.author.name}**'
        dev_channel = self.get_channel(DEV_CHANNEL_ID)
        Logger.log(log)
        await dev_channel.send(log)
        while(voice.is_playing()):
            await asyncio.sleep(1)
        await voice.disconnect()
        return

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        
        try:
            # route DMs / GroupChannel messages differently
            if isinstance(message.channel, DMChannel):
                if re.search("whisper.*", message.content.lower()):
                    await self.whisper(message)
            else:
                for regex, action in GM_REGEX_TO_ACTION.items():
                    if re.search(regex, message.content.lower()):
                        await action(message)
        except ClientException as ce:
            if str(ce) == "Already connected to a voice channel.":
                await message.channel.send(file=File('pics/slowDownNeighbor.jpg'))
                Logger.log("Voice channel already active, asking user to slow down")
            else:
                await message.channel.send("I\'m kinda confused right now bruh")
                Logger.log(f'Unknown ClientExceptionError: {ce}')
        except Exception as e:
            if str(e) == "The Riot API returned an error on the request. The received error was 403: \"Forbidden\"":
                await message.channel.send("I think the Riot API may have expired!")
                Logger.log(f'Riot API Exception occured: {e}')
            else:
                await message.channel.send("I\'m kinda confused right now bruh")
                Logger.log(f'Unknown Exception occured: {e}')
        