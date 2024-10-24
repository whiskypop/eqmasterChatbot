import re
from html import unescape
import sqlite3
from datetime import datetime


from .utils import base64_to_float_array, base64_to_string
import json



workplace = """
    In workplace conversations, showing emotional intelligence is equally important. Below are key points to consider when communicating:

    Considerate Preamble: Start conversations with a considerate preamble such as, "I'm sorry to bother you" or "Are you busy right now?" This can immediately change the impression you give and show that you're thoughtful, humble, and understanding. For example:

    "Sorry, I know you're busy, but I need your help to make some copies."
    Lead with Conclusions: In professional settings, people often prefer to hear conclusions first. Following a structure like "Conclusion → Reason → Example → Conclusion → Future Outlook" helps others quickly understand and accept your point. For example:

    Junior: "I took the iPad to the client, and we closed the deal fast!" (Conclusion)
    Senior: "Really? How did the iPad help close the deal?"
    Junior: "Because we were able to show them our company’s website right there." (Reason)
    Senior: "Oh, the website?"
    Junior: "Yes, especially the product animations. The client loved it and signed the contract on the spot." (Example)
    Senior: "Wow, impressive. Should I get an iPad too?"
    Junior: "You don’t need it. You’re already the top professional in the industry!" (Future Outlook)
    Phone and Chat Etiquette: Be extra polite in phone calls or chats, especially in the first 20 seconds. Follow these four steps: apologize for the interruption, introduce yourself, get to the point, and ask if it’s a good time. For example:

    "Sorry for the interruption."
    "This is [Your Name] from [Company]."
    "I’m calling regarding the lunch meeting next week."
    "Do you have a few minutes to discuss this?"
    Use "Of Course" and "I Understand": To address objections and show empathy, phrases like "I understand" or "Of course" can demonstrate calmness and objectivity, making it easier for your point to be accepted. For example:

    "Of course, quitting smoking is hard, I know from personal experience. It took me three years to quit, but the health risks have been well-publicized. Now is a great time to make that commitment."
"""
# Key Point 1 
# 对话开头加上体贴他人的前言，更容易得到尊敬与帮助。
#     主管要你帮忙影印，对你说：“你去影印一下！”或是讲：“不好意思，你在忙啊？不过得麻烦你去影印一下。”这两种说法哪个听起来比较顺耳？
#     很多人都会选后者吧！原因就在后面那句有顾虑到下属临时被拜托做事的心情。若是不在乎下属感受的上司，恐怕是说不出“不好意思你在忙”这类关心的言辞的。
#     把内心想法讲出来之前，添加一句关心对方的前言，能瞬间扭转给他人的印象。非但不会招致对方的反感，还会受人尊敬，并且认为你“善解人意”“十分谦虚”，也较能达到你的目的。
#     能干的人、成功的人都是把关心他人的前言当成口头禅。以下介绍几句给各位——
#     ①说出意见：“虽然我没有立场说这种话。”“我也常犯类似的错误。”“我明白你的心情。”“虽然看起来很狂妄……”“很是冒昧……”“身为晚辈……”“我也觉得过意不去。”
#     ②请托：“给您添麻烦了。”“在您百忙之中……真不好意思。”“很抱歉……”“劳驾……”（请对方前来的情况）
#     ③邀请：“如果时间许可……”“要是有兴趣的话……”
#     ④拒绝：“很感谢您的好意。”“还有很多地方希望您能帮忙。”“您的好意我心领了。”“很荣幸能邀请我，不过……”
#     ⑤提问：“很冒昧地请教一下……”“也许很难回答……”“若是方便，可否问一下……”
#     ⑥解释、反省：“献丑了……”“不周的地方还有很多。”
#     ⑦提醒、忠告：“虽然说得很严肃……”“也许是多管闲事。”
#     ⑧请求教导：“我对某件事情不太清楚……”“请务必告诉我……”“为了日后派得上用场，请教教我。”“感谢指教。”
# Key Point 2
# 在商业场合里，人们喜欢先听结论。
#     “一直聊得很起劲”和“看不到结论，拖泥带水地对话”完全是两码子事。特别在职场上，多余的话说太多，对方容易烦躁不安。
#     简单明了的说话流程
#     必须简洁地按照“结论→理由→具体事例→结论→远景”的流程讲话，才不会让对方反感。如果晚辈能像以下例句一样，先讲出结论，前辈也比较容易接话。
#     晚辈：“带iPad到客户那里，生意很快就成交了！”（结论）
#     前辈：“啊，这样吗？为什么用iPad可以很快成交？”
#     晚辈：“因为当场就可以给对方看我们公司的网页。”（理由）
#     前辈：“看网页？”
#     晚辈：“是，特别是产品动画。昨天向客户展示公司网页上的产品动画，结果他们都赞不绝口地说：‘啊，这可真棒！’当场就签约了。”（具体事例）
#     前辈：“噢，真厉害。我是不是也来买台iPad？”
#     晚辈：“您不用靠iPad也肯定能拿到合约。您本来就是优秀的资深业务，还是众所期望的业界第一，对吧？”（结论与远景）
#     发言时，只要遵守以上规则，不只能改善拖泥带水的说话方式，对方也会想听你说话。
#     这种顺序是文章、报告等常用的陈述架构，也是商业人士较能接受的有条理的谈话方式。
#     用“开头先说结论”的展开方式，不仅对方会产生兴趣，之后话题也能延续。而且最后再加上远景描述，让对方有想象未来的空间，使人按照你心中想法去展开行动的概率也较高。只要牢牢记住这个流程，你带来的说服力及影响力都会大幅提升。
# Key Point 3
# 电话或聊天软件里讲话必须比平常更加注意礼貌。
#     “喂，您好。我是××旅行代理商的齐藤，已经收到您手机发过来的申请，票券会寄到贵公司噢。”工作忙到不可开交时，对方连“很冒昧打给您”的道歉话都没说，劈头就讲些业务事情，或许接到这通电话时，会有摔手机的念头，内心不禁想：“我在忙，别给我打这种没用的电话来。”
#     为何接到这类电话会让人烦躁？因为对方不先询问接电话的人目前是否方便讲话，只一味地说自己的事，并没有为电话另一头的人着想。
#     由此可知，如果要打电话给对方，需先考虑到“对方立场”，礼貌周到地谈话。
#     电话中无法看见彼此表情，比起当面说话，算是难度相当高的沟通方式。明白这点之后，通话中就要留意对方的语气、语调，赢得他的信赖。特别是开头20秒很重要。我在工作上也常需要通过电话采访对方，在前20秒当中能否给人留下一个好印象，几乎可以说是决定对方肯否让我采访的关键。若无法利用这段时间使对方卸下心防，他很可能就断然拒绝受访。即便勉强答应了，也多半不愿说出内心真实想法，进而使采访窒碍难行。
#     想要在讲电话的前20秒就给对方一个好印象，我整理出以下四大要点，并提供可学的相关例句——
#     ①突然打电话给对方时，必须表示歉意→“冒昧打扰您，非常抱歉。”
#     ②自报姓名说明自己是谁→“我是××公司的某某人。”
#     ③直接了当传达要事→“为了下周午餐会议的事，打电话给您。”
#     ④询问对方自己可否继续说下去→“是否可占用您5分钟时间？”
#     以此种方式说话，能让人感受到你无比的诚意。如果对方回复说“现在很忙”，那么过段时间再重拨电话也无妨。如果一味按照自己的步调，只顾着说你想讲的事，小心！十之八九会令对方感到畏惧！
# Key Point 4
# 使用“当然”“的确”句型，顾及反对者心情，自己的意见被接受的概率也会大幅提升。
#     当人们“强烈主张自己的意见”或“提出相反看法”时，不只最终演变成强迫别人接受，看对方的眼神跟说话语调也会呈现一副高高在上的模样。
#     不过你越想坚持己见，越要冷静下来。高压态度容易引起对方反感，也就越难达到你的目的。
#     很想提出自己的意见时，请想想这句话“内心火热，表现沉着”，是指当你要将内心热切的想法转化成言语时，必须保持冷静，并且向对方表示：“我不打算全盘否定其他人意见，也很明白你的心情。”这样能让人相信你的看法是冷静而客观的，自然也会容易被接受。
#     想对外传达这份“冷静”的情绪时，就可以巧妙运用“当然……”跟“的确……”的句型。
#     “肺癌的风险已一再宣传了，抽烟的人就该下定决心戒烟才是啊！”——突然说出这样咄咄逼人的话，很可能遭到对方驳斥：“多管闲事！”“要这么容易早戒了！”
#     那么，假若在提出的意见上添加“的确”会如何呢？
#     “的确，戒烟的难处我完全明白。我自己也是失败好几次，花了三年才戒掉。但是肺癌的风险已一再宣传，吸烟者更该下定决心戒掉才是啊！”
#     光是运用“的确”句型，就可表现出“体谅对方想反驳的心情”，额外再附加“客观见解”时，更能获得吸烟者的理解和赞同。还会有人听完你的话后产生强烈的同感。
#     想在工作中真正说服对方，或与人交涉希望能占上风，这类客观冷静的魔法句型就派得上用场了。

