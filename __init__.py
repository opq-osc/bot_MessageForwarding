"""私聊转发"""
from botoy import Action, GroupMsg, FriendMsg, decorators, jconfig, logger
from botoy.contrib import plugin_receiver, download, file_to_base64
from botoy.decorators import ignore_botself, startswith
from botoy.parser import group as gp  # 群消息(GroupMsg)相关解析
import json, re, time, httpx, demjson

action = Action(qq=jconfig.qq)

JSONPATH = './plugins/bot_MessageForwarding/MessageForwarding_data.json'  # 配置文件路径

bot_dict = {}

switch = ""  # 总开关阿
bot_uin = ""  # 机器人UIN
boss_uin = []  # 管理员UIN列表
friend_type = ""  # 私聊监听模式
friend_key = []  # 私聊监听关键词列表
friend_uin = []  # 私聊监听UIN列表
group_type = ""  # 群聊监听模式s
group_key = []  # 群聊监听关键词列表
group_uin = []  # 群聊监听UIN列表
relay_type = ""  # 转发模式
relay_friend_uin = []  # 转发私聊UIN列表
relay_group_uin = []  # 转发群聊UIN列表
relay_length_max = ""  # 转发文本限制最长长度
relay_length_min = ""  # 转发文本限制最短长度
blacklist_friend_uin = []  # 私聊UIN黑名单列表
blacklist_group_uin = []  # 群聊UIN黑名单列表
blacklist_friend_key = []  # 私聊关键词黑名单列表
blacklist_group_key = []  # 群聊关键词黑名单列表
reply_type = ""  # 回复模式


# 判断字符串是否全为数字
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


# 读取配置
def get_json_data(json_path):
    # 获取json里面数据

    with open(json_path, 'rb') as f:
        # 定义为只读模型，并定义名称为f

        params = json.load(f)
        # 加载json文件中的内容给params

        # params['data']['switch'] = "0"
        # 修改内容

        # print("params", params)
        # 打印

        dict = params
        # 将修改后的内容保存在dict中

    f.close()
    # 关闭json读模式

    return dict
    # 返回dict字典内容


# 保存所有配置
def write_json_data(json_dict):
    # 写入json文件
    # print(dict)
    with open(JSONPATH, 'w') as r:
        # 定义为写模式，名称定义为r

        json.dump(json_dict, r)
        # 将dict写入名称为r的文件中

    r.close()
    # 关闭json写模式


# 设置总开关
def set_switch(json_dict, text="0"):
    if text == "0":
        json_dict['data']['switch'] = "0"
        write_json_data(json_dict)
        return "关闭监听转发成功"
    elif text == "1":
        json_dict['data']['switch'] = "1"
        write_json_data(json_dict)
        return "打开监听转发成功"
    elif text == "2":  # 返回设置
        return str(json_dict['data']['switch'])
    else:  # 默认关闭
        json_dict['data']['switch'] = "0"
        write_json_data(json_dict)
        return "关闭监听转发成功"


# 设置管理员UIN列表
def set_boss_uin(json_dict, uin="", pattern="0"):
    global boss_uin

    boss_uin = []
    uin_i = -1  # 判断uin是否存在
    a = 0
    try:
        for i in json_dict['data']['boss_uin']:
            if i == uin and uin != "":
                uin_i = a
            boss_uin.append(i)  # 添加
            a = a + 1
    except Exception as e:
        logger.warning(f"管理员UIN列表为空\r\n {e}")

    if pattern == "0":
        if uin != "":
            if uin_i == -1:
                if is_number(uin):
                    boss_uin.append(uin)
                    json_dict['data']['boss_uin'] = boss_uin
                    write_json_data(json_dict)
                    return "添加管理员UIN：" + uin + " 成功\n管理员UIN列表：" + str(boss_uin)
                else:
                    return "添加管理员UIN：" + uin + " 失败\nUIN必须全为数字"
            else:
                return "添加管理员UIN：" + uin + " 失败\nUIN已存在\n管理员UIN列表：" + str(boss_uin)
        else:
            return "UIN为空"
    elif pattern == "1":
        if uin != "":
            if uin_i == -1:
                return "删除管理员UIN：" + uin + " 失败\nUIN不存在\n管理员UIN列表：" + str(boss_uin)
            else:
                if is_number(uin):
                    del boss_uin[uin_i]
                    json_dict['data']['boss_uin'] = boss_uin
                    write_json_data(json_dict)
                    return "删除管理员UIN：" + uin + " 成功\n管理员UIN列表：" + str(boss_uin)
                else:
                    return "删除管理员UIN：" + uin + " 失败\nUIN必须全为数字"
        else:
            return "UIN为空"
    elif pattern == "2":  # 返回设置
        return str(boss_uin)
    else:
        return str(boss_uin)


# 设置私聊监听模式
def set_friend_type(json_dict, pattern="-1"):
    global friend_key, friend_uin
    if pattern == "-1":
        json_dict['data']['set'][0]['monitor'][0]['friend_type'] = "-1"
        write_json_data(json_dict)
        return "私聊监听模式：全部监听"
    elif pattern == "0":
        json_dict['data']['set'][0]['monitor'][0]['friend_type'] = "0"
        write_json_data(json_dict)

        friend_key = []
        try:
            for i in json_dict['data']['set'][0]['monitor'][0]['friend_key']:
                friend_key.append(i)  # 添加
        except Exception as e:
            logger.warning(f"监听私聊关键词列表为空\r\n {e}")
        return "私聊监听模式：关键词监听\n关键词列表：" + str(friend_key)
    elif pattern == "1":
        json_dict['data']['set'][0]['monitor'][0]['friend_type'] = "1"
        write_json_data(json_dict)

        friend_uin = []
        try:
            for i in json_dict['data']['set'][0]['monitor'][0]['friend_uin']:
                friend_uin.append(i)  # 添加
        except Exception as e:
            logger.warning(f"监听私聊UIN列表为空\r\n {e}")
        return "私聊监听模式：UIN监听\nUIN列表：" + str(friend_uin)
    elif pattern == "2":  # 返回设置
        return str(json_dict['data']['set'][0]['monitor'][0]['friend_type'])
    else:
        json_dict['data']['set'][0]['monitor'][0]['friend_type'] = "-1"
        write_json_data(json_dict)
        return "私聊监听模式：全部监听"


# 设置私聊监听关键词列表
def set_friend_key(json_dict, key="", pattern="0"):
    global friend_key

    friend_key = []
    key_i = -1  # 判断关键词是否存在
    a = 0
    try:
        for i in json_dict['data']['set'][0]['monitor'][0]['friend_key']:
            if i == key and key != "":
                key_i = a
            friend_key.append(i)  # 添加
            a = a + 1
    except Exception as e:
        logger.warning(f"监听私聊关键词列表为空\r\n {e}")

    if pattern == "0":
        if key != "":
            if key_i == -1:
                friend_key.append(key)
                json_dict['data']['set'][0]['monitor'][0]['friend_key'] = friend_key
                write_json_data(json_dict)
                return "添加私聊监听关键词：" + key + " 成功\n关键词列表：" + str(friend_key)
            else:
                return "添加私聊监听关键词：" + key + " 失败\n关键词已存在\n关键词列表：" + str(friend_key)
        else:
            return "关键词为空"
    elif pattern == "1":
        if key != "":
            if key_i == -1:
                return "删除私聊监听关键词：" + key + " 失败\n关键词不存在\n关键词列表：" + str(friend_key)
            else:
                del friend_key[key_i]
                json_dict['data']['set'][0]['monitor'][0]['friend_key'] = friend_key
                write_json_data(json_dict)
                return "删除私聊监听关键词：" + key + " 成功\n关键词列表：" + str(friend_key)
        else:
            return "关键词为空"
    elif pattern == "2":  # 返回设置
        return str(friend_key)
    else:
        return str(friend_key)


