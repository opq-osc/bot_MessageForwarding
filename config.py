from botoy import logger
import json, re, httpx

JSONPATH = './plugins/bot_MessageForwarding/MessageForwarding_data.json'  # 配置文件路径


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
def get_json_data():
    # 获取json里面数据

    with open(JSONPATH, 'rb') as f:
        # 定义为只读模型，并定义名称为f

        params = json.load(f)
        # 加载json文件中的内容给params

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


# 获取QQ昵称
def get_name(uin):
    url = "http://api.xtaoa.com/api/qqinfo.php"
    params = {
        "qq": uin
    }
    try:
        res = httpx.get(url, params=params).json()
    except Exception as e:
        logger.warning(f"昵称请求失败\r\n {e}")
        return str(uin)
    return res['name']


# 获取回复人UIN
def get_ReplyUin(text, reply_text):
    result = re.findall("(\(.*\))", text)
    if len(result) < 1:
        result = re.findall("(\(.*\))", reply_text)
    try:
        return int(result[0].replace("(", "").replace(")", ""))
    except Exception as e:
        return 1340219674


# 设置总开关
def set_switch(text="0"):
    json_dict = get_json_data()
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
def set_boss_uin(uin="", pattern="0"):
    json_dict = get_json_data()
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
        return boss_uin
    else:
        return boss_uin


# 设置私聊监听模式
def set_friend_type(pattern="-1"):
    json_dict = get_json_data()
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
def set_friend_key(key="", pattern="0"):
    json_dict = get_json_data()
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
        return friend_key
    else:
        return friend_key


# 设置私聊监听UIN列表
def set_friend_uin(uin="", pattern="0"):
    json_dict = get_json_data()
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
        return friend_uin
    else:
        return friend_uin


# 设置群聊监听模式
def set_group_type(pattern="-1"):
    json_dict = get_json_data()
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
def set_group_key(key="", pattern="0"):
    json_dict = get_json_data()
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
        return group_key
    else:
        return group_key


# 设置群聊监听UIN列表
def set_group_uin(uin="", pattern="0"):
    json_dict = get_json_data()
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
        return group_uin
    else:
        return group_uin


# 设置转发模式
def set_relay_type(pattern="1"):
    json_dict = get_json_data()
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
        return json_dict['data']['set'][0]['relay'][0]['type']
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
def set_relay_friend_uin(uin="", pattern="0"):
    json_dict = get_json_data()
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
        return relay_friend_uin
    else:
        return relay_friend_uin


# 设置转发群聊UIN列表
def set_relay_group_uin(uin="", pattern="0"):
    json_dict = get_json_data()
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
        return relay_group_uin
    else:
        return relay_group_uin


# 设置转发文本限制最长长度
def set_relay_length_max(length=-1):
    json_dict = get_json_data()
    if length < 1 and length != -1 and length != -2:
        return "文本长度必须大于0"
    elif length == -1:  # 无限制
        json_dict['data']['set'][0]['relay'][0]['length'][0]['max'] = str(length)
        write_json_data(json_dict)
        return "设置成功，转发文本最长长度无限制"
    elif length == -2:  # 返回设置
        return json_dict['data']['set'][0]['relay'][0]['length'][0]['max']
    else:
        try:
            json_dict['data']['set'][0]['relay'][0]['length'][0]['max'] = str(length)
            write_json_data(json_dict)
            return "设置成功，转发文本限制最长长度为：" + str(length)
        except Exception as e:
            logger.warning(f"设置转发文本限制最长长度失败\r\n {e}")
            return "设置失败"


# 设置转发文本限制最短长度
def set_relay_length_min(length=-1):
    json_dict = get_json_data()
    if length < 1 and length != -1 and length != -2:
        return "文本长度必须大于0"
    elif length == -1:  # 无限制
        json_dict['data']['set'][0]['relay'][0]['length'][1]['min'] = str(length)
        write_json_data(json_dict)
        return "设置成功，转发文本最短长度无限制"
    elif length == -2:  # 返回设置
        return json_dict['data']['set'][0]['relay'][0]['length'][1]['min']
    else:
        try:
            json_dict['data']['set'][0]['relay'][0]['length'][1]['min'] = str(length)
            write_json_data(json_dict)
            return "设置成功，转发文本限制最短长度为：" + str(length)
        except Exception as e:
            logger.warning(f"设置转发文本限制最短长度失败\r\n {e}")
            return "设置失败"


# 设置私聊UIN黑名单列表
def set_blacklist_friend_uin(uin="", pattern="0"):
    json_dict = get_json_data()
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
        return blacklist_friend_uin
    else:
        return blacklist_friend_uin


# 设置群聊UIN黑名单列表
def set_blacklist_group_uin(uin="", pattern="0"):
    json_dict = get_json_data()
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
        return blacklist_group_uin
    else:
        return blacklist_group_uin


# 设置私聊关键词黑名单列表
def set_blacklist_friend_key(key="", pattern="0"):
    json_dict = get_json_data()
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
        return blacklist_friend_key
    else:
        return blacklist_friend_key


# 设置群聊关键词黑名单列表
def set_blacklist_group_key(key="", pattern="0"):
    json_dict = get_json_data()
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
        return blacklist_group_key
    else:
        return blacklist_group_key


# 设置回复模式
def set_reply_type(pattern="1"):
    json_dict = get_json_data()
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
def format_json_data():
    json_dict = get_json_data()
    switch = json_dict['data']['switch']  # 0关，非0开

    bot_uin = json_dict['data']['bot_uin']  # 机器人UIN

    boss_uin = []
    try:
        for i in json_dict['data']['boss_uin']:
            boss_uin.append(i)  # 添加
    except Exception as e:
        logger.warning(f"管理员UIN列表为空\r\n {e}")

    # 私聊监听设置
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
    relay_length_max = json_dict['data']['set'][0]['relay'][0]['length'][0]['max']
    relay_length_min = json_dict['data']['set'][0]['relay'][0]['length'][1]['min']
    print("转发文本限制长度为：" + str(relay_length_min) + "~" + str(relay_length_max))

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
        relay_friend_uin) + "\n群聊UIN列表：" + str(relay_group_uin) + "\n转发文本限制长度为：" + str(relay_length_min) + "~" + str(
        relay_length_max) + "\n黑名单：\n" + "私聊UIN黑名单列表：" + str(blacklist_friend_uin) + "\n群聊UIN黑名单列表：" + str(
        blacklist_group_uin) + "\n私聊关键词黑名单列表：" + str(blacklist_friend_key) + "\n群聊关键词黑名单列表：" + str(
        blacklist_group_key) + "\n" + reply_type_text
