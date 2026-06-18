#!/usr/bin/env python3
# =============================================================================
# VORTEX BOT v3.0 - Instagram Reset Link Sender (2 Methods Parallel)
# With Referral + Coins + Gift Code System
# By @xtxz7 | @kai_olds | @louis_olds
# =============================================================================

import os, sys, json, asyncio, subprocess, importlib, ssl, random, datetime
from concurrent.futures import ThreadPoolExecutor

# ─── AUTO INSTALL ──────────────────────────────────────────────────────────
try:
    import requests
    from telethon import TelegramClient, events, Button
    from telethon.sessions import StringSession
except ImportError:
    os.system("pip install requests telethon --upgrade -q")
    import requests
    from telethon import TelegramClient, events, Button
    from telethon.sessions import StringSession

# ─── INSTALL httpx + h2 ───────────────────────────────────────────────────
def install_dependencies():
    packages = ["httpx", "h2"]
    for package in packages:
        try:
            importlib.import_module(package.split("==")[0])
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_dependencies()

import httpx

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

API_ID = 35964213
API_HASH = "49f6f929d59ba8c565c498015a48adb1"
BOT_TOKEN = "8641933652:AAHB0gABOR-Pyg6TRQcCHLQCo_Ek47nFrZc"
ADMIN_IDS = [7691071175]
CONFIG_FILE = "channel_config.json"
USERS_FILE = "bot_users.json"
COINS_FILE = "user_coins.json"
REFERRALS_FILE = "user_referrals.json"
GIFT_CODES_FILE = "gift_codes.json"

BOT_USERNAME = "Reset_link_send_Bot"

CHANNELS = {
    1: {"type": "public", "link": "https://t.me/vrtxportal", "username": "@vrtxportal", "invite_link": "https://t.me/vrtxportal"}
}

user_state = {}
bot_users = set()
executor = ThreadPoolExecutor(max_workers=20)

# Coins database
user_coins = {}
user_referrals = {}
gift_codes = {}

# Colors
G = '\033[92m'
Y = '\033[1;33m'
Z = '\033[1;31m'
N = '\033[1;37m'


def load_channels():
    global CHANNELS
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                for k, v in json.load(f).items():
                    if "type" not in v:
                        v["type"] = "public"
                        v["invite_link"] = v.get("link", "")
                    CHANNELS[int(k)] = v
        except:
            pass
    save_channels()


def save_channels():
    with open(CONFIG_FILE, "w") as f:
        json.dump({str(k): v for k, v in CHANNELS.items()}, f, indent=2)


def load_users():
    global bot_users
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE) as f:
                bot_users = set(json.load(f))
        except:
            bot_users = set()


def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(list(bot_users), f)


def load_coins():
    global user_coins
    if os.path.exists(COINS_FILE):
        try:
            with open(COINS_FILE) as f:
                user_coins = json.load(f)
        except:
            user_coins = {}
    user_coins = {k: int(v) for k, v in user_coins.items()}


def save_coins():
    with open(COINS_FILE, "w") as f:
        json.dump({str(k): v for k, v in user_coins.items()}, f, indent=2)


def load_referrals():
    global user_referrals
    if os.path.exists(REFERRALS_FILE):
        try:
            with open(REFERRALS_FILE) as f:
                raw = json.load(f)
                user_referrals = {}
                for k, v in raw.items():
                    user_referrals[int(k)] = {
                        "referred_by": v.get("referred_by"),
                        "referral_count": v.get("referral_count", 0),
                        "referral_link": f"https://t.me/{BOT_USERNAME}?start=ref_{k}",
                        "username": v.get("username", ""),
                        "ref_code": f"{k}"
                    }
        except:
            user_referrals = {}
    else:
        user_referrals = {}


def save_referrals():
    to_save = {}
    for k, v in user_referrals.items():
        to_save[str(k)] = v
    with open(REFERRALS_FILE, "w") as f:
        json.dump(to_save, f, indent=2)


def load_gift_codes():
    global gift_codes
    if os.path.exists(GIFT_CODES_FILE):
        try:
            with open(GIFT_CODES_FILE) as f:
                raw = json.load(f)
                gift_codes = {}
                for code, data in raw.items():
                    gift_codes[code.upper()] = data
        except:
            gift_codes = {}
    else:
        gift_codes = {}