# 设置私聊监听UIN列表
def set_friend_uin(json_dict, uin="", pattern="0"):
    global friend_uin

    friend_uin = []
    uin_i = -1  # 判断关键词是否存在
    a = 0
    try:
        for i in json_dict['data']['set'][0]['monitor'][0]['friend_uin']:
            if i == uin and uin != "":
                uin_i = a
            friend_uin.append(i)  # 添加
            a = a + 1
    except Exception as e:
        logger.warning(f"监听私聊UIN列表为空\r\n {e}")

    if pattern == "0":
        if uin != "":
            if uin_i == -1:
                if is_number(uin):
                    friend_uin.append(uin)
                    json_dict['data']['set'][0]['monitor'][0]['friend_uin'] = friend_uin
                    write_json_data(json_dict)
                    return "添加私聊监听UIN：" + uin + " 成功\nUIN列表：" + str(friend_uin)
                else:
                    return "添加私聊监听UIN：" + uin + " 失败\nUIN必须全为数字"
            else:
                return "添加私聊监听UIN：" + uin + " 失败\nUIN已存在\nUIN列表：" + str(friend_uin)
        else:
            return "UIN为空"
    elif pattern == "1":
        if uin != "":
            if uin_i == -1:
                return "删除私聊监听UIN：" + uin + " 失败\nUIN不存在\n关键词列表：" + str(friend_uin)
            else:
                if is_number(uin):
                    del friend_uin[uin_i]
                    json_dict['data']['set'][0]['monitor'][0]['friend_uin'] = friend_uin
                    write_json_data(json_dict)
                    return "删除私聊监听UIN：" + uin + " 成功\nUIN列表：" + str(friend_uin)
                else:
                    return "删除私聊监听UIN：" + uin + " 失败\nUIN必须全为数字"
        else:
            return "UIN为空"
    elif pattern == "2":  # 返回设置
        return str(friend_uin)
    else:
        return str(friend_uin)


# 设置群聊监听模式
def set_group_type(json_dict, pattern="-1"):
    global group_key, group_uin
    if pattern == "-1":
        json_dict['data']['set'][0]['monitor'][1]['group_type'] = "-1"
        write_json_data(json_dict)
        return "群聊监听模式：全部监听"
    elif pattern == "0":
        json_dict['data']['set'][0]['monitor'][1]['group_type'] = "0"
        write_json_data(json_dict)

        group_key = []
        try:
            for i in json_dict['data']['set'][0]['monitor'][1]['group_key']:
                group_key.append(i)  # 添加
        except Exception as e:
            logger.warning(f"监听群聊关键词列表为空\r\n {e}")
        return "群聊监听模式：关键词监听\n关键词列表：" + str(group_key)
    elif pattern == "1":
        json_dict['data']['set'][0]['monitor'][1]['group_type'] = "1"
        write_json_data(json_dict)

        group_uin = []
        try:
            for i in json_dict['data']['set'][0]['monitor'][1]['group_uin']:
                group_uin.append(i)  # 添加
        except Exception as e:
            logger.warning(f"监听群聊UIN列表为空\r\n {e}")
        return "群聊监听模式：UIN监听\nUIN列表：" + str(group_uin)
    elif pattern == "2":  # 返回设置
        json_dict['data']['set'][0]['monitor'][1]['group_type'] = "2"
        write_json_data(json_dict)
        return "群聊监听模式：关闭"
    elif pattern == "3":  # 返回设置
        return str(json_dict['data']['set'][0]['monitor'][1]['group_type'])
    else:
        json_dict['data']['set'][0]['monitor'][1]['group_type'] = "-1"
        write_json_data(json_dict)
        return "群聊监听模式：全部监听"


# 设置群聊监听关键词列表
def set_group_key(json_dict, key="", pattern="0"):
    global group_key

    group_key = []
    key_i = -1  # 判断关键词是否存在
    a = 0
    try:
        for i in json_dict['data']['set'][0]['monitor'][1]['group_key']:
            if i == key and key != "":
                key_i = a
            group_key.append(i)  # 添加s
            a = a + 1
    except Exception as e:
        logger.warning(f"监听群聊关键词列表为空\r\n {e}")

    if pattern == "0":
        if key != "":
            if key_i == -1:
                group_key.append(key)
                json_dict['data']['set'][0]['monitor'][1]['group_key'] = group_key
                write_json_data(json_dict)
                return "添加群聊监听关键词：" + key + " 成功\n关键词列表：" + str(group_key)
            else:
                return "添加群聊监听关键词：" + key + " 失败\n关键词已存在\n关键词列表：" + str(group_key)
        else:
            return "关键词为空"
    elif pattern == "1":
        if key != "":
            if key_i == -1:
                return "删除群聊监听关键词：" + key + " 失败\n关键词不存在\n关键词列表：" + str(group_key)
            else:
                del group_key[key_i]
                json_dict['data']['set'][0]['monitor'][1]['group_key'] = group_key
                write_json_data(json_dict)
                return "删除群聊监听关键词：" + key + " 成功\n关键词列表：" + str(group_key)
        else:
            return "关键词为空"
    elif pattern == "2":  # 返回设置
        return str(group_key)
    else:
        return str(group_key)


# 设置群聊监听UIN列表
def set_group_uin(json_dict, uin="", pattern="0"):
    global group_uin

    group_uin = []
    uin_i = -1  # 判断关键词是否存在
    a = 0
    try:
        for i in json_dict['data']['set'][0]['monitor'][1]['group_uin']:
            if i == uin and uin != "":
                uin_i = a
            group_uin.append(i)  # 添加
            a = a + 1
    except Exception as e:
        logger.warning(f"监听群聊UIN列表为空\r\n {e}")

    if pattern == "0":
        if uin != "":
            if uin_i == -1:
                if is_number(uin):
                    group_uin.append(uin)
                    json_dict['data']['set'][0]['monitor'][1]['group_uin'] = group_uin
                    write_json_data(json_dict)
                    return "添加群聊监听UIN：" + uin + " 成功\nUIN列表：" + str(group_uin)
                else:
                    return "添加群聊监听UIN：" + uin + " 失败\nUIN必须全为数字"
            else:
                return "添加群聊监听UIN：" + uin + " 失败\nUIN已存在\nUIN列表：" + str(group_uin)
        else:
            return "UIN为空"
    elif pattern == "1":
        if uin != "":
            if uin_i == -1:
                return "删除群聊监听UIN：" + uin + " 失败\nUIN不存在\n关键词列表：" + str(group_uin)
            else:
                if is_number(uin):
                    del group_uin[uin_i]
                    json_dict['data']['set'][0]['monitor'][1]['group_uin'] = group_uin
                    write_json_data(json_dict)
                    return "删除群聊监听UIN：" + uin + " 成功\nUIN列表：" + str(group_uin)
                else:
                    return "删除群聊监听UIN：" + uin + " 失败\nUIN必须全为数字"
        else:
            return "UIN为空"
    elif pattern == "2":  # 返回设置
        return str(group_uin)
    else:
        return str(group_uin)


