"""
Main Discord bot class for Sefaria integration
"""
import discord
from discord.ext import commands
import logging
# Streamlined commands only
from .sefaria_client import SefariaClient
from .hebcal_client import HebcalClient
from .nli_client import NLIClient
from .chabad_client import ChabadClient
from .dicta_client import DictaClient
from .opentorah_client import OpenTorahClient
from .torahcalc_client import TorahCalcClient
from .orayta_client import OraytaClient
from .opensiddur_client import OpenSiddurClient
from .pninim_client import PninimClient
from .ai_client import AIClient

logger = logging.getLogger(__name__)

class SefariaBot(commands.Bot):
    """Discord bot for Sefaria Jewish texts"""
    
    def __init__(self):
        # Configure intents - need message content for @mentions to work
        intents = discord.Intents.default()
        intents.message_content = True  # Required for reading message content when @mentioned
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description="A Discord bot for accessing Jewish texts from Sefaria"
        )
        
        # Initialize all API clients
        self.sefaria_client = SefariaClient()
        self.hebcal_client = HebcalClient()
        self.nli_client = NLIClient()
        self.chabad_client = ChabadClient()
        self.dicta_client = DictaClient()
        self.opentorah_client = OpenTorahClient()
        self.torahcalc_client = TorahCalcClient()
        self.orayta_client = OraytaClient()
        self.opensiddur_client = OpenSiddurClient()
        self.pninim_client = PninimClient()
        self.ai_client = AIClient()
        
        # Track processed messages to prevent duplicates
        self.processed_messages = set()
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        try:
            # Add comprehensive commands with ALL functionality preserved
            from .comprehensive_commands import ComprehensiveCommands
            await self.add_cog(ComprehensiveCommands(
                self,
                sefaria=self.sefaria_client,
                hebcal=self.hebcal_client,
                nli=self.nli_client,
                chabad=self.chabad_client,
                dicta=self.dicta_client,
                ai=self.ai_client,
                opentorah=self.opentorah_client,
                torahcalc=self.torahcalc_client,
                orayta=self.orayta_client,
                opensiddur=self.opensiddur_client,
                pninim=self.pninim_client
            ))
            logger.info("Loaded comprehensive commands with ALL APIs and functionality")
            
            # Add AI message handling for @mentions
            try:
                from .ai_message_handler import AIMessageHandler
                await self.add_cog(AIMessageHandler(self, self.ai_client))
                logger.info("Loaded AI message handler for conversations")
            except Exception as e:
                logger.info(f"AI message handler not available: {e}")
            
            # Sync slash commands (should be much fewer now)
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} organized command(s)")
            
        except Exception as e:
            logger.error(f"Error in setup_hook: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot activity
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="Jewish wisdom | /sefaria help"
        )
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        logger.error(f"Command error: {error}")
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument. Use `/sefaria help` for usage information.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
        else:
            await ctx.send("❌ An error occurred while processing your command.")
    
    async def on_error(self, event, *args, **kwargs):
        """Global error handler for events"""
        logger.error(f"An error occurred in event {event}", exc_info=True)
    
    async def on_message(self, message):
        """Handle incoming messages for AI responses"""
        # Don't respond to our own messages
        if message.author == self.user:
            return
        
        # Check if the bot was mentioned
        if self.user and self.user.mentioned_in(message):
            # Check for duplicate message processing FIRST
            message_id = message.id
            if message_id in self.processed_messages:
                return  # Already processed this message
            
            # Mark message as processed immediately to prevent duplicates
            self.processed_messages.add(message_id)
            
            # Check if auto-reply is enabled for this guild
            guild_id = message.guild.id if message.guild else 0
            
            # Auto-reply is enabled by default in streamlined version
            
            # Clean up old message IDs (keep only last 1000 to prevent memory issues)
            if len(self.processed_messages) > 1000:
                # Remove oldest 100 entries
                old_messages = list(self.processed_messages)[:100]
                for old_id in old_messages:
                    self.processed_messages.discard(old_id)
            
            # Remove the bot mention from the message content
            content = message.content
            for mention in message.mentions:
                if mention == self.user:
                    content = content.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '').strip()
            
            if content:  # Only respond if there's actual content after removing mentions
                try:
                    # Generate AI response
                    response = await self.ai_client.generate_response(
                        content, 
                        user_name=message.author.display_name
                    )
                    
                    # Send response
                    await message.reply(response)
                    
                except Exception as e:
                    logger.error(f"Error generating AI response: {e}")
                    await message.reply("I'm sorry, I'm having trouble responding right now. Please try again later.")
        
        # Process commands as usual
        await self.process_commands(message)