def save_gift_codes():
    with open(GIFT_CODES_FILE, "w") as f:
        json.dump(gift_codes, f, indent=2)


load_channels()
load_users()
load_coins()
load_referrals()
load_gift_codes()


def get_user_coins(user_id):
    uid = str(user_id)
    return int(user_coins.get(uid, 0))


def set_user_coins(user_id, amount):
    uid = str(user_id)
    user_coins[uid] = max(0, int(amount))
    save_coins()


def add_user_coins(user_id, amount):
    uid = str(user_id)
    current = int(user_coins.get(uid, 0))
    user_coins[uid] = current + int(amount)
    save_coins()
    return user_coins[uid]


def deduct_user_coins(user_id, amount):
    uid = str(user_id)
    current = int(user_coins.get(uid, 0))
    if current < int(amount):
        return False
    user_coins[uid] = current - int(amount)
    save_coins()
    return True


def init_user_referral(user_id, username=""):
    uid = int(user_id)
    if uid not in user_referrals:
        user_referrals[uid] = {
            "referred_by": None,
            "referral_count": 0,
            "referral_link": f"https://t.me/{BOT_USERNAME}?start=ref_{uid}",
            "username": username,
            "ref_code": f"{uid}"
        }
        save_referrals()
    else:
        existing = user_referrals[uid]
        expected_link = f"https://t.me/{BOT_USERNAME}?start=ref_{uid}"
        if existing.get("referral_link") != expected_link:
            existing["referral_link"] = expected_link
            existing["ref_code"] = f"{uid}"
            save_referrals()
    return user_referrals[uid]


def get_referral_by_code(ref_code):
    ref_code = ref_code.replace("ref_", "").strip()
    for uid, data in user_referrals.items():
        if str(uid) == ref_code:
            return uid, data
    return None, None


# ─── CHANNEL CHECK ─────────────────────────────────────────────────────────
def check_user_channels_sync(user_id):
    not_joined = []
    for idx, ch_data in CHANNELS.items():
        username = ch_data.get("username", "").lstrip("@")
        if not username:
            not_joined.append(idx)
            continue
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember",
                params={"chat_id": f"@{username}", "user_id": user_id},
                timeout=4
            )
            data = r.json()
            if data.get("ok"):
                status = data["result"]["status"]
                if status in ("member", "administrator", "creator", "restricted"):
                    continue
            not_joined.append(idx)
        except:
            not_joined.append(idx)
    return len(not_joined) == 0, not_joined


async def check_user_channels(user_id):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, check_user_channels_sync, user_id)


# ═══════════════════════════════════════════════════════════════════════════
# INSTAGRAM RESET LINK SENDER - 2 METHODS 🔥
# ═══════════════════════════════════════════════════════════════════════════

def try_method_1(username_or_email):
    try:
        url = "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/"
        headers = {
            "User-Agent": "Instagram Android",
            "x-csrftoken": "missing",
            "accept-language": "tr-TR,tr;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"email_or_username": username_or_email, "flow": "fxcal"}
        with httpx.Client(http2=True, headers=headers, timeout=15) as c:
            r = c.post(url, data=data)
            try:
                j = r.json()
                if r.status_code == 200 and j.get("status") == "ok":
                    return True, "✅ Method 1 (Android HTTP/2) - Başarılı"
            except:
                if r.status_code == 200:
                    return True, "✅ Method 1 (Android HTTP/2) - Başarılı"
            return False, f"M1: HTTP {r.status_code}"
    except Exception as e:
        return False, f"M1: {str(e)[:40]}"


def try_method_2(username_or_email):
    try:
        url = "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/?hl=en"
        cookies = {
            "csrftoken": "qXbOywPKhDdMfdTceKhs2DcocVgMz4q8",
            "mid": "adiAuAAEAAFqNhj2f7KBf56OjV5_",
            "ig_did": "6C2A174F-093F-4BAC-8DDF-B7D6527F73AE",
        }
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=1.0",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
            "x-ig-app-id": "936619743392459",
            "x-csrftoken": "qXbOywPKhDdMfdTceKhs2DcocVgMz4q8",
            "x-requested-with": "XMLHttpRequest",
        }
        jazoest_list = ["22603", "22913", "22785", "22841", "22567"]
        data = {
            "email_or_username": username_or_email,
            "jazoest": random.choice(jazoest_list)
        }
        context = ssl.create_default_context()
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        with httpx.Client(http2=True, verify=context, timeout=20) as client:
            r = client.post(url, headers=headers, cookies=cookies, data=data)
            try:
                j = r.json()
                if r.status_code == 200:
                    return True, "✅ Method 2 (iPhone Safari) - Başarılı"
            except:
                if r.status_code == 200:
                    return True, "✅ Method 2 (iPhone Safari) - Başarılı"
            return False, f"M2: HTTP {r.status_code}"
    except Exception as e:
        return False, f"M2: {str(e)[:40]}"


