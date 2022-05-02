"""监控转发"""
from botoy import Action, jconfig
from botoy.contrib import plugin_receiver, download, file_to_base64
from botoy.decorators import ignore_botself, startswith
from botoy.parser import group as gp  # 群消息(GroupMsg)相关解析

import re, time, demjson

from .config import *

action = Action(qq=jconfig.qq)

def SendMessage(ctxTypeNumber, MsgType, times, fromGroupId="", GroupName="", fromUin="", content="", picUrl="",
                picBase64="", voiceUrl=""):
    re_content = '({fuin})\n{fname}{gname}{guin}\n收到一条{qtype}{tyepe}消息\n{ttime}\n{cont}'.format(
        fuin=fromUin,
        fname=get_name(fromUin),
        gname="" if GroupName == "" else "\n" + GroupName,
        guin="" if fromGroupId == "" else "(" + fromGroupId + ")",
        qtype="群聊" if ctxTypeNumber == 0 else "私聊",
        tyepe=MsgType.replace("TextMsg", "文字").replace("AtMsg", "文字").replace("PicMsg", "图片").replace("VoiceMsg", "语音"),
        ttime=times,
        cont="" if content == "" else "“" + content + "”"
    )
    if set_relay_type(pattern="2") == "-1":
        # 语音消息
        if voiceUrl is not None and voiceUrl != "":
            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                action.sendFriendText(int(i), re_content)
                action.sendFriendVoice(user=int(i), voiceUrl=voiceUrl)
            for i in set_relay_group_uin(pattern="2"):  # 转发消息到所有群聊UIN
                action.sendGroupText(int(i), re_content)
                action.sendgroupVoice(group=int(i), voiceUrl=voiceUrl)
            return
        # 图片消息
        elif (picUrl is not None and picUrl != "") or (picBase64 is not None and picBase64 != ""):
            if picUrl is not None and picUrl != "":
                for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                    action.sendFriendPic(user=int(i), content=re_content)
                for i in relay_group_uin:  # 转发消息到所有群聊UIN
                    action.sendGroupPic(group=int(i), content=re_content)
                return
            # Base64
            else:
                for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                    action.sendFriendPic(user=int(i), picBase64Buf=picBase64, content=re_content)
                for i in relay_group_uin:  # 转发消息到所有群聊UIN
                    action.sendGroupPic(group=int(i), picBase64Buf=picBase64, content=re_content)
                return
        # 文字消息
        else:
            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                action.sendFriendText(int(i), re_content)
            for i in set_relay_group_uin(pattern="2"):  # 转发消息到所有群聊UIN
                action.sendGroupText(int(i), re_content)
            return
    elif set_relay_type(pattern="2") == "0":
        # 语音消息
        if voiceUrl is not None and voiceUrl != "":
            for i in set_relay_group_uin(pattern="2"):  # 转发消息到所有群聊UIN
                action.sendGroupText(int(i), re_content)
                action.sendgroupVoice(group=int(i), voiceUrl=voiceUrl)
            return
        # 图片消息
        elif (picUrl is not None and picUrl != "") or (picBase64 is not None and picBase64 != ""):
            if picUrl is not None and picUrl != "":
                for i in relay_group_uin:  # 转发消息到所有群聊UIN
                    action.sendGroupPic(group=int(i), picUrl=picUrl, content=re_content)
                return
            # Base64
            else:
                for i in relay_group_uin:  # 转发消息到所有群聊UIN
                    action.sendGroupPic(group=int(i), picBase64Buf=picBase64,
                                        content="收到一条群聊消息\n" + GroupName + "(" + fromGroupId + ")\n来自用户：" + get_name(
                                            fromUin) + "(" + fromUin + ") " + "\n" + times + "\n“" + content + "”")
                return
        # 文字消息
        else:
            for i in set_relay_group_uin(pattern="2"):  # 转发消息到所有群聊UIN
                action.sendGroupText(int(i), re_content)
            return
    else:
        # 语音消息
        if voiceUrl is not None and voiceUrl != "":
            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                action.sendFriendText(int(i), re_content)
                action.sendFriendVoice(user=int(i), voiceUrl=voiceUrl)
            return
        # 图片消息
        elif (picUrl is not None and picUrl != "") or (picBase64 is not None and picBase64 != ""):
            if picUrl is not None and picUrl != "":
                for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                    action.sendFriendPic(user=int(i), picUrl=picUrl, content=re_content)
                return
            # Base64
            else:
                for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                    action.sendFriendPic(user=int(i), picBase64Buf=picBase64, content=re_content)
                return
        # 文字消息
        else:
            for i in set_relay_friend_uin(pattern="2"):  # 转发消息到所有私聊UIN
                action.sendFriendText(int(i), re_content)
            return


