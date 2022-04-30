"""私聊转发"""
from botoy import Action, GroupMsg, FriendMsg, decorators, jconfig
from botoy.contrib import plugin_receiver, download, file_to_base64
from botoy.decorators import ignore_botself, startswith
from botoy.parser import group as gp  # 群消息(GroupMsg)相关解析
import re, time, demjson

from .config import *

action = Action(qq=jconfig.qq)


@ignore_botself  # 忽略机器人自身的消息
def receive_friend_msg(ctx: FriendMsg):
    # 判断是否是管理员
    boss_i = 0
    for i in set_boss_uin(pattern="2"):
        if str(ctx.FromUin) == i:
            boss_i = 1
            break
    if boss_i == 1:
        cont = ctx.Content
        # 总开关设置与查看
        if cont == "打开监控转发":
            action.sendFriendText(user=ctx.FromUin, content=set_switch(bot_dict, text="1"))
        elif cont == "关闭监控转发":
            action.sendFriendText(user=ctx.FromUin, content=set_switch(bot_dict, text="0"))
        elif cont == "监控转发状态" or cont == "查看监控转发":
            action.sendFriendText(user=ctx.FromUin, content=format_json_data(bot_dict))
        # 设置与查看管理员UIN
        elif cont.startswith("添加监控转发管理员"):
            boss_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_boss_uin(bot_dict, uin=boss_uin_pattern, pattern="0"))
        elif cont.startswith("删除监控转发管理员"):
            boss_uin_pattern = cont[9:]
            if len(set_boss_uin(pattern="2")) > 1:
                action.sendFriendText(user=ctx.FromUin,content=set_boss_uin(bot_dict, uin=boss_uin_pattern, pattern="1"))
            else:
                action.sendFriendText(user=ctx.FromUin,
                                      content="删除失败\n仅剩一位管理员，如果需要删除请手动删除\n管理员UIN列表：" + str(set_boss_uin(pattern="2")))
        elif cont == "监控转发管理员查看" or cont == "查看监控转发管理员":
            action.sendFriendText(user=ctx.FromUin, content=set_boss_uin(bot_dict, pattern="2"))
        # 设置私聊监听模式
        elif cont.startswith("设置私聊监听模式"):
            friend_type_pattern = cont[8:].replace("全部监听", "-1").replace("全部", "-1").replace("关键词监听", "0").replace(
                "关键词", "0").replace("UIN监听", "1").replace("uin监听", "1").replace("UIN", "1").replace("uin", "1")
            if is_number(friend_type_pattern) and len(friend_type_pattern) <= 2:
                action.sendFriendText(user=ctx.FromUin, content=set_friend_type(bot_dict, pattern=friend_type_pattern))
            else:
                action.sendFriendText(user=ctx.FromUin, content="设置私聊监听模式失败\n私聊监听模式只有：全部监听、关键词监听、UIN监听 三种模式")
        # 查看私聊监听模式
        elif cont == "私聊监听模式状态" or cont == "查看私聊监听模式":
            friend_key_pattern = "私聊监听模式：关键词监听\n关键词列表：" + str(friend_key)
            friend_uin_pattern = "私聊监听模式：UIN监听\nUIN列表：" + str(friend_uin)
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_friend_type(bot_dict, pattern="2").replace("-1", "私聊监听模式：全部监听").replace(
                                      "0",
                                      friend_key_pattern).replace(
                                      "1", friend_uin_pattern))
        # 设置与查看私聊监听关键词列表
        elif cont.startswith("添加私聊监听关键词"):
            friend_key_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_friend_key(key=friend_key_pattern, pattern="0"))
        elif cont.startswith("删除私聊监听关键词"):
            friend_key_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_friend_key(key=friend_key_pattern, pattern="1"))
        elif cont == "私聊监听关键词查看" or cont == "查看私聊监听关键词":
            action.sendFriendText(user=ctx.FromUin, content=set_friend_key(pattern="2"))
        # 设置与查看私聊监听UIN列表
        elif cont.startswith("添加私聊监听UIN") or cont.startswith("添加私聊监听uin"):
            friend_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_friend_uin(uin=friend_uin_pattern, pattern="0"))
        elif cont.startswith("删除私聊监听UIN") or cont.startswith("删除私聊监听uin"):
            friend_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_friend_uin(uin=friend_uin_pattern, pattern="1"))
        elif cont == "私聊监听UIN查看" or cont == "查看私聊监听UIN" or cont == "私聊监听uin查看" or cont == "查看私聊监听uin":
            action.sendFriendText(user=ctx.FromUin, content=set_friend_uin(pattern="2"))
        # 设置群聊监听模式
        elif cont.startswith("设置群聊监听模式"):
            group_type_pattern = cont[8:].replace("全部监听", "-1").replace("全部", "-1").replace("关键词监听", "0").replace("关键词",
                                                                                                                  "0").replace(
                "UIN监听", "1").replace("uin监听", "1").replace("UIN", "1").replace("uin", "1").replace("关闭", "2")
            if is_number(group_type_pattern) and len(group_type_pattern) <= 2:
                action.sendFriendText(user=ctx.FromUin, content=set_group_type(bot_dict, pattern=group_type_pattern))
            else:
                action.sendFriendText(user=ctx.FromUin, content="设置群聊监听模式失败\n群聊监听模式只有：全部监听、关键词监听、UIN监听、关闭 四种模式")
        # 查看群聊监听模式
        elif cont == "群聊监听模式状态" or cont == "查看群聊监听模式":
            group_key_pattern = "群聊监听模式：关键词监听\n关键词列表：" + str(group_key)
            group_uin_pattern = "群聊监听模式：UIN监听\nUIN列表：" + str(group_uin)
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_group_type(bot_dict, pattern="3").replace("-1", "群聊监听模式：全部监听").replace(
                                      "0",
                                      group_key_pattern).replace(
                                      "1", group_uin_pattern).replace("2", "群聊监听模式：关闭"))
        # 设置与查看群聊监听关键词列表
        elif cont.startswith("添加群聊监听关键词"):
            group_key_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_group_key(key=group_key_pattern, pattern="0"))
        elif cont.startswith("删除群聊监听关键词"):
            group_key_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_group_key(key=group_key_pattern, pattern="1"))
        elif cont == "群聊监听关键词查看" or cont == "查看群聊监听关键词":
            action.sendFriendText(user=ctx.FromUin, content=set_group_key(pattern="2"))
        # 设置与查看群聊监听UIN列表
        elif cont.startswith("添加群聊监听UIN") or cont.startswith("添加群聊监听uin"):
            group_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_group_uin(uin=group_uin_pattern, pattern="0"))
        elif cont.startswith("删除群聊监听UIN") or cont.startswith("删除群聊监听uin"):
            group_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_group_uin(uin=group_uin_pattern, pattern="1"))
        elif cont == "群聊监听UIN查看" or cont == "查看群聊监听UIN" or cont == "群聊监听uin查看" or cont == "查看群聊监听uin":
            action.sendFriendText(user=ctx.FromUin, content=set_group_uin(pattern="2"))
        # 设置转发模式
        elif cont.startswith("设置转发模式"):
            relay_type_pattern = cont[6:].replace("全部转发", "-1").replace("全部", "-1").replace("群聊UIN转发", "0").replace(
                "群聊uin转发", "0").replace("群聊", "0").replace("私聊UIN转发", "1").replace("私聊uin转发", "1").replace("私聊", "1")
            if is_number(relay_type_pattern) and len(relay_type_pattern) <= 2:
                action.sendFriendText(user=ctx.FromUin, content=set_relay_type(bot_dict, pattern=relay_type_pattern))
            else:
                action.sendFriendText(user=ctx.FromUin, content="设置转发模式失败\n转发模式只有：全部转发、私聊UIN转发、群聊UIN转发 三种模式")
        # 查看转发模式
        elif cont == "转发模式状态" or cont == "查看转发模式":
            relay_all_uin_pattern = "转发模式：全部转发\n私聊UIN列表：" + str(set_relay_friend_uin(pattern="2")) + "\n群聊UIN列表：" + str(
                relay_group_uin)
            relay_friend_uin_pattern = "转发模式：私聊UIN转发\n私聊UIN列表：" + str(set_relay_friend_uin(pattern="2"))
            relay_group_uin_pattern = "转发模式：群聊UIN转发\n群聊UIN列表：" + str(relay_group_uin)
            relay_type_i = set_relay_type(bot_dict, pattern="2")
            if relay_type_i == "-1":
                action.sendFriendText(user=ctx.FromUin, content=relay_all_uin_pattern)
            elif relay_type_i == "0":
                action.sendFriendText(user=ctx.FromUin, content=relay_group_uin_pattern)
            else:
                action.sendFriendText(user=ctx.FromUin, content=relay_friend_uin_pattern)
        # 设置与查看转发私聊UIN列表
        elif cont.startswith("添加转发私聊UIN") or cont.startswith("添加转发私聊uin"):
            relay_friend_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_relay_friend_uin(bot_dict, uin=relay_friend_uin_pattern, pattern="0"))
        elif cont.startswith("删除转发私聊UIN") or cont.startswith("删除转发私聊uin"):
            relay_friend_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_relay_friend_uin(bot_dict, uin=relay_friend_uin_pattern, pattern="1"))
        elif cont == "转发私聊UIN查看" or cont == "查看转发私聊UIN" or cont == "转发私聊uin查看" or cont == "查看转发私聊uin":
            action.sendFriendText(user=ctx.FromUin, content=set_relay_friend_uin(bot_dict, pattern="2"))
        # 设置与查看转发群聊UIN列表
        elif cont.startswith("添加转发群聊UIN") or cont.startswith("添加转发群聊uin"):
            relay_group_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_relay_group_uin(uin=relay_group_uin_pattern, pattern="0"))
        elif cont.startswith("删除转发群聊UIN") or cont.startswith("删除转发群聊uin"):
            relay_group_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_relay_group_uin(uin=relay_group_uin_pattern, pattern="1"))
        elif cont == "转发群聊UIN查看" or cont == "查看转发群聊UIN" or cont == "转发私聊uin查看" or cont == "查看转发私聊uin":
            action.sendFriendText(user=ctx.FromUin, content=set_relay_group_uin(pattern="2"))
        # 设置与查看转发文本限制长度
        elif cont.startswith("设置转发文本限制最长长度"):
            relay_length_text = cont[12:].replace("无限制", "-1")
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_relay_length_max(bot_dict, length=int(relay_length_text)))
        elif cont.startswith("设置转发文本限制最短长度"):
            relay_length_text = cont[12:].replace("无限制", "-1")
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_relay_length_min(bot_dict, length=int(relay_length_text)))
        elif cont == "转发文本限制长度查看" or cont == "查看转发文本限制长度":
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_relay_length_min(bot_dict, length=-2) + "\n" + set_relay_length_max(
                                      bot_dict, length=-2))
        # 设置与查看转发私聊UIN黑名单列表
        elif cont.startswith("添加黑名单转发私聊UIN") or cont.startswith("添加黑名单转发私聊uin"):
            blacklist_friend_uin_pattern = cont.replace("添加黑名单转发私聊UIN", "").replace("添加黑名单转发私聊uin", "")
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_friend_uin(bot_dict, uin=blacklist_friend_uin_pattern,
                                                                   pattern="0"))
        elif cont.startswith("删除黑名单转发私聊UIN") or cont.startswith("删除黑名单转发私聊uin"):
            blacklist_friend_uin_pattern = cont.replace("删除黑名单转发私聊UIN", "").replace("删除黑名单转发私聊uin", "")
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_friend_uin(bot_dict, uin=blacklist_friend_uin_pattern,
                                                                   pattern="1"))
        elif cont == "转发私聊UIN黑名单查看" or cont == "查看转发私聊UIN黑名单" or cont == "转发私聊uin黑名单查看" or cont == "查看转发私聊uin黑名单":
            action.sendFriendText(user=ctx.FromUin, content=set_blacklist_friend_uin(bot_dict, pattern="2"))
        # 设置与查看转发群聊UIN黑名单列表
        elif cont.startswith("添加黑名单转发群聊UIN") or cont.startswith("添加黑名单转发群聊uin"):
            blacklist_group_uin_pattern = cont.replace("添加黑名单转发群聊UIN", "").replace("添加黑名单转发群聊uin", "")
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_group_uin(uin=blacklist_group_uin_pattern, pattern="0"))
        elif cont.startswith("删除黑名单转发群聊UIN") or cont.startswith("删除黑名单转发群聊uin"):
            blacklist_group_uin_pattern = cont.replace("删除黑名单转发群聊UIN", "").replace("删除黑名单转发群聊uin", "")
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_group_uin(uin=blacklist_group_uin_pattern, pattern="1"))
        elif cont == "转发群聊UIN黑名单查看" or cont == "查看转发群聊UIN黑名单" or cont == "转发群聊uin黑名单查看" or cont == "查看转发群聊uin黑名单":
            action.sendFriendText(user=ctx.FromUin, content=set_blacklist_group_uin(pattern="2"))
        # 设置与查看转发私聊关键词黑名单列表
        elif cont.startswith("添加转发私聊关键词黑名单"):
            blacklist_friend_key_pattern = cont[12:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_friend_key(bot_dict, key=blacklist_friend_key_pattern,
                                                                   pattern="0"))
        elif cont.startswith("删除转发私聊关键词黑名单"):
            blacklist_friend_key_pattern = cont[12:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_friend_key(bot_dict, key=blacklist_friend_key_pattern,
                                                                   pattern="1"))
        elif cont == "转发私聊关键词黑名单查看" or cont == "查看转发私聊关键词黑名单":
            action.sendFriendText(user=ctx.FromUin, content=set_blacklist_friend_key(bot_dict, pattern="2"))
        # 设置与查看转发群聊关键词黑名单列表
        elif cont.startswith("添加转发群聊关键词黑名单"):
            blacklist_group_key_pattern = cont[12:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_group_key(key=blacklist_group_key_pattern, pattern="0"))
        elif cont.startswith("删除转发群聊关键词黑名单"):
            blacklist_group_key_pattern = cont[12:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_group_key(key=blacklist_group_key_pattern, pattern="1"))
        elif cont == "转发群聊关键词黑名单查看" or cont == "查看转发群聊关键词黑名单":
            action.sendFriendText(user=ctx.FromUin, content=set_blacklist_group_key(pattern="2"))
        # 设置回复模式
        elif cont.startswith("设置回复模式"):
            reply_type_pattern = cont[6:].replace("关闭", "0").replace("关", "0").replace("开启", "1").replace("开", "1")
            if is_number(reply_type_pattern) and len(reply_type_pattern) <= 2:
                action.sendFriendText(user=ctx.FromUin, content=set_reply_type(pattern=reply_type_pattern))
            else:
                action.sendFriendText(user=ctx.FromUin, content="设置回复模式失败\n回复模式只有：开启、关闭 两种情况")
        # 查看回复模式
        elif cont == "回复模式状态" or cont == "查看回复模式":
            reply_type_on_pattern = "当上一条消息为转发消息时，默认需要回复的UIN与上条消息相同：开启"
            reply_type_off_pattern = "当上一条消息为转发消息时，默认需要回复的UIN与上条消息相同：关闭"
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_reply_type(pattern="2").replace("0", reply_type_off_pattern).replace(
                                      "1", reply_type_on_pattern))
        # 帮助菜单
        elif cont == "监控转发菜单" or cont == "监控转发帮助":
            action.sendFriendPic(ctx.FromUin, picBase64Buf=file_to_base64('./plugins/bot_MessageForwarding/help2.png'))
        # 回复消息
        elif ctx.MsgType == "ReplayMsg":
            # 判断是否是管理员
            boss_i = 0
            for i in set_boss_uin(pattern="2"):
                if str(ctx.FromUin) == i:
                    boss_i = 1
                    break
            if boss_i != 1:  # 如果为boss
                return
            reply_Pic = ""
            Pic_Md5 = ""
            data_text = demjson.decode(ctx.Content)
            SrcContent_text = data_text['SrcContent']  # 回复的消息的内容
            try:
                reply_Pic = data_text['FriendPic'][0]['Url']  # 实际需要回复的内容
                download(url=reply_Pic, dist='./plugins/bot_MessageForwarding/1.png')
                Pic_Md5 = file_to_base64('./plugins/bot_MessageForwarding/1.png')  # 图片Md5
                try:
                    reply_text = data_text['Content']  # 实际需要回复的内容
                except Exception as e:
                    reply_text = ""  # 没有需要回复的内容
            except Exception as e:  # 没有需要回复的图像
                reply_text = data_text['Content']  # 实际需要回复的内容
            Uin = get_ReplyUin(SrcContent_text, reply_text)  # 获取回复人UIN
            # 用于判断是否为图文消息时候手动指定回复人
            if len(re.findall("(\(.*\))", reply_text)) > 0:  # 真
                if reply_Pic == "":  # 没有图片时
                    action.sendFriendText(Uin, reply_text.replace(re.findall("(\(.*\))", reply_text)[0], ""))
                else:
                    try:
                        # 文本和图片同时存在
                        action.sendFriendPic(user=Uin, picBase64Buf=Pic_Md5,
                                             content=reply_text.replace(re.findall("(\(.*\))", reply_text)[0], ""))
                    except Exception as e:
                        # 仅为图片
                        action.sendFriendPic(user=Uin, picBase64Buf=Pic_Md5)
            else:
                if reply_Pic == "":  # 没有图片时
                    action.sendFriendText(Uin, reply_text)
                else:
                    try:
                        # 文本和图片同时存在
                        action.sendFriendPic(user=Uin, picBase64Buf=Pic_Md5, content=reply_text)
                    except Exception as e:
                        # 仅为图片
                        action.sendFriendPic(user=Uin, picBase64Buf=Pic_Md5)
        else:
            return
    else:
        if set_switch(text="2") == "1":  # 转发功能打开时
            friend_type = set_friend_type(pattern="2")
            Uin = str(ctx.FromUin)  # 获取回复人UIN
            for i in set_blacklist_friend_uin(pattern="2"):  # 判断是否私聊uin黑名单
                if i == Uin:
                    return

            cont = ctx.Content
            for i in set_blacklist_friend_key(pattern="2"):  # 判断是否私聊关键词黑名单
                if cont.find(i) != -1:
                    return
            if friend_type == "-1":  # 私聊监听模式：全部监听
                time_text = time.strftime("%Y/%m/%d %H:%M:%S")  # 获取消息时间
                if ctx.MsgType == "TextMsg":  # 当为文本消息时
                    if set_relay_length_max(length=-2) != -1:  # 判断是否超出字数
                        if len(cont) > int(set_relay_length_max(length=-2)):
                            return
                    if set_relay_length_min(length=-2) != -1:  # 判断是否小于字数
                        if len(cont) < int(set_relay_length_min(length=-2)):
                            return
                    if set_relay_type(pattern="2") == "-1":
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendText(int(i), "(" + Uin + ") " + get_name(
                                Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont + "”")
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i), "(" + Uin + ") " + get_name(
                                Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont + "”")
                        return
                    elif set_relay_type(pattern="2") == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i), "(" + Uin + ") " + get_name(
                                Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont + "”")
                        return
                    else:
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendText(int(i), "(" + Uin + ") " + get_name(
                                Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont + "”")
                        return
                elif ctx.MsgType == "PicMsg":  # 当为图文消息时
                    data_text = demjson.decode(ctx.Content)  # 回复的消息的内容
                    if str(data_text).find("[闪照]") != -1:
                        picUrl_text = data_text['Url']  # 图片url
                    else:
                        FriendPic_text = data_text['FriendPic'][0]
                        picUrl_text = FriendPic_text['Url']  # 图片url
                    try:
                        download(url=picUrl_text, dist='./plugins/bot_MessageForwarding/1.png')
                        Pic_Md5 = file_to_base64('./plugins/bot_MessageForwarding/1.png')  # 图片Md5
                        # 文本和图片同时存在
                        cont_text = data_text['Content']
                        if set_relay_length_max(length=-2) != -1:  # 判断是否超出字数
                            if len(cont_text) > int(set_relay_length_max(length=-2)):
                                return
                        if set_relay_type(pattern="2") == "-1":
                            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                        elif set_relay_type(pattern="2") == "0":
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                        else:
                            print("哈哈哈哈")
                            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                    except Exception as e:
                        # 仅为图片
                        if set_relay_type(pattern="2") == "-1":
                            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊")
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                        elif set_relay_type(pattern="2") == "0":
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                        else:
                            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                elif ctx.MsgType == "VoiceMsg":
                    data_text = demjson.decode(ctx.Content)  # 回复的消息的内容
                    voiceUrl_text = data_text['Url']
                    if set_relay_type(pattern="2") == "-1":
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendText(int(i),
                                                  "收到一条私聊语音(请在手机上查看)\n来自：" + get_name(
                                                      Uin) + "(" + Uin + ") " + "\n" + time_text)
                            action.sendFriendVoice(user=int(i), voiceUrl=voiceUrl_text)
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i),
                                                 "收到一条私聊语音(请在手机上查看)\n来自：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                            action.sendgroupVoice(group=int(i), voiceUrl=voiceUrl_text)
                        return
                    elif set_relay_type(pattern="2") == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i),
                                                 "收到一条私聊语音(请在手机上查看)\n来自：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                            action.sendgroupVoice(group=int(i), voiceUrl=voiceUrl_text)
                        return
                    else:
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendText(int(i),
                                                  "收到一条私聊语音(请在手机上查看)\n来自：" + get_name(
                                                      Uin) + "(" + Uin + ") " + "\n" + time_text)
                            action.sendFriendVoice(user=int(i), voiceUrl=voiceUrl_text)
                        return
            # 私聊监听模式：关键词监听
            elif friend_type == "0":
                if len(friend_key) < 1:  # 没有关键词时
                    return
                for i in friend_key:  # 判断是否需要转发消息
                    if cont.find(i) == -1:
                        return
                time_text = time.strftime("%Y/%m/%d %H:%M:%S")  # 获取消息时间
                if ctx.MsgType == "TextMsg":  # 当为文本消息时
                    if set_relay_length_max(length=-2) != -1:  # 判断是否超出字数
                        if len(cont) > int(set_relay_length_max(length=-2)):
                            return
                    if set_relay_length_min(length=-2) != -1:  # 判断是否小于字数
                        if len(cont) < int(set_relay_length_min(length=-2)):
                            return
                    if set_relay_type(pattern="2") == "-1":
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        return
                    elif set_relay_type(pattern="2") == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        return
                    else:
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        return
                elif ctx.MsgType == "PicMsg":  # 当为图文消息时
                    data_text = demjson.decode(ctx.Content)  # 回复的消息的内容
                    if str(data_text).find("[闪照]") != -1:
                        picUrl_text = data_text['Url']  # 图片url
                    else:
                        FriendPic_text = data_text['FriendPic'][0]
                        picUrl_text = FriendPic_text['Url']  # 图片url
                    try:
                        download(url=picUrl_text, dist='./plugins/bot_MessageForwarding/1.png')
                        Pic_Md5 = file_to_base64('./plugins/bot_MessageForwarding/1.png')  # 图片Md5
                        # 文本和图片同时存在
                        cont_text = data_text['Content']
                        if set_relay_length_max(length=-2) != -1:  # 判断是否超出字数
                            if len(cont_text) > int(set_relay_length_max(length=-2)):
                                return
                        if set_relay_type(pattern="2") == "-1":
                            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                        elif set_relay_type(pattern="2") == "0":
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                        else:
                            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                    except Exception as e:
                        # 仅为图片
                        if set_relay_type(pattern="2") == "-1":
                            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊")
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                        elif set_relay_type(pattern="2") == "0":
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                        else:
                            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
            # 私聊监听模式：UIN监听
            elif friend_type == "1":
                if len(friend_uin) < 1:  # 没有UIN时
                    return
                    # 判断UIN是否存在在监听UIN列表中
                friend_uin_i = 0
                for i in friend_uin:  # 判断是否需要转发消息
                    if Uin == i:
                        friend_uin_i = 1
                        continue
                if friend_uin_i == 0:
                    return

                time_text = time.strftime("%Y/%m/%d %H:%M:%S")  # 获取消息时间
                if ctx.MsgType == "TextMsg":  # 当为文本消息时
                    if set_relay_length_max(length=-2) != -1:  # 判断是否超出字数
                        if len(cont) > int(set_relay_length_max(length=-2)):
                            return
                    if set_relay_length_min(length=-2) != -1:  # 判断是否小于字数
                        if len(cont) < int(set_relay_length_min(length=-2)):
                            return
                    if set_relay_type(pattern="2") == "-1":
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        return
                    elif set_relay_type(pattern="2") == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        return
                    else:
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        return
                elif ctx.MsgType == "PicMsg":  # 当为图文消息时
                    data_text = demjson.decode(ctx.Content)  # 回复的消息的内容
                    if str(data_text).find("[闪照]") != -1:
                        picUrl_text = data_text['Url']  # 图片url
                    else:
                        FriendPic_text = data_text['FriendPic'][0]
                        picUrl_text = FriendPic_text['Url']  # 图片url
                    try:
                        download(url=picUrl_text, dist='./plugins/bot_MessageForwarding/1.png')
                        Pic_Md5 = file_to_base64('./plugins/bot_MessageForwarding/1.png')  # 图片Md5
                        # 文本和图片同时存在
                        cont_text = data_text['Content']
                        if set_relay_length_max(length=-2) != -1:  # 判断是否超出字数
                            if len(cont_text) > int(set_relay_length_max(length=-2)):
                                return
                        if set_relay_type(pattern="2") == "-1":
                            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                        elif set_relay_type(pattern="2") == "0":
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                        else:
                            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                    except Exception as e:
                        # 仅为图片
                        if set_relay_type(pattern="2") == "-1":
                            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊")
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                        elif set_relay_type(pattern="2") == "0":
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                        else:
                            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
        else:
            return