def send_reset_2x_parallel(username_or_email):
    methods = [
        ("🤖 Android HTTP/2", try_method_1),
        ("🍏 iPhone Safari", try_method_2),
    ]
    results = []
    success = False
    success_method = ""
    for name, func in methods:
        ok, msg = func(username_or_email)
        results.append(f"{name}: {msg}")
        if ok and not success:
            success = True
            success_method = name
    return {
        "success": success,
        "results": results,
        "tried": len(results),
        "message": f"Tried {len(results)} methods" if not success else f"✅ Success via {success_method}",
        "username": username_or_email,
    }


# ═══════════════════════════════════════════════════════════════════════════
# TELEGRAM BOT
# ═══════════════════════════════════════════════════════════════════════════

client = TelegramClient(StringSession(), API_ID, API_HASH).start(bot_token=BOT_TOKEN)
print(f"{G}[+] VORTEX v3.0 - 2x PARALLEL RESET MODE 🔥{N}")
print(f"{G}[+] Users loaded: {len(bot_users)}{N}")
print(f"{G}[+] Coins system active 💰{N}")
print(f"{G}[+] Referral system active 🔗{N}")
print(f"{G}[+] Gift code system active 🎁{N}")


def mk_btns(nj):
    btns = []
    for idx in nj:
        cd = CHANNELS.get(idx, {})
        lbl = "🔒" if cd.get("type") == "private" else "📢"
        btns.append([Button.url(f"{lbl} Channel {idx}", cd.get("invite_link") or cd.get("link", ""))])
    if btns:
        btns.append([Button.inline("✅ Joined All", b"joined")])
    return btns


# ─── /START ────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/start"))
async def start_cmd(event):
    s = await event.get_sender()
    uid = s.id
    uname = s.username or s.first_name or f"User{uid}"

    parts = event.message.text.strip().split()
    ref_code = None
    if len(parts) > 1:
        ref_param = parts[1]
        if ref_param.startswith("ref_"):
            ref_code = ref_param.replace("ref_", "")

    bot_users.add(uid)
    save_users()

    init_user_referral(uid, uname)

    uid_str = str(uid)
    if uid_str not in user_coins or user_coins[uid_str] == 0:
        add_user_coins(uid, 10)

        if ref_code:
            ref_uid, ref_data = get_referral_by_code(ref_code)
            if ref_uid and int(ref_uid) != uid:
                if user_referrals[uid]["referred_by"] is None:
                    add_user_coins(int(ref_uid), 3)
                    user_referrals[int(ref_uid)]["referral_count"] += 1
                    user_referrals[uid]["referred_by"] = int(ref_uid)
                    save_referrals()
                    await event.respond(
                        f"🎉 **Referral Bonus!**\n\n"
                        f"You were referred by **{ref_data.get('username', 'User')}**!\n"
                        f"You both got bonus coins! 🪙"
                    )

    all_joined, nj = await check_user_channels(uid)

    if all_joined:
        user_state[uid] = {"step": "username"}
        coins = get_user_coins(uid)
        await event.respond(
            "**🔐 VORTEX PREMIUM v5.0 | **\n\n"
            "✅ **ACCESS GRANTED**\n\n"
            f"💰 **Your Coins:** `{coins}`\n\n"
            "📌 **Send Instagram Username or Email**\n"
            "**📤 Send now:**",
            buttons=[
                [Button.inline("💰 Referral System", b"referral")],
                [Button.url("📞 Contact Admin", "https://t.me/dochains")]
            ]
        )
    else:
        msg = "⚠️ **VERIFICATION REQUIRED**\n\n"
        for idx in nj:
            cd = CHANNELS.get(idx, {})
            typ = cd.get("type", "public")
            if typ == "private":
                msg += f"🔒 **Channel {idx}:** {cd.get('username', '')}\n   Click → Join \n"
            else:
                msg += f"❌ **Channel {idx}:** {cd.get('username', '')}\n   Click → Tap Join → Done\n"
        msg += "\n⏳ **After Joined then Tap On **✅ Joined All**"
        await event.respond(msg, buttons=mk_btns(nj))


