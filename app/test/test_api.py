import requests
# 风格视频生成
# response = requests.get(
#     "http://localhost:8000/wan-video/",
#     params={
#         "soul_id": "wangjing",
#         "cue": "王静独自走进保龄球馆，手指轻抚过冰冷的球体，她不是为竞技而来，而是将保龄球视为一种隐喻：每一次滚动都像在与记忆中父亲的灵魂交流。她选了一个重量适中的球，闭上眼深呼吸，回想父亲生前的教诲。当她掷出球时，它缓缓滚向球瓶，发出清脆的撞击声，她低声喃喃：“爸爸，我还在学习平衡感性与理性。”她的眼中闪过一丝泪光，但嘴角挂着微笑，这个场景成了她内心疗愈的仪式，安静而深刻，没有旁人打扰。",
#         "user_id": "user_001"
#     }
# )

# response = requests.get(
#     "http://localhost:8000/wan-video/",
#     params={
#         "soul_id": "linna",
#         "cue": "林娜蹦跳着走进咖啡店，立刻被熟悉的音乐吸引。她点了一杯拿铁，然后自然地加入一群陌生人的谈话，分享自己最近的旅行趣事。当一位朋友提议玩桌游时，她兴奋地举手参与，笑声回荡在店内。她不时调整帽子，确保自己的打扮引人注目，还主动帮店员分发小点心，把整个场景变成了即兴派对。林娜的举止随意而亲切，仿佛每个人都是她的老朋友，她用热情感染了周围，让咖啡店充满了欢乐的波动。",
#         "user_id": "user_001"
#     }
# )

# response = requests.get(
#     "http://localhost:8000/wan-video/",
#     params={
#         "soul_id": "lizhe",
#         "cue": "李哲走进画室，目光冷静地扫过画架上的作品。他并非来作画，而是受朋友之托分析画作的构图数据。他戴上手套，拿出平板电脑记录色彩分布，手指轻点屏幕，计算着黄金比例是否适用。当一位陌生画家热情地邀请他尝试挥笔时，李哲微微摇头，用平静的语气解释：“艺术需要感性，但我更擅长用逻辑解构美。”他继续专注于数据，仿佛整个空间只是他思考的延伸，没有丝毫情感波动。",
#         "user_id": "user_001"
#     }
# )

# response = requests.post(
#     "http://localhost:8000/wan-video/selfie",
#     json={
#         "soul_id": "lizhe",
#         "city_key": "tokyo",
#         "mood": "happy",
#         "user_id": "user_001"
#     }
# )

# response = requests.post(
#     "http://localhost:8000/wan-video/selfie",
#     json={
#         "soul_id": "linna",
#         "city_key": "paris",
#         "mood": "happy",
#         "user_id": "user_001"
#     }
# )

response = requests.post(
    "http://localhost:8000/wan-video/selfie",
    json={
        "soul_id": "wangjing",
        "city_key": "london",
        "mood": "happy",
        "user_id": "user_001"
    }
)


print(response.json())