@plugin_receiver.group
@decorators.ignore_botself
@ignore_botself  # 忽略机器人自身的消息
def receive_group_msg(ctx: GroupMsg):
    if set_switch(text="2") != "0":  # 转发功能打开时
        group_type = set_group_type(pattern="3")
        if group_type == "2":  # 群聊监听模式：关闭
            return

        q_uin = str(ctx.FromGroupId)  # 群聊UIN
        Uin = str(ctx.FromUserId)  # 获取回复人UIN

        for i in blacklist_friend_uin:  # 判断是否私聊uin黑名单
            if i == Uin:
                return
        for i in blacklist_group_uin:  # 判断是否群聊uin黑名单
            if i == q_uin:
                return

        cont = ctx.Content

        for i in blacklist_friend_key:  # 判断是否私聊关键词黑名单
            if cont.find(i) != -1:
                return
        for i in blacklist_group_key:  # 判断是否群聊关键词黑名单
            if cont.find(i) != -1:
                return
        if group_type == "-1":  # 群聊监听模式：全部监听
            time_text = time.strftime("%Y/%m/%d %H:%M:%S")  # 获取消息时间
            if ctx.MsgType == "TextMsg":  # 当为文本消息时
                if set_relay_length_max(length=-2) != -1:  # 判断是否超出字数
                    if len(cont) > int(set_relay_length_max(length=-2)):
                        return
                if set_relay_length_min(length=-2) != -1:  # 判断是否小于字数
                    if len(cont) < int(set_relay_length_min(length=-2)):
                        return
                if set_relay_type(pattern="2") == "-1":
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                elif set_relay_type(pattern="2") == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                else:
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
            elif ctx.MsgType == "PicMsg":  # 当为图文消息时
                data_text = demjson.decode(ctx.Content)  # 回复的消息的内容
                GroupPic_text = data_text['GroupPic'][0]
                picUrl_text = GroupPic_text['Url']  # 图片url
                download(url=picUrl_text, dist='./plugins/bot_MessageForwarding/1.png')
                Pic_Md5 = file_to_base64('./plugins/bot_MessageForwarding/1.png')  # 图片Md5
                try:
                    # 文本和图片同时存在
                    cont_text = data_text['Content']
                    if set_relay_length_max(length=-2) != -1:  # 判断是否超出字数
                        if len(cont_text) > int(set_relay_length_max(length=-2)):
                            return
                    if set_relay_type(pattern="2") == "-1":
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                    elif set_relay_type(pattern="2") == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                    else:
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                except Exception as e:
                    # 仅为图片
                    if set_relay_type(pattern="2") == "-1":
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
                    elif set_relay_type(pattern="2") == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
                    else:
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
            file_data = gp.file(ctx)
            if file_data is not None:
                file_id = action.getGroupFileURL(
                    group=ctx.FromGroupId, fileID=file_data.FileID)
                file_name = file_data.FileName
                file_size = file_data.FileSize
                address = f"文件名:\n{file_name}\n文件大小{round(file_size / 1024 / 1024, 2)}MB\n来自群:{ctx.FromGroupName}({ctx.FromGroupId})\n来自用户:{ctx.FromNickName}({ctx.FromUserId})\n下载地址:\n{file_id['Url']}"
                if set_relay_type(pattern="2") == "-1":
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(user=int(i), content=address)
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendFriendText(user=int(i), content=address)
                    return
                elif set_relay_type(pattern="2") == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendFriendText(user=int(i), content=address)
                    return
                else:
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(user=int(i), content=address)
                    return
            elif ctx.MsgType == "VoiceMsg":
                data_text = demjson.decode(ctx.Content)  # 回复的消息的内容
                voiceUrl_text = data_text['Url']
                if set_relay_type(pattern="2") == "-1":
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊语音消息(请在手机上查看)\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text)
                        action.sendFriendVoice(user=int(i), voiceUrl=voiceUrl_text)
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊语音消息(请在手机上查看)\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text)
                        action.sendgroupVoice(group=int(i), voiceUrl=voiceUrl_text)
                    return
                elif set_relay_type(pattern="2") == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊语音消息(请在手机上查看)\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text)
                        action.sendgroupVoice(group=int(i), voiceUrl=voiceUrl_text)
                    return
                else:
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊语音消息(请在手机上查看)\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text)
                        action.sendFriendVoice(user=int(i), voiceUrl=voiceUrl_text)
                    return
        # 群聊聊监听模式：关键词监听
        elif group_type == "0":
            if len(group_key) < 1:  # 没有关键词时
                return
            for i in group_key:  # 判断是否需要转发消息
                if cont.find(i) == -1:
                    return
            time_text = time.strftime("%Y/%m/%d %H:%M:%S")  # 获取消息时间
            if ctx.MsgType == "TextMsg":  # 当为文本消息时
                if set_relay_length_max(length=-2) != -1:  # 判断是否超出字数
                    if len(cont) > int(set_relay_length_max(length=-2)):
                        return
                if set_relay_length_min(length=-2) != -1:  # 判断是否小于字数
                    if len(cont) < int(set_relay_length_min(length=-2)):
                        return
                if set_relay_type(pattern="2") == "-1":
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    return
                elif set_relay_type(pattern="2") == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    return
                else:
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    return
            elif ctx.MsgType == "PicMsg":  # 当为图文消息时
                data_text = demjson.decode(ctx.Content)  # 回复的消息的内容
                GroupPic_text = data_text['GroupPic'][0]
                picUrl_text = GroupPic_text['Url']  # 图片url
                download(url=picUrl_text, dist='./plugins/bot_MessageForwarding/1.png')
                Pic_Md5 = file_to_base64('./plugins/bot_MessageForwarding/1.png')  # 图片Md5
                try:
                    # 文本和图片同时存在
                    cont_text = data_text['Content']
                    if set_relay_length_max(length=-2) != -1:  # 判断是否超出字数
                        if len(cont_text) > int(set_relay_length_max(length=-2)):
                            return
                    if set_relay_type(pattern="2") == "-1":
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                    elif set_relay_type(pattern="2") == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                    else:
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                except Exception as e:
                    # 仅为图片
                    if set_relay_type(pattern="2") == "-1":
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
                    elif set_relay_type(pattern="2") == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
                    else:
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
        # 群聊监听模式：UIN监听
        elif group_type == "1":
            if len(group_uin) < 1:  # 没有UIN时
                return
                # 判断UIN是否存在在监听UIN列表中
            group_uin_i = 0
            for i in group_uin:  # 判断是否需要转发消息
                if q_uin == i:
                    group_uin_i = 1
                    break
            if group_uin_i == 0:
                return
            time_text = time.strftime("%Y/%m/%d %H:%M:%S")  # 获取消息时间
            if ctx.MsgType == "TextMsg":  # 当为文本消息时
                if set_relay_length_max(length=-2) != -1:  # 判断是否超出字数
                    if len(cont) > int(set_relay_length_max(length=-2)):
                        return
                if set_relay_length_min(length=-2) != -1:  # 判断是否小于字数
                    if len(cont) < int(set_relay_length_min(length=-2)):
                        return
                if set_relay_type(pattern="2") == "-1":
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    return
                elif set_relay_type(pattern="2") == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    return
                else:
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    return
            elif ctx.MsgType == "PicMsg":  # 当为图文消息时
                data_text = demjson.decode(ctx.Content)  # 回复的消息的内容
                GroupPic_text = data_text['GroupPic'][0]
                picUrl_text = GroupPic_text['Url']  # 图片url
                download(url=picUrl_text, dist='./plugins/bot_MessageForwarding/1.png')
                Pic_Md5 = file_to_base64('./plugins/bot_MessageForwarding/1.png')  # 图片Md5
                try:
                    # 文本和图片同时存在
                    cont_text = data_text['Content']
                    if set_relay_length_max(length=-2) != -1:  # 判断是否超出字数
                        if len(cont_text) > int(set_relay_length_max(length=-2)):
                            return
                    if set_relay_type(pattern="2") == "-1":
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                    elif set_relay_type(pattern="2") == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                    else:
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                except Exception as e:
                    # 仅为图片
                    if set_relay_type(pattern="2") == "-1":
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
                    elif set_relay_type(pattern="2") == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
                    else:
                        for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
            elif ctx.MsgType == "VoiceMsg":
                data_text = demjson.decode(ctx.Content)  # 回复的消息的内容
                voiceUrl_text = data_text['Url']
                if set_relay_type(pattern="2") == "-1":
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊语音消息(请在手机上查看)\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text)
                        action.sendFriendVoice(user=int(i), voiceUrl=voiceUrl_text)
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊语音消息(请在手机上查看)\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text)
                        action.sendgroupVoice(group=int(i), voiceUrl=voiceUrl_text)
                    return
                elif set_relay_type(pattern="2") == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊语音消息(请在手机上查看)\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text)
                        action.sendgroupVoice(group=int(i), voiceUrl=voiceUrl_text)
                    return
                else:
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊语音消息(请在手机上查看)\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text)
                        action.sendFriendVoice(user=int(i), voiceUrl=voiceUrl_text)
                    return
            file_data = gp.file(ctx)
            if file_data is not None:
                file_id = action.getGroupFileURL(
                    group=ctx.FromGroupId, fileID=file_data.FileID)
                file_name = file_data.FileName
                file_size = file_data.FileSize
                address = f"文件名:\n{file_name}\n文件大小{round(file_size / 1024 / 1024, 2)}MB\n来自群:{ctx.FromGroupName}({ctx.FromGroupId})\n来自用户:{ctx.FromNickName}({ctx.FromUserId})\n下载地址:\n{file_id['Url']}"
                if set_relay_type(pattern="2") == "-1":
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(user=int(i), content=address)
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(group=int(i), content=address)
                    return
                elif set_relay_type(pattern="2") == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(group=int(i), content=address)
                    return
                else:
                    for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                        action.sendFriendText(user=int(i), content=address)
                    return
    else:
        return