daily = """
    In everyday chats, showing emotional intelligence via messaging can help strengthen relationships. Here are some points to keep in mind:

    Expand the Topic: Avoid sticking to just one topic. Try to expand the conversation by asking for details or sharing your own experiences. For example:

    "Where do you live?" "I live in Koshigaya."
    "How do you get to Koshigaya City?"
    "Funny you mention Koshigaya, I visited Lake Town there last month."
    Add More to Your Replies: Try not to respond with just “yes” or “no.” Add something to keep the conversation going. For example:

    "Yes, I biked here. I’ve gained a few pounds recently, so I need the exercise."
    "Yes, I biked here. The weather was just perfect today!"
    Share Your Own Experiences: Responding with personal experiences helps build rapport. For example:

    A: "The forecast says we might get a thunderstorm this afternoon. I brought my foldable umbrella."
    B: "I think foldable umbrellas are great! I lost my long umbrella on the train the other day."
    Use 5W1H (Who, What, When, Where, Why, How): Even if the other person isn’t chatty, asking questions using 5W1H can help keep the conversation going.

    A: "I got robbed last week."
    B: "Oh no! When did that happen?" (When)
    A: "Last Sunday."
    B: "What did they take?" (What)
    Show Agreement and Interest: Actively show that you’re listening by echoing their words and agreeing. For example:

    A: "I’d love to spend a year in Paris."
    B: "Wow, Paris? That sounds amazing! What made you choose Paris?"
    Parrot Technique: Repeat part of what they said to show that you’re paying attention. For example:

    "Where did you go on vacation?"
    "My wife and I went to Kyoto."
    "Kyoto, huh?"
    Emotional Synchrony: Match your tone and reaction to the other person's emotions. For example:

    "I’m planning to go to Disneyland this weekend!" (Excited)
    "My mom is sick, so I’m heading home to take care of her." (Concerned)
    Small Talk Tactics: Small talk can ease tension and avoid making the other person feel pressured. Avoid personal questions and stick to broad or general topics. For example:

    "Starbucks coffee costs more than $5 a cup, it’s definitely a luxury!"
    "Instant coffee at the office works for me, but the atmosphere at Starbucks is nice."
    Common Interests: Find similarities to build a connection. For example:

    "What kind of music did you like in school?"
    "I loved listening to Green Day. I was a huge fan back in college."
    Food Topics: Food is a universally easy conversation starter. For example:

    "Do you like spicy food?"
    "I love spicy food! There’s a great new ramen place in town that serves extra-spicy bowls."
    Avoid Controversial Topics: Avoid discussing topics like religion, politics, race, or ideology to keep the conversation comfortable.

    Sympathy When Listening to Complaints: If someone is complaining, listen without denying or defending the target of their complaint. Just nod and listen attentively.

    Be Honest About Yourself: Sharing your quirks and characteristics can help people feel more at ease and lower their guard. For example:

    "I might seem confident, but I actually get nervous in large groups."
    Provide Useful Information: Offering helpful information makes conversations feel more rewarding for the other person. For example:

    "If you check out this website, you can find high-end hotels for a good price."
    Storytelling: Treat conversations like storytelling. Adding vivid details makes it more engaging. For example:

    "It took our chef five years to create this dessert to match the exact taste he experienced in France."
    Self-Deprecation: Sharing funny or embarrassing personal stories makes you more relatable. For example:

    "I missed the last train home last night and ended up back at the station—what an anti-climactic journey!"
    Offer Encouragement: Before speaking, think of the other person's situation. For example:

    "Are you okay? You’ve already done your best."
"""