# 设置转发模式
def set_relay_type(json_dict, pattern="1"):
    global relay_type, relay_group_uin, relay_friend_uin
    if pattern == "-1":
        json_dict['data']['set'][0]['relay'][0]['type'] = "-1"
        write_json_data(json_dict)

        relay_group_uin = []
        relay_friend_uin = []

        try:
            for i in json_dict['data']['set'][0]['relay'][0]['uin'][1]['group_uin']:
                relay_group_uin.append(i)  # 添加
            for i in json_dict['data']['set'][0]['relay'][0]['uin'][0]['friend_uin']:
                relay_friend_uin.append(i)  # 添加
        except Exception as e:
            logger.warning(f"转发列表为空\r\n {e}")
        return "转发模式：全部转发\n私聊UIN列表：" + str(relay_friend_uin) + "\n群聊UIN列表：" + str(relay_group_uin)
    elif pattern == "0":
        json_dict['data']['set'][0]['relay'][0]['type'] = "0"
        write_json_data(json_dict)

        relay_group_uin = []
        try:
            for i in json_dict['data']['set'][0]['relay'][0]['uin'][1]['group_uin']:
                relay_group_uin.append(i)  # 添加
        except Exception as e:
            logger.warning(f"群聊转发列表为空\r\n {e}")
        return "转发模式：群聊UIN转发\n群聊UIN列表：" + str(relay_group_uin)
    elif pattern == "1":
        json_dict['data']['set'][0]['relay'][0]['type'] = "1"
        write_json_data(json_dict)

        relay_friend_uin = []
        try:
            for i in json_dict['data']['set'][0]['relay'][0]['uin'][0]['friend_uin']:
                relay_friend_uin.append(i)  # 添加
        except Exception as e:
            logger.warning(f"私聊转发列表为空\r\n {e}")
        return "转发模式：私聊UIN转发\n私聊UIN列表：" + str(relay_friend_uin)
    elif pattern == "2":  # 返回设置
        return str(json_dict['data']['set'][0]['relay'][0]['type'])
    else:
        json_dict['data']['set'][0]['relay'][0]['type'] = "1"
        write_json_data(json_dict)

        relay_friend_uin = []
        try:
            for i in json_dict['data']['set'][0]['relay'][0]['uin'][0]['friend_uin']:
                relay_friend_uin.append(i)  # 添加
        except Exception as e:
            logger.warning(f"私聊转发列表为空\r\n {e}")
        return "转发模式：私聊UIN转发\n私聊UIN列表：" + str(relay_friend_uin)


# 设置转发私聊UIN列表
def set_relay_friend_uin(json_dict, uin="", pattern="0"):
    global relay_friend_uin

    relay_friend_uin = []
    uin_i = -1  # 判断关键词是否存在
    a = 0
    try:
        for i in json_dict['data']['set'][0]['relay'][0]['uin'][0]['friend_uin']:
            if i == uin and uin != "":
                uin_i = a
            relay_friend_uin.append(i)  # 添加
            a = a + 1
    except Exception as e:
        logger.warning(f"转发私聊UIN列表为空\r\n {e}")

    if pattern == "0":
        if uin != "":
            if uin_i == -1:
                if is_number(uin):
                    relay_friend_uin.append(uin)
                    json_dict['data']['set'][0]['relay'][0]['uin'][0]['friend_uin'] = relay_friend_uin
                    write_json_data(json_dict)
                    return "添加转发私聊UIN：" + uin + " 成功\nUIN列表：" + str(relay_friend_uin)
                else:
                    return "添加转发私聊UIN：" + uin + " 失败\nUIN必须全为数字"
            else:
                return "添加转发私聊UIN：" + uin + " 失败\nUIN已存在\nUIN列表：" + str(relay_friend_uin)
        else:
            return "UIN为空"
    elif pattern == "1":
        if uin != "":
            if uin_i == -1:
                return "删除转发私聊UIN：" + uin + " 失败\nUIN不存在\nUIN列表：" + str(relay_friend_uin)
            else:
                if is_number(uin):
                    del relay_friend_uin[uin_i]
                    json_dict['data']['set'][0]['relay'][0]['uin'][0]['friend_uin'] = relay_friend_uin
                    write_json_data(json_dict)
                    return "删除转发私聊UIN：" + uin + " 成功\nUIN列表：" + str(relay_friend_uin)
                else:
                    return "删除转发私聊UIN：" + uin + " 失败\nUIN必须全为数字"
        else:
            return "UIN为空"
    elif pattern == "2":  # 返回设置
        return str(relay_friend_uin)
    else:
        return str(relay_friend_uin)


# 设置转发群聊UIN列表
def set_relay_group_uin(json_dict, uin="", pattern="0"):
    global relay_group_uin

    relay_group_uin = []
    uin_i = -1  # 判断关键词是否存在
    a = 0
    try:
        for i in json_dict['data']['set'][0]['relay'][0]['uin'][1]['group_uin']:
            if i == uin and uin != "":
                uin_i = a
            relay_group_uin.append(i)  # 添加
            a = a + 1
    except Exception as e:
        logger.warning(f"转发群聊UIN列表为空\r\n {e}")

    if pattern == "0":
        if uin != "":
            if uin_i == -1:
                if is_number(uin):
                    relay_group_uin.append(uin)
                    json_dict['data']['set'][0]['relay'][0]['uin'][1]['group_uin'] = relay_group_uin
                    write_json_data(json_dict)
                    return "添加转发群聊UIN：" + uin + " 成功\nUIN列表：" + str(relay_group_uin)
                else:
                    return "添加转发群聊UIN：" + uin + " 失败\nUIN必须全为数字"
            else:
                return "添加转发群聊UIN：" + uin + " 失败\nUIN已存在\nUIN列表：" + str(relay_group_uin)
        else:
            return "UIN为空"
    elif pattern == "1":
        if uin != "":
            if uin_i == -1:
                return "删除转发群聊UIN：" + uin + " 失败\nUIN不存在\nUIN列表：" + str(relay_group_uin)
            else:
                if is_number(uin):
                    del relay_group_uin[uin_i]
                    json_dict['data']['set'][0]['relay'][0]['uin'][1]['group_uin'] = relay_group_uin
                    write_json_data(json_dict)
                    return "删除转发群聊UIN：" + uin + " 成功\nUIN列表：" + str(relay_group_uin)
                else:
                    return "删除转发群聊UIN：" + uin + " 失败\nUIN必须全为数字"
        else:
            return "UIN为空"
    elif pattern == "2":  # 返回设置
        return str(relay_group_uin)
    else:
        return str(relay_group_uin)


# 设置转发文本限制最长长度
def set_relay_length_max(json_dict, length=-1):
    if length < 1 and length != -1 and length != -2:
        return "文本长度必须大于0"
    elif length == -1:  # 无限制
        json_dict['data']['set'][0]['relay'][0]['length'][0]['max'] = str(length)
        write_json_data(json_dict)
        return "设置成功，转发文本最长长度无限制"
    elif length == -2:  # 返回设置
        return "转发文本限制最长长度为：" + str(json_dict['data']['set'][0]['relay'][0]['length'][0]['max'])
    else:
        try:
            json_dict['data']['set'][0]['relay'][0]['length'][0]['max'] = str(length)
            write_json_data(json_dict)
            return "设置成功，转发文本限制最长长度为：" + str(length)
        except Exception as e:
            logger.warning(f"设置转发文本限制最长长度失败\r\n {e}")
            return "设置失败"
            
            
