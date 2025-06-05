import os
import praw
import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from typing import List, Dict, Optional


load_dotenv()

class MemeBot:
    def __init__(self):
        # Configuration
        self.SUBREDDITS = ["memes", "dankmemes", "wholesomememes", "me_irl"]
        self.MIN_SCORE = 5000
        self.POST_LIMIT = 50
        self.MAX_TITLE_LENGTH = 250
        
        # State
        self.viewed_memes: List[dict] = []
        self.current_index: int = 0
        self.favorites: List[dict] = []
        self.active_favorites_messages: Dict[int, int] = {}  # {chat_id: message_id}
        self.main_message_ids: Dict[int, int] = {}  # Tracks main messages
        
        # Initialize bot
        self.bot = Bot(
            token=os.getenv("BOT_TOKEN"),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        
        # Reddit API
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="TelegramMemeBot/1.0"
        )
        
        self._register_handlers()

    def _register_handlers(self):
        self.dp.message(Command("start"))(self.cmd_start)
        self.dp.callback_query(lambda c: c.data in ["new_meme", "prev_meme", "next_meme"])(self.handle_navigation)
        self.dp.callback_query(lambda c: c.data == "toggle_favorite")(self.toggle_favorite)
        self.dp.callback_query(lambda c: c.data == "show_favorites")(self.show_favorites)
        self.dp.callback_query(lambda c: c.data.startswith("fav_"))(self.handle_favorites)
        self.dp.callback_query(lambda c: c.data == "back_to_main")(self.back_to_main)

    async def fetch_meme(self) -> Optional[dict]:
        try:
            subreddit = self.reddit.subreddit(random.choice(self.SUBREDDITS))
            posts = [
                post for post in subreddit.hot(limit=self.POST_LIMIT)
                if (not post.over_18 and
                    post.url and
                    post.url.endswith(("jpg", "jpeg", "png", "gif")) and
                    post.score >= self.MIN_SCORE and
                    post.id not in [m['id'] for m in self.viewed_memes])
            ]
            if not posts:
                return None
            
            post = random.choice(posts)
            return {
                'id': post.id,
                'url': post.url,
                'title': post.title[:self.MAX_TITLE_LENGTH] + "..." 
                        if len(post.title) > self.MAX_TITLE_LENGTH 
                        else post.title,
                'score': post.score,
                'subreddit': str(subreddit)
            }
        except Exception as e:
            print(f"Error fetching meme: {e}")
            return None

    def get_meme_keyboard(self) -> InlineKeyboardMarkup:
        buttons = []
        current_meme = self.viewed_memes[self.current_index] if self.viewed_memes else None
        
        # Navigation buttons
        nav_buttons = []
        if self.current_index > 0:
            nav_buttons.append(InlineKeyboardButton(text="◀️ Previous", callback_data="prev_meme"))
        
        if self.current_index < len(self.viewed_memes) - 1:
            nav_buttons.append(InlineKeyboardButton(text="Next ▶️", callback_data="next_meme"))
        else:
            nav_buttons.append(InlineKeyboardButton(text="🔄 New", callback_data="new_meme"))
        
        buttons.append(nav_buttons)
        
        # Favorite button
        if current_meme:
            if current_meme in self.favorites:
                buttons.append([InlineKeyboardButton(text="❌ Remove from favorites", callback_data="toggle_favorite")])
            else:
                buttons.append([InlineKeyboardButton(text="❤️ Add to favorites", callback_data="toggle_favorite")])
        
        if self.favorites:
            buttons.append([InlineKeyboardButton(text="⭐ Favorites", callback_data="show_favorites")])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    def get_favorites_keyboard(self, index: int) -> InlineKeyboardMarkup:
        buttons = []
        
        # Navigation buttons
        nav_buttons = []
        if index > 0:
            nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"fav_prev_{index}"))
        if index < len(self.favorites) - 1:
            nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"fav_next_{index}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        buttons.append([
            InlineKeyboardButton(text="❌ Delete", callback_data=f"fav_remove_{index}"),
            InlineKeyboardButton(text="◀️ Back", callback_data="back_to_main")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def show_meme(self, context: types.Message | types.CallbackQuery, meme: dict, is_new: bool = True):
        try:
            if is_new and isinstance(context, types.CallbackQuery):
                self.current_index = len(self.viewed_memes) - 1
            
            caption = (f"📌 <b>r/{meme['subreddit']}</b>\n"
                      f"🔥 <i>Score:</i> <b>{meme['score']:,}</b>\n"
                      f"📝 <i>{meme['title']}</i>\n\n"
                      f"🔗 <a href='https://redd.it/{meme['id']}'>Source</a>")
            
            target = context if isinstance(context, types.Message) else context.message
            chat_id = target.chat.id
            
            self.main_message_ids[chat_id] = target.message_id
            
            if hasattr(target, 'photo') and target.photo:
                await target.edit_media(
                    types.InputMediaPhoto(media=meme['url'], caption=caption),
                    reply_markup=self.get_meme_keyboard()
                )
            else:
                await target.answer_photo(
                    meme['url'],
                    caption=caption,
                    reply_markup=self.get_meme_keyboard()
                )
        except Exception as e:
            print(f"Display error: {e}")
            if isinstance(context, types.CallbackQuery):
                await context.answer("⚠️ Update failed", show_alert=False)

    async def cmd_start(self, message: types.Message):
        try:
            meme_data = await self.fetch_meme()
            if not meme_data:
                await message.answer("😢 Couldn't load memes. Try later!")
                return
            
            self.viewed_memes.append(meme_data)
            await self.show_meme(message, meme_data)
        except Exception as e:
            print(f"/start error: {e}")
            await message.answer("⚠️ Error occurred. Please try again.")

    async def handle_navigation(self, callback: types.CallbackQuery):
        try:
            if callback.data == "new_meme":
                meme_data = await self.fetch_meme()
                if not meme_data:
                    await callback.answer("No new memes available", show_alert=False)
                    return
                
                self.viewed_memes.append(meme_data)
                self.current_index = len(self.viewed_memes) - 1
                await self.show_meme(callback, meme_data)
            
            elif callback.data == "prev_meme":
                if self.current_index > 0:
                    self.current_index -= 1
                    await self.show_meme(callback, self.viewed_memes[self.current_index], False)
                else:
                    await callback.answer("This is the first meme", show_alert=False)
            
            elif callback.data == "next_meme":
                if self.current_index < len(self.viewed_memes) - 1:
                    self.current_index += 1
                    await self.show_meme(callback, self.viewed_memes[self.current_index], False)
                else:
                    await callback.answer("Press '🔄 New'", show_alert=False)
        
        except Exception as e:
            print(f"Navigation error: {e}")
            await callback.answer("⚠️ Navigation error", show_alert=False)
        
        await callback.answer()

    async def toggle_favorite(self, callback: types.CallbackQuery):
        try:
            if not self.viewed_memes or self.current_index >= len(self.viewed_memes):
                await callback.answer("Error: Meme not found", show_alert=False)
                return
            
            meme = self.viewed_memes[self.current_index]
            chat_id = callback.message.chat.id
            
            if meme in self.favorites:
                self.favorites.remove(meme)
                await callback.answer("Removed from favorites", show_alert=False)
            else:
                self.favorites.append(meme)
                await callback.answer("★ Added to favorites", show_alert=False)
            
            await self.show_meme(callback, meme, False)
            
            if chat_id in self.active_favorites_messages:
                await self.update_active_favorites(chat_id)
                
        except Exception as e:
            print(f"Favorite error: {e}")
            await callback.answer("⚠️ Operation failed", show_alert=False)

    async def update_active_favorites(self, chat_id: int):
        if chat_id not in self.active_favorites_messages:
            return

        try:
            message_id = self.active_favorites_messages[chat_id]
            current_index = 0

            if not self.favorites:
                await self.bot.delete_message(chat_id, message_id)
                del self.active_favorites_messages[chat_id]
                return

            meme = self.favorites[current_index]
            await self.bot.edit_message_media(
                chat_id=chat_id,
                message_id=message_id,
                media=types.InputMediaPhoto(
                    media=meme['url'],
                    caption=(f"⭐ <b>Favorites (1/{len(self.favorites)})</b>\n\n"
                            f"📌 r/{meme['subreddit']}\n"
                            f"🔥 {meme['score']:,} | {meme['title']}")
                ),
                reply_markup=self.get_favorites_keyboard(current_index)
            )
        except Exception as e:
            print(f"Favorites update error: {e}")

    async def show_favorites(self, callback: types.CallbackQuery):
        try:
            chat_id = callback.message.chat.id
            
            if chat_id in self.active_favorites_messages:
                await callback.answer("Favorites already open", show_alert=False)
                return
            
            if not self.favorites:
                await callback.answer("Favorites are empty", show_alert=False)
                return
            
            first_meme = self.favorites[0]
            message = await callback.message.answer_photo(
                first_meme['url'],
                caption=(f"⭐ <b>Favorites (1/{len(self.favorites)})</b>\n\n"
                        f"📌 r/{first_meme['subreddit']}\n"
                        f"🔥 {first_meme['score']:,} | {first_meme['title']}"),
                reply_markup=self.get_favorites_keyboard(0)
            )
            
            self.active_favorites_messages[chat_id] = message.message_id
        except Exception as e:
            print(f"Favorites display error: {e}")
            await callback.answer("⚠️ Loading error", show_alert=False)
        
        await callback.answer()

    async def handle_favorites(self, callback: types.CallbackQuery):
        try:
            chat_id = callback.message.chat.id
            
            if not self.favorites:
                if chat_id in self.active_favorites_messages:
                    del self.active_favorites_messages[chat_id]
                await callback.message.delete()
                await callback.answer("Favorites are empty")
                return
            
            action, _, index = callback.data.partition('_')[2].partition('_')
            index = int(index)
            removed_meme = None

            if action == "prev":
                new_index = max(0, index - 1)
            elif action == "next":
                new_index = min(len(self.favorites) - 1, index + 1)
            elif action == "remove":
                removed_meme = self.favorites.pop(index)
                await callback.answer(f"Deleted: {removed_meme['title'][:30]}...", show_alert=False)
                new_index = min(index, len(self.favorites) - 1) if self.favorites else 0

                if removed_meme in self.viewed_memes:
                    meme_index = self.viewed_memes.index(removed_meme)
                    if chat_id in self.main_message_ids:
                        try:
                            await self.bot.edit_message_reply_markup(
                                chat_id=chat_id,
                                message_id=self.main_message_ids[chat_id],
                                reply_markup=self.get_meme_keyboard()
                            )
                        except Exception as e:
                            print(f"Main message update error: {e}")

            if self.favorites:
                meme = self.favorites[new_index]
                await callback.message.edit_media(
                    types.InputMediaPhoto(
                        media=meme['url'],
                        caption=(f"⭐ <b>Favorites ({new_index + 1}/{len(self.favorites)})</b>\n\n"
                                f"📌 r/{meme['subreddit']}\n"
                                f"🔥 {meme['score']:,} | {meme['title']}")
                    ),
                    reply_markup=self.get_favorites_keyboard(new_index)
                )
            else:
                await callback.message.delete()
                if chat_id in self.active_favorites_messages:
                    del self.active_favorites_messages[chat_id]
                await callback.answer("Favorites cleared", show_alert=False)
        
        except Exception as e:
            print(f"Favorites error: {e}")
            await callback.answer("⚠️ Operation failed", show_alert=False)
        
        await callback.answer()

    async def back_to_main(self, callback: types.CallbackQuery):
        try:
            chat_id = callback.message.chat.id
            if chat_id in self.active_favorites_messages:
                del self.active_favorites_messages[chat_id]
            
            if self.viewed_memes:
                await self.show_meme(callback, self.viewed_memes[self.current_index], False)
            else:
                await callback.message.answer("Start with /start")
        except Exception as e:
            print(f"Return error: {e}")
            await callback.answer("⚠️ Return error", show_alert=False)
        
        await callback.answer()

    async def run(self):
        await self.dp.start_polling(self.bot)

if __name__ == '__main__':
    bot = MemeBot()
    asyncio.run(bot.run())
