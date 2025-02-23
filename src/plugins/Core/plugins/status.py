from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot import get_app
from nonebot.params import CommandArg
from nonebot import on_command
from nonebot.exception import FinishedException
import psutil
from . import _error
from . import _lang
import traceback
import json
import getpass
import time
import socket
import platform

status = on_command("status", aliases={"系统状态", "状态"})
ctrlGroup = json.load(open("data/ctrl.json", encoding="utf-8"))["control"]


@get_app().get("/status")
async def get_status_from_web():
    return {"status": "OK"}


def cpu_percent():
    return psutil.cpu_percent()


def cpu_freq():
    return f"{round(psutil.cpu_freq().current/1000,2)}GHz"


def cpu_count():
    return psutil.cpu_count()


def mem_used():
    return round(psutil.virtual_memory().used / 1024 / 1024 / 1024, 1)


def mem_total():
    return round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 1)


def mem_percent():
    return psutil.virtual_memory().percent


def swap_used():
    return round(psutil.swap_memory().used / 1024 / 1024 / 1024, 1)


def swap_total():
    return round(psutil.swap_memory().total / 1024 / 1024 / 1024, 1)


def swap_percent():
    return psutil.swap_memory().percent


def format_time(seconds):
    d = int(seconds / 86400)
    h = int(seconds / 3600) % 24
    m = int(seconds / 60) % 60
    s = seconds % 60
    return f"{d}d {h}:{m}:{s}"


def uptime():
    try:
        seconds = int(
            float(
                open(
                    "/proc/uptime",
                    encoding="utf-8").read().split(" ")[0]))
    except BaseException:
        return "Unknown"
    return format_time(seconds)


def datetime():
    return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())


def user():
    return getpass.getuser()


def hostname():
    return socket.gethostname()


def osData():
    return platform.platform()


def pyver():
    return platform.python_version()


@status.handle()
async def statusHandle(bot: Bot, event: MessageEvent, message: Message = CommandArg()):
    try:
        initData = json.load(open("data/init.json", encoding="utf-8"))
        argument = message.extract_plain_text()
        if argument == "":
            await status.finish(
                f"""{_lang.text("status.title",[],event.get_user_id())}
{_lang.text("status.cpu",[],event.get_user_id())}{cpu_percent()}% {cpu_freq()}
{_lang.text("status.ram",[],event.get_user_id())}{mem_used()}GiB / {mem_total()}GiB ({mem_percent()}%)
{_lang.text("status.swap",[],event.get_user_id())}{swap_used()}GiB / {swap_total()}GiB
{_lang.text("status.run",[],event.get_user_id())}{format_time(int(time.time() - initData['time']))}
{_lang.text("status.boot",[],event.get_user_id())}{uptime()}
{_lang.text("status.py",[],event.get_user_id())}{pyver()}"""
            )
        elif argument == "cpu":
            await status.finish(
                f"{_lang.text('status.cpu',[],event.get_user_id())}{cpu_percent()}%（{cpu_freq()} x{cpu_count()}）"
            )
        elif argument in ["mem", "内存"]:
            bar = ""
            for _ in range(int(mem_percent() / 10)):
                bar += "="
            for _ in range(10 - int(mem_percent() / 10)):
                bar += "  "
            await status.finish(
                f"{_lang.text('status.ram',[],event.get_user_id())}{mem_used()}GiB / {mem_total()}GiB ({mem_percent()}%) [{bar}]"
            )
        elif argument in ["swap", "交换内存"]:
            await status.finish(
                f"{_lang.text('status.swap',[],event.get_user_id())}{swap_used()}GiB / {swap_total()}GiB ({swap_percent()}%)"
            )
        elif argument in ["system", "系统"]:
            await status.finish(osData())
        elif argument in ["host"]:
            await status.finish(f"{user()}@{hostname()}")
        else:
            await status.finish(
                _lang.text("status.error", [argument], event.get_user_id())
            )

    except FinishedException:
        raise FinishedException()
    except Exception:
        await _error.report(traceback.format_exc())


# [HELPSTART] Version: 2
# Command: status
# Info: 查询 XDbot2 后端运行状态
# Msg: 系统状态
# Usage: status：查看状态概述
# Usage: status <cpu/mem/swap/system/host>：查看详细状态
# [HELPEND]