def boss_reply(ctxTypeNumber, fromGroupId="", fromUin="", content="", picUrl="", picBase64="", picMd5=""):
    if ctxTypeNumber == 0:
        # 图片消息
        if ((picUrl is not None and picUrl != "") or (picBase64 is not None and picBase64 != "") or (
                picMd5 is not None and picMd5 != "")):
            if picUrl is not None and picUrl != "":
                if len(content) > 0:
                    action.sendGroupPic(group=fromGroupId, picUrl=picUrl, content=content)
                    return
                else:
                    action.sendGroupPic(group=fromGroupId, picUrl=picUrl)
                    return
            # Base64
            elif picBase64 is not None and picBase64 != "":
                if len(content) > 0:
                    action.sendGroupPic(group=fromGroupId, picBase64Buf=picBase64, content=content)
                    return
                else:
                    action.sendGroupPic(group=fromGroupId, picBase64Buf=picBase64)
                    return
            # md5
            elif picMd5 is not None and picMd5 != "":
                if len(content) > 0:
                    action.sendGroupPic(group=fromGroupId, picMd5s=picMd5, content=content)
                    return
                else:
                    action.sendGroupPic(group=fromGroupId, picMd5s=picMd5)
                    return
        # 文字消息
        else:
            action.sendGroupText(fromGroupId, content)
            return
    elif ctxTypeNumber == 1:
        # 图片消息
        if ((picUrl is not None and picUrl != "") or (picBase64 is not None and picBase64 != "") or (
                picMd5 is not None and picMd5 != "")):
            if picUrl is not None and picUrl != "":
                if len(content) > 0:
                    action.sendFriendPic(user=fromUin, picUrl=picUrl, content=content)
                    return
                else:
                    action.sendFriendPic(user=fromUin, picUrl=picUrl)
                    return
            # Base64
            elif picBase64 is not None and picBase64 != "":
                if len(content) > 0:
                    action.sendFriendPic(user=fromUin, picBase64Buf=picBase64, content=content)
                    return
                else:
                    action.sendFriendPic(user=fromUin, picBase64Buf=picBase64)
                    return
            # md5
            elif picMd5 is not None and picMd5 != "":
                print(content, picMd5)
                if len(content) > 0:
                    action.sendFriendPic(user=fromUin, picMd5s=picMd5, content=content)
                    return
                else:
                    action.sendFriendPic(user=fromUin, picMd5s=picMd5)
                    return
        # 文字消息
        else:
            action.sendFriendText(fromUin, content)
            return


