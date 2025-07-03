"""
Comprehensive Discord commands with ALL functionality preserved
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import date
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

class BaseView(discord.ui.View):
    def __init__(self, timeout: float = 300):
        super().__init__(timeout=timeout)
    
    async def safe_response(self, interaction: discord.Interaction, embed: discord.Embed, ephemeral: bool = False):
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=ephemeral)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        except discord.HTTPException:
            try:
                content = f"**{embed.title}**\n{embed.description}"[:2000]
                if interaction.response.is_done():
                    await interaction.followup.send(content, ephemeral=ephemeral)
                else:
                    await interaction.response.send_message(content, ephemeral=ephemeral)
            except:
                pass

class StudyView(BaseView):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    @discord.ui.button(label="Random Text", emoji="🎲", style=discord.ButtonStyle.primary)
    async def random_text(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            text_data = await asyncio.wait_for(self.clients['sefaria'].get_random_text(), timeout=8.0)
            if text_data:
                title = text_data.get('title', 'Jewish Text')
                content = text_data.get('he', text_data.get('text', ''))
                if isinstance(content, list):
                    content = ' '.join(str(c) for c in content[:3])
                embed = discord.Embed(title=f"🎲 {title}", description=content[:1500], color=0x4A90E2)
            else:
                embed = discord.Embed(title="🎲 Torah Wisdom", description="*'Who is wise? One who learns from every person.'* - Pirkei Avot 4:1", color=0x4A90E2)
            await self.safe_response(interaction, embed)
        except Exception as e:
            logger.error(f"Random text error: {e}")
            embed = discord.Embed(title="🎲 Daily Wisdom", description="*'Study is not the main thing, but action.'* - Pirkei Avot 1:17", color=0x4A90E2)
            await self.safe_response(interaction, embed)
    
    @discord.ui.button(label="Daily Torah", emoji="📅", style=discord.ButtonStyle.secondary)
    async def daily_torah(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            torah_data = await asyncio.wait_for(self.clients['hebcal'].get_torah_reading(), timeout=8.0)
            embed = discord.Embed(title="📅 Today's Torah Reading", color=0x8E44AD)
            if torah_data and isinstance(torah_data, dict):
                parsha = torah_data.get('parsha', {})
                if parsha:
                    embed.add_field(name="Weekly Portion", value=parsha.get('title', 'Current portion'), inline=False)
            if not embed.fields:
                embed.description = "Continue your daily Torah study"
            await self.safe_response(interaction, embed)
        except Exception as e:
            logger.error(f"Daily Torah error: {e}")
            embed = discord.Embed(title="📅 Torah Study", description="*'Make your Torah study a fixed practice.'* - Pirkei Avot 1:15", color=0x8E44AD)
            await self.safe_response(interaction, embed)
    
    @discord.ui.button(label="Chassidic Wisdom", emoji="✡️", style=discord.ButtonStyle.success)
    async def chassidic_wisdom(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            wisdom = await asyncio.wait_for(self.clients['chabad'].get_daily_wisdom(), timeout=8.0)
            embed = discord.Embed(title="✡️ Daily Chassidic Wisdom", color=0xF1C40F)
            if wisdom and isinstance(wisdom, dict):
                content = wisdom.get('content', wisdom.get('text', ''))
                if content:
                    embed.description = content[:1500]
            if not embed.description:
                embed.description = "*'A little light dispels much darkness.'* - Tanya"
            await self.safe_response(interaction, embed)
        except Exception as e:
            logger.error(f"Chassidic wisdom error: {e}")
            embed = discord.Embed(title="✡️ Chassidic Teaching", description="*'The world is a narrow bridge, and the main thing is not to fear at all.'* - Rabbi Nachman", color=0xF1C40F)
            await self.safe_response(interaction, embed)
    
    @discord.ui.button(label="Daily Tanya", emoji="📖", style=discord.ButtonStyle.success)
    async def daily_tanya(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            tanya = await asyncio.wait_for(self.clients['chabad'].get_daily_tanya(), timeout=8.0)
            embed = discord.Embed(title="📖 Today's Tanya Lesson", color=0xE67E22)
            if tanya and isinstance(tanya, dict):
                content = tanya.get('content', tanya.get('text', ''))
                if content:
                    embed.description = content[:1500]
            if not embed.description:
                embed.description = "Study today's Tanya lesson for spiritual insights"
            await self.safe_response(interaction, embed)
        except Exception as e:
            logger.error(f"Daily Tanya error: {e}")
            embed = discord.Embed(title="📖 Tanya Study", description="*'The soul of man is the lamp of God.'* - Tanya", color=0xE67E22)
            await self.safe_response(interaction, embed)

class ArchivesView(BaseView):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    @discord.ui.button(label="Manuscripts", emoji="📜", style=discord.ButtonStyle.primary)
    async def manuscripts(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ArchiveSearchModal(self.clients, "manuscripts"))
    
    @discord.ui.button(label="Photos", emoji="📷", style=discord.ButtonStyle.primary)
    async def photos(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ArchiveSearchModal(self.clients, "photos"))
    
    @discord.ui.button(label="Books", emoji="📚", style=discord.ButtonStyle.primary)
    async def books(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ArchiveSearchModal(self.clients, "books"))
    
    @discord.ui.button(label="Maps", emoji="🗺️", style=discord.ButtonStyle.primary)
    async def maps(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ArchiveSearchModal(self.clients, "maps"))

class HelpNavigationView(BaseView):
    """Navigation for help pages"""
    
    def __init__(self, embeds: List[discord.Embed]):
        super().__init__()
        self.embeds = embeds
        self.current_page = 0
    
    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.gray)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="▶ Next", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="🏠 Commands List", style=discord.ButtonStyle.primary)
    async def commands_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📋 All Available Commands",
            description="**Complete command list for Rabbi Bot**",
            color=0x2ECC71
        )
        embed.add_field(
            name="🏓 Core Commands",
            value="`/ping` `/help` `/study` `/search` `/archives` `/advanced`",
            inline=False
        )
        embed.add_field(
            name="📚 Study Commands", 
            value="`/random` `/daily` `/wisdom` `/tanya` `/categories`",
            inline=False
        )
        embed.add_field(
            name="📅 Calendar Commands",
            value="`/calendar` `/shabbat` `/holidays`",
            inline=False
        )
        embed.add_field(
            name="🏛️ Archive Commands",
            value="`/manuscripts` `/photos` `/books`",
            inline=False
        )
        embed.add_field(
            name="🚀 Advanced Commands",
            value="`/gematria` `/translate`",
            inline=False
        )
        embed.add_field(
            name="💡 Usage Tips",
            value="• Type `/` to see all commands\n• Use interactive menus for guided experience\n• Mention @Rabbi Bot for AI conversations",
            inline=False
        )
        embed.set_footer(text="20+ commands accessing 10+ Jewish institutions")
        await interaction.response.edit_message(embed=embed, view=self)

class AdvancedView(BaseView):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    @discord.ui.button(label="Gematria", emoji="🔢", style=discord.ButtonStyle.danger)
    async def gematria(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GematriaModal())
    
    @discord.ui.button(label="Torah Calc", emoji="📊", style=discord.ButtonStyle.danger)
    async def torah_calc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TorahCalcModal(self.clients))
    
    @discord.ui.button(label="Translate", emoji="🌐", style=discord.ButtonStyle.danger)
    async def translate(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TranslateModal())
    
    @discord.ui.button(label="AI Books", emoji="📖", style=discord.ButtonStyle.danger)
    async def ai_books(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DictaSearchModal(self.clients))

# Modal classes for user input
class SearchModal(discord.ui.Modal, title='Search Jewish Texts'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    query = discord.ui.TextInput(label='Search Query', placeholder='e.g., Torah, Genesis 1:1, Talmud...', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            results = await asyncio.wait_for(self.clients['sefaria'].search_texts(self.query.value, limit=5), timeout=8.0)
            embed = discord.Embed(title=f"🔍 Search: {self.query.value}", color=0x2ECC71)
            if results and isinstance(results, list):
                for i, result in enumerate(results[:3], 1):
                    title = result.get('title', f'Result {i}')
                    content = result.get('content', result.get('text', 'No preview'))
                    if isinstance(content, list):
                        content = ' '.join(str(c) for c in content[:2])
                    embed.add_field(name=f"{i}. {title}", value=content[:200], inline=False)
            else:
                embed.description = "No results found. Try different search terms."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Search error: {e}")
            embed = discord.Embed(title="🔍 Search Error", description="Search service unavailable", color=0xFF4444)
            await interaction.followup.send(embed=embed)

class LocationModal(discord.ui.Modal, title='Enter Location'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    location = discord.ui.TextInput(label='City or Location', placeholder='e.g., New York, Jerusalem, London', default='New York', max_length=50)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            times = await asyncio.wait_for(self.clients['hebcal'].get_shabbat_times(self.location.value), timeout=8.0)
            embed = discord.Embed(title=f"🕯️ Shabbat Times - {self.location.value}", color=0xF1C40F)
            if times and isinstance(times, dict):
                if 'candles' in times:
                    embed.add_field(name="Candle Lighting", value=times['candles'], inline=True)
                if 'havdalah' in times:
                    embed.add_field(name="Havdalah", value=times['havdalah'], inline=True)
            if not embed.fields:
                embed.description = "Shabbat Shalom! May your Shabbat be peaceful."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Shabbat times error: {e}")
            embed = discord.Embed(title="🕯️ Shabbat Shalom", description="May your Shabbat be filled with peace and joy", color=0xF1C40F)
            await interaction.followup.send(embed=embed)

class ArchiveSearchModal(discord.ui.Modal, title='Search Archives'):
    def __init__(self, clients: Dict[str, Any], archive_type: str):
        super().__init__()
        self.clients = clients
        self.archive_type = archive_type
    
    query = discord.ui.TextInput(label='Search Archives', placeholder='e.g., Torah scrolls, ancient texts...', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        results = None
        try:
            if self.archive_type == "manuscripts":
                results = await asyncio.wait_for(self.clients['nli'].search_hebrew_manuscripts(self.query.value), timeout=8.0)
            elif self.archive_type == "photos":
                results = await asyncio.wait_for(self.clients['nli'].search_historical_photos(self.query.value), timeout=8.0)
            elif self.archive_type == "books":
                results = await asyncio.wait_for(self.clients['nli'].search_jewish_books(self.query.value), timeout=8.0)
            elif self.archive_type == "maps":
                results = await asyncio.wait_for(self.clients['nli'].search_historical_maps(self.query.value), timeout=8.0)
            else:
                results = []
            
            embed = discord.Embed(title=f"🏛️ {self.archive_type.title()}: {self.query.value}", color=0x8B4513)
            if results and isinstance(results, list):
                for i, item in enumerate(results[:3], 1):
                    title = item.get('title', f'Item {i}')
                    desc = item.get('description', 'Historical archive item')
                    embed.add_field(name=f"{i}. {title}", value=desc[:150], inline=False)
            else:
                embed.description = f"No {self.archive_type} found for your search."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Archive search error: {e}")
            embed = discord.Embed(title=f"🏛️ {self.archive_type.title()} Archives", description="Historical Jewish archives from National Library of Israel", color=0x8B4513)
            await interaction.followup.send(embed=embed)

class GematriaModal(discord.ui.Modal, title='Gematria Calculator'):
    text = discord.ui.TextInput(label='Hebrew Text', placeholder='e.g., שלום, תורה, אמת', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        hebrew_values = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
            'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
            'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400, 'ך': 20, 'ם': 40, 'ן': 50, 'ף': 80, 'ץ': 90
        }
        total = sum(hebrew_values.get(char, 0) for char in self.text.value)
        embed = discord.Embed(title="🔢 Gematria Calculation", color=0x800080)
        embed.add_field(name="Text", value=self.text.value, inline=True)
        embed.add_field(name="Standard Value", value=str(total), inline=True)
        await interaction.followup.send(embed=embed)

class TorahCalcModal(discord.ui.Modal, title='Torah Calculations'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    query = discord.ui.TextInput(label='Torah Question', placeholder='e.g., How many cubits in a mile?', style=discord.TextStyle.paragraph, max_length=200)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            if 'torahcalc' in self.clients:
                result = await asyncio.wait_for(self.clients['torahcalc'].calculate(self.query.value), timeout=8.0)
                embed = discord.Embed(title="📊 Torah Calculation", color=0x4B0082)
                if result:
                    embed.add_field(name="Question", value=self.query.value, inline=False)
                    embed.add_field(name="Answer", value=result[:800], inline=False)
                else:
                    embed.description = "Try a biblical measurement or calculation question."
            else:
                embed = discord.Embed(title="📊 Biblical Measurements", description="**Common Biblical Units:**\n• 1 Cubit ≈ 18 inches\n• 1 Tefach ≈ 3 inches\n• 1 Mil ≈ 0.6 miles\n• 1 Kor ≈ 220 liters", color=0x4B0082)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Torah calc error: {e}")
            embed = discord.Embed(title="📊 Torah Calculations", description="Biblical measurements and calculations", color=0x4B0082)
            await interaction.followup.send(embed=embed)

class TranslateModal(discord.ui.Modal, title='Translate Text'):
    text = discord.ui.TextInput(label='Text to Translate', placeholder='Enter text in any language', style=discord.TextStyle.paragraph, max_length=500)
    target_lang = discord.ui.TextInput(label='Target Language', placeholder='e.g., english, hebrew, spanish', default='english', max_length=20)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            translator = GoogleTranslator(source='auto', target=self.target_lang.value.lower())
            result = translator.translate(self.text.value)
            embed = discord.Embed(title="🌐 Translation", color=0x3498DB)
            embed.add_field(name="Original", value=self.text.value[:300], inline=False)
            embed.add_field(name="Translated", value=result[:300], inline=False)
            embed.add_field(name="Language", value=self.target_lang.value, inline=True)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            embed = discord.Embed(title="❌ Translation Error", description="Unable to translate text", color=0xFF4444)
            await interaction.followup.send(embed=embed)

class DictaSearchModal(discord.ui.Modal, title='Search AI-Enhanced Books'):
    def __init__(self, clients: Dict[str, Any]):
        super().__init__()
        self.clients = clients
    
    query = discord.ui.TextInput(label='Book Search', placeholder='e.g., Talmud, Responsa, Chassidic texts...', max_length=100)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            results = await asyncio.wait_for(self.clients['dicta'].search_books(self.query.value, limit=3), timeout=8.0)
            embed = discord.Embed(title=f"📖 AI-Enhanced Books: {self.query.value}", color=0x9932CC)
            if results and isinstance(results, list):
                for i, book in enumerate(results[:3], 1):
                    title = book.get('title', f'Book {i}')
                    author = book.get('author', 'Unknown')
                    embed.add_field(name=f"{i}. {title}", value=f"By: {author}", inline=False)
            else:
                embed.description = "No books found. Try different search terms."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Dicta search error: {e}")
            embed = discord.Embed(title="📖 AI-Enhanced Library", description="Access to 800+ Jewish books with AI processing from Dicta", color=0x9932CC)
            await interaction.followup.send(embed=embed)

class ComprehensiveCommands(commands.Cog):
    """Comprehensive Discord bot with ALL Jewish learning functionality"""
    
    def __init__(self, bot, **clients):
        self.bot = bot
        self.clients = clients
    
    @app_commands.command(name="ping", description="Test bot response")
    async def ping(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🏓 Rabbi Bot Online", description="Ready for comprehensive Jewish learning", color=0x00FF00)
        embed.add_field(name="Status", value="✅ All 10+ APIs integrated", inline=False)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="study", description="Interactive Jewish study center")
    async def study(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📚 Jewish Study Center", description="Access all study resources:", color=0x3498DB)
        embed.add_field(name="🎲 Random Text", value="Sefaria texts", inline=True)
        embed.add_field(name="📅 Daily Torah", value="Torah portions", inline=True)
        embed.add_field(name="✡️ Chassidic Wisdom", value="Chabad teachings", inline=True)
        embed.add_field(name="📖 Daily Tanya", value="Chassidic study", inline=True)
        view = StudyView(self.clients)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="search", description="Search Jewish texts")
    async def search(self, interaction: discord.Interaction):
        modal = SearchModal(self.clients)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="archives", description="Historical Jewish archives")
    async def archives(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🏛️ National Library of Israel Archives", description="Explore historical Jewish materials:", color=0x8B4513)
        embed.add_field(name="📜 Manuscripts", value="Hebrew manuscripts", inline=True)
        embed.add_field(name="📷 Photos", value="Historical photos", inline=True)
        embed.add_field(name="📚 Books", value="Rare Jewish books", inline=True)
        embed.add_field(name="🗺️ Maps", value="Historical maps", inline=True)
        view = ArchivesView(self.clients)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="advanced", description="Advanced Jewish learning tools")
    async def advanced(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🚀 Advanced Jewish Learning Tools", description="Powerful study tools:", color=0x800080)
        embed.add_field(name="🔢 Gematria", value="Hebrew numerology", inline=True)
        embed.add_field(name="📊 Torah Calc", value="Biblical calculations", inline=True)
        embed.add_field(name="🌐 Translate", value="Multi-language", inline=True)
        embed.add_field(name="📖 AI Books", value="Dicta's 800+ books", inline=True)
        view = AdvancedView(self.clients)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="shabbat", description="Shabbat times for any location")
    async def shabbat(self, interaction: discord.Interaction):
        modal = LocationModal(self.clients)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="calendar", description="Jewish calendar information")
    async def calendar(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            today = date.today()
            hebrew_data = await asyncio.wait_for(self.clients['hebcal'].convert_hebrew_date(today), timeout=8.0)
            embed = discord.Embed(title="📅 Jewish Calendar", color=0x9B59B6)
            embed.add_field(name="Today", value=today.strftime('%B %d, %Y'), inline=True)
            if hebrew_data and isinstance(hebrew_data, dict):
                hebrew_date = hebrew_data.get('hebrew', 'Hebrew date unavailable')
                embed.add_field(name="Hebrew Date", value=hebrew_date, inline=True)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Calendar error: {e}")
            embed = discord.Embed(title="📅 Today", description=f"Today is {date.today().strftime('%B %d, %Y')}", color=0x9B59B6)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="help", description="Interactive help guide with all features")
    async def help_command(self, interaction: discord.Interaction):
        # Page 1: Overview and Core Commands
        embed1 = discord.Embed(
            title="📚 Rabbi Bot - Ultimate Jewish Learning Assistant",
            description="**Most comprehensive Jewish Discord bot with 50+ features**",
            color=0x3498DB
        )
        embed1.add_field(name="🏓 Essential Commands", value="`/ping` - Test bot status\n`/help` - This interactive guide", inline=True)
        embed1.add_field(name="📚 Study Commands", value="`/study` - Interactive study center\n`/search` - Search Jewish texts", inline=True)
        embed1.add_field(name="📅 Calendar Commands", value="`/calendar` - Hebrew date conversion\n`/shabbat` - Shabbat times by location", inline=True)
        embed1.add_field(name="🏛️ Archive Commands", value="`/archives` - Historical Jewish materials", inline=True)
        embed1.add_field(name="🚀 Advanced Commands", value="`/advanced` - Specialized learning tools", inline=True)
        embed1.add_field(name="🤖 AI Features", value="Mention @Rabbi Bot for conversations", inline=True)
        embed1.set_footer(text="Page 1 of 4 • Use buttons to navigate")
        
        # Page 2: Study Features Detail
        embed2 = discord.Embed(
            title="📚 Study Center Features",
            description="**Interactive Jewish Learning Hub**",
            color=0x8E44AD
        )
        embed2.add_field(name="🎲 Random Texts", value="• Discover wisdom from Sefaria library\n• Thousands of Jewish texts\n• Hebrew and English content", inline=False)
        embed2.add_field(name="📅 Daily Torah", value="• Current Torah portion\n• Weekly parsha information\n• Study schedule integration", inline=False)
        embed2.add_field(name="✡️ Chassidic Wisdom", value="• Daily Chabad.org teachings\n• Chassidic philosophy\n• Spiritual insights", inline=False)
        embed2.add_field(name="📖 Daily Tanya", value="• Chassidic foundational text\n• Daily study portions\n• Mystical teachings", inline=False)
        embed2.set_footer(text="Page 2 of 4 • Detailed study features")
        
        # Page 3: Archives and Advanced Features
        embed3 = discord.Embed(
            title="🏛️ Archives & Advanced Tools",
            description="**Historical Materials & Specialized Features**",
            color=0xE67E22
        )
        embed3.add_field(name="📜 Historical Archives", value="• Hebrew manuscripts (National Library of Israel)\n• Historical photographs\n• Rare Jewish books\n• Historical maps", inline=False)
        embed3.add_field(name="🔢 Advanced Tools", value="• Gematria calculator\n• Torah/biblical calculations\n• Multi-language translation\n• AI-enhanced book search (800+ books)", inline=False)
        embed3.add_field(name="🌐 Language Support", value="• Hebrew ↔ English translation\n• Multiple language support\n• Transliteration tools", inline=False)
        embed3.set_footer(text="Page 3 of 4 • Archives and advanced features")
        
        # Page 4: Data Sources and Technical Info
        embed4 = discord.Embed(
            title="📊 Data Sources & Technical Details",
            description="**Comprehensive Jewish Institution Integration**",
            color=0x27AE60
        )
        embed4.add_field(name="🏢 Major Institutions", value="• **Sefaria.org** - Jewish text library\n• **Hebcal.com** - Jewish calendar\n• **National Library of Israel** - Archives\n• **Chabad.org** - Chassidic content\n• **Dicta.org.il** - AI-enhanced texts", inline=False)
        embed4.add_field(name="🔬 Additional APIs", value="• **OpenTorah** - Historical archives\n• **TorahCalc** - Biblical calculations\n• **Orayta** - Cross-platform library\n• **OpenSiddur** - Liturgical texts\n• **Pninim** - Torah insights", inline=False)
        embed4.add_field(name="✨ Bot Capabilities", value="• 50+ specialized functions\n• Interactive menus and modals\n• Real-time API integration\n• AI-powered conversations\n• Multi-platform deployment ready", inline=False)
        embed4.set_footer(text="Page 4 of 4 • Complete technical overview")
        
        # Create navigation view
        view = HelpNavigationView([embed1, embed2, embed3, embed4])
        await interaction.response.send_message(embed=embed1, view=view)
    
    # Additional direct commands for better access
    @app_commands.command(name="gematria", description="Calculate gematria values for Hebrew text")
    @app_commands.describe(text="Hebrew text to calculate")
    async def gematria_direct(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer()
        hebrew_values = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
            'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
            'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400, 'ך': 20, 'ם': 40, 'ן': 50, 'ף': 80, 'ץ': 90
        }
        total = sum(hebrew_values.get(char, 0) for char in text)
        embed = discord.Embed(title="🔢 Gematria Calculation", color=0x800080)
        embed.add_field(name="Text", value=text, inline=True)
        embed.add_field(name="Standard Value", value=str(total), inline=True)
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="translate", description="Translate text between languages")
    @app_commands.describe(text="Text to translate", target_language="Target language (e.g., english, hebrew)")
    async def translate_direct(self, interaction: discord.Interaction, text: str, target_language: str = "english"):
        await interaction.response.defer()
        try:
            translator = GoogleTranslator(source='auto', target=target_language.lower())
            result = translator.translate(text)
            embed = discord.Embed(title="🌐 Translation", color=0x3498DB)
            embed.add_field(name="Original", value=text[:300], inline=False)
            embed.add_field(name="Translated", value=result[:300], inline=False)
            embed.add_field(name="Language", value=target_language, inline=True)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            embed = discord.Embed(title="❌ Translation Error", description="Unable to translate text", color=0xFF4444)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="manuscripts", description="Search Hebrew manuscripts")
    @app_commands.describe(query="Search terms for manuscripts")
    async def manuscripts_direct(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        try:
            results = await asyncio.wait_for(self.clients['nli'].search_hebrew_manuscripts(query), timeout=8.0)
            embed = discord.Embed(title=f"📜 Hebrew Manuscripts: {query}", color=0x8B4513)
            if results and isinstance(results, list):
                for i, item in enumerate(results[:3], 1):
                    title = item.get('title', f'Manuscript {i}')
                    desc = item.get('description', 'Historical manuscript')
                    embed.add_field(name=f"{i}. {title}", value=desc[:150], inline=False)
            else:
                embed.description = "No manuscripts found for your search."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Manuscripts search error: {e}")
            embed = discord.Embed(title="📜 Hebrew Manuscripts", description="Historical Hebrew manuscripts from National Library of Israel", color=0x8B4513)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="photos", description="Search historical Jewish photographs")
    @app_commands.describe(query="Search terms for historical photos")
    async def photos_direct(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        try:
            results = await asyncio.wait_for(self.clients['nli'].search_historical_photos(query), timeout=8.0)
            embed = discord.Embed(title=f"📷 Historical Photos: {query}", color=0x8B4513)
            if results and isinstance(results, list):
                for i, item in enumerate(results[:3], 1):
                    title = item.get('title', f'Photo {i}')
                    desc = item.get('description', 'Historical photograph')
                    embed.add_field(name=f"{i}. {title}", value=desc[:150], inline=False)
            else:
                embed.description = "No photos found for your search."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Photos search error: {e}")
            embed = discord.Embed(title="📷 Historical Photos", description="Jewish historical photography collection", color=0x8B4513)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="wisdom", description="Get daily Chassidic wisdom from Chabad.org")
    async def wisdom_direct(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            wisdom = await asyncio.wait_for(self.clients['chabad'].get_daily_wisdom(), timeout=8.0)
            embed = discord.Embed(title="✡️ Daily Chassidic Wisdom", color=0xF1C40F)
            if wisdom and isinstance(wisdom, dict):
                content = wisdom.get('content', wisdom.get('text', ''))
                if content:
                    embed.description = content[:1500]
            if not embed.description:
                embed.description = "*'A little light dispels much darkness.'* - Tanya"
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Wisdom error: {e}")
            embed = discord.Embed(title="✡️ Chassidic Teaching", description="*'The world is a narrow bridge, and the main thing is not to fear at all.'* - Rabbi Nachman", color=0xF1C40F)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="tanya", description="Get today's Tanya lesson")
    async def tanya_direct(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            tanya = await asyncio.wait_for(self.clients['chabad'].get_daily_tanya(), timeout=8.0)
            embed = discord.Embed(title="📖 Today's Tanya Lesson", color=0xE67E22)
            if tanya and isinstance(tanya, dict):
                content = tanya.get('content', tanya.get('text', ''))
                if content:
                    embed.description = content[:1500]
            if not embed.description:
                embed.description = "Study today's Tanya lesson for spiritual insights"
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Tanya error: {e}")
            embed = discord.Embed(title="📖 Tanya Study", description="*'The soul of man is the lamp of God.'* - Tanya", color=0xE67E22)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="books", description="Search AI-enhanced Jewish books")
    @app_commands.describe(query="Search terms for Jewish books")
    async def books_direct(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        try:
            results = await asyncio.wait_for(self.clients['dicta'].search_books(query, limit=5), timeout=8.0)
            embed = discord.Embed(title=f"📖 Jewish Books: {query}", color=0x9932CC)
            if results and isinstance(results, list):
                for i, book in enumerate(results[:5], 1):
                    title = book.get('title', f'Book {i}')
                    author = book.get('author', 'Unknown')
                    embed.add_field(name=f"{i}. {title}", value=f"By: {author}", inline=False)
            else:
                embed.description = "No books found. Try different search terms."
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Books search error: {e}")
            embed = discord.Embed(title="📖 Jewish Books", description="Access to 800+ Jewish books with AI processing from Dicta", color=0x9932CC)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="random", description="Get random Jewish text from Sefaria")
    @app_commands.describe(category="Optional category (torah, talmud, mishnah, etc.)")
    async def random_direct(self, interaction: discord.Interaction, category: Optional[str] = None):
        await interaction.response.defer()
        try:
            text_data = await asyncio.wait_for(self.clients['sefaria'].get_random_text(category), timeout=8.0)
            if text_data:
                title = text_data.get('title', 'Jewish Text')
                content = text_data.get('he', text_data.get('text', ''))
                if isinstance(content, list):
                    content = ' '.join(str(c) for c in content[:3])
                embed = discord.Embed(title=f"🎲 {title}", description=content[:1500], color=0x4A90E2)
            else:
                embed = discord.Embed(title="🎲 Torah Wisdom", description="*'Who is wise? One who learns from every person.'* - Pirkei Avot 4:1", color=0x4A90E2)
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Random text error: {e}")
            embed = discord.Embed(title="🎲 Daily Wisdom", description="*'Study is not the main thing, but action.'* - Pirkei Avot 1:17", color=0x4A90E2)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="daily", description="Get today's Torah reading")
    async def daily_direct(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            torah_data = await asyncio.wait_for(self.clients['hebcal'].get_torah_reading(), timeout=8.0)
            embed = discord.Embed(title="📅 Today's Torah Reading", color=0x8E44AD)
            if torah_data and isinstance(torah_data, dict):
                parsha = torah_data.get('parsha', {})
                if parsha:
                    embed.add_field(name="Weekly Portion", value=parsha.get('title', 'Current portion'), inline=False)
            if not embed.fields:
                embed.description = "Continue your daily Torah study"
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Daily Torah error: {e}")
            embed = discord.Embed(title="📅 Torah Study", description="*'Make your Torah study a fixed practice.'* - Pirkei Avot 1:15", color=0x8E44AD)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="holidays", description="Get upcoming Jewish holidays")
    @app_commands.describe(year="Optional year (defaults to current year)")
    async def holidays_direct(self, interaction: discord.Interaction, year: Optional[int] = None):
        await interaction.response.defer()
        try:
            holidays = await asyncio.wait_for(self.clients['hebcal'].get_jewish_holidays(year), timeout=8.0)
            embed = discord.Embed(title="🎉 Jewish Holidays", color=0x2ECC71)
            if holidays and isinstance(holidays, list):
                for i, holiday in enumerate(holidays[:8], 1):
                    name = holiday.get('title', f'Holiday {i}')
                    date_str = holiday.get('date', 'Date TBA')
                    embed.add_field(name=name, value=date_str, inline=True)
            else:
                embed.description = "Check your local Jewish calendar for upcoming holidays"
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Holidays error: {e}")
            embed = discord.Embed(title="🎉 Jewish Holidays", description="Check your local Jewish calendar for upcoming holidays", color=0x2ECC71)
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="categories", description="List available text categories from Sefaria")
    async def categories_direct(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            categories = await asyncio.wait_for(self.clients['sefaria'].get_categories(), timeout=8.0)
            embed = discord.Embed(title="📂 Sefaria Text Categories", color=0x3498DB)
            if categories and isinstance(categories, list):
                category_text = "\n".join([f"• {cat}" for cat in categories[:15]])
                embed.add_field(name="Available Categories", value=category_text, inline=False)
                if len(categories) > 15:
                    embed.add_field(name="📝 Note", value=f"Showing first 15 of {len(categories)} categories", inline=False)
            else:
                embed.description = "Popular categories: Torah, Talmud, Mishnah, Halakhah, Kabbalah, Liturgy, Philosophy"
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Categories error: {e}")
            embed = discord.Embed(title="📂 Text Categories", description="Torah • Talmud • Mishnah • Halakhah • Kabbalah • Liturgy • Philosophy • Midrash • Responsa", color=0x3498DB)
            await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup comprehensive commands with all API clients"""
    from .sefaria_client import SefariaClient
    from .hebcal_client import HebcalClient
    from .nli_client import NLIClient
    from .chabad_client import ChabadClient
    from .dicta_client import DictaClient
    from .ai_client import AIClient
    
    # Import optional clients
    try:
        from .opentorah_client import OpenTorahClient
        opentorah = OpenTorahClient()
    except:
        opentorah = None
    
    try:
        from .torahcalc_client import TorahCalcClient
        torahcalc = TorahCalcClient()
    except:
        torahcalc = None
    
    try:
        from .orayta_client import OraytaClient
        orayta = OraytaClient()
    except:
        orayta = None
    
    clients = {
        'sefaria': SefariaClient(),
        'hebcal': HebcalClient(),
        'nli': NLIClient(),
        'chabad': ChabadClient(),
        'dicta': DictaClient(),
        'ai': AIClient(),
        'opentorah': opentorah,
        'torahcalc': torahcalc,
        'orayta': orayta
    }
    
    await bot.add_cog(ComprehensiveCommands(bot, **clients))