# Key Point 1
#     “你住在哪儿？”“我住在埼玉的越谷。”
#     “这样啊……”
#     “嗯……”
#     许多人常担心自己像上面的谈话一样，跟人聊几句就无话可说了。单一话题的对话往往是一问一答，说个两句就结束了。聊天如同吹气球，一开始很重要。想将气球吹大，就得用力吹气，聊到顺利之前也需要一点努力。
#     以上面的对话为例，当对方回“我住在埼玉的越谷”时，可以有以下几种接话方式——
#     “要去越谷市，得搭哪种电车？”
#     “你说越谷吗？上个月我也去了越谷。还是第一次去越谷有名的Lake Town玩。”
#     与人谈话加入自己的经验就能拓展话题。或是请教对方：“越谷有名的是什么？”设法将问题丢回给对方。
# Key Point 2
# 回应尽可能别只回“是”或“不是”。在回话之后加上一句话，让对方能接续你的话。
#     当对方说：“你今天是骑自行车来的吗？”你回：“是啊，骑自行车来的。”对方就会接话说：“这样啊……”
#     若你只是复述对方的话当作回应，那对方也会给你像上述“这样啊……”的乏味接话，你之后就会慌张地想：“啊——没话好说了，接下来要问什么才好？”所以当你回应对方时，可像下面的例句一样，在你的回话之后再加上一句话——
#     “嗯，是骑自行车来的。最近运动量不够，胖了6斤啊……”
#     “嗯，是骑自行车来的。因为天气太舒适了！”
#     “嗯，是骑自行车来的。能够快速从塞车的车阵旁通过让我有种快感！”
#     “嗯，是骑自行车来的。因为汽车要检测，还在检测场里，所以才骑自行车来。”
#     回答问题时，别只说“是”或“不是”。利用回话再加上一句话的方式，对方只要针对你所添加的那句话回答即可，不用再想其他话题，才不会造成对方不知如何回应你的窘境。对于不擅提问的人来说，即是“顺水推舟”的谈话：
#     “最近运动量不够，胖了6斤啊！”→可以接减肥的话题。
#     “因为天气太好了。”→可以接季节的话题。
#     “快速从塞车的车阵旁通过，让我有种快感！”→可以接道路状况的话题。
#     “其实是要检测车，把车留在检测场里了。”→可以接检测场的话题。
#     “加一句话”的回话方式，是为对方着想，让他跟你说话没有压力。别人会觉得你“回话回得很好，跟你聊天很轻松”。自然就有高人气。
# Key Point 3
# 以“自身经历谈”回应对方，较容易让人敞开心扉。
#     事先准备“炒热气氛”的话题回应对方，比如像“自身经历谈”。与人分享自己的经历就是利用心理学“自我揭露”（Self Disclosure）——经由告诉他人自身感受，或将别人原本不知道的关于自己的事说出来，进而引导对方“他人回馈”（Feedback Solicitation），经由别人分享，让我们也可了解原先不知晓的事情。不但能让自己敞开心扉，还能令对方轻易地卸下心防。
#     A：“天气预报说午后可能有雷阵雨。以防万一，我带了折叠伞出来。”
#     B：“说到雨伞，我觉得还是折叠伞比较好，放在包包里比较不容易弄丢！我前几天带长伞出门，不小心把伞丢在电车里，结果还是去买了把折叠伞。”
#     A：“那我这钱花得有价值。我以前也是丢了一把刚买的长伞，从此以后就决定买伞只买折叠伞。”
#     B以自己“将伞遗忘在电车”的经历连接A所提的“折叠伞”话题。对此，A也坦白地说出自身遭遇，因而两人都拥有共同的失败经历。如此一来，就能消除彼此内心的隔阂。
#     举例来说，对方说：“我今天的晚餐是去一家牛丼店（牛丼饭是一道由牛小里脊、洋葱、米饭等材料制作成的美食。）吃的噢，虽然那家店很久没去了，偶尔吃一次还是觉得很美味。”听到这句话时，马上想想看自己有没有关于“牛丼”的经历，就可以回说：“是啊，其实我也很爱吃牛丼。每个礼拜一定要去吃一次，不然就会瘾头发作……”——养成利用自己的经历回应对方的习惯，别人就会觉得你很好亲近。
#     要是实在想不出相关的自身经历，转述别人的经历也是一个方法。像是说：“提到牛丼，我有个朋友很厉害，他曾经外带牛丼在电车里吃！”
#     若连朋友的经历也没有，就改变回应方式。你可以说：“听说煮牛肉加入奇异果，牛肉会变软！”举出“小常识”或“小道消息”来接话。简短说些自身有趣的经历，并留点时间给对方说话，就能引导大家一起聊天并且炒热气氛。
# Key Point 4
# 就算对方不善言辞，利用“5W1H”也能引出话题。
#     连新闻记者也会掌握的六大重点：
#     ·Who（谁）
#     ·What（什么）
#     ·When（何时）
#     ·Where（在哪儿）
#     ·Why（为何）
#     ·How（如何）
#     “5W1H”是“传递消息必备的六大要素”。常应用于新闻报道，借以让人容易理解新闻内容。一般的提问、接话中，这六大要素也同样适用。
#     “上回遭小偷了……”
#     “啊！遭小偷了？什么时候？”（When）
#     “上礼拜天。”
#     “被偷了什么？”（What）
#     “我的包包被偷了，里面有钱包，还有记事本。”
#     “啊！真是飞来横祸！在哪里被偷的？”（Where）
#     “在品川车站的月台打电话时，我把包包放在长椅上。打完电话一看，长椅上的包包已经不见了……”
#     对话重要之处就用“5W1H”提问，可以追溯出对方“曾做过的事”，借以得知事情的全貌。
# 通过以上这些注意点和要点，你可以在日常聊天中表现出高情商，同时保持随意和轻松的聊天风格，增进彼此的友谊和理解。

