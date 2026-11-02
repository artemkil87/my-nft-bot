import os
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from PIL import Image, ImageDraw, ImageFont
from aiohttp import web

TOKEN = os.environ.get("BOT_TOKEN", "ВАШ_ТОКЕН")
bot = Bot(token=TOKEN)
dp = Dispatcher()

FONT_FILE = "Roboto-Bold.ttf"
# Новая 100% рабочая ссылка на шрифт напрямую от Google
FONT_URL = "https://gstatic.com"

def check_font():
    if not os.path.exists(FONT_FILE):
        print("Скачиваю шрифт...")
        response = requests.get(FONT_URL)
        if response.status_code == 200:
            with open(FONT_FILE, "wb") as f:
                f.write(response.content)
        else:
            raise Exception("Не удалось скачать шрифт.")

def generate_nft_offer(nft_name: str, price_ton: float, user_id: int) -> str:
    width, height = 750, 260
    bg_color = (24, 34, 45)       
    bubble_color = (36, 47, 61)   
    
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([40, 20, 710, 240], radius=18, fill=bubble_color)
    
    font_large = ImageFont.truetype(FONT_FILE, 30)
    font_medium = ImageFont.truetype(FONT_FILE, 26)
    font_small = ImageFont.truetype(FONT_FILE, 20)
    
    price_usd = price_ton * 5.20
    
    draw.text((70, 45), "⚡️ New NFT Offer Received", fill=(255, 215, 0), font=font_large)
    draw.text((70, 105), "Asset: ", fill=(142, 153, 163), font=font_medium)
    draw.text((150, 105), f"{nft_name}", fill=(255, 255, 255), font=font_medium)
    draw.text((70, 155), "Amount: ", fill=(142, 153, 163), font=font_medium)
    draw.text((175, 155), f"{price_ton:,.2f} TON", fill=(74, 177, 247), font=font_medium)
    draw.text((400, 155), f"(~${price_usd:,.2f})", fill=(112, 124, 136), font=font_small)
    draw.text((560, 205), "via Fragment", fill=(112, 124, 136), font=font_small)
    
    output_path = f"offer_{user_id}.png"
    img.save(output_path)
    return output_path

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🤖 Привет! Я бот для генерации NFT-офферов.\n\n"
        "Отправь команду в формате:\n"
        "/offer [Название_NFT] [Цена_в_TON]\n\n"
        "Пример: /offer @anonymous 1450"
    )

@dp.message(Command("offer"))
async def make_offer_cmd(message: types.Message):
    payload = message.text.replace("/offer", "").strip()
    if not payload:
        await message.answer("❌ Вы не ввели данные.")
        return
    try:
        parts = payload.split()
        price_str = parts[-1]
        nft_name = " ".join(parts[:-1])
        price_ton = float(price_str.replace(",", "."))
        
        await message.answer("⏳ Генерирую оффер...")
        image_path = generate_nft_offer(nft_name, price_ton, message.from_user.id)
        
        photo = FSInputFile(image_path)
        await message.answer_photo(photo=photo, caption=f"✅ Оффер для {nft_name} готов!")
        
        if os.path.exists(image_path):
            os.remove(image_path)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

async def handle_render_ping(request):
    return web.Response(text="Бот работает!")

async def main():
    check_font()
    app = web.Application()
    app.router.add_get('/', handle_render_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    
    await asyncio.gather(
        site.start(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
  