# ─── REFERRAL CALLBACK ────────────────────────────────────────────────────
@client.on(events.CallbackQuery(data=b"referral"))
async def referral_cb(event):
    s = await event.get_sender()
    uid = s.id
    uname = s.username or s.first_name or f"User{uid}"

    ref_info = init_user_referral(uid, uname)
    coins = get_user_coins(uid)

    msg = (
        f"**💰 REFERRAL SYSTEM**\n\n"
        f"**👤 Your Info:**\n"
        f"├ **User ID:** `{uid}`\n"
        f"├ **Username:** @{uname}\n"
        f"├ **🪙 Coins:** `{coins}`\n"
        f"└ **👥 Referrals:** `{ref_info.get('referral_count', 0)}`\n\n"
        f"**📋 Referral Link:**\n"
        f"`{ref_info.get('referral_link', '')}`\n\n"
        f"**📌 How it works:**\n"
        f"├ 🆓 **Free:** `10` coins on start\n"
        f"├ 🔄 **Reset:** `1` coin per reset\n"
        f"└ 👥 **Referral:** `3` coins per referral\n\n"
        f"**✅ Share your referral link with friends!**"
    )

    await event.edit(
        msg,
        buttons=[
            [Button.switch_inline("📤 Share Referral Link", f"@vrtxportal Join VORTEX! Use my referral: https://t.me/{BOT_USERNAME}?start=ref_{uid}")],
            [Button.inline("🔙 Back", b"back_main")]
        ]
    )


# ─── BACK TO MAIN CALLBACK ────────────────────────────────────────────────
@client.on(events.CallbackQuery(data=b"back_main"))
async def back_main_cb(event):
    s = await event.get_sender()
    uid = s.id

    all_joined, nj = await check_user_channels(uid)
    if not all_joined:
        msg = "⚠️ **VERIFY FIRST**\n\n"
        for idx in nj:
            cd = CHANNELS.get(idx, {})
            msg += f"❌ **Ch {idx}:** {cd.get('username', '')}\n"
        msg += "\nTap **✅ Joined All** when approved"
        return await event.edit(msg, buttons=mk_btns(nj))

    coins = get_user_coins(uid)
    await event.edit(
        "**🔐 VORTEX PREMIUM v5.0 | **\n\n"
        "✅ **ACCESS GRANTED**\n\n"
        f"💰 **Your Coins:** `{coins}`\n\n"
        "📌 **Send Instagram Username or Email**\n"
        "**📤 Send now:**",
        buttons=[
            [Button.inline("💰 Referral System", b"referral")],
            [Button.url("📞 Contact Admin", "https://t.me/dochains")]
        ]
    )


# ─── /REDEEM COMMAND ──────────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/redeem"))
async def redeem_cmd(event):
    s = await event.get_sender()
    uid = s.id

    parts = event.message.text.strip().split()
    if len(parts) < 2:
        return await event.respond(
            "**🎁 REDEEM GIFT CODE**\n\n"
            "Usage: `/redeem <code>`\n\n"
            "Enter a gift code to claim coins."
        )

    code = parts[1].upper()

    if code not in gift_codes:
        return await event.respond(
            f"**❌ Invalid Code!**\n\n"
            f"Code `{code}` not found or expired."
        )

    code_data = gift_codes[code]

    if code_data.get("expires_at"):
        expiry = datetime.datetime.fromisoformat(code_data["expires_at"])
        if datetime.datetime.now() > expiry:
            del gift_codes[code]
            save_gift_codes()
            return await event.respond(f"**❌ Code Expired!**\n\nCode `{code}` has expired.")

    if uid in code_data.get("used_by", []):
        return await event.respond(f"**❌ Already Used!**\n\nYou have already redeemed code `{code}`.")

    if len(code_data.get("used_by", [])) >= code_data.get("max_uses", 99999):
        return await event.respond(f"**❌ Code Fully Used!**\n\nCode `{code}` has reached its max usage limit.")

    coins_to_add = code_data.get("coins", 0)
    new_balance = add_user_coins(uid, coins_to_add)

    if "used_by" not in code_data:
        code_data["used_by"] = []
    code_data["used_by"].append(uid)
    save_gift_codes()

    await event.respond(
        f"**🎁 CODE REDEEMED!**\n\n"
        f"**Code:** `{code}`\n"
        f"**Coins Added:** `+{coins_to_add}` 🪙\n"
        f"**New Balance:** `{new_balance}` 🪙\n\n"
        f"✅ **Success!** Use /start to check."
    )