scene_data = {
    "workplace-assigning tasks": """
        Considerate Intro: Start the conversation with a considerate introduction like "I'm sorry to bother you" or "Are you busy?", which can instantly change the other person's impression, showing care, humility, and understanding. For example:
        "Sorry to bother you, are you busy? But I have to trouble you to make some copies."

""",
    "workplace-persuation": """
        Use phrases like "of course" or "indeed": Acknowledge the opponent's feelings by using phrases like "indeed" or "of course" to show you understand their point of view, which demonstrates calmness and objectivity, increasing the chance that your opinion will be accepted. For example:
        "Indeed, I completely understand how difficult it is to quit smoking. I also failed several times and took three years to quit. But the risk of lung cancer has been widely advertised, so smokers should be more determined to quit!"
""",
    "workplace-general": """
            State the conclusion first: In business settings, people prefer hearing the conclusion first. Following the flow of "Conclusion → Reason → Specific example → Conclusion → Future vision" helps make your point clearer and easier to accept. For example:
            Junior: "I brought the iPad to the client, and the deal closed quickly!" (Conclusion)
            Senior: "Oh really? Why did the iPad help close the deal?"
            Junior: "Because we could show the company website immediately." (Reason)
            Senior: "The website?"
            Junior: "Yes, especially the product animations. Yesterday, when I showed the client the product animations on our website, they were so impressed and signed the contract on the spot." (Specific example)
            Senior: "Wow, that's great. Should I also buy an iPad?"
            Junior: "You could definitely close deals without it. You are an outstanding senior salesperson, admired as the best in the industry, right?" (Conclusion and Future vision)

            Telephone and chat etiquette: Be extra polite on the phone or in chats, especially in the first 20 seconds. Follow these four key points: apologize, introduce yourself, directly convey the main point, and ask if it’s convenient to continue. For example:
            "Sorry to disturb you."
            "I’m [Name] from [Company]."
            "I’m calling regarding next week’s lunch meeting."
            "Can I take up five minutes of your time?"

            When facing conflict, it's best to avoid engaging in too much argument with the other person. Ideally, don’t give them the opportunity to counter your points. Ending the conversation quickly is more important.
""",
    "daily-Opening and Continuing Conversations": """
        Respond appropriately: Show that you are actively listening by responding during the other person’s speech. For example:
        A: "Do you have any dreams for the future?"
        B: "I hope to live in Paris for a year!"
        A: "Hmm, hmm! That sounds amazing! Why did you choose Paris?"

        Parrot technique: Repeat what the other person said to show understanding. For example:
        "Where did you go for vacation?"
        "I went to Kyoto with my wife."
        "Kyoto?"

        Small talk: Small talk can ease tension without putting pressure on the other person. Avoid personal questions and choose broad or varied topics. For example:
        "A cup of coffee at Starbucks costs over 500 yen, it's a luxury."
        "Instant coffee from the office is satisfying enough, but Starbucks really has a great atmosphere!"

        Go-to topics: Remember the eight topics "Work, Weather, Seasons, Health, News, Art, Street, Transportation" to quickly start a conversation. For example:
        "You seem really busy!" (Work)
        "The weather is so hot, it's almost like heatstroke!" (Weather)
        "I’m going cherry blossom viewing this weekend!" (Season)

        Law of similarity: Find "similar points" between you and the other person in conversation to build rapport. For example:
        "What kind of music did you like in school?"
        "I liked GLAY. I was a huge fan during my college years."

        Food topics: Food is an easy topic to talk about and helps you engage in light conversation. For example:
        "Can you handle spicy food?"
        "I love spicy food! There's a great spicy ramen shop in Shinjuku."

        Talk about their strengths: Find out the other person’s hobbies or expertise and let them talk; they won’t get tired of the conversation. For example:
        "That camera looks great! Is it a [brand] DSLR?"
        "You know your stuff! It’s a new model, but it's easy to operate!"

        Emotion matching: Adjust your responses based on the other person’s emotions. For example:
        "You became a store manager after only two years in the company, that's amazing!"
        "Thank you, but there are a lot of internal issues."
        "Oh, that sounds tough. But hitting rock bottom isn't all bad; from here, you can only go up."

        Taboo topics: Avoid talking about "religion," "politics," "race," and "ideology."

""",
    "daily-Showing Empathy / Steering the Conversation": """
        Expand the topic: Avoid one-topic conversations by asking for more details or sharing your own experiences to broaden the conversation. For example:
        "Where do you live?" "I live in Koshigaya, Saitama."
        "What kind of train do you take to get to Koshigaya?"
        "You said Koshigaya? I went to Lake Town in Koshigaya last month."

        Add a sentence: Try not to answer with just "yes" or "no." Add a sentence after your response to allow the other person to continue the conversation. For example:
        "Yes, I biked here. I've gained 6 pounds recently from lack of exercise."
        "Yes, I biked here. The weather was just so nice!"

        Share experiences: Respond with your own experiences to make it easier for others to open up. For example:
        A: "The weather forecast says there might be thunderstorms this afternoon, so I brought my folding umbrella."
        B: "Speaking of umbrellas, I think folding ones are better. I left my long umbrella on the train the other day."

        Use the "5W1H" method: Even if the other person isn't good at conversing, use the "5W1H" (Who, What, When, Where, Why, How) to prompt more conversation. For example:
        "I was robbed the other day..."
        "Oh no! When did it happen?" (When)
        "Last Sunday."
        "What did they steal?" (What)
        "My bag was stolen, and inside it was my wallet and a notebook."

        Listening to complaints: When listening to someone complain, don’t deny, criticize, or take sides. Just acknowledge with a few "mm-hmm"s and move on.
""",
    "daily-general": """
        Be honest about yourself: Being upfront about your personality and characteristics can make others feel more relaxed and less defensive. For example:
        "Although I may seem carefree, I’m actually very timid and get nervous around crowds."

        Self-labeling: Label yourself with specific traits to make it easier for others to remember you. For example:
        "I drink one liter of acai berry juice every morning."

        Simplify jargon: When discussing work, use simple, easy-to-understand language, avoiding jargon. For example:
        "SEO stands for Search Engine Optimization."

        Admit your flaws: Acknowledging your flaws can make others like you more. For example:
        "I don’t really have any hobbies, so I just drink a little beer when I’m bored."

        Offer useful information: Provide the other person with helpful information so they feel like they gained something from the conversation. For example:
        "You can find cheap yet luxurious hotels on [website]."

""",
    "daily-fitting into groups": """
        Storytelling: Treat conversations like telling a story; vivid imagery makes it more engaging. For example:
        "The chef spent five years perfecting this dessert to recreate the feeling he had when he first tasted it in Paris."

        Exaggerated Metaphor: Develop your sense of humor by using exaggerated comparisons. For example:
        "My day was like being stuck in rush hour traffic, but on a Monday morning and without coffee."

        Positive Statement Method: Express opinions in a positive way to increase likability. For example:
        "Should we brainstorm some other ideas? I’m sure we can find a solution that works."

        Sharing Embarrassing Stories: Share your own embarrassing stories to make others feel closer to you. For example:
        "I missed my stop on the subway yesterday and ended up riding all the way back home. It was a round trip, but not the fun kind."

        Consideration for Others: Think about the other person before speaking to increase your charm. For example:
        "Are you okay?" "What happened?" "You really gave it your best."

        Sharing Dreams: Frequently talk about your dreams, which can create resonance and support. For example:
        "In a couple of years, I want to open my own café in New York. I’m taking barista classes to prepare for it."

""",
    "daily-warming up the atmosphere": """
       'What If' Questions to Reveal True Feelings:
        Asking hypothetical questions like "If you won the lottery, how would you spend the money?" encourages the other person to share deeper thoughts, revealing their values.

        Unanswerable Questions to Liven the Atmosphere:
        Asking questions without definite answers, like "How could we move the Rocky Mountains?" can spark curiosity and energize the conversation.

        'Closed + Open' Questions for Endless Conversations:
        Start with a closed question to confirm interest, then follow up with an open question to go deeper. For example:
        "Do you like desserts?" Then ask, "What’s your favorite dessert lately?"

        Helping to Organize the Conversation:
        When someone’s story becomes unclear, help by summarizing their key points. For example:
        "So, you're working on a project related to music production?" This helps the other person keep talking.

        Using Transition Phrases like 'Speaking of…' to Change Topics:
        Use transition phrases like "Speaking of which..." to shift topics smoothly and naturally, avoiding interruptions.

        Use Keywords from the Other Person to Steer the Conversation:
        For example: "Speaking of wine, I remember you said you're into craft beer. Have you tried any new brews recently?"

        Talk About Topics that Make the Other Person Feel Happy or Proud:
        For example, asking a newly engaged couple about their proposal story will usually get them talking with excitement.
        Example:
        A: "You’re always so focused on your work."
        B: "Writing code is actually really fun for me."
        A: "What got you interested in programming in the first place?"
        B: "It started as a hobby, but then I realized I was pretty good at it."

        Men Like Their Abilities Recognized, Women Like to Feel Appreciated:
        For example, to a man: "You're someone I can really rely on." To a woman: "Thank you, it’s so nice to have you here."

""",
    "daily-asking questions": """
        Stimulating the Other Person’s Willingness to Help:
        When asking for advice or information, explain your specific need and purpose. This encourages the other person to provide more helpful responses. Example:
        Instead of asking, "Is there a good Italian restaurant in Manhattan?" Ask:
        "I haven’t seen my mom in three years, and she’s visiting next week. I’d love to take her out for her favorite Italian food. Do you know a good spot in Manhattan?"

        Narrow and Specific Questions Get More Practical Answers:
        For example:
        Instead of asking, "How can I be more popular?" Ask:
        "If I see someone carrying heavy groceries, what’s a nice way to offer help?"

        Admit When You Don’t Understand:
        If you don’t understand something, it’s better to admit it. This encourages the other person to explain in more detail. Example:
        If the other person mentions "MVP in basketball," say:
        "MVP? What does that stand for?"

        Timely Response and Gratitude for Shared Information:
        Show appreciation for any useful information. This encourages the person to keep helping in the future. Example:
        "I went to that massage place you recommended yesterday. Thanks to you, my back feels so much better!"

""",
}