@plugin_receiver.group
@plugin_receiver.friend
@ignore_botself  # 忽略机器人自身的消息
def receiver(ctx):
    # 私聊群聊消息处理
    MsgType_t = ctx.MsgType  # 消息类型
    ctx_t = 0  # 记录消息是群聊还是私聊
    time_text = time.strftime("%Y/%m/%d %H:%M:%S")  # 获取消息时间
    q_uin = ""  # QQ群UIN
    uin = ""  # 消息人UIN
    cont = ""  # 消息文字内容
    friend_type = set_friend_type(pattern="2")  # 私聊监听模式
    group_type = set_group_type(pattern="3")  # 群聊监听模式
    picUrl_text = ""  # 图片url
    Pic_Bs64 = ""  # 图片Base64
    voiceUrl_text = ""  # 语音url
    # 群聊消息
    try:
        q_uin = str(ctx.FromGroupId)  # QQ群UIN
        group_name = str(ctx.FromGroupId)  # QQ群名称
        uin = str(ctx.FromUserId)  # 消息人UIN
        if group_type == "2":  # 群聊监听模式：关闭
            return
        # 判断是否群聊uin黑名单
        for i in set_blacklist_group_uin(pattern="2"):
            if i == q_uin:
                return
    # 私聊消息
    except Exception as e:
        uin = str(ctx.FromUin)  # 消息人UIN
        ctx_t = 1

    # 判断是否为私聊uin黑名单
    for i in set_blacklist_friend_uin(pattern="2"):
        if i == uin:
            return

    # 判断消息类型
    if MsgType_t == "TextMsg" or MsgType_t == "AtMsg":  # 文字消息
        if MsgType_t == "AtMsg":
            try:
                Content_data = decode(ctx.Content)
            except Exception as e:
                logger.warning(f"AtMsg消息编码失败\r\n {e}")
                return
            cont = sub(r'@(.+) ', "", Content_data['Content'])
        else:
            cont = ctx.Content

        # 仅文字消息需要判断是否小于限制长度
        if set_relay_length_min(length=-2) != -1:  # 判断是否小于字数
            if len(cont) < int(set_relay_length_min(length=-2)):
                return
    else:
        data_text = demjson.decode(ctx.Content)
        # 图文消息
        if MsgType_t == "PicMsg":
            if str(data_text).find("[闪照]") != -1:
                picUrl_text = data_text['Url']  # 图片url
            else:
                if ctx_t == 1:  # 私聊消息
                    Pic_text = data_text['FriendPic'][0]
                elif ctx_t == 0:  # 群聊消息
                    Pic_text = data_text['GroupPic'][0]
                picUrl_text = Pic_text['Url']  # 图片url
            try:
                download(url=picUrl_text, dist='./plugins/bot_MessageForwarding/1.png')
                Pic_Bs64 = file_to_base64('./plugins/bot_MessageForwarding/1.png')  # 图片Base64
                # 文本和图片同时存在
                cont = data_text['Content']
            except Exception as e:
                # 仅为图片
                cont = ""
        # 语音消息
        elif MsgType_t == "VoiceMsg":
            voiceUrl_text = data_text['Url']

    if len(cont) > 0:
        # 判断文字内容是否超出字数
        if set_relay_length_max(length=-2) != -1:
            if len(cont) > int(set_relay_length_max(length=-2)):
                return

        if ctx_t == 1:
            # 判断是否私聊关键词黑名单
            for i in set_blacklist_friend_key(pattern="2"):
                if cont.find(i) != -1:
                    return
        elif ctx_t == 0:
            # 判断是否群聊关键词黑名单
            for i in set_blacklist_group_key(pattern="2"):
                if cont.find(i) != -1:
                    return

    # 判断是否是管理员
    boss_i = 0
    for i in set_boss_uin(pattern="2"):
        if str(uin) == i:
            boss_i = 1
            break
    # 管理员
    if boss_i == 1:
        # 总开关设置与查看
        if cont == "打开监控转发":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_switch(text="1"))
            return
        elif cont == "关闭监控转发":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_switch(text="0"))
            return
        elif cont == "监控转发状态" or cont == "查看监控转发":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=format_json_data())
            return
        # 设置与查看管理员UIN
        elif cont.startswith("添加监控转发管理员"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_boss_uin(uin=cont[9:], pattern="0"))
            return
        elif cont.startswith("删除监控转发管理员"):
            boss_uin_pattern = cont[9:]
            if len(set_boss_uin(pattern="2")) > 1:
                boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_boss_uin(uin=cont[9:], pattern="0"))
                return
            else:
                boss_reply(ctxTypeNumber=1, fromUin=uin, content="删除失败\n仅剩一位管理员，如果需要删除请手动删除\n管理员UIN列表：" + str(set_boss_uin(pattern="2")))
                return
        elif cont == "监控转发管理员查看" or cont == "查看监控转发管理员":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_boss_uin(pattern="2"))
            return
        # 设置私聊监听模式
        elif cont.startswith("设置私聊监听模式"):
            friend_type_pattern = cont[8:].replace("全部监听", "-1").replace("全部", "-1").replace("关键词监听", "0").replace(
                "关键词", "0").replace("UIN监听", "1").replace("uin监听", "1").replace("UIN", "1").replace("uin", "1")
            if is_number(friend_type_pattern) and len(friend_type_pattern) <= 2:
                boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_friend_type(pattern=friend_type_pattern))
                return
            else:
                boss_reply(ctxTypeNumber=1, fromUin=uin, content="设置私聊监听模式失败\n私聊监听模式只有：全部监听、关键词监听、UIN监听 三种模式")
                return
        # 查看私聊监听模式
        elif cont == "私聊监听模式状态" or cont == "查看私聊监听模式":
            friend_key_pattern = "私聊监听模式：关键词监听\n关键词列表：" + str(set_friend_key(pattern="2"))
            friend_uin_pattern = "私聊监听模式：UIN监听\nUIN列表：" + str(set_friend_uin(pattern="2"))
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_friend_type(pattern="2").replace("-1", "私聊监听模式：全部监听").replace("0",friend_key_pattern).replace("1", friend_uin_pattern))
            return
        # 设置与查看私聊监听关键词列表
        elif cont.startswith("添加私聊监听关键词"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_friend_key(key=cont[9:], pattern="0"))
            return
        elif cont.startswith("删除私聊监听关键词"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_friend_key(key=cont[9:], pattern="1"))
            return
        elif cont == "私聊监听关键词查看" or cont == "查看私聊监听关键词":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_friend_key(pattern="2"))
            return
        # 设置与查看私聊监听UIN列表
        elif cont.startswith("添加私聊监听UIN") or cont.startswith("添加私聊监听uin"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_friend_uin(uin=cont[9:], pattern="0"))
            return
        elif cont.startswith("删除私聊监听UIN") or cont.startswith("删除私聊监听uin"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_friend_uin(uin=cont[9:], pattern="1"))
            return
        elif cont == "私聊监听UIN查看" or cont == "查看私聊监听UIN" or cont == "私聊监听uin查看" or cont == "查看私聊监听uin":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_friend_uin(pattern="2"))
            return
        # 设置群聊监听模式
        elif cont.startswith("设置群聊监听模式"):
            group_type_pattern = cont[8:].replace("全部监听", "-1").replace("全部", "-1").replace("关键词监听", "0").replace("关键词",
                                                                                                                  "0").replace(
                "UIN监听", "1").replace("uin监听", "1").replace("UIN", "1").replace("uin", "1").replace("关闭", "2")
            if is_number(group_type_pattern) and len(group_type_pattern) <= 2:
                boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_group_type(pattern=group_type_pattern))
                return
            else:
                boss_reply(ctxTypeNumber=1, fromUin=uin, content="设置群聊监听模式失败\n群聊监听模式只有：全部监听、关键词监听、UIN监听、关闭 四种模式")
                return
        # 查看群聊监听模式
        elif cont == "群聊监听模式状态" or cont == "查看群聊监听模式":
            group_key_pattern = "群聊监听模式：关键词监听\n关键词列表：" + str(set_group_key(pattern="2"))
            group_uin_pattern = "群聊监听模式：UIN监听\nUIN列表：" + str(set_group_uin(pattern="2"))
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_group_type(pattern="3").replace("-1", "群聊监听模式：全部监听").replace("0",group_key_pattern).replace("1",group_uin_pattern).replace("2", "群聊监听模式：关闭"))
            return
        # 设置与查看群聊监听关键词列表
        elif cont.startswith("添加群聊监听关键词"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_group_key(key=cont[9:], pattern="0"))
            return
        elif cont.startswith("删除群聊监听关键词"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_group_key(key=cont[9:], pattern="1"))
            return
        elif cont == "群聊监听关键词查看" or cont == "查看群聊监听关键词":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_group_key(pattern="2"))
            return
        # 设置与查看群聊监听UIN列表
        elif cont.startswith("添加群聊监听UIN") or cont.startswith("添加群聊监听uin"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_group_uin(uin=cont[9:], pattern="0"))
            return
        elif cont.startswith("删除群聊监听UIN") or cont.startswith("删除群聊监听uin"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_group_uin(uin=cont[9:], pattern="1"))
            return
        elif cont == "群聊监听UIN查看" or cont == "查看群聊监听UIN" or cont == "群聊监听uin查看" or cont == "查看群聊监听uin":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_group_uin(pattern="2"))
            return
        # 设置转发模式
        elif cont.startswith("设置转发模式"):
            relay_type_pattern = cont[6:].replace("全部转发", "-1").replace("全部", "-1").replace("群聊UIN转发", "0").replace(
                "群聊uin转发", "0").replace("群聊", "0").replace("私聊UIN转发", "1").replace("私聊uin转发", "1").replace("私聊", "1")
            if is_number(relay_type_pattern) and len(relay_type_pattern) <= 2:
                boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_relay_type(pattern=relay_type_pattern))
                return
            else:
                boss_reply(ctxTypeNumber=1, fromUin=uin, content="设置转发模式失败\n转发模式只有：全部转发、私聊UIN转发、群聊UIN转发 三种模式")
                return
        # 查看转发模式
        elif cont == "转发模式状态" or cont == "查看转发模式":
            relay_all_uin_pattern = "转发模式：全部转发\n私聊UIN列表：" + str(set_relay_friend_uin(pattern="2")) + "\n群聊UIN列表：" + str(
                set_relay_group_uin(pattern="2"))
            relay_friend_uin_pattern = "转发模式：私聊UIN转发\n私聊UIN列表：" + str(set_relay_friend_uin(pattern="2"))
            relay_group_uin_pattern = "转发模式：群聊UIN转发\n群聊UIN列表：" + str(set_relay_group_uin(pattern="2"))
            relay_type_i = set_relay_type(pattern="2")
            if relay_type_i == "-1":
                boss_reply(ctxTypeNumber=1, fromUin=uin, content=relay_all_uin_pattern)
                return
            elif relay_type_i == "0":
                boss_reply(ctxTypeNumber=1, fromUin=uin, content=relay_group_uin_pattern)
                return
            else:
                boss_reply(ctxTypeNumber=1, fromUin=uin, content=relay_friend_uin_pattern)
                return
        # 设置与查看转发私聊UIN列表
        elif cont.startswith("添加转发私聊UIN") or cont.startswith("添加转发私聊uin"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_relay_friend_uin(uin=cont[9:], pattern="0"))
            return
        elif cont.startswith("删除转发私聊UIN") or cont.startswith("删除转发私聊uin"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_relay_friend_uin(uin=cont[9:], pattern="1"))
            return
        elif cont == "转发私聊UIN查看" or cont == "查看转发私聊UIN" or cont == "转发私聊uin查看" or cont == "查看转发私聊uin":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_relay_friend_uin(pattern="2"))
            return
        # 设置与查看转发群聊UIN列表
        elif cont.startswith("添加转发群聊UIN") or cont.startswith("添加转发群聊uin"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_relay_group_uin(uin=cont[9:], pattern="0"))
            return
        elif cont.startswith("删除转发群聊UIN") or cont.startswith("删除转发群聊uin"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_relay_group_uin(uin=cont[9:], pattern="1"))
            return
        elif cont == "转发群聊UIN查看" or cont == "查看转发群聊UIN" or cont == "转发私聊uin查看" or cont == "查看转发私聊uin":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_relay_group_uin(pattern="2"))
            return
        # 设置与查看转发文本限制长度
        elif cont.startswith("设置转发文本限制最长长度"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_relay_length_max(length=int(cont[12:].replace("无限制", "-1"))))
            return
        elif cont.startswith("设置转发文本限制最短长度"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_relay_length_min(length=int(cont[12:].replace("无限制", "-1"))))
            return
        elif cont == "转发文本限制长度查看" or cont == "查看转发文本限制长度":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_relay_length_min(length=-2) + "\n" + set_relay_length_max(bot_dict, length=-2))
            return
        # 设置与查看转发私聊UIN黑名单列表
        elif cont.startswith("添加黑名单转发私聊UIN") or cont.startswith("添加黑名单转发私聊uin"):
            blacklist_friend_uin_pattern = cont.replace("添加黑名单转发私聊UIN", "").replace("添加黑名单转发私聊uin", "")
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_blacklist_friend_uin(uin=blacklist_friend_uin_pattern,pattern="0"))
            return
        elif cont.startswith("删除黑名单转发私聊UIN") or cont.startswith("删除黑名单转发私聊uin"):
            blacklist_friend_uin_pattern = cont.replace("删除黑名单转发私聊UIN", "").replace("删除黑名单转发私聊uin", "")
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_blacklist_friend_uin(uin=blacklist_friend_uin_pattern,pattern="1"))
            return
        elif cont == "转发私聊UIN黑名单查看" or cont == "查看转发私聊UIN黑名单" or cont == "转发私聊uin黑名单查看" or cont == "查看转发私聊uin黑名单":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_blacklist_friend_uin(pattern="2"))
            return
        # 设置与查看转发群聊UIN黑名单列表
        elif cont.startswith("添加黑名单转发群聊UIN") or cont.startswith("添加黑名单转发群聊uin"):
            blacklist_group_uin_pattern = cont.replace("添加黑名单转发群聊UIN", "").replace("添加黑名单转发群聊uin", "")
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_blacklist_group_uin(uin=blacklist_group_uin_pattern, pattern="0"))
            return
        elif cont.startswith("删除黑名单转发群聊UIN") or cont.startswith("删除黑名单转发群聊uin"):
            blacklist_group_uin_pattern = cont.replace("删除黑名单转发群聊UIN", "").replace("删除黑名单转发群聊uin", "")
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_blacklist_group_uin(uin=blacklist_group_uin_pattern, pattern="1"))
            return
        elif cont == "转发群聊UIN黑名单查看" or cont == "查看转发群聊UIN黑名单" or cont == "转发群聊uin黑名单查看" or cont == "查看转发群聊uin黑名单":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_blacklist_group_uin(pattern="2"))
            return
        # 设置与查看转发私聊关键词黑名单列表
        elif cont.startswith("添加转发私聊关键词黑名单"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_blacklist_friend_key(key=cont[12:],pattern="0"))
            return
        elif cont.startswith("删除转发私聊关键词黑名单"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_blacklist_friend_key(key=cont[12:],pattern="1"))
            return
        elif cont == "转发私聊关键词黑名单查看" or cont == "查看转发私聊关键词黑名单":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_blacklist_friend_key(pattern="2"))
            return
        # 设置与查看转发群聊关键词黑名单列表
        elif cont.startswith("添加转发群聊关键词黑名单"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_blacklist_group_key(key=cont[12:], pattern="0"))
            return
        elif cont.startswith("删除转发群聊关键词黑名单"):
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_blacklist_group_key(key=cont[12:], pattern="1"))
            return
        elif cont == "转发群聊关键词黑名单查看" or cont == "查看转发群聊关键词黑名单":
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_blacklist_group_key(pattern="2"))
            return
        # 设置回复模式
        elif cont.startswith("设置回复模式"):
            reply_type_pattern = cont[6:].replace("关闭", "0").replace("关", "0").replace("开启", "1").replace("开", "1")
            if is_number(reply_type_pattern) and len(reply_type_pattern) <= 2:
                boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_reply_type(pattern=reply_type_pattern))
                return
            else:
                boss_reply(ctxTypeNumber=1, fromUin=uin, content="设置回复模式失败\n回复模式只有：开启、关闭 两种情况")
                return
        # 查看回复模式
        elif cont == "回复模式状态" or cont == "查看回复模式":
            reply_type_on_pattern = "当上一条消息为转发消息时，默认需要回复的UIN与上条消息相同：开启"
            reply_type_off_pattern = "当上一条消息为转发消息时，默认需要回复的UIN与上条消息相同：关闭"
            boss_reply(ctxTypeNumber=1, fromUin=uin, content=set_reply_type(pattern="2").replace("0", reply_type_off_pattern).replace(
                                  "1", reply_type_on_pattern))
            return
        # 帮助菜单
        elif cont == "监控转发菜单" or cont == "监控转发帮助":
            boss_reply(ctxTypeNumber=1, fromUin=uin,picBase64=file_to_base64('./plugins/bot_MessageForwarding/help2.png'))
        # 回复消息
        elif MsgType_t == "ReplayMsg":
            reply_picUrl_text = ""  # 回复图片url
            reply_Pic_Bs64 = ""  # 回复图片Base64
            reply_Pic_Md5 = ""  # 回复图片Md5
            reply_cont = ""  # 回复内容
            data_text = demjson.decode(ctx.Content)
            SrcContent_text = data_text['SrcContent']  # 回复的消息的内容
            try:
                reply_picUrl_text = data_text['FriendPic'][0]['Url']  # 实际需要回复的内容
                if len(reply_picUrl_text) > 48:
                    download(url=reply_picUrl_text, dist='./plugins/bot_MessageForwarding/1.png')
                    reply_Pic_Bs64 = file_to_base64('./plugins/bot_MessageForwarding/1.png')  # 图片Base64
                else:
                    reply_Pic_Md5 = data_text['FriendPic'][0]['FileMd5']
                try:
                    reply_cont = data_text['ReplayContent']  # 实际需要回复的内容
                except Exception as e:
                    reply_cont = ""  # 没有需要回复的内容
            except Exception as e:  # 没有需要回复的图像
                reply_cont = data_text['Content']  # 实际需要回复的内容
            reply_uin = get_ReplyUin(SrcContent_text, cont)  # 获取回复人UIN
            # 用于判断是否为图文消息时候手动指定回复人
            if len(re.findall("(\(.*\))", reply_cont)) > 0:  # 真
                if reply_picUrl_text == "":  # 没有图片时
                    boss_reply(ctxTypeNumber=1, fromUin=reply_uin,
                               content=reply_cont.replace(re.findall("(\(.*\))", reply_cont)[0], ""))
                    return
                else:
                    if reply_Pic_Bs64 != "":
                        try:
                            # 文本和图片同时存在
                            boss_reply(ctxTypeNumber=1, fromUin=reply_uin,
                                       content=reply_cont.replace(re.findall("(\(.*\))", reply_cont)[0], ""),
                                       picBase64=reply_Pic_Bs64)
                            return
                        except Exception as e:
                            # 仅为图片
                            boss_reply(ctxTypeNumber=1, fromUin=reply_uin, picBase64Buf=reply_Pic_Md5)
                            return
                    else:
                        try:
                            # 文本和图片同时存在
                            boss_reply(ctxTypeNumber=1, fromUin=reply_uin,
                                       content=reply_cont.replace(re.findall("(\(.*\))", reply_cont)[0], ""),
                                       picMd5=reply_Pic_Md5)
                            return
                        except Exception as e:
                            # 仅为图片
                            boss_reply(ctxTypeNumber=1, fromUin=reply_uin, picMd5=reply_Pic_Md5)
                            return
            # 假
            else:
                if reply_picUrl_text == "":  # 没有图片时
                    boss_reply(ctxTypeNumber=1, fromUin=reply_uin, content=reply_cont)
                    return
                else:
                    if reply_Pic_Bs64 != "":
                        try:
                            # 文本和图片同时存在
                            boss_reply(ctxTypeNumber=1, fromUin=reply_uin, content=reply_cont, picBase64=reply_Pic_Bs64)
                            return
                        except Exception as e:
                            # 仅为图片
                            boss_reply(ctxTypeNumber=1, fromUin=reply_uin, picBase64=reply_Pic_Bs64)
                            return
                    else:
                        try:
                            # 文本和图片同时存在
                            boss_reply(ctxTypeNumber=1, fromUin=reply_uin, content=reply_cont, picMd5=reply_Pic_Md5)
                            return
                        except Exception as e:
                            # 仅为图片
                            boss_reply(ctxTypeNumber=1, fromUin=reply_uin, picMd5=reply_Pic_Md5)
                            return
    # 非管理员
    else:
        # 转发功能是否打开
        if set_switch(text="2") == "1":  # 转发功能开启
            # 监听模式检测
            if ctx_t == 1:
                # 私聊监听模式：关键词监听
                if friend_type == "0":
                    friend_key = set_friend_key(pattern="2")  # 私聊监听关键词列表
                    if len(friend_key) < 1:  # 没有关键词时
                        return
                    for i in friend_key:  # 判断是否需要转发消息
                        if cont.find(i) == -1:
                            return
                    SendMessage(ctxTypeNumber=ctx_t, MsgType=MsgType_t, fromGroupId=q_uin, fromUin=uin, times=time_text,
                                content=cont, picUrl=picUrl_text, picBase64=Pic_Bs64, voiceUrl=voiceUrl_text)
                    return
                # 私聊监听模式：UIN监听
                elif friend_type == "1":
                    friend_uin = set_friend_uin(pattern="2")  # 私聊监听UIN列表
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
                    SendMessage(ctxTypeNumber=ctx_t, MsgType=MsgType_t, fromGroupId=q_uin, fromUin=uin, times=time_text,
                                content=cont, picUrl=picUrl_text, picBase64=Pic_Bs64, voiceUrl=voiceUrl_text)
                    return
                # 私聊监听模式：全部监听
                else:
                    SendMessage(ctxTypeNumber=ctx_t, MsgType=MsgType_t, fromGroupId=q_uin, fromUin=uin, times=time_text,
                                content=cont, picUrl=picUrl_text, picBase64=Pic_Bs64, voiceUrl=voiceUrl_text)
                    return
            elif ctx_t == 0:
                # 群聊聊监听模式：关键词监听
                if group_type == "0":
                    group_key = set_group_key(pattern="2")  # 群聊监听关键词列表
                    if len(group_key) < 1:  # 没有关键词时
                        return
                    for i in group_key:  # 判断是否需要转发消息
                        if cont.find(i) == -1:
                            return
                    SendMessage(ctxTypeNumber=ctx_t, MsgType=MsgType_t, fromGroupId=q_uin, GroupName=group_name,
                                fromUin=uin,
                                times=time_text, content=cont, picUrl=picUrl_text, picBase64=Pic_Bs64,
                                voiceUrl=voiceUrl_text)
                    return
                # 群聊监听模式：UIN监听
                elif group_type == "1":
                    group_uin = set_group_uin(pattern="2")  # 群聊监听UIN列表
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
                    SendMessage(ctxTypeNumber=ctx_t, MsgType=MsgType_t, fromGroupId=q_uin, fromUin=uin, times=time_text,
                                content=cont, picUrl=picUrl_text, picBase64=Pic_Bs64, voiceUrl=voiceUrl_text)
                    return
                # 私聊监听模式：全部监听
                else:
                    # 判断是否为群文件消息
                    file_data = gp.file(ctx)
                    if file_data is not None:
                        file_id = action.getGroupFileURL(
                            group=ctx.FromGroupId, fileID=file_data.FileID)
                        file_name = file_data.FileName
                        file_size = file_data.FileSize
                        address = f"文件名:\n{file_name}\n文件大小{round(file_size / 1024 / 1024, 2)}MB\n来自群:{GroupName}({ctx.FromGroupId})\n来自用户:{ctx.FromNickName}({ctx.FromUserId})\n下载地址:\n{file_id['Url']}"
                        SendMessage(ctxTypeNumber=ctx_t, MsgType=MsgType_t, fromGroupId=q_uin, GroupName=group_name,
                                    fromUin=uin,
                                    times=time_text, content=address, picUrl=picUrl_text, picBase64=Pic_Bs64,
                                    voiceUrl=voiceUrl_text)
                        return
                    # 群聊监听模式：全部监听
                    SendMessage(ctxTypeNumber=ctx_t, MsgType=MsgType_t, fromGroupId=q_uin, fromUin=uin,
                                GroupName=group_name,
                                times=time_text, content=cont, picUrl=picUrl_text, picBase64=Pic_Bs64,
                                voiceUrl=voiceUrl_text)
                    return
        # 转发功能关闭
        else:
            return