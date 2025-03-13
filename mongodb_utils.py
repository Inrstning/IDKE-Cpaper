
import pytz
from datetime import datetime

# 获取当前日期和时间
def get_real_time_str():
    now_utc = datetime.now(pytz.utc)
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now_beijing = now_utc.astimezone(beijing_tz)

    # 格式化日期和时间
    formatted_date = now_beijing.strftime("%Y-%m-%d")
    formatted_time = now_beijing.strftime("%H:%M:%S")
    return f"{formatted_date} {formatted_time}"

def return_random_data(connection, user_name = None, sample_size = 1):
    # connection和gpt生成表连接

    # 返回随机数据供标注，默认是返回 list，sample_size 为 1con
    if user_name is not None:
        query = [
            {
                "$match": {
                    "$and": [
                        {
                            "$expr": {
                                "$lt": [
                                    {"$size": "$check_emails"},  # 检查 check_emails 的大小是否小于 3
                                    3
                                ]
                            }
                        },
                        {
                            "tool_choice": {"$ne": get_real_time_str()}  # tool_choice 不等于 now_tool
                        },
                        {
                            "$expr": {
                                "$not": {
                                    "$in": [user_name, "$check_emails"]
                                }
                            }
                        }
                    ]
                }
            },
            {
                "$sample": {
                    "size": 1
                }
            },
        ]
    else:
        query = [
            {
                "$match": {
                    "$and": [
                        {
                            "$expr": {
                                "$lt": [
                                    {"$size": "$check_emails"},  # 检查 check_emails 的大小是否小于 3
                                    3
                                ]
                            }
                        },
                        {
                            "tool_choice": {"$ne": get_real_time_str()}  # tool_choice 不等于 now_tool
                        },
                        # 如果是匿名邮箱，就随机返回
                    ]
                }
            },
            {
                "$sample": {
                    "size": 1
                }
            },
        ]
    
    result = connection.aggregate(query) 
    return result[0] if result else {}



def insert_user_score_info(connection,dict):
    # 传入连接的connection和需要插入的用户标注字典信息dict
    # 这个connection连接的是用户标注信息表
    connection.insert(dict)




def update_user_infos(connection,dict):
    # connection和用户信息表连接
    # user_name为用户名称
    # question_id为标注题目的id
    # 返回值为用户已经标注信息的长度

    user_name = dict['user_name']
    question_id = dict['question_id']

    query = [
            {
                "$match": {
                    "$and": [
                        {"user_name": user_name},
                        {
                            "tool_choice": {"$ne": get_real_time_str()}  # tool_choice 不等于 now_tool
                        },
                    ]
                }
            },
            {
                "$sample": {
                    "size": 1
                }
            },
        ]

    user_data = connection.aggregate(query)
    if len(user_data) > 0:
        # ori_user_data = user_data[0]
        # new_user_data = user_data[0]
        # new_user_data['check_callbacks'].append(question_id)
        # new_values = { "$set": new_user_data }
        
        # connection.update_one(ori_user_data,new_values)
        connection.update_one({"user_name":user_name},  # 查找条件
            {
                "$inc": {"check_nums": 1},  # 增加 check_nums 的值
                "$push": {"check_data_list":question_id},  # 将 idx 添加到 check_data_list 数组
            },
            upsert=True)

        # return user_data[0]['check_nums'] + 1

    else:
        user_info_dict = {
            "user_name":user_name,
            "check_callbacks":[question_id],
            "check_nums":1
        }
        connection.insert(user_info_dict)
        
        # return 1

       

    # if connection.find({"user_name": {"$gt": user_name}}):
    #     # 将标注的信息更新到表中
    #     connection.update

    # else:
    #     user_info_dict = {
    #         "user"
    #     }
    #     connection.insert(dict)

    # connection.insert(dict)

