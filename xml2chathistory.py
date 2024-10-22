import xml.etree.ElementTree as ET

# 假设xml_data是存储该XML内容的字符串
xml_data = '''
<?xml version="1.0"?>
<msg>
        <appmsg appid="" sdkver="0">
                <title>WHISKYpop 🍭和c.llm.high 公羽的聊天记录</title>
                <des>WHISKYpop 🍭: 姐，麻烦看下邮件呢，那个资料必须今天要了，都是星期五了
c.llm.high 公羽: 那个不是我负责的
WHISKYpop 🍭: 不是一直都是你负责的吗
WHISKYpop 🍭: 以前每个月都是你发给我们的啊</des>
                <type>19</type>
                <url>https://support.weixin.qq.com/cgi-bin/mmsupport-bin/readtemplate?t=page/favorite_record__w_unsupport</url>
                <appattach>
                        <cdnthumbaeskey />
                        <aeskey />
                </appattach>
                <recorditem><![CDATA[<recordinfo><info>WHISKYpop 🍭: 姐，麻烦看下邮件呢，那个资料必须今天要了，都是星期五了  
c.llm.high 公羽: 那个不是我负责的
WHISKYpop 🍭: 不是一直都是你负责的吗
WHISKYpop 🍭: 以前每个月都是你发给我们的啊</info><datalist count="6"><dataitem datatype="1" dataid="66b74bfcaf103f5d45a3c44542ecdedb"><srcMsgLocalid>57</srcMsgLocalid><sourcetime>2024-9-4 11:47</sourcetime><fromnewmsgid>8993421136309840276</fromnewmsgid><srcMsgCreateTime>1725421626</srcMsgCreateTime><datadesc>姐，麻烦看下邮件呢，那个资料必须今天要了，都是星期五了</datadesc><dataitemsource><hashusername>71ed45edafecfc9d10c30ebfa895ad0bfce2197d66fee4d4116c3f82e8291ee2</hashusername></dataitemsource><sourcename>WHISKYpop 🍭</sourcename><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/ySBTUZnGfPLtXIMibwPD3uBISom3q2yEGcWXTQ9DPqFOZdE8AxDxFtrpgToURCMW2sRLIoqj4T14EqRBKeCiaiaMLHmHiaZ0lFHD92ic9bx3GcsBe07KTu2QRs3X5hDpnITeX/132</sourceheadurl></dataitem><dataitem datatype="1" dataid="6a2d05344e1195222493b0ee841859ea"><srcMsgLocalid>58</srcMsgLocalid><sourcetime>2024-9-4 11:49</sourcetime><fromnewmsgid>4281004847165201392</fromnewmsgid><srcMsgCreateTime>1725421762</srcMsgCreateTime><datadesc>那个不 是我负责的</datadesc><dataitemsource><hashusername>8806ba731a09f4cd55803390b669c146e8c3f8b3bbd488953c5ced8cbf29b937</hashusername></dataitemsource><sourcename>c.llm.high 公羽</sourcename><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/RhibE3hq3pdqhtoWCTP6icjvjAhZFMhM8d1tXjWJER7EaD4CtibJ0d1hgtNURhuVRPtDx2w0gIG7noDtbTo5Ytlh99kPTeUYqyHmkYSDcmjZ3L6UsTzHluBNxW3hxmGO6Vm1RCxbwp4z9eIziaFiahcCWJw/132</sourceheadurl></dataitem><dataitem datatype="1" dataid="f624fabdf0fef9850101a1d3aace79b8"><srcMsgLocalid>59</srcMsgLocalid><sourcetime>2024-9-4 13:01</sourcetime><fromnewmsgid>2114684940026698258</fromnewmsgid><srcMsgCreateTime>1725426104</srcMsgCreateTime><datadesc>不是一直都是你负责的吗</datadesc><dataitemsource><hashusername>71ed45edafecfc9d10c30ebfa895ad0bfce2197d66fee4d4116c3f82e8291ee2</hashusername></dataitemsource><sourcename>WHISKYpop 🍭</sourcename><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/ySBTUZnGfPLtXIMibwPD3uBISom3q2yEGcWXTQ9DPqFOZdE8AxDxFtrpgToURCMW2sRLIoqj4T14EqRBKeCiaiaMLHmHiaZ0lFHD92ic9bx3GcsBe07KTu2QRs3X5hDpnITeX/132</sourceheadurl></dataitem><dataitem datatype="1" dataid="128e9e24db8bd6672517b6a170e4889d"><srcMsgLocalid>60</srcMsgLocalid><sourcetime>2024-9-4 13:01</sourcetime><fromnewmsgid>6683813952718799123</fromnewmsgid><srcMsgCreateTime>1725426114</srcMsgCreateTime><datadesc>以前每个月都是你发给我们的啊</datadesc><dataitemsource><hashusername>71ed45edafecfc9d10c30ebfa895ad0bfce2197d66fee4d4116c3f82e8291ee2</hashusername></dataitemsource><sourcename>WHISKYpop 🍭</sourcename><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/ySBTUZnGfPLtXIMibwPD3uBISom3q2yEGcWXTQ9DPqFOZdE8AxDxFtrpgToURCMW2sRLIoqj4T14EqRBKeCiaiaMLHmHiaZ0lFHD92ic9bx3GcsBe07KTu2QRs3X5hDpnITeX/132</sourceheadurl></dataitem><dataitem datatype="1" dataid="82a9c480a09b424802f1212ed3427c54"><srcMsgLocalid>61</srcMsgLocalid><sourcetime>2024-9-4 13:02</sourcetime><fromnewmsgid>6941016904960416681</fromnewmsgid><srcMsgCreateTime>1725426120</srcMsgCreateTime><datadesc>是业务交给别人了吗</datadesc><dataitemsource><hashusername>71ed45edafecfc9d10c30ebfa895ad0bfce2197d66fee4d4116c3f82e8291ee2</hashusername></dataitemsource><sourcename>WHISKYpop 🍭</sourcename><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/ySBTUZnGfPLtXIMibwPD3uBISom3q2yEGcWXTQ9DPqFOZdE8AxDxFtrpgToURCMW2sRLIoqj4T14EqRBKeCiaiaMLHmHiaZ0lFHD92ic9bx3GcsBe07KTu2QRs3X5hDpnITeX/132</sourceheadurl></dataitem><dataitem datatype="1" dataid="49c95e32c9f455cc46ddbd5da67fa3e9"><srcMsgLocalid>62</srcMsgLocalid><sourcetime>2024-9-4 13:02</sourcetime><fromnewmsgid>6399128180307103139</fromnewmsgid><srcMsgCreateTime>1725426177</srcMsgCreateTime><datadesc>不知道 反 正不是我负责的&quot;</datadesc><dataitemsource><hashusername>8806ba731a09f4cd55803390b669c146e8c3f8b3bbd488953c5ced8cbf29b937</hashusername></dataitemsource><sourcename>c.llm.high 公羽</sourcename><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/RhibE3hq3pdqhtoWCTP6icjvjAhZFMhM8d1tXjWJER7EaD4CtibJ0d1hgtNURhuVRPtDx2w0gIG7noDtbTo5Ytlh99kPTeUYqyHmkYSDcmjZ3L6UsTzHluBNxW3hxmGO6Vm1RCxbwp4z9eIziaFiahcCWJw/132</sourceheadurl></dataitem></datalist><desc>WHISKYpop 🍭: 姐，麻烦看下邮件呢，那个资料必须今天要了，都是星期五了
c.llm.high 公羽: 那个不是我负责的
WHISKYpop 🍭: 不是一直都是你负责的吗
WHISKYpop 🍭: 以前每个月都是你发给我们的啊</desc><fromscene>2</fromscene></recordinfo>]]></recorditem>
        </appmsg>
        <fromusername>wxid_3cnxu4266mt012</fromusername>
        <scene>0</scene>
        <appinfo>
                <version>1</version>
                <appname></appname>
        </appinfo>
        <commenturl></commenturl>
</msg>
'''

# 解析XML
xml_data = xml_data.strip()
root = ET.fromstring(xml_data)


# 获取聊天标题
title = root.find('.//title').text
print("Chat Title:", title)

# 获取聊天描述
description = root.find('.//des').text
print("Description:", description)

# 获取消息列表中的记录项
record_item = root.find('.//recorditem').text

# recorditem 内嵌的 XML 需要再次解析
record_root = ET.fromstring(record_item)

# 获取具体的聊天记录
info = record_root.find('.//info').text
print("Chat Records:")
print(info)

# 获取每条消息的时间、发送者和内容
for dataitem in record_root.findall('.//dataitem'):
    sourcetime = dataitem.find('sourcetime').text
    sourcename = dataitem.find('sourcename').text
    datadesc = dataitem.find('datadesc').text
    print(f"Time: {sourcetime}, Sender: {sourcename}, Message: {datadesc}")