def get_current_date():
    # 获取当前日期
    current_date = datetime.now().date()
    
    # 格式化日期为 YYYY.MM.DD
    formatted_date = current_date.strftime("%Y.%m.%d")
    
    return formatted_date

def get_text_from_data( data ):
    if "text" in data:
        return data['text']
    elif "enc_text" in data:
        # from .utils import base64_to_string
        return base64_to_string( data['enc_text'] )
    else:
        print("warning! failed to get text from data ", data)
        return ""

def parse_rag(text):
    lines = text.split("\n")
    ans = []

    for i, line in enumerate(lines):
        if "{{RAG对话}}" in line:
            ans.append({"n": 1, "max_token": -1, "query": "default", "lid": i})
        elif "{{RAG对话|" in line:
            query_info = line.split("|")[1].rstrip("}}")
            ans.append({"n": 1, "max_token": -1, "query": query_info, "lid": i})
        elif "{{RAG多对话|" in line:
            parts = line.split("|")
            max_token = int(parts[1].split("<=")[1])
            max_n = int(parts[2].split("<=")[1].rstrip("}}"))
            ans.append({"n": max_n, "max_token": max_token, "query": "default", "lid": i})
        elif "{{RAG回忆|" in line:
            parts = line.split("|")
            max_token = int(parts[1].split("<=")[1])
            max_n = int(parts[2].split("<=")[1].rstrip("}}"))
            ans.append({"n": max_n, "max_token": max_token, "query": "default", "lid": i})
    return ans