# ─── JOINED CALLBACK ───────────────────────────────────────────────────────
@client.on(events.CallbackQuery(data=b"joined"))
async def joined_cb(event):
    s = await event.get_sender()
    uid = s.id
    all_joined, nj = await check_user_channels(uid)

    if all_joined:
        user_state[uid] = {"step": "username"}
        coins = get_user_coins(uid)
        await event.edit(
            f"**✅ VERIFIED!**\n\n"
            f"💰 **Your Coins:** `{coins}`\n\n"
            "**📤 Send Instagram username or email:**",
            buttons=[
                [Button.inline("💰 Referral System", b"referral")],
                [Button.url("📞 Contact Admin", "https://t.me/dochains")]
            ]
        )
    else:
        msg = "❌ **NOT APPROVED YET**\n\n"
        for idx in nj:
            cd = CHANNELS.get(idx, {})
            typ = cd.get("type", "public")
            msg += f"❌ **Channel {idx}:** {cd.get('username', '')}\n"
        msg += "\n📌 Click channel → Then Join it→ Tap ✅\n\n👉 Tap **✅ Joined All** to re-check"
        await event.edit(msg, buttons=mk_btns(nj))


# ─── /USERS COMMAND ────────────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/users"))
async def users_cmd(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS:
        return await event.respond("**⛔ UNAUTHORIZED**")

    total = len(bot_users)
    await event.respond(
        f"**📊 USER DATABASE**\n\n"
        f"**Total Registered Users:** `{total}`\n"
        f"**Database File:** `{USERS_FILE}`"
    )


# ─── /BROADCAST COMMAND ────────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/broadcast"))
async def broadcast_cmd(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS:
        return await event.respond("**⛔ UNAUTHORIZED**")

    parts = event.message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        return await event.respond(
            "**📢 BROADCAST**\n\n"
            "Usage: `/broadcast <message>`\n\n"
            "Sends message to all registered users in database."
        )

    broadcast_msg = parts[1]
    sent = 0
    failed = 0

    status_msg = await event.respond("**📤 Broadcasting to all users...**")

    for uid in bot_users:
        try:
            await client.send_message(uid, broadcast_msg)
            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1

    await status_msg.edit(
        f"**📢 BROADCAST COMPLETE**\n\n"
        f"✅ **Sent:** `{sent}`\n"
        f"❌ **Failed:** `{failed}`\n"
        f"📊 **Total in DB:** `{len(bot_users)}`"
    )


# ─── /GIFT COMMAND (ADMIN ONLY) ───────────────────────────────────────────
@client.on(events.NewMessage(pattern="/gift"))
async def gift_cmd(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS:
        return await event.respond("**⛔ UNAUTHORIZED**")

    parts = event.message.text.strip().split()
    if len(parts) < 3:
        return await event.respond(
            "**🎁 GIFT CODE GENERATOR**\n\n"
            "Usage: `/gift <code> <coins>`  (no expiry)\n"
            "       `/gift <code> <coins> <days>`  (expires after N days)\n"
            "       `/gift <code> <coins> <days> <max_uses>`  (max uses limit)\n\n"
            "**Examples:**\n"
            "`/gift WELCOME10 10` - 10 coins, never expires\n"
            "`/gift WELCOME10 10 30` - 10 coins, expires in 30 days\n"
            "`/gift WELCOME10 10 30 100` - 10 coins, 30 days, 100 uses max"
        )

    code = parts[1].upper()
    try:
        coins = int(parts[2])
    except:
        return await event.respond("❌ **Invalid coins amount!** Must be a number.")

    days = None
    max_uses = 99999

    if len(parts) >= 4:
        try:
            days = int(parts[3])
        except:
            pass

    if len(parts) >= 5:
        try:
            max_uses = int(parts[4])
        except:
            pass

    expires_at = None
    if days:
        expires_at = (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat()

    gift_codes[code] = {
        "coins": coins,
        "created_at": datetime.datetime.now().isoformat(),
        "expires_at": expires_at,
        "max_uses": max_uses,
        "used_by": [],
        "created_by": s.id
    }
    save_gift_codes()

    expiry_msg = f"Expires: `{days} days`" if days else "No expiry"
    uses_msg = f"Max Uses: `{max_uses}`" if max_uses < 99999 else "Unlimited uses"

    await event.respond(
        f"**✅ GIFT CODE CREATED**\n\n"
        f"**Code:** `{code}`\n"
        f"**🪙 Coins:** `{coins}`\n"
        f"**📅 {expiry_msg}**\n"
        f"**👥 {uses_msg}**\n\n"
        f"Users can redeem with: `/redeem {code}`"
    )


# ─── /GIFTLIST COMMAND (ADMIN ONLY) ───────────────────────────────────────
@client.on(events.NewMessage(pattern="/giftlist"))
async def giftlist_cmd(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS:
        return await event.respond("**⛔ UNAUTHORIZED**")

    if not gift_codes:
        return await event.respond("**📭 No gift codes found.**\n\nUse `/gift <code> <coins>` to create one.")

    msg = "**🎁 GIFT CODES LIST**\n\n"
    for code, data in sorted(gift_codes.items()):
        used = len(data.get("used_by", []))
        max_u = data.get("max_uses", 99999)
        max_str = str(max_u) if max_u < 99999 else "∞"

        expiry = data.get("expires_at")
        if expiry:
            exp_date = datetime.datetime.fromisoformat(expiry)
            if datetime.datetime.now() > exp_date:
                status = "❌ EXPIRED"
            else:
                days_left = (exp_date - datetime.datetime.now()).days
                status = f"✅ {days_left}d left"
        else:
            status = "♾️ No expiry"

        msg += f"`{code}` - 🪙{data['coins']} - Used: {used}/{max_str} - {status}\n"

    await event.respond(msg)


# ─── /COINS COMMAND ───────────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/coins"))
async def coins_cmd(event):
    s = await event.get_sender()
    uid = s.id

    parts = event.message.text.strip().split()

    if len(parts) == 1:
        coins = get_user_coins(uid)
        ref_info = user_referrals.get(uid, {})
        ref_count = ref_info.get("referral_count", 0)

        await event.respond(
            f"**💰 YOUR BALANCE**\n\n"
            f"**🆔 User ID:** `{uid}`\n"
            f"**🪙 Coins:** `{coins}`\n"
            f"**👥 Referrals:** `{ref_count}`\n\n"
            f"**🔗 Your referral link:**\n"
            f"`{ref_info.get('referral_link', 'N/A')}`\n\n"
            f"Each reset = `-1` coin\n"
            f"Each referral = `+3` coins"
        )
    elif uid in ADMIN_IDS and len(parts) == 2:
        try:
            target_uid = int(parts[1])
            target_coins = get_user_coins(target_uid)
            target_ref = user_referrals.get(target_uid, {})
            await event.respond(
                f"**💰 USER COINS**\n\n"
                f"**🆔 User ID:** `{target_uid}`\n"
                f"**🪙 Coins:** `{target_coins}`\n"
                f"**👥 Referrals:** `{target_ref.get('referral_count', 0)}`"
            )
        except:
            await event.respond("❌ Invalid user ID. Usage: `/coins <user_id>` (admin only)")


# ─── /ADDCOINS COMMAND (ADMIN ONLY) ───────────────────────────────────────
@client.on(events.NewMessage(pattern="/addcoins"))
async def addcoins_cmd(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS:
        return await event.respond("**⛔ UNAUTHORIZED**")

    parts = event.message.text.strip().split()
    if len(parts) < 3:
        return await event.respond(
            "**💳 ADD COINS (ADMIN)**\n\n"
            "Usage: `/addcoins <user_id> <amount>`\n"
            "Example: `/addcoins 123456789 50`"
        )

    try:
        target_uid = int(parts[1])
        amount = int(parts[2])
    except:
        return await event.respond("❌ Invalid format. Use: `/addcoins <user_id> <amount>`")

    new_balance = add_user_coins(target_uid, amount)

    await event.respond(
        f"**✅ COINS ADDED**\n\n"
        f"**User ID:** `{target_uid}`\n"
        f"**➕ Added:** `+{amount}`\n"
        f"**🪙 New Balance:** `{new_balance}`"
    )


# ─── MESSAGE HANDLER ───────────────────────────────────────────────────────
@client.on(events.NewMessage)
async def msg_handler(event):
    if event.message.text.startswith("/"):
        return

    s = await event.get_sender()
    uid = s.id
    txt = event.message.text.strip()

    bot_users.add(uid)
    save_users()

    all_joined, nj = await check_user_channels(uid)
    if not all_joined:
        msg = "⚠️ **VERIFY FIRST**\n\n"
        for idx in nj:
            cd = CHANNELS.get(idx, {})
            typ = cd.get("type", "public")
            if typ == "private":
                msg += f"🔒 **Ch {idx}:** {cd.get('username', '')} (Request & Wait)\n"
            else:
                msg += f"❌ **Ch {idx}:** {cd.get('username', '')}\n"
        msg += "\nTap **✅ Joined All** when approved"
        return await event.respond(msg, buttons=mk_btns(nj))

    if uid not in user_state:
        user_state[uid] = {"step": "username"}

    if user_state[uid]["step"] == "username":
        if len(txt) < 3:
            return await event.respond(
                "**❌ Too short!** Send valid username/email.",
                buttons=[
                    [Button.inline("💰 Referral System", b"referral")],
                    [Button.url("📞 Contact Admin", "https://t.me/dochains")]
                ]
            )

        # CHECK COINS
        coins = get_user_coins(uid)
        if coins <= 0:
            ref_info = user_referrals.get(uid, {})
            return await event.respond(
                "**❌ INSUFFICIENT COINS**\n\n"
                f"**🪙 Your Coins:** `{coins}`\n\n"
                "You need at least **1 coin** to send a reset link.\n\n"
                "**Ways to get coins:**\n"
                "1. 👥 **Refer friends** - Get `+3` coins per referral\n"
                "2. 🎁 **Use gift codes** - `/redeem <code>`\n"
                "3. 📞 **Contact Admin** for bonus\n\n"
                f"**🔗 Your referral link:**\n"
                f"`{ref_info.get('referral_link', 'N/A')}`",
                buttons=[
                    [Button.inline("💰 Referral System", b"referral")],
                    [Button.url("📞 Contact Admin", "https://t.me/dochains")]
                ]
            )

        processing_msg = await event.respond("**🔄 Sending Reset Link Wait... 🤖 🍏**")

        try:
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(executor, send_reset_2x_parallel, txt)

            results_detail = "\n".join(res.get("results", []))

            if res.get("success"):
                deduct_user_coins(uid, 1)
                new_coins = get_user_coins(uid)

                final_msg = (
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**✅ RESET LINK SENT SUCCESSFULLY**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"**👤 Account:** `{txt}`\n\n"
                    f"**✅ Sent Successfully**\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"**🪙 Coin Used:** `-1` | **Remaining:** `{new_coins}`\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**⚡ VORTEX PREMIUM v5.0**\n"
                    "By @vrtxportal\n\n"
                    "Send /start for new request"
                )
            else:
                final_msg = (
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**❌ BOTH METHODS FAILED**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"**👤 Account:** `{txt}`\n\n"
                    f"**📊 Results (tried 2):**\n"
                    "📌 Try again later or different account.\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Send /start to retry"
                )

            await processing_msg.edit(
                final_msg,
                buttons=[
                    [Button.inline("💰 Referral System", b"referral")],
                    [Button.url("📞 Contact Admin ", "https://t.me/dochains")]
                ]
            )

        except Exception as ex:
            await processing_msg.edit(
                f"**❌ Error:** `{str(ex)}`\n\nSend `/start` to retry",
                buttons=[
                    [Button.inline("💰 Referral System", b"referral")],
                    [Button.url("📞 Contact Admin ", "https://t.me/dochains")]
                ]
            )

        user_state[uid] = {"step": "done"}

    elif user_state[uid]["step"] == "done":
        await event.respond(
            "**✅ Already sent!** Send `/start` for new request.",
            buttons=[
                [Button.inline("💰 Referral System", b"referral")],
                [Button.url("📞 Contact Admin @dochains", "https://t.me/dochains")]
            ]
        )


# ─── ADMIN: ADD CHANNEL ────────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/addchannel"))
async def add_ch(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS:
        return await event.respond("**⛔ UNAUTHORIZED**")
    parts = event.message.text.strip().split(maxsplit=3)
    if len(parts) < 3:
        return await event.respond(
            "**Usage:**\n**Public:** `/addchannel <link> <@username>`\n"
            "**Private:** `/addchannel <link> <@username> private`"
        )
    link = parts[1]
    uname = "@" + parts[2].lstrip("@")
    typ = "private" if (len(parts) > 3 and parts[3].lower() == "private") else "public"
    nxt = max(CHANNELS.keys()) + 1 if CHANNELS else 1
    CHANNELS[nxt] = {"type": typ, "link": link, "username": uname, "invite_link": link}
    save_channels()
    await event.respond(f"**✅ Channel {nxt} Added** ({typ})\n{uname}")


# ─── ADMIN: REMOVE CHANNEL ────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/rmchannel"))
async def rm_ch(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS:
        return await event.respond("**⛔ UNAUTHORIZED**")
    parts = event.message.text.strip().split()
    if len(parts) < 2:
        cl = "\n".join([f"  {k}: {v['username']}" for k, v in CHANNELS.items()])
        return await event.respond(f"Usage: `/rmchannel <n>`\n\nCurrent:\n{cl}")
    try:
        idx = int(parts[1])
        if idx not in CHANNELS:
            return await event.respond(f"❌ Channel {idx} not found")
        rem = CHANNELS.pop(idx)
        save_channels()
        await event.respond(f"✅ Removed Ch {idx}: {rem['username']}")
    except:
        await event.respond("❌ Invalid number")


# ─── ADMIN: LIST CHANNELS ──────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/channels"))
async def list_ch(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS:
        return await event.respond("**⛔ UNAUTHORIZED**")
    if not CHANNELS:
        return await event.respond("No channels. Use `/addchannel`")
    msg = "**📢 CHANNELS**\n\n"
    for idx, cd in sorted(CHANNELS.items()):
        ic = "🔒" if cd.get("type") == "private" else "📢"
        msg += f"{ic} **{idx}:** {cd['username']}\n"
    await event.respond(msg)


# ─── LEGACY /SET ──────────────────────────────────────────────────────────
@client.on(events.NewMessage(pattern="/set"))
async def set_ch(event):
    s = await event.get_sender()
    if s.id not in ADMIN_IDS:
        return await event.respond("**⛔ UNAUTHORIZED**")
    cmd = event.message.text.strip().split()[0].lower()
    mp = {"/set": 1, "/set2": 2, "/set3": 3}
    idx = mp.get(cmd, 0)
    if not idx:
        return
    parts = event.message.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        return await event.respond(f"Usage: `{cmd} <link> <@username>`")
    CHANNELS[idx] = {"type": "public", "link": parts[1], "username": "@" + parts[2].lstrip("@"), "invite_link": parts[1]}
    save_channels()
    await event.respond(f"**✅ Channel {idx} Updated**\n{CHANNELS[idx]['username']}")


# ─── CHAT ACTION ──────────────────────────────────────────────────────────
@client.on(events.ChatAction)
async def chat_action(event):
    try:
        if event.user_joined or event.user_added:
            uid = event.user_id
            chat = await event.get_chat()
            ch_user = chat.username if hasattr(chat, 'username') else ""
            for idx, cd in CHANNELS.items():
                if cd.get("username", "").lstrip("@").lower() == ch_user.lower():
                    print(f"{G}[+] User {uid} APPROVED in channel {idx}{N}")
                    break
    except:
        pass


# ─── MAIN ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"{G}[+] VORTEX PREMIUM v3.0 - 2x PARALLEL RESET 🔥{N}")
    print(f"{G}[+] {len(CHANNELS)} channels loaded{N}")
    print(f"{G}[+] {len(bot_users)} users in database{N}")
    print(f"{G}[+] {len(user_coins)} users with coins{N}")
    print(f"{G}[+] {len(gift_codes)} gift codes active{N}")
    print(f"{G}[+] Methods: Android HTTP/2 🤖 + iPhone Safari 🍏{N}")
    print(f"{G}[+] Bot Running - All Systems Active{N}")

    try:
        client.run_until_disconnected()
    except KeyboardInterrupt:
        print(f"\n{Z}[-] Stopped{N}")
    except Exception as e:
        print(f"\n{Z}[-] Error: {e}{N}")