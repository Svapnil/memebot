from config.meme_config import REGEX_TO_MEME
from discord import VoiceChannel, Message, Member
import discord
from utils.logger import Logger
import re
import asyncio

class MemeClient:
    @staticmethod
    async def play_meme(message: Message) -> None:
        content = message.content
        for regex, meme in REGEX_TO_MEME.items():
            if re.search(regex, content.lower()):
                channel = None
                if isinstance(message.author, Member): 
                    if message.author.voice and message.author.voice.channel:
                        channel = message.author.voice.channel
                    else:
                        name = message.author.nick or message.author.name
                        await message.channel.send(f'You\'re not in a Discord channel neighbor {name}!')             
                        return
                voice = await channel.connect()
                audio = meme.audio
                voice.play(audio)
                Logger.log(f'Playing {regex}')
                while(voice.is_playing()):
                    await asyncio.sleep(1)
                await voice.disconnect()
                break

    @staticmethod
    async def display_meme_help(message: Message) -> None:
        memehelp = "*Messages that will play audio clips:*\n\n"
        for regex,meme in REGEX_TO_MEME.items():
            title = meme.title
            desc = regex[2:-2].replace('|',' or ')
            pattern = re.compile(r'[^a-zA-Z\d\s\)\()]')
            regex = re.sub(pattern,'',desc)
            if title:
                memehelp += f'**{title}:** {desc}\n'
            else:
                memehelp += f'{desc}\n'
            
        await message.channel.send(memehelp)
        Logger.log("Outputting Meme Help")

    @staticmethod
    async def display_whisper_help(message) -> None:
        whisper_help = "*DM the Memebot:*\n```whisper {message}```"
        await message.channel.send(whisper_help)
        Logger.log("Outputting Whisper Help")