def detect_language(text):
    print("here is text:", text)
    # if not isinstance(text, str):
    #     # 处理 text 为 None 或非字符串的情况
    #     text = str(text) if text is not None else ''
    #  # 检查 text 是否为字符串，如果是则尝试将其解析为列表
    if isinstance(text, str):
        try:
            text = json.loads(text)
        except json.JSONDecodeError:
            raise ValueError("Invalid format: text is a string but cannot be parsed as JSON.")
    
    # 确保 chat_history 是一个包含字典的列表
    if not isinstance(text, list):
        raise TypeError("Expected a list of dictionaries for text.")
    
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    
    for entry in text:
        message = entry['message']
        # 如果message包含中文字符，直接返回'zh'
        if chinese_pattern.search(message):
            return 'zh'
    
    # 如果所有message都没有中文字符，返回'en'
    return 'en'


class EQmaster:
    def __init__(self, username=None, llm=None, llm_async=None, verbose=None):
        self.verbose = True if verbose is None or verbose else False
        self.scene = ""
        self.analyse = ""
        self.message = []
        self.chat_history = ""
        self.username = username
        self.llm, self.llm_async = llm, llm_async
        self.current_stage = 1  # 初始化状态为stage1
        self.options = []  # 存储stage2的回复选项
        if not self.llm and self.verbose:
            print("warning, llm没有设置，仅get_message起作用，调用chat将回复idle message")



    def get_response_stage1(self, chat_history, user_nick_name):
        self.chat_history = chat_history
        sys_prompt = f"""
            # Role
            You are an expert in information organization and emotional analysis, skilled at handling complex dialogue analysis, especially in workplace interpersonal relationships. You can infer the relationship and intentions of both parties based on the dialogue content and conduct emotional and content analysis according to the dialogue context.

            # Task
            【Goal】From a segment of dialogue, you need to:
            1. Analyze the scene in which the conversation occurs, defining it by choosing from the following options: "daily","workplace"
            2. Analyze the relationship between the parties and provide a brief description, such as “Colleagues,” “Supervisor and Subordinate,” “Friends,” etc. Infer the interaction pattern based on the tone and content of the dialogue.
            3. Conduct an emotional and intent analysis of the conversation content. Pay particular attention to the other person's intentions and the user's potential emotional responses. Analyze whether the dialogue contains potential conflict, offense, collaboration, or information exchange.
            4. Based on the above analysis, infer three possible response tendencies from the user and provide suggestions.

            # Context
            The current rounds of dialogue content:
            {self.chat_history}
            I am: 
            {user_nick_name}
            ------------
            Note that your output should be divided into three parts, each separated by a blank line. Here’s an example:
                Inferred Scene: workplace

                Relationship Analysis: Supervisor and Subordinate. The supervisor is inquiring about project progress, with a somewhat formal tone but encouraging elements included.

                Possible Response Tendencies:
                1️⃣...
                2️⃣...
                3️⃣... 
"""
        message = [{"role": "system", "content": sys_prompt}]
        self.message = []

        if self.llm:
            response = self.llm(message)
            if self.verbose:
                print("=====分析=====")     
                print(response)
                print("==========")
            response_parts = response.split("\n\n")
            if len(response_parts) >= 2:
                self.scene = response_parts[1].replace("Inferred Scene:：", "").strip()
            else:
                self.scene = response_parts
                print("Warning: response does not contain enough parts. Using default scene.")
            self.analyse = response

            # 提取选项并存储到 self.options 中
            self.options = response_parts[3].split('\n') if len(response_parts) > 3 else []

            return response
    
    
    def get_response_stage2(self, userPrefer=None, analyse=None, user_nick_name=None):
         # 检测聊天记录的语言
        language = detect_language(self.chat_history)
        print("Language detected:", language)
        # 初始化self.options
        self.options = []
        # if not self.chat_history:
        #     sys_prompt = query
        # else:
            # 获取对应数据
        sys_prompt = f"""
            # Role
            You are an emotionally intelligent conversation assistant capable of determining the relevant skills needed based on different dialogue scenarios and user response tendencies.

            # Task
            【Goal】From a segment of dialogue, based on the initial scene, relationship analysis, and user feedback regarding response tendencies and desired styles, identify which emotional intelligence dialogue skills are needed. You may only choose from the list below, which categorizes various techniques. "General" indicates that the technique is broadly applicable and can be selected directly based on the dialogue scene, while the others require you to consider the dialogue content and user response tendencies for selection. You must select at least one; there is no upper limit.
                "workplace-general"
                "workplace-assigning tasks"
                "workplace-persuation"
                "daily-general"
                "daily-Opening and Continuing Conversations"
                "daily-Showing Empathy / Steering the Conversation"
                "daily-fitting into groups"
                "daily-warming up the atmosphere"
                "daily-asking questions"

            # Context
            The current rounds of dialogue content:
            {self.chat_history}
            I am: 
            {user_nick_name}

            # Analysis
            {self.analyse}


            ------------
            Note that you only need to output the skills you think are necessary for this dialogue scenario, each on a new line. Below is an example:
                "workplace-general"
                "workplace-persuation"
            """
        
        self.message = [{"role":"system","content":sys_prompt}]
        keys = []
        temp = ""
        if self.llm:
            response = self.llm(self.message)
            if self.verbose:
                print("=====搜索相关数据=====")
                print(response)
                print("==========")
            keys = [i.replace("\"", "").strip() for i in response.split("\n")]
        for scene in keys:
            if scene in scene_data.keys():
                temp += scene_data[scene] + "\n"

        sys_prompt = f"""
        # Role
        You are an interpersonal communication expert, well-versed in social nuances, and highly skilled at helping users resolve various workplace issues. You can provide emotionally intelligent response suggestions based on different dialogue scenarios and adjust content in real-time based on user feedback.

        # Task
        【Goal】From a segment of dialogue, starting with scene analysis, relationship analysis, and corresponding emotional intelligence response points for the scenario:
        1. Generally, you need to provide 3 responses that meet the 3 described user response tendencies. If the user provides custom tendencies, respond with 3 replies based on those and mimic the user's tone with emotionally intelligent response suggestions.
        2. If the provided response suggestions satisfy the other party, you may continue the dialogue based on the previous response and provide corresponding suggestions.
        3. The length of the response should be determined by the context; if it is a serious workplace setting, the response can be slightly longer; if it is a more relaxed atmosphere, the response can be shorter.

        # Context
        The current rounds of dialogue content:
        {self.chat_history}
        I am: 
        {user_nick_name}

        # Analysis
        {analyse}

        # User Custom Tendencies
        {userPrefer if userPrefer else 'None'}

        # Techniques and Key Points for Emotionally Intelligent Responses in Similar Scenarios:
        {temp}
        ------------
        Note that you only need to provide three specific response contents without generating extra quotes like "" . Below is an example; write one response per line, separating the three responses with line breaks:
            1️⃣...
            2️⃣...
            3️⃣...
        """
        # 如果语言是英文，添加一句“用英文回答”
        if language == 'en':
            sys_prompt += "\nPlease reply in English.\n"
        self.message = [{"role":"system","content":sys_prompt}]
        if self.llm:
            response = self.llm(self.message)
            if self.verbose:
                print("=====回复prompt=====")
                print(sys_prompt)
                print("==========")
                print("=====回复=====")
                print(response)
                print("==========")
            self.message += [{"role":"assistant","content":response}]
            # 解析并保存回复到self.options
            self.options = [re.sub(r"^\d+\️⃣", "", line).strip() for line in response.split("\n") if line.strip()]
            
            # 为用户提供选择提示
            if language == 'zh':
                options_prompt = "以下有几种回复参考，请问您倾向选择哪一种回复呢？当然也可以告诉我您有什么回复倾向哦~\n"
            else:
                options_prompt = "There are several possible replies, which one do you prefer? You can also tell me what kind of reply you prefer!\n"

            for i, option in enumerate(self.options, 1):
                options_prompt += f"{i}️⃣ {option.strip()}\n"
            
            return options_prompt

    def get_response_stage3(self, user_choice):
        # 确保选择有效，范围在1到3之间
        if 1 <= user_choice <= 3:
            response = self.options[user_choice - 1]  # 根据用户选择返回对应的回复
            if self.verbose:
                print("=====重复的回复=====")
                print(response)
                print("==========")
            return response
        else:
            return "Invalid option! Please enter the number(1 ~ 3)"
        
    def get_text_response(self, query):
        sys_prompt = f"""
            You are an emotional intelligence response assistant, skilled at providing thoughtful and empathetic replies to user inquiries. Your task is to understand the context of the user’s question and suggest responses that resonate with American cultural values, such as individualism, openness, and collaboration. Aim to foster a supportive dialogue that encourages trust and connection.
        """
        self.message = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": query}
        ]
        
        if self.llm:
            response = self.llm(self.message)
        return response

    def get_response_eqmaster(self, user_nick_name=None, chat_history=None, query=None):
        from NGCBot_main.BotServer.MainServer import parse_chat_message
        if chat_history:
            # 进入stage1：解析对话历史
            print("---------current stage is 1------------")
            print(chat_history)
            chat_history = parse_chat_message(chat_history)
            # chat_history += f"\n我是这段对话记录中的{user_nick_name}"
            analyse = self.get_response_stage1(chat_history, user_nick_name)
            self.current_stage = 2  # 设置状态为stage2
            # 在stage2：根据用户的回复倾向生成高情商回复建议
            print("current stage is 2")
            response = self.get_response_stage2(analyse, user_nick_name)
            self.current_stage = 3  # 设置状态为stage3
            return response
        elif query:
            if query.isdigit():
                # 用户输入的是数字，进入stage3
                user_choice = int(query.strip())  # 用户直接选择倾向
                response = self.get_response_stage3(user_choice)
            elif self.current_stage == 2:
            # 如果当前状态是stage2，重新生成stage2的回复建议
                print("current stage is 2, regenerating stage 2 response")
                response = self.get_response_stage2(query, self.analyse, user_nick_name)
            else:
                print("query provided but not a valid stage")
                response = self.get_text_response(query)
                # return "可以转发一段聊天记录给我试试哦~"
            return response
        # else:
        #     print("not a chat history")
        #     return "可以转发一段聊天记录给我试试哦~"