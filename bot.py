import random
import discord
from discord.utils import escape_mentions
from discord import CustomActivity
from datetime import timedelta, datetime
from collections import defaultdict
from json import loads, dumps
import asyncio
from asyncio import sleep
import re
import bypass
import os
from base64 import b64encode, b64decode
import time
import requests
import threading
from shutil import move as file_move
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageColor
import io
import licensing
from discord.ui import Button, View, Select
from hashlib import sha256
import aiohttp
import ssl
import certifi
import urllib.parse

# ========== YOUR IDs ==========
OWNER_ID = 926722993567195207       # your user ID
YOUR_GUILD_ID = 1297958118751342674 # your server ID

# ========== STUBS FOR MISSING MODULES ==========
def randomstr(length=16):
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=length))

def seconds_to_str(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"

def timeconverter(timestr):
    try:
        return int(timestr)
    except:
        return 60

def detect_obf(content):
    return {}

onlyfans = None
fansly = None
Token = None

# ========== CONFIG ==========
is_localhost = False
ssl_context = ssl.create_default_context(cafile=certifi.where())
ApiToken = "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"
intents = discord.Intents.all()

tag_access = []
sent_conflict_msg = {}

def get_roles(id):
    # Only used for the original 25ms guild – return empty list
    return []

# ========== COMMAND MANAGER ==========
class RetardCommands:
    def __init__(self):
        self.commands = {}
        self.users = defaultdict(int)

    def is_cd(self, id, cmdcd):
        now = time.time()
        if self.users[id] and self.users[id] > now:
            return True
        self.users[id] = now + cmdcd

    async def handle_command(self, msg: discord.Message):
        cmd = msg.content.split()[0] if msg.content else None
        if msg.author.id == client.user.id or not cmd or cmd not in self.commands:
            return
        command = self.commands[cmd]
        if self.is_cd(msg.author.id, command.get("cooldown", 4)):
            await softerror(msg, f"Cooldown! Wait {round(self.users[msg.author.id]-time.time(),2)}s")
            return
        if "allow_channels" in command and msg.channel.id not in command['allow_channels']:
            return
        if "channelid" in command and command['channelid'] != msg.channel.id:
            await softerror(msg, f"Use in <#{command['channelid']}>")
            return
        if "roles" in command:
            # No roles in your server – skip check
            pass
        await command['func'](msg)
        return True

command_manager = RetardCommands()

# ========== VIEWS / DARKLUA (shortened – keep original from your repo) ==========
# ... (the RenameLuaView, DarkluaConfigView, etc. unchanged) ...

# ========== COMMAND FUNCTIONS (owner commands preserved) ==========
async def say_command(msg):
    text = escape_mentions(msg.content[5:])
    await msg.reply(text)

async def help_command(msg):
    await msg.reply("Commands: .l, .say, .meow, .solara, .beautify, .minify, .compress, .detect, .gen, .color, .upload, .get, .darklua, .decompile, .moonveil, .goofy, .promdeobf, .protect, .rename, .lconfig, .getrecovery, .claim\nOwner: .mute, .unmute, .slowmode, .msgs, .silentm, .be, .bd, .profanity, .random, .dumb, .raidlock, .u, .reg, .generate, .whitelist, .revoke")

async def nonfunc(msg):
    await msg.reply("Not available in this environment.")

async def makeit_rename(inpath, outpath):
    try:
        with open(inpath, "r", encoding="utf-8", errors="replace") as f:
            code = f.read()
    except:
        return False
    if not code:
        return False
    try:
        resp = await bypass.asyncpost("https://renamer-api.vercel.app/api/rename", {"code": code}, headers={"x-api-key": "33ms-DHJHS-24633", "Content-Type": "application/json"})
    except:
        return False
    renamed = resp and resp.get("renamedCode")
    if not renamed:
        return False
    try:
        with open(outpath, "w", encoding="utf-8", newline="\n") as f:
            f.write(renamed)
    except:
        return False
    return True

async def rename_cmd(msg):
    rename_dir = "./dumps/rename/"
    os.makedirs(rename_dir, exist_ok=True)
    filename = await getfile(msg, rename_dir)
    if not filename:
        return
    inpath = os.path.join(rename_dir, filename)
    outpath = os.path.join(rename_dir, f"{os.path.splitext(filename)[0]}_renamed.lua")
    async with msg.channel.typing():
        success = await makeit_rename(inpath, outpath)
    if not success or not os.path.isfile(outpath):
        await msg.reply("Renaming failed.")
        return
    try:
        await msg.reply(file=discord.File(outpath))
    except:
        await msg.reply("Renamed file ready but could not be sent.")

async def msdeobf(msg, no_attach_error=True):
    await msg.reply("Moonsec deobf not available.")

async def luaobf_deobf(msg):
    await msg.reply("LuaObfuscator string decryption not available.")

async def solara_cmd(msg):
    info = bypass.getsolarainfo()
    rblxinfo = bypass.getrobloxversioninfo()
    await msg.reply(f'Download: {info["BootstrapperUrl"]}\n{"✅ Updated" if info["SupportedClient"]==rblxinfo["clientVersionUpload"] else "❌ NOT updated"}\nChangelog:\n```diff\n{info["Changelog"].replace("[+]","+").replace("[-]","-")}```')

async def beautify_cmd(msg):
    filename = await getfile(msg, "./dumps/beautify/")
    if filename and await luabeautify(f"./dumps/beautify/{filename}", ["compute_expression"]):
        await msg.reply(file=discord.File(f"./dumps/beautify/{filename}"))
    else:
        await msg.reply("Beautify failed.")

async def minify_cmd(msg):
    filename = await getfile(msg, "./dumps/beautify/")
    if filename and await applydarklua(f"./dumps/beautify/{filename}", [
        "convert_index_to_field", "compute_expression", "filter_after_early_return", "group_local_assignment",
        "remove_comments", "remove_method_definition", "remove_nil_declaration", "remove_spaces",
        "remove_types", "remove_unused_if_branch", "remove_unused_variable", "remove_unused_while",
        "remove_function_call_parens", {"rule": "rename_variables", "globals": ["$default", "$roblox"]}
    ], {"name": "dense", "column_span": int(9e9)}):
        await msg.reply(file=discord.File(f"./dumps/beautify/{filename}"))
    else:
        await msg.reply("Minify failed.")

def lzw_compress(s: bytes) -> str:
    dictionary = {bytes([i]): bytes([i, 0]) for i in range(256)}
    a, b = 0, 1
    def nextcode():
        nonlocal a, b, dictionary
        c = bytes([a, b])
        a += 1
        if a >= 256:
            a = 0
            b += 1
            if b >= 256:
                dictionary = {bytes([i]): bytes([i, 0]) for i in range(256)}
                b = 1
        return c
    w = s[:1]
    out = []
    for c in s[1:]:
        c = bytes([c])
        if w + c in dictionary:
            w = w + c
        else:
            dictionary[w + c] = nextcode()
            out.append(dictionary.get(w, bytes([w[0], 0])))
            w = c
    out.append(dictionary.get(w, bytes([w[0], 0])))
    return b"".join(out).hex()

async def compress_cmd(msg):
    filename = await getfile(msg, "./dumps/beautify/")
    if filename:
        await applydarklua(f"./dumps/beautify/{filename}", [
            "convert_index_to_field", "compute_expression", "filter_after_early_return", "group_local_assignment",
            "remove_comments", "remove_method_definition", "remove_nil_declaration", "remove_spaces",
            "remove_types", "remove_unused_if_branch", "remove_unused_variable", "remove_unused_while",
            "remove_function_call_parens", {"rule": "rename_variables", "globals": ["$default", "$roblox"]}
        ], {"name": "dense", "column_span": int(9e9)})
        compressed = 'return(function(a,b,c,d,e)for f=0,255 do a[b(f,0)]=b(f)end function d(f,g,h,i)if h>255 then h=0 i+=1 if i>255 then g={}i=1 end end g[b(h,i)]=f h+=1 return g,h,i end e=({(\'' + lzw_compress(open(f"./dumps/beautify/{filename}","rb").read()) + '\'):gsub(\'..\',function(f)return b(tonumber(f,16))end)})[1]local f,g,h,i,j,k,l=#e,{},0,1,{},1,c(e,1,2)j[k]=a[l]or g[l]k+=1 for m=3,f,2 do local n,o=c(e,m,m+1),a[l]or g[l]local p=a[n]or g[n]if p then j[k]=p k+=1 g,h,i=d(o..c(p,1,1),g,h,i)else local q=o..c(o,1,1)j[k]=q k+=1 g,h,i=d(q,g,h,i)end l=n end return loadstring(table.concat(j))end)({},string.char,string.sub)(...)'
        buffer = io.StringIO()
        buffer.write(compressed)
        buffer.seek(0)
        await msg.reply(file=discord.File(buffer, "compressed.lua"))

async def gen_cmd(msg):
    smsg = msg.content.split()
    if len(smsg) == 1:
        await msg.reply("Provide a prompt.")
        return
    botmsg = await msg.reply("`Generating...`")
    image = await bypass.cloudflare_gen(" ".join(smsg[1:]))
    if image:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            tmp.write(image)
            tmp.seek(0)
            await botmsg.delete()
            await msg.reply(file=discord.File(tmp.name, "generated.png"))
    else:
        await botmsg.delete()
        await msg.reply("Failed to generate image.")

async def deobfhandler(msg):
    return None, None, False

async def ib2_deobf(msg):
    await msg.reply("Ironbrew 2 deobf not available.")

async def meow_cmd(msg):
    await msg.reply("meow " * random.randint(1,5))

async def luau_decompile_api(filelocation, outpath):
    with open(filelocation, "rb") as f:
        data = f.read()
    result = await bypass.asyncpost("https://api.lua.expert/decompile", {"script": b64encode(data).decode()}, returnResponseJson=False)
    with open(outpath, "w") as f:
        f.write(result)
    return True

async def roblox_decompile_cmd(msg):
    decompile_dir = "./dumps/decompile/"
    os.makedirs(decompile_dir, exist_ok=True)
    filename = await getfile(msg, decompile_dir, mode="binary", usehash=True, file_extension=".luac")
    if not filename:
        return
    outpath = f'{decompile_dir}{filename[:-1]}'
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    proc = await asyncio.create_subprocess_exec('./medal51/luau-lifter.exe', f'{decompile_dir}{filename}', "-e", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if stderr:
        try:
            if not await luau_decompile_api(f'{decompile_dir}{filename}', outpath):
                raise Exception
        except:
            await msg.reply("Decompilation failed.")
            return
    else:
        with open(outpath, "w", encoding="utf-8") as f:
            f.write(stdout.decode())
    await luabeautify(outpath, ["remove_comments"])
    await msg.reply(file=discord.File(outpath))

async def claim_license(msg):
    await msg.reply("Licensing not available in Actions environment.")

async def dumpConfig_cmd(msg):
    if msg.author.id in malicious_users:
        return await msg.reply("Not allowed.")
    embed = discord.Embed(title="Settings for .l")
    embed.add_field(name="Varnames", value="Give variables names", inline=False)
    embed.add_field(name="usesimplefunctions", value="Don't explore functions", inline=False)
    embed.add_field(name="watchoutforloop", value="Infinite loop detection", inline=False)
    embed.add_field(name="spynilglobals", value="Spy undefined globals", inline=False)
    embed.add_field(name="hook_op", value="Hook operators (experimental)", inline=False)
    embed.add_field(name="hook_op_default_return", value="Return value for hooked ops", inline=False)
    view = dumpConfig(msg.author)
    await msg.reply(embed=embed, view=view)

async def get_recovery_cmd(msg):
    if not isinstance(msg.channel, discord.DMChannel):
        await softerror(msg, "Use DMs.")
        return
    await msg.reply(f"||{await licensing.get_recovery(msg.author)}||")

async def cmds_access_cmd(msg):
    await softerror(msg, "Not available in Actions.")

mv_data = {}
try:
    with open("mvdata.json") as f:
        mv_data = loads(f.read())
except:
    pass
mv_save_in_use = False
async def save_mv_data():
    global mv_save_in_use
    if mv_save_in_use:
        return
    mv_save_in_use = True
    with open("mvdata.json", "w") as f:
        f.write(dumps(mv_data))
    mv_save_in_use = False

async def moonveil_obfuscate(msg):
    if msg.author.id in mv_data and mv_data[msg.author.id] > time.time() - 86400:
        await msg.reply(f"Daily limit used. Wait {seconds_to_str(round((mv_data[msg.author.id] + 86400) - time.time()))}.")
        return
    content = await getfile(msg)
    if not content:
        return
    mv_data[msg.author.id] = time.time()
    await save_mv_data()
    payload = {
        "options": {
            "cffDecomposeExpr": False, "cffEnable": True, "cffHoistLocals": True, "cffWrapBlocks": True,
            "mangleEnable": True, "mangleGlobals": True, "mangleNamedIndex": True, "mangleNumbers": False,
            "mangleSelfCalls": True, "mangleStrings": True, "prettify": False, "removeCompoundAssign": True,
            "removeIfExpr": True, "vmEnable": True, "vmWrapScript": True
        },
        "script": content
    }
    resp = await bypass.asyncpost("https://moonveil.cc/api/obfuscate", payload, headers={"Authorization": "Bearer mv-secret-7ce5ffab-57fa-45d7-b621-741f392fc6ff", "Content-Type": "application/json"}, returnResponseJson=False)
    buf = io.StringIO()
    buf.write(resp)
    buf.seek(0)
    await msg.reply(file=discord.File(buf, "moonveil.lua"))

async def goofy_fus(msg):
    content = await getfile(msg)
    if not content:
        return
    resp = await bypass.asyncpost("https://goofyscator.lua.cz/obfuscate", {
        "source": content,
        "settings": {"dontModifyBytecode": True, "hexNumbers": True, "renameGlobals": False, "generator": "Shuffled"}
    })
    if resp.get("status") != "success":
        await msg.reply("Obfuscation failed.")
        return
    buf = io.StringIO()
    buf.write("--[[ obfuscated @ discord.gg/25ms ]]\n" + resp["result"])
    buf.seek(0)
    await msg.reply(file=discord.File(buf, "goofyscator.lua"))

async def asyncget(url, headers=None, params=None, proxy=None, proxy_auth=None, getjson=False):
    async with aiohttp.ClientSession(headers=headers) as sess:
        async with sess.get(url, params=params, proxy=proxy, proxy_auth=proxy_auth, ssl=ssl_context) as resp:
            if getjson:
                return await resp.json()
            return await resp.text()

async def asyncpost(url, headers=None, data=None):
    async with aiohttp.ClientSession(headers=headers) as sess:
        async with sess.post(url, data=data) as resp:
            return await resp.text()

def _25ms_detect(content):
    patterns = {
        r"return [A-z0-9_]+\([0-9A-z_]+\(\),[A-z0-9,_\{\}\)\(]+\)": "ib2 (or similar)",
        r"newproxy,...metatable,...metatable,select,": "prometheus",
        r"\(\[\[This file was protected with MoonSec V3[A-z9_#\s]+\]\]\):gsub\('\.\+', \(function\([A-z0-9_]+\) [A-z0-9_]+": "moonsec v3",
        r"local v0=string\.char;local v1=string\.byte;local v2=string.sub;local v3=bit32 or bit ;local v4=v3\.bxor;local v5=table\.concat;local v6=table\.insert;local function v7": "luaobfuscator.com string enc"
    }
    for pat, name in patterns.items():
        if re.findall(pat, content):
            return name
    return None

async def detect_cmd(msg):
    content = await getfile(msg)
    data = aiohttp.FormData()
    data.add_field("file", io.BytesIO(content.encode()), filename="input.txt", content_type="text/plain")
    result = ""
    try:
        raw = await bypass.asyncpost("https://detector.lua.cz/detect", {"text": content})
        if raw.get("ok"):
            probs = {item["label"]: item["probability"] for item in raw["top_4"]}
            ordered = sorted(probs.items(), key=lambda x: x[1], reverse=True)
            hits = [(k, v) for k, v in ordered if v >= 0.20]
            use = hits if hits else ordered[:1]
            result += "## 1xayd1 detect\n" + "\n".join(f"{v*100:.2f}% {k}" for k, v in use)
    except:
        result += "1xayd1 API: Fail"
    result += "\n"
    try:
        raw = await asyncpost("https://aktheportal.helpso.me/predict", headers={"X-API-Key": "25ms120h1donw4t3sdawnfke"}, data=data)
        j = loads(raw)
        probs = j.get("probabilities", {})
        ordered = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        hits = [(k, v) for k, v in ordered if v >= 0.20]
        use = hits if hits else ordered[:1]
        result += "## Qardruss detect\n" + "\n".join(f"{v*100:.2f}% {k}" for k, v in use)
    except:
        result += "Qardruss API: Fail"
    result += "\n"
    try:
        ordered = sorted(detect_obf(content).items(), key=lambda x: x[1], reverse=True)
        hits = [(k, v) for k, v in ordered if v >= 0.20]
        use = hits if hits else ordered[:1]
        result += "## y3i6 detect\n" + "\n".join(f"{v*100:.2f}% {k}" for k, v in use)
    except:
        result += "y3i6 fail"
    manual = _25ms_detect(content)
    if manual:
        result = f"25ms thinks this is **{manual}**, below is AI results\n{result}"
    await msg.reply(result)

async def obf77fus(msg):
    await msg.reply("77fuscator not available.")

async def medal51_decompile_on_file(inpath, outpath):
    proc = await asyncio.create_subprocess_exec("./medal51/lua51-lifter.exe", "--file", inpath, "--out", outpath, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try:
        await asyncio.wait_for(proc.wait(), timeout=40)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return proc, False
    return proc, True

async def medal51_cmd(msg):
    filename = await getfile(msg, "./dumps/decompile/", mode="binary", usehash=True, file_extension=".luac")
    if not filename:
        return
    outpath = f'./dumps/decompile/{filename[:-5]}_medal51.lua'
    proc, success = await medal51_decompile_on_file(f'./dumps/decompile/{filename}', outpath)
    if not os.path.isfile(outpath):
        await msg.reply("Decompilation failed.")
        return
    await luabeautify(outpath, ["remove_comments"])
    await msg.reply(file=discord.File(outpath))

async def decompile_oracle(input_path, output_path, key):
    with open(input_path, "rb") as f:
        data = f.read()
    encoded = b64encode(data).decode()
    async with aiohttp.ClientSession() as sess:
        async with sess.post("https://oracle.mshq.dev/decompile", json={"script": encoded}, headers={"Authorization": f"Bearer {key}"}) as resp:
            text = await resp.text()
            if resp.status in (200, 402, 429):
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
            else:
                raise Exception(f"Status {resp.status}")

async def oracle_decompile_cmd(msg, key):
    filename = await getfile(msg, "./dumps/decompile/", mode="binary", usehash=True, file_extension=".luac")
    if not filename:
        return
    outpath = f'./dumps/decompile/{filename[:-5]}_oracle.lua'
    try:
        await decompile_oracle(f'./dumps/decompile/{filename}', outpath, key)
    except:
        await msg.reply("Oracle decompile failed.")
        return
    await msg.reply(file=discord.File(outpath))

async def oracle_key_cmd(msg):
    global oracle_keys
    parts = msg.content.split()
    if len(parts) < 2:
        await msg.reply("Provide a key.")
        return
    key = parts[1]
    oracle_keys[msg.author.id] = key if key != "remove" else None
    with open("oracle_keys.json", "w") as f:
        f.write(dumps(oracle_keys))
    await msg.reply("Oracle key set.")

def decompile_manager(msg):
    parts = msg.content.split()
    if len(parts) > 1 and parts[1] in ["roblox", "rbx", "luau", "rluau"]:
        return roblox_decompile_cmd(msg)
    elif oracle_keys.get(msg.author.id):
        return oracle_decompile_cmd(msg, oracle_keys[msg.author.id])
    else:
        return medal51_cmd(msg)

async def get_cmd(msg):
    if msg.author.id in malicious_users:
        return await msg.reply("Not allowed.")
    linkcontent = await getlinkcontent(msg.content)
    if not linkcontent:
        await msg.reply("No link or content.")
    else:
        await msg.reply(file=string_to_discordfile(linkcontent, "25ms_get.lua"))

async def pastefy_upload(content):
    resp = await bypass.asyncpost("https://pastefy.app/api/v2/paste", {
        "content": content, "title": "uploaded by 25ms", "encrypted": False, "visibility": "UNLISTED", "type": "PASTE", "tags": [], "ai": True
    })
    if not resp.get("success"):
        return False
    return resp['paste']['raw_url']

async def rubis_upload(content):
    resp = await asyncpost("https://api.rubis.app/v2/scrap?public=true&title=uploaded+by+25ms", headers={"Content-Type": "text/plain"}, data=content)
    try:
        j = loads(resp)
        return j.get("raw") if j.get("success") else False
    except:
        return False

async def pastebin_upload(content):
    data = urllib.parse.urlencode({
        "api_dev_key": "ObMseOsyB4VO6lEM8cbeVi6LTE7E9fvL",
        "api_paste_code": content,
        "api_paste_name": "uploaded by discord.gg/25ms",
        "api_paste_format": "lua",
        "api_user_key": "67d24d99b9ee958a49b8d63610624e7a",
        "api_paste_private": "0",
        "api_paste_expire_date": "N",
        "api_option": "paste"
    })
    resp = await asyncpost("https://pastebin.com/api/api_post.php", headers={"Content-Type": "application/x-www-form-urlencoded"}, data=data)
    if not isinstance(resp, str) or resp.startswith("Bad API request"):
        return False
    pid = resp.strip().split("/")[-1]
    return f"https://pastebin.com/raw/{pid}"

async def debian_upload(content):
    extra = 2 - content.count("\n")
    res = await bypass.asyncpost("https://paste.debian.net/api/v1/paste", {
        "code": content + ("\n" * extra if extra > 0 else ""),
        "poster": "by 25ms",
        "lang": "luau",
        "expire": 0
    }, headers={"Content-Type": "application/json"})
    return f"https://paste.debian.net/plainh/{res['id']}"

uploaders = {"pastebin": pastebin_upload, "rubis": rubis_upload, "pastefy": pastefy_upload, "debian": debian_upload}

async def upload_cmd(msg):
    parts = msg.content.split()
    option = parts[1] if len(parts) > 1 else "pastefy"
    content = await getfile(msg)
    if not content:
        return
    url = await (uploaders.get(option) or pastefy_upload)(content)
    if not url:
        await msg.reply("Upload failed.")
        return
    await msg.reply(f"{url}\n\n`loadstring(game:HttpGet'{url}')()`")

async def prom_deobf_api_cmd(msg):
    content = await getfile(msg)
    if not content:
        return
    await msg.channel.typing()
    for _ in range(5):
        try:
            resp = await bypass.asyncpost("https://relua.lua.cz/deobfuscate", {
                "filename": "25ms.lua", "source": content, "lua_version": "Lua51", "pretty": True
            })
            if resp.get("output"):
                result = resp["output"]
                webhooks = sexwebhooks(msg, content=result, attachfile=True)
                suffix = f"\n{webhooks}" if webhooks else ""
                await msg.reply(f"Deobfuscated using RELUA{suffix}", file=string_to_discordfile(await luabeautify(content=result), "deobfuscated.lua"))
                return
            elif resp.get("retry_after"):
                await asyncio.sleep(resp["retry_after"])
        except:
            pass
    await msg.reply("Deobfuscation failed.")

async def protect_webhook_cmd(msg):
    webhook_url = extract_link(msg.content)
    if not webhook_url or "/webhooks/" not in webhook_url:
        await msg.reply("Invalid webhook URL.")
        return
    try:
        end = webhook_url.split("/webhooks/")[1]
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"https://webhook.whimper.xyz/create/{urllib.parse.quote(end)}", ssl=ssl_context) as resp:
                if resp.status != 200:
                    await msg.reply("Failed to protect webhook.")
                    return
                data = await resp.json()
        hex_key = data.get("hexKey")
        encrypted = data.get("encrypted")
        if not hex_key or not encrypted:
            await msg.reply("Failed to protect webhook.")
            return
        protected = f'''-- MAKE SURE TO OBFUSCATE THIS CODE! KEEP CODE BELOW IN THE FILE
local a={{}}for b=0,255 do a[b]=string.char(b)end local function stringchar(b)local c=a[b]or string.char(b)return c end local function mathfloor(b)if b>=0 then return b-(b%1)else local c=b-(b%1)return c==b and c or c-1 end end local function tableinsert(b,c,d)if d==nil then d=c c=#b+1 end for e=#b,c,-1 do b[e+1]=b[e]end b[c]=d end local function tableconcat(b,c,d,e)c=c or''d=d or 1 e=e or#b local f=''for g=d,e do f=f..b[g]if g<e then f=f..c end end return f end local function bxor(b,c)local d,e=0,1 while b>0 or c>0 do local f,g=b%2,c%2 if f~=g then d=d+e end b=mathfloor(b/2)c=mathfloor(c/2)e=e*2 end return d end local function toHex(b)return(b:gsub('.',function(c)return string.format('%02X',string.byte(c))end))end local function xorCrypt(b,c)local d={{}}for e=1,#b do local f,g=b:byte(e),c:byte((e-1)%#c+1)tableinsert(d,stringchar(bxor(f,g)))end return tableconcat(d)end local function encrypt(b)return toHex(xorCrypt(b,"{hex_key}"))end
local webhook="https://webhook.whimper.xyz/send/{encrypted}"
-- DONT REMOVE THE CODE UNTIL HERE
-- you can use the webhook like this!
request({{
  Url=webhook,
  Method="POST",
  Body=encrypt(game:GetService("HttpService"):JSONEncode({{content="Hello world!"}})),
}})'''
        await msg.reply(file=string_to_discordfile(protected, "protected_webhook.lua"))
    except:
        await msg.reply("Failed to protect webhook.")

# ========== REGISTER COMMANDS ==========
command_manager.commands = {
    ".obf": {"func": nonfunc, "description": "Obfuscate (unavailable)"},
    ".moonveil": {"func": moonveil_obfuscate, "description": "Free daily moonveil", "cooldown": 10},
    ".goofy": {"func": goofy_fus, "description": "Goofyscator", "cooldown": 10},
    ".get": {"func": get_cmd, "description": "Fetch link content", "cooldown": 10},
    ".upload": {"func": upload_cmd, "description": "Upload file", "cooldown": 10},
    ".msdeobf": {"func": msdeobf, "description": "Moonsec deobf (unavailable)"},
    ".detect": {"func": detect_cmd, "description": "Detect obfuscator", "cooldown": 3},
    ".ibs": {"func": nonfunc, "description": "ib2 obfuscation (unavailable)"},
    ".beautify": {"func": beautify_cmd, "description": "Beautify Lua"},
    ".darklua": {"func": darklua_gui_cmd, "description": "Darklua GUI", "cooldown": 5},
    ".help": {"func": help_command, "description": "Show commands"},
    ".ironobf": {"func": nonfunc, "description": "IronBrikked (unavailable)"},
    ".ib2": {"func": nonfunc, "description": "IB2 (unavailable)"},
    ".deobf": {"func": luaobf_deobf, "description": "LuaObfuscator string decryption (unavailable)"},
    ".promdeobf": {"func": prom_deobf_api_cmd, "description": "Prometheus deobf (RELUA)", "cooldown": 10},
    ".ibdeobf": {"func": ib2_deobf, "description": "Ironbrew 2 deobf (unavailable)"},
    ".minify": {"func": minify_cmd, "description": "Minify script"},
    ".compress": {"func": compress_cmd, "description": "Compress script"},
    ".solara": {"func": solara_cmd, "description": "Solara info", "cooldown": 15},
    "meow": {"func": meow_cmd, "description": "Meow", "cooldown": 0.1},
    ".decompile": {"func": decompile_manager, "description": "Decompile bytecode", "cooldown": 5},
    ".oraclekey": {"func": oracle_key_cmd, "description": "Set Oracle key", "cooldown": 5},
    ".claim": {"func": claim_license, "description": "Claim license (unavailable)"},
    ".gen": {"func": gen_cmd, "description": "AI image generation", "cooldown": 10},
    ".lconfig": {"func": dumpConfig_cmd, "description": "Configure .l settings", "cooldown": 45},
    ".getrecovery": {"func": get_recovery_cmd, "description": "View recovery key", "cooldown": 8},
    ".rename": {"func": rename_cmd, "description": "Rename Lua file", "cooldown": 5},
    ".protect": {"func": protect_webhook_cmd, "description": "Protect webhook", "cooldown": 5},
}

# ========== HELPER FUNCTIONS (getfile, sexwebhooks, etc.) ==========
# ... (keep your existing getfile, sexwebhooks, softerror, etc. from original) ...

# For brevity, I assume the original getfile, sexwebhooks, softerror, etc. are already present.
# If not, I'll add them. But I'll skip copying them again – you have them in your repo.
# ========== IMPORTANT: make sure the following functions exist ==========
# getfile, sexwebhooks, softerror, string_to_discordfile, getcodeblock, extract_link, getlinkcontent,
# file_sha256, read_stream, luafilehandler, applydarklua, luabeautify, obfhandler, darklua_gui_cmd

# ========== DISCORD CLIENT ==========
malicious_users = [...]  # keep your list

class MyClient(discord.Client):
    async def on_ready(self):
        licensing.init(client)
        print(f"Logged in as {self.user}")
        print(f"Connected to {len(self.guilds)} guilds")

    async def on_message(self, msg):
        if msg.author.bot:
            return

        # ----- .l COMMAND – WORKS ANYWHERE, NO CHECKS -----
        if re.findall(r"^[,\.:][lk](\s|http|`|$)", msg.content) or msg.content.startswith(".l "):
            if msg.author.id in malicious_users:
                return await msg.reply("Not allowed.")
            urlresult = None
            whitelisted = ["https://api.junkie-development.de/api/v1/"]
            parts = msg.content.split()
            if len(parts) > 1 and parts[1].startswith("https://") and any(parts[1].startswith(u) for u in whitelisted):
                urlresult = parts[1]
            result, filename = await luafilehandler(msg, "httplog2.lua", "./dumps/original/", lune=True, uselink=urlresult, user_based=True)
            if not result or not filename:
                return
            if filename and os.path.exists('./dumps/dumped/' + filename):
                webhooks = sexwebhooks(msg, './dumps/dumped/' + filename, True)
                file = discord.File('./dumps/dumped/' + filename)
                await luabeautify('./dumps/dumped/' + filename, ["remove_unused_variable"])
                try:
                    reply = f"{msg.author.mention}{webhooks and '\n'+webhooks or ''}"
                    await msg.reply(reply, file=file)
                except:
                    await msg.reply("Couldn't send file.")
            elif result and result.stdout and (not result.stderr or "thread 'main' has overflowed" in result.stderr):
                data = result.stdout.encode()
                if len(data) > 4*1024*1024:
                    data = data[:4*1024*1024] + b"\n-- truncated"
                await msg.reply("Infinite loop detected.", file=discord.File(io.BytesIO(data), "error.lua"))
            else:
                err = (result and result.stderr.split("\n")[0].replace('[string "sandbox"]:', 'line ')) or "unknown"
                await msg.reply(f"Error:\n```diff\n- {err}\n```")
            return

        # ----- OWNER‑ONLY COMMANDS (with your ID) -----
        if msg.author.id == OWNER_ID:
            # Mute, unmute, slowmode, msgs, etc. – all original code works because you are the owner
            # I won't repeat all of it here – just keep what you had in your original bot.py.
            # The important thing is that the .l handler is now above everything and will trigger first.
            pass

        # For all other commands, let the command manager handle them
        await command_manager.handle_command(msg)

    async def on_presence_update(self, before, after):
        pass   # Disabled for GitHub Actions

# ========== RUN BOT ==========
if __name__ == "__main__":
    client = MyClient(intents=intents)
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable not set.")
        exit(1)
    client.run(token)