# 设置转发文本限制最短长度
def set_relay_length_min(json_dict, length=-1):
    if length < 1 and length != -1 and length != -2:
        return "文本长度必须大于0"
    elif length == -1:  # 无限制
        json_dict['data']['set'][0]['relay'][0]['length'][1]['min'] = str(length)
        write_json_data(json_dict)
        return "设置成功，转发文本最短长度无限制"
    elif length == -2:  # 返回设置
        return "转发文本限制最短长度为：" + str(json_dict['data']['set'][0]['relay'][0]['length'][1]['min'])
    else:
        try:
            json_dict['data']['set'][0]['relay'][0]['length'][1]['min'] = str(length)
            write_json_data(json_dict)
            return "设置成功，转发文本限制最短长度为：" + str(length)
        except Exception as e:
            logger.warning(f"设置转发文本限制最短长度失败\r\n {e}")
            return "设置失败"


# 设置私聊UIN黑名单列表
def set_blacklist_friend_uin(json_dict, uin="", pattern="0"):
    global blacklist_friend_uin

    blacklist_friend_uin = []
    uin_i = -1  # 判断关键词是否存在
    a = 0
    try:
        for i in json_dict['data']['blacklist'][0]['friend_uin']:
            if i == uin and uin != "":
                uin_i = a
            blacklist_friend_uin.append(i)  # 添加
            a = a + 1
    except Exception as e:
        logger.warning(f"私聊UIN黑名单列表为空\r\n {e}")

    if pattern == "0":
        if uin != "":
            if uin_i == -1:
                if is_number(uin):
                    blacklist_friend_uin.append(uin)
                    json_dict['data']['blacklist'][0]['friend_uin'] = blacklist_friend_uin
                    write_json_data(json_dict)
                    return "添加私聊UIN黑名单：" + uin + " 成功\n私聊UIN黑名单列表：" + str(blacklist_friend_uin)
                else:
                    return "添加私聊UIN黑名单：" + uin + " 失败\nUIN必须全为数字"
            else:
                return "添加私聊UIN黑名单：" + uin + " 失败\nUIN已存在\n私聊UIN黑名单列表：" + str(blacklist_friend_uin)
        else:
            return "UIN为空"
    elif pattern == "1":
        if uin != "":
            if uin_i == -1:
                return "删除私聊UIN黑名单：" + uin + " 失败\nUIN不存在\n私聊UIN黑名单列表：" + str(blacklist_friend_uin)
            else:
                if is_number(uin):
                    del blacklist_friend_uin[uin_i]
                    json_dict['data']['blacklist'][0]['friend_uin'] = blacklist_friend_uin
                    write_json_data(json_dict)
                    return "删除私聊UIN黑名单：" + uin + " 成功\n私聊UIN黑名单列表：" + str(blacklist_friend_uin)
                else:
                    return "删除私聊UIN黑名单：" + uin + " 失败\nUIN必须全为数字"
        else:
            return "UIN为空"
    elif pattern == "2":  # 返回设置
        return str(blacklist_friend_uin)
    else:
        return str(blacklist_friend_uin)


# 设置群聊UIN黑名单列表
def set_blacklist_group_uin(json_dict, uin="", pattern="0"):
    global blacklist_group_uin

    blacklist_group_uin = []
    uin_i = -1  # 判断关键词是否存在
    a = 0
    try:
        for i in json_dict['data']['blacklist'][1]['group_uin']:
            if i == uin and uin != "":
                uin_i = a
            blacklist_group_uin.append(i)  # 添加
            a = a + 1
    except Exception as e:
        logger.warning(f"群聊UIN黑名单列表为空\r\n {e}")

    if pattern == "0":
        if uin != "":
            if uin_i == -1:
                if is_number(uin):
                    blacklist_group_uin.append(uin)
                    json_dict['data']['blacklist'][1]['group_uin'] = blacklist_group_uin
                    write_json_data(json_dict)
                    return "添加群聊UIN黑名单：" + uin + " 成功\n群聊UIN黑名单列表：" + str(blacklist_group_uin)
                else:
                    return "添加群聊UIN黑名单：" + uin + " 失败\nUIN必须全为数字"
            else:
                return "添加群聊UIN黑名单：" + uin + " 失败\nUIN已存在\n群聊UIN黑名单列表：" + str(blacklist_group_uin)
        else:
            return "UIN为空"
    elif pattern == "1":
        if uin != "":
            if uin_i == -1:
                return "删除群聊UIN黑名单：" + uin + " 失败\nUIN不存在\n群聊UIN黑名单列表：" + str(blacklist_group_uin)
            else:
                if is_number(uin):
                    del blacklist_group_uin[uin_i]
                    json_dict['data']['blacklist'][1]['group_uin'] = blacklist_group_uin
                    write_json_data(json_dict)
                    return "删除群聊UIN黑名单：" + uin + " 成功\n群聊UIN黑名单列表：" + str(blacklist_group_uin)
                else:
                    return "删除群聊UIN黑名单：" + uin + " 失败\nUIN必须全为数字"
        else:
            return "UIN为空"
    elif pattern == "2":  # 返回设置
        return str(blacklist_group_uin)
    else:
        return str(blacklist_group_uin)


# 设置私聊关键词黑名单列表
def set_blacklist_friend_key(json_dict, key="", pattern="0"):
    global blacklist_friend_key

    blacklist_friend_key = []
    key_i = -1  # 判断关键词是否存在
    a = 0
    try:
        for i in json_dict['data']['blacklist'][2]['friend_key']:
            if i == key and key != "":
                key_i = a
            blacklist_friend_key.append(i)  # 添加
            a = a + 1
    except Exception as e:
        logger.warning(f"私聊关键词黑名单列表为空\r\n {e}")

    if pattern == "0":
        if key != "":
            if key_i == -1:
                blacklist_friend_key.append(key)
                json_dict['data']['blacklist'][2]['friend_key'] = blacklist_friend_key
                write_json_data(json_dict)
                return "添加私聊关键词黑名单：" + key + " 成功\n私聊关键词黑名单列表：" + str(blacklist_friend_key)
            else:
                return "添加私聊关键词黑名单：" + key + " 失败\n关键词已存在\n私聊关键词黑名单列表：" + str(blacklist_friend_key)
        else:
            return "关键词为空"
    elif pattern == "1":
        if key != "":
            if key_i == -1:
                return "删除私聊关键词黑名单：" + key + " 失败\n关键词不存在\n私聊关键词黑名单列表：" + str(blacklist_friend_key)
            else:
                del blacklist_friend_key[key_i]
                json_dict['data']['blacklist'][2]['friend_key'] = blacklist_friend_key
                write_json_data(json_dict)
                return "删除私聊关键词黑名单：" + key + " 成功\n私聊关键词黑名单列表：" + str(blacklist_friend_key)
        else:
            return "关键词为空"
    elif pattern == "2":  # 返回设置
        return str(blacklist_friend_key)
    else:
        return str(blacklist_friend_key)


# 设置群聊关键词黑名单列表
def set_blacklist_group_key(json_dict, key="", pattern="0"):
    global blacklist_group_key

    blacklist_group_key = []
    key_i = -1  # 判断关键词是否存在
    a = 0
    try:
        for i in json_dict['data']['blacklist'][3]['group_key']:
            if i == key and key != "":
                key_i = a
            blacklist_group_key.append(i)  # 添加
            a = a + 1
    except Exception as e:
        logger.warning(f"群聊关键词黑名单列表为空\r\n {e}")

    if pattern == "0":
        if key != "":
            if key_i == -1:
                blacklist_group_key.append(key)
                json_dict['data']['blacklist'][3]['group_key'] = blacklist_group_key
                write_json_data(json_dict)
                return "添加群聊关键词黑名单：" + key + " 成功\n群聊关键词黑名单列表：" + str(blacklist_group_key)
            else:
                return "添加群聊关键词黑名单：" + key + " 失败\n关键词已存在\n群聊关键词黑名单列表：" + str(blacklist_group_key)
        else:
            return "关键词为空"
    elif pattern == "1":
        if key != "":
            if key_i == -1:
                return "删除群聊关键词黑名单：" + key + " 失败\n关键词不存在\n群聊关键词黑名单列表：" + str(blacklist_group_key)
            else:
                del blacklist_group_key[key_i]
                json_dict['data']['blacklist'][3]['group_key'] = blacklist_group_key
                write_json_data(json_dict)
                return "删除群聊关键词黑名单：" + key + " 成功\n群聊关键词黑名单列表：" + str(blacklist_group_key)
        else:
            return "关键词为空"
    elif pattern == "2":  # 返回设置
        return str(blacklist_group_key)
    else:
        return str(blacklist_group_key)


# 设置回复模式
def set_reply_type(json_dict, pattern="1"):
    if pattern == "0":
        json_dict['data']['reply'][0]['type'] = "0"
        write_json_data(json_dict)
        return "回复模式设置成功\n当上一条消息为转发消息时，默认需要回复的UIN与上条消息相同：关闭"
    elif pattern == "1":
        json_dict['data']['reply'][0]['type'] = "1"
        write_json_data(json_dict)
        return "回复模式设置成功\n当上一条消息为转发消息时，默认需要回复的UIN与上条消息相同：开启"
    elif pattern == "2":  # 返回设置
        return str(json_dict['data']['reply'][0]['type'])
    else:  # 默认开启
        json_dict['data']['reply'][0]['type'] = "1"
        write_json_data(json_dict)
        return "回复模式设置成功\n当上一条消息为转发消息时，默认需要回复的UIN与上条消息相同：开启"


# 配置全解析
def format_json_data(json_dict):
    global bot_dict, switch, bot_uin, boss_uin, friend_type, friend_key, friend_uin, group_type, group_key, group_uin, relay_type, relay_friend_uin, relay_group_uin, relay_length_max, relay_length_min, blacklist_friend_uin, blacklist_group_uin, blacklist_friend_key, blacklist_group_key, reply_type

    switch = ""  # 总开关
    switch = json_dict['data']['switch']  # 0关，非0开

    bot_uin = ""  # 机器人UIN
    bot_uin = json_dict['data']['bot_uin']  # 机器人UIN

    boss_uin = []
    try:
        for i in json_dict['data']['boss_uin']:
            boss_uin.append(i)  # 添加
    except Exception as e:
        logger.warning(f"管理员UIN列表为空\r\n {e}")

    # 私聊监听设置
    friend_type = ""  # 私聊监听模式
    friend_type = json_dict['data']['set'][0]['monitor'][0]['friend_type']  # -1全部监听，0关键词监听，其他UIN监听
    if friend_type == "-1":
        friend_type_text = "全部监听"
    elif friend_type == "0":
        friend_type_text = "关键词监听"

        friend_key = []  # 私聊监听关键词列表
        try:
            for i in json_dict['data']['set'][0]['monitor'][0]['friend_key']:
                friend_key.append(i)  # 添加
        except Exception as e:
            logger.warning(f"监听私聊关键词列表为空\r\n {e}")
    else:
        friend_type_text = "UIN监听"

        friend_uin = []  # 私聊监听UIN列表
        try:
            for i in json_dict['data']['set'][0]['monitor'][0]['friend_uin']:
                friend_uin.append(i)  # 添加
        except Exception as e:
            logger.warning(f"监听私聊UIN列表为空\r\n {e}")

    # 群聊监听设置
    group_type = ""  # 群聊监听模式
    group_type = json_dict['data']['set'][0]['monitor'][1]['group_type']  # -1全部监听，0关键词监听，1UIN监听，其他关闭
    if group_type == "-1":
        group_type_text = "全部监听"
    elif group_type == "0":
        group_type_text = "关键词监听"

        group_key = []  # 群聊监听关键词列表
        try:
            for i in json_dict['data']['set'][0]['monitor'][1]['group_key']:
                group_key.append(i)  # 添加
        except Exception as e:
            logger.warning(f"监听群聊关键词列表为空\r\n {e}")
    elif group_type == "1":
        group_type_text = "UIN监听"

        group_uin = []  # 群聊监听UIN列表
        try:
            for i in json_dict['data']['set'][0]['monitor'][1]['group_uin']:
                group_uin.append(i)  # 添加
        except Exception as e:
            logger.warning(f"监听群聊UIN列表为空\r\n {e}")
    else:
        group_type_text = "关闭"

    # 转发
    relay_type = ""  # 转发模式
    relay_type = json_dict['data']['set'][0]['relay'][0]['type']  # -1全部转发，0群聊UIN转发,其他私聊UIN转发
    if relay_type == "-1":
        relay_type_text = "全部转发"

        relay_friend_uin = []  # 转发私聊UIN列表
        relay_group_uin = []  # 转发群聊UIN列表
        try:
            for i in json_dict['data']['set'][0]['relay'][0]['uin'][1]['group_uin']:
                relay_group_uin.append(i)  # 添加
            for i in json_dict['data']['set'][0]['relay'][0]['uin'][0]['friend_uin']:
                relay_friend_uin.append(i)  # 添加
        except Exception as e:
            logger.warning(f"转发列表为空\r\n {e}")
    elif relay_type == "0":
        relay_type_text = "群聊UIN转发"

        relay_group_uin = []  # 转发群聊UIN列表
        try:
            for i in json_dict['data']['set'][0]['relay'][0]['uin'][1]['group_uin']:
                relay_group_uin.append(i)  # 添加
        except Exception as e:
            logger.warning(f"转发群聊UIN列表为空\r\n {e}")
    else:
        relay_type_text = "私聊UIN转发"

        relay_friend_uin = []  # 转发私聊UIN列表
        try:
            for i in json_dict['data']['set'][0]['relay'][0]['uin'][0]['friend_uin']:
                relay_friend_uin.append(i)  # 添加
        except Exception as e:
            logger.warning(f"转发私聊UIN列表为空\r\n {e}")

    # 转发文本限制长度
    relay_length_max = ""
    relay_length_max = json_dict['data']['set'][0]['relay'][0]['length'][0]['max']
    relay_length_min = ""
    relay_length_min = json_dict['data']['set'][0]['relay'][0]['length'][1]['min']
    print("转发文本限制长度为：" + str(relay_length_min)+"~"+ str(relay_length_max))

    # 黑名单
    blacklist_friend_uin = []  # 私聊UIN黑名单列表
    blacklist_group_uin = []  # 群聊UIN黑名单列表
    blacklist_friend_key = []  # 私聊关键词黑名单列表
    blacklist_group_key = []  # 群聊关键词黑名单列表
    try:
        for i in json_dict['data']['blacklist'][0]['friend_uin']:
            blacklist_friend_uin.append(i)  # 添加
        for i in json_dict['data']['blacklist'][1]['group_uin']:
            blacklist_group_uin.append(i)  # 添加
        for i in json_dict['data']['blacklist'][2]['friend_key']:
            blacklist_friend_key.append(i)  # 添加
        for i in json_dict['data']['blacklist'][3]['group_key']:
            blacklist_group_key.append(i)  # 添加
    except Exception as e:
        logger.warning(f"黑名单UIN列表为空\r\n {e}")

    # 回复设置
    reply_type = ""  # 回复模式
    reply_type = json_dict['data']['reply'][0]['type']  # 0关，非0开
    if reply_type == "0":
        reply_type_text = "当上一条消息为转发消息时，默认需要回复的UIN与上条消息相同：关闭"
    else:
        reply_type_text = "当上一条消息为转发消息时，默认需要回复的UIN与上条消息相同：开启"

    write_json_data(json_dict)  # 保存配置

    return switch.replace("0", "关闭").replace("1", "开启") + "\n" + "机器人UIN：" + bot_uin + "\n管理员UIN列表：" + str(
        boss_uin) + "\n监听：\n私聊设置：\n模式：\n" + friend_type_text + "\n关键词列表：" + str(
        friend_key) + "\nUIN列表：" + str(friend_uin) + "\n群聊设置：\n模式：\n" + group_type_text + "\nUIN列表：" + str(
        group_uin) + "\n关键词列表：" + str(group_key) + "\n转发：\n模式：\n" + relay_type_text + "\n私聊UIN列表：" + str(
        relay_friend_uin) + "\n群聊UIN列表：" + str(relay_group_uin) + "\n转发文本限制长度为：" +str(relay_length_min)+"~"+ str(relay_length_max) +"\n黑名单：\n" + "私聊UIN黑名单列表：" + str(blacklist_friend_uin) + "\n群聊UIN黑名单列表：" + str(blacklist_group_uin) + "\n私聊关键词黑名单列表：" + str(blacklist_friend_key) + "\n群聊关键词黑名单列表：" + str(blacklist_group_key) + "\n" + reply_type_text


bot_dict = get_json_data(JSONPATH)
print(format_json_data(bot_dict))


# 获取QQ昵称
def get_name(uin):
    try:
        getSummaryCard_name = action.getSummaryCard(int(uin))['NickName']
        if len(getSummaryCard_name.replace(" ", "").replace("\r", "").replace("\n", "")) > 0:
            return getSummaryCard_name
    except Exception as e:
        logger.warning(f"getSummaryCard昵称请求失败\r\n {e},{uin}")
    url = "http://xiaoapi.cn/api/qqnick.php"
    params = {
        "qq": uin
    }
    try:
        res = httpx.get(url, params=params).text
        if res.find("<html>") != -1:
            return str(uin)
    except Exception as e:
        logger.warning(f"昵称请求失败\r\n {e}")
        return str(uin)
    return res


# 获取回复人UIN
def get_ReplyUin(text, reply_text):
    result = re.findall("(\(.*\))", text)
    if len(result) < 1:
        result = re.findall("(\(.*\))", reply_text)
    try:
        return int(result[0].replace("(", "").replace(")", ""))
    except Exception as e:
        return 1340219674


@ignore_botself  # 忽略机器人自身的消息
def receive_friend_msg(ctx: FriendMsg):
    # 判断是否是管理员
    global Pic_Md5
    boss_i = 0
    for i in boss_uin:
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
            if len(boss_uin) > 1:
                action.sendFriendText(user=ctx.FromUin, content=set_boss_uin(bot_dict, uin=boss_uin_pattern, pattern="1"))
            else:
                action.sendFriendText(user=ctx.FromUin, content="删除失败\n仅剩一位管理员，如果需要删除请手动删除\n管理员UIN列表：" + str(boss_uin))
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
                                  content=set_friend_type(bot_dict, pattern="2").replace("-1", "私聊监听模式：全部监听").replace("0",
                                                                                                                      friend_key_pattern).replace(
                                      "1", friend_uin_pattern))
        # 设置与查看私聊监听关键词列表
        elif cont.startswith("添加私聊监听关键词"):
            friend_key_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_friend_key(bot_dict, key=friend_key_pattern, pattern="0"))
        elif cont.startswith("删除私聊监听关键词"):
            friend_key_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_friend_key(bot_dict, key=friend_key_pattern, pattern="1"))
        elif cont == "私聊监听关键词查看" or cont == "查看私聊监听关键词":
            action.sendFriendText(user=ctx.FromUin, content=set_friend_key(bot_dict, pattern="2"))
        # 设置与查看私聊监听UIN列表
        elif cont.startswith("添加私聊监听UIN") or cont.startswith("添加私聊监听uin"):
            friend_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_friend_uin(bot_dict, uin=friend_uin_pattern, pattern="0"))
        elif cont.startswith("删除私聊监听UIN") or cont.startswith("删除私聊监听uin"):
            friend_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_friend_uin(bot_dict, uin=friend_uin_pattern, pattern="1"))
        elif cont == "私聊监听UIN查看" or cont == "查看私聊监听UIN" or cont == "私聊监听uin查看" or cont == "查看私聊监听uin":
            action.sendFriendText(user=ctx.FromUin, content=set_friend_uin(bot_dict, pattern="2"))
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
                                  content=set_group_type(bot_dict, pattern="3").replace("-1", "群聊监听模式：全部监听").replace("0",
                                                                                                                     group_key_pattern).replace(
                                      "1", group_uin_pattern).replace("2", "群聊监听模式：关闭"))
        # 设置与查看群聊监听关键词列表
        elif cont.startswith("添加群聊监听关键词"):
            group_key_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_group_key(bot_dict, key=group_key_pattern, pattern="0"))
        elif cont.startswith("删除群聊监听关键词"):
            group_key_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_group_key(bot_dict, key=group_key_pattern, pattern="1"))
        elif cont == "群聊监听关键词查看" or cont == "查看群聊监听关键词":
            action.sendFriendText(user=ctx.FromUin, content=set_group_key(bot_dict, pattern="2"))
        # 设置与查看群聊监听UIN列表
        elif cont.startswith("添加群聊监听UIN") or cont.startswith("添加群聊监听uin"):
            group_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_group_uin(bot_dict, uin=group_uin_pattern, pattern="0"))
        elif cont.startswith("删除群聊监听UIN") or cont.startswith("删除群聊监听uin"):
            group_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin, content=set_group_uin(bot_dict, uin=group_uin_pattern, pattern="1"))
        elif cont == "群聊监听UIN查看" or cont == "查看群聊监听UIN" or cont == "群聊监听uin查看" or cont == "查看群聊监听uin":
            action.sendFriendText(user=ctx.FromUin, content=set_group_uin(bot_dict, pattern="2"))
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
            relay_all_uin_pattern = "转发模式：全部转发\n私聊UIN列表：" + str(relay_friend_uin) + "\n群聊UIN列表：" + str(relay_group_uin)
            relay_friend_uin_pattern = "转发模式：私聊UIN转发\n私聊UIN列表：" + str(relay_friend_uin)
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
                                  content=set_relay_group_uin(bot_dict, uin=relay_group_uin_pattern, pattern="0"))
        elif cont.startswith("删除转发群聊UIN") or cont.startswith("删除转发群聊uin"):
            relay_group_uin_pattern = cont[9:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_relay_group_uin(bot_dict, uin=relay_group_uin_pattern, pattern="1"))
        elif cont == "转发群聊UIN查看" or cont == "查看转发群聊UIN" or cont == "转发私聊uin查看" or cont == "查看转发私聊uin":
            action.sendFriendText(user=ctx.FromUin, content=set_relay_group_uin(bot_dict, pattern="2"))
        # 设置与查看转发文本限制长度
        elif cont.startswith("设置转发文本限制最长长度"):
            relay_length_text = cont[12:].replace("无限制", "-1")
            action.sendFriendText(user=ctx.FromUin, content=set_relay_length_max(bot_dict, length=int(relay_length_text)))
        elif cont.startswith("设置转发文本限制最短长度"):
            relay_length_text = cont[12:].replace("无限制", "-1")
            action.sendFriendText(user=ctx.FromUin, content=set_relay_length_min(bot_dict, length=int(relay_length_text)))
        elif cont == "转发文本限制长度查看" or cont == "查看转发文本限制长度":
            action.sendFriendText(user=ctx.FromUin, content=set_relay_length_min(bot_dict, length=-2)+"\n"+set_relay_length_max(bot_dict, length=-2))
        # 设置与查看转发私聊UIN黑名单列表
        elif cont.startswith("添加黑名单转发私聊UIN") or cont.startswith("添加黑名单转发私聊uin"):
            blacklist_friend_uin_pattern = cont.replace("添加黑名单转发私聊UIN", "").replace("添加黑名单转发私聊uin", "")
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_friend_uin(bot_dict, uin=blacklist_friend_uin_pattern, pattern="0"))
        elif cont.startswith("删除黑名单转发私聊UIN") or cont.startswith("删除黑名单转发私聊uin"):
            blacklist_friend_uin_pattern = cont.replace("删除黑名单转发私聊UIN", "").replace("删除黑名单转发私聊uin", "")
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_friend_uin(bot_dict, uin=blacklist_friend_uin_pattern, pattern="1"))
        elif cont == "转发私聊UIN黑名单查看" or cont == "查看转发私聊UIN黑名单" or cont == "转发私聊uin黑名单查看" or cont == "查看转发私聊uin黑名单":
            action.sendFriendText(user=ctx.FromUin, content=set_blacklist_friend_uin(bot_dict, pattern="2"))
        # 设置与查看转发群聊UIN黑名单列表
        elif cont.startswith("添加黑名单转发群聊UIN") or cont.startswith("添加黑名单转发群聊uin"):
            blacklist_group_uin_pattern = cont.replace("添加黑名单转发群聊UIN", "").replace("添加黑名单转发群聊uin", "")
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_group_uin(bot_dict, uin=blacklist_group_uin_pattern, pattern="0"))
        elif cont.startswith("删除黑名单转发群聊UIN") or cont.startswith("删除黑名单转发群聊uin"):
            blacklist_group_uin_pattern = cont.replace("删除黑名单转发群聊UIN", "").replace("删除黑名单转发群聊uin", "")
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_group_uin(bot_dict, uin=blacklist_group_uin_pattern, pattern="1"))
        elif cont == "转发群聊UIN黑名单查看" or cont == "查看转发群聊UIN黑名单" or cont == "转发群聊uin黑名单查看" or cont == "查看转发群聊uin黑名单":
            action.sendFriendText(user=ctx.FromUin, content=set_blacklist_group_uin(bot_dict, pattern="2"))
        # 设置与查看转发私聊关键词黑名单列表
        elif cont.startswith("添加转发私聊关键词黑名单"):
            blacklist_friend_key_pattern = cont[12:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_friend_key(bot_dict, key=blacklist_friend_key_pattern, pattern="0"))
        elif cont.startswith("删除转发私聊关键词黑名单"):
            blacklist_friend_key_pattern = cont[12:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_friend_key(bot_dict, key=blacklist_friend_key_pattern, pattern="1"))
        elif cont == "转发私聊关键词黑名单查看" or cont == "查看转发私聊关键词黑名单":
            action.sendFriendText(user=ctx.FromUin, content=set_blacklist_friend_key(bot_dict, pattern="2"))
        # 设置与查看转发群聊关键词黑名单列表
        elif cont.startswith("添加转发群聊关键词黑名单"):
            blacklist_group_key_pattern = cont[12:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_group_key(bot_dict, key=blacklist_group_key_pattern, pattern="0"))
        elif cont.startswith("删除转发群聊关键词黑名单"):
            blacklist_group_key_pattern = cont[12:]
            action.sendFriendText(user=ctx.FromUin,
                                  content=set_blacklist_group_key(bot_dict, key=blacklist_group_key_pattern, pattern="1"))
        elif cont == "转发群聊关键词黑名单查看" or cont == "查看转发群聊关键词黑名单":
            action.sendFriendText(user=ctx.FromUin, content=set_blacklist_group_key(bot_dict, pattern="2"))
        # 设置回复模式
        elif cont.startswith("设置回复模式"):
            reply_type_pattern = cont[6:].replace("关闭", "0").replace("关", "0").replace("开启", "1").replace("开", "1")
            if is_number(reply_type_pattern) and len(reply_type_pattern) <= 2:
                action.sendFriendText(user=ctx.FromUin, content=set_reply_type(bot_dict, pattern=reply_type_pattern))
            else:
                action.sendFriendText(user=ctx.FromUin, content="设置回复模式失败\n回复模式只有：开启、关闭 两种情况")
        # 查看回复模式
        elif cont == "回复模式状态" or cont == "查看回复模式":
            reply_type_on_pattern = "当上一条消息为转发消息时，默认需要回复的UIN与上条消息相同：开启"
            reply_type_off_pattern = "当上一条消息为转发消息时，默认需要回复的UIN与上条消息相同：关闭"
            action.sendFriendText(user=ctx.FromUin, content=set_reply_type(bot_dict, pattern="2").replace("0",
                                                                                                          reply_type_off_pattern).replace(
                "1", reply_type_on_pattern))
        # 帮助菜单
        elif cont == "监控转发菜单" or cont == "监控转发帮助":
            action.sendFriendPic(ctx.FromUin, picBase64Buf=file_to_base64('./plugins/bot_MessageForwarding/help2.png'))
        # 回复消息
        elif ctx.MsgType == "ReplayMsg":
            # 判断是否是管理员
            boss_i = 0
            for i in boss_uin:
                if str(ctx.FromUin) == i:
                    boss_i = 1
                    break
            if boss_i != 1:  # 如果为boss
                return
            reply_Pic = ""
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
        if switch == "1":  # 转发功能打开时
            friend_type = bot_dict['data']['set'][0]['monitor'][0]['friend_type']
            Uin = str(ctx.FromUin)  # 获取回复人UIN
            for i in blacklist_friend_uin:  # 判断是否私聊uin黑名单
                if i == Uin:
                    return

            cont = ctx.Content
            for i in blacklist_friend_key:  # 判断是否私聊关键词黑名单
                if cont.find(i) != -1:
                    return
            if friend_type == "-1":  # 私聊监听模式：全部监听
                time_text = time.strftime("%Y/%m/%d %H:%M:%S")  # 获取消息时间
                if ctx.MsgType == "TextMsg":  # 当为文本消息时
                    if relay_length_max != -1:  # 判断是否超出字数
                        if len(cont) > int(relay_length_max):
                            return
                    if relay_length_min != -1:  # 判断是否小于字数
                        if len(cont) < int(relay_length_min):
                            return
                    if relay_type == "-1":
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendText(int(i), "(" + Uin + ") " + get_name(
                                Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont + "”")
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i), "(" + Uin + ") " + get_name(
                                Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont + "”")
                        return
                    elif relay_type == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i), "(" + Uin + ") " + get_name(
                                Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont + "”")
                        return
                    else:
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                        if relay_length_max != -1:  # 判断是否超出字数
                            if len(cont_text) > int(relay_length_max):
                                return
                        if relay_length_min != -1:  # 判断是否小于字数
                            if len(cont_text) < int(relay_length_min):
                                return
                        if relay_type == "-1":
                            for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                        elif relay_type == "0":
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                        else:
                            for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                    except Exception as e:
                        # 仅为图片
                        if relay_type == "-1":
                            for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊")
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                        elif relay_type == "0":
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                        else:
                            for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                elif ctx.MsgType == "VoiceMsg":
                    data_text = demjson.decode(ctx.Content)  # 回复的消息的内容
                    voiceUrl_text = data_text['Url']
                    if relay_type == "-1":
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                    elif relay_type == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i),
                                                 "收到一条私聊语音(请在手机上查看)\n来自：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                            action.sendgroupVoice(group=int(i), voiceUrl=voiceUrl_text)
                        return
                    else:
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                    if relay_length_max != -1:  # 判断是否超出字数
                        if len(cont) > int(relay_length_max):
                            return
                    if relay_length_min != -1:  # 判断是否小于字数
                        if len(cont) < int(relay_length_min):
                            return
                    if relay_type == "-1":
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        return
                    elif relay_type == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        return
                    else:
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                        if relay_length_max != -1:  # 判断是否超出字数
                            if len(cont_text) > int(relay_length_max):
                                return
                        if relay_length_min != -1:  # 判断是否小于字数
                            if len(cont_text) < int(relay_length_min):
                                return
                        if relay_type == "-1":
                            for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                        elif relay_type == "0":
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                        else:
                            for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                    except Exception as e:
                        # 仅为图片
                        if relay_type == "-1":
                            for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊")
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                        elif relay_type == "0":
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                        else:
                            for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                    if relay_length_max != -1:  # 判断是否超出字数
                        if len(cont) > int(relay_length_max):
                            return
                    if relay_length_min != -1:  # 判断是否小于字数
                        if len(cont) < int(relay_length_min):
                            return
                    if relay_type == "-1":
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        return
                    elif relay_type == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupText(int(i), "收到一条私聊\n来自：" + get_name(
                                Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                        return
                    else:
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                        if relay_length_max != -1:  # 判断是否超出字数
                            if len(cont_text) > int(relay_length_max):
                                return
                        if relay_length_min != -1:  # 判断是否小于字数
                            if len(cont_text) < int(relay_length_min):
                                return
                        if relay_type == "-1":
                            for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                        elif relay_type == "0":
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                        else:
                            for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊\n“" + cont_text + "”")
                            return
                    except Exception as e:
                        # 仅为图片
                        if relay_type == "-1":
                            for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                                action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                     content="(" + Uin + ") " + get_name(
                                                         Uin) + "\n" + time_text + "\n收到一条私聊")
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                        elif relay_type == "0":
                            for i in relay_group_uin:  # 转发消息到所有群聊UIN
                                action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                    content="(" + Uin + ") " + get_name(
                                                        Uin) + "\n" + time_text + "\n收到一条私聊")
                            return
                        else:
                            for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
    if switch != "0":  # 转发功能打开时
        group_type = bot_dict['data']['set'][0]['monitor'][1]['group_type']
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
                if relay_length_max != -1:  # 判断是否超出字数
                    if len(cont) > int(relay_length_max):
                        return
                if relay_length_min != -1:  # 判断是否小于字数
                    if len(cont) < int(relay_length_min):
                        return
                if relay_type == "-1":
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                elif relay_type == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                else:
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                    if relay_length_max != -1:  # 判断是否超出字数
                        if len(cont_text) > int(relay_length_max):
                            return
                    if relay_length_min != -1:  # 判断是否小于字数
                        if len(cont_text) < int(relay_length_min):
                            return
                    if relay_type == "-1":
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                    elif relay_type == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                    else:
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                except Exception as e:
                    # 仅为图片
                    if relay_type == "-1":
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
                    elif relay_type == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
                    else:
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                if relay_type == "-1":
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                        action.sendFriendText(user=int(i), content=address)
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendFriendText(user=int(i), content=address)
                    return
                elif relay_type == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendFriendText(user=int(i), content=address)
                    return
                else:
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                        action.sendFriendText(user=int(i), content=address)
                    return
            elif ctx.MsgType == "VoiceMsg":
                data_text = demjson.decode(ctx.Content)  # 回复的消息的内容
                voiceUrl_text = data_text['Url']
                if relay_type == "-1":
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                elif relay_type == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊语音消息(请在手机上查看)\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text)
                        action.sendgroupVoice(group=int(i), voiceUrl=voiceUrl_text)
                    return
                else:
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                if relay_length_max != -1:  # 判断是否超出字数
                    if len(cont) > int(relay_length_max):
                        return
                if relay_length_min != -1:  # 判断是否小于字数
                    if len(cont) < int(relay_length_min):
                        return
                if relay_type == "-1":
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    return
                elif relay_type == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    return
                else:
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                    if relay_length_max != -1:  # 判断是否超出字数
                        if len(cont_text) > int(relay_length_max):
                            return
                    if relay_length_min != -1:  # 判断是否小于字数
                        if len(cont_text) < int(relay_length_min):
                            return
                    if relay_type == "-1":
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                    elif relay_type == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                    else:
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                except Exception as e:
                    # 仅为图片
                    if relay_type == "-1":
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
                    elif relay_type == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
                    else:
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                if relay_length_max != -1:  # 判断是否超出字数
                    if len(cont) > int(relay_length_max):
                        return
                if relay_length_min != -1:  # 判断是否小于字数
                    if len(cont) < int(relay_length_min):
                        return
                if relay_type == "-1":
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                        action.sendFriendText(int(i),
                                              "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                  Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    return
                elif relay_type == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont + "”")
                    return
                else:
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                    if relay_length_max != -1:  # 判断是否超出字数
                        if len(cont_text) > int(relay_length_max):
                            return
                    if relay_length_min != -1:  # 判断是否小于字数
                        if len(cont_text) < int(relay_length_min):
                            return
                    if relay_type == "-1":
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                    elif relay_type == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ")\n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                    else:
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text + "\n“" + cont_text + "”")
                        return
                except Exception as e:
                    # 仅为图片
                    if relay_type == "-1":
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
                    elif relay_type == "0":
                        for i in relay_group_uin:  # 转发消息到所有群聊UIN
                            action.sendGroupPic(group=int(i), picBase64Buf=Pic_Md5,
                                                content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                    Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
                    else:
                        for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                            action.sendFriendPic(user=int(i), picBase64Buf=Pic_Md5,
                                                 content="收到一条群聊消息\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                     Uin) + "(" + Uin + ") " + "\n" + time_text)
                        return
            elif ctx.MsgType == "VoiceMsg":
                data_text = demjson.decode(ctx.Content)  # 回复的消息的内容
                voiceUrl_text = data_text['Url']
                if relay_type == "-1":
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                elif relay_type == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(int(i),
                                             "收到一条群聊语音消息(请在手机上查看)\n" + ctx.FromGroupName + "(" + q_uin + ") \n来自用户：" + get_name(
                                                 Uin) + "(" + Uin + ") " + "\n" + time_text)
                        action.sendgroupVoice(group=int(i), voiceUrl=voiceUrl_text)
                    return
                else:
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
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
                if relay_type == "-1":
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                        action.sendFriendText(user=int(i), content=address)
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(group=int(i), content=address)
                    return
                elif relay_type == "0":
                    for i in relay_group_uin:  # 转发消息到所有群聊UIN
                        action.sendGroupText(group=int(i), content=address)
                    return
                else:
                    for i in relay_friend_uin:  # 转发消息到所有私聊UIN
                        action.sendFriendText(user=int(i), content=address)
                    return
    else:
        return