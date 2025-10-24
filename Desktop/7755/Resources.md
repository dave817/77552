商量大语言模型-拟人对话
SenseChat-Character-Pro
拟人对话
模型简介	日日新-商量大语言模型-拟人对话-高级版
模型最大上下文长度限制	32K(32768)，单位 token
模型权限	公开调用
模型速率限制	60 RPM
适配接口	拟人对话生成
模型能力说明
能力提升：在标准版的基础上，角色对话、人设、及剧情推动能力全面提升 
更长记忆：支持32K上下文长度，使AI角色可精准记忆百轮以上历史对话内容
中英适配：支持中/英文对话，赋能海外拟人对话场景
特殊参数说明
请求体参数中的max_new_tokens取值范围[1,4096]，默认值500



A. 如何使用【对话生成】
在本入门教程中，我们将演示如何通过我们的 OpenAPI ，使用对话生成。


一、调用前的准备工作
首先，您需要完成一些调用前的准备工作，主要包括：

“获取访问密钥”
“生成API_TOKEN”

二、获取您可用的模型列表
调用 “获取模型列表” 接口，查看您可用的模型ID。 关于每个模型的介绍，可以查看 模型清单 。


三、使用对话生成
调用 “对话生成” 接口，进行对话。其中，有几个参数的使用方法需要注意：

请求体中的 model 参数
直接填写您从第二步获取到的模型ID即可。

请求体中的 messages 参数
您可以在这个参数中填写您想跟大模型对话的内容，也可以给一些对话历史，例如：

直接对话：
{
    "messages": [
        {
            "role": "user",
            "content": "北京有哪些好吃的？"
        }
    ]
}
带对话历史：
{
    "messages": [
        {
            "role": "user",
            "content": "北京有哪些好吃的？"
        },
        {
            "role": "assistant",
            "content": "北京作为中国首都，拥有丰富的饮食文化，以下是一些北京著名的美食：\n\n1. 烤鸭：烤鸭是北京最著名的传统美食之一，其肉质鲜美，皮脆肉嫩。\n\n2. 烤羊肉串：羊肉串是北京特色小吃之一，口感鲜美，价格实惠。"
        },
        {
            "role": "user",
            "content": "还有哪些？"
        }
    ]
}

B. 如何使用【知识库构建】
在本入门教程中，我们将演示如何通过我们的 OpenAPI 构建一个简单的知识库。


一、调用前的准备工作
首先，您需要完成一些调用前的准备工作，主要包括：

“获取访问密钥”
“生成API_TOKEN”

二、创建一个知识库
目前版本（Beta），可按照以下步骤，一步一步调用接口，完成一个知识库的创建：

准备一份给知识库使用的文件，请您注意，当前版本（Beta）对数据格式和文件格式有一些要求，具体要求如下：

对中文支持较好，其他语言的支持后续会逐步完善
1个知识库支持上传50个文件
单个文件大小不能超过20M
此处说明的文件格式为 .json，其余格式请参考创建并上传文件
编码格式为 UTF-8
内容需遵循以下格式
{
    "qa_lst": [ //问答对知识
        {
            "std_q": "xxx", //问题描述
            "simi_qs": ["xxx", "xxx"], //相似问题描述
            "answer": "xxx" //答案描述
        },
        {
            "std_q": "xxx", //问题描述
            "simi_qs": ["xxx", "xxx"], //相似问题描述
            "answer": "xxx" //答案描述
        }
    ],
    "text_lst": [ //文本知识，纯文本数据（当前版本（Beta），建议每条数据尽量是一个独立的语义主题，便于提升检索效率和效果）
        "xxx",
        "xxx"
    ]
}


调用 创建并上传文件 接口，上传知识库文件，获得一个“文件ID”

调用 查询文件详情 接口，查看“文件格式校验状态”：

当 “文件状态” = NOTUPLOADED 时，表明文件正在上传过程中
当 “文件状态” = UPLOADED 时，表明文件已经上传完成
当 “文件状态” = VALID 时，表明文件格式校验通过，可以开始执行下一步
当 “文件状态” = INVALID 时，表明文件格式或数据格式有问题、没通过校验，此时您需要参照详细校验信息（validate_result）调整您的知识库文件，并在调整完成后重新上传
调用 创建知识库 接口，使用步骤2获得的“文件ID”创建知识库，获得一个“知识库ID”

调用 查询知识库详情 接口，查看“知识库状态”：

当 “知识库状态” = PENDING时，表明知识库等待创建中
当 “知识库状态” = LOADING时，表明知识库正在创建过程中
当 “知识库状态” = UNAVAILABLE时，表明知识库创建失败
当 “知识库状态” = AVAILABLE时，表明知识库已经创建成功

三、尝试在对话中使用该知识库
完成创建知识库后，您可以开始调用 对话生成 接口，尝试使用您的知识库，具体使用方法如下：

在接口请求体的 know_ids 里，填写您第二步获得的“知识库ID”即可。

C. 接口鉴权
注意：平台已支持API Key调用，请用户保管好自己的API Key，在ModelStudio 管理中心 API Key管理进行密钥的创建操作

请求头（Request Header）
在请求头里，添加 Authorization 字段，如下所示：

Authorization: Bearer $API_TOKEN //$API_TOKEN 可直接用$API_KEY替换


Authorization` 生成方式
遵循JWT（Json Web Token, RFC 7519）标准。

JWT由三个部分组成：Header、Payload、Signature。

JWT Header 的构建方式
{"typ":"JWT","alg":"HS256"}  # 手动生成JWT，JWT Header中alg填写HS256

JWT Payload 的构建方式
名称	类型	必须	描述
iss	String	是	AK（Access Key ID，获取方式请参考使用手册-“获取访问密钥”）
exp	Integer	是	超时时间（Unix时间戳，单位秒）
nbf	Integer	否	生效时间（Unix时间戳，单位秒），在此时间前无法使用
JWT Signature 的构建方式
SK（Access Key Secret，获取方式请参考使用手册-“获取访问密钥”）


生成示例
1 Python Sample Code
首先，您可以通过 pip 安装的方式将 PyJWT 安装到您的环境中，在命令行中执行如下命令：

pip3 install PyJWT==2.6.0

然后，可按照以下样例生成 Authorization：

import time
import jwt

ak = "" # 填写您的ak
sk = "" # 填写您的sk

def encode_jwt_token(ak, sk):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 1800, # 填写您期望的有效时间，此处示例代表当前时间+30分钟
        "nbf": int(time.time()) - 5 # 填写您期望的生效时间，此处示例代表当前时间-5秒
    }
    token = jwt.encode(payload, sk, headers=headers)
    return token

authorization = encode_jwt_token(ak, sk)
print(authorization) # 打印生成的API_TOKEN


2 Java Sample Code
package test;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;

public class JWTDemo {
    
    static String ak = ""; // 填写您的ak
    static String sk = ""; // 填写您的sk
    
    public static void main(String[] args) {
        String token = sign(ak, sk);
        System.out.println(token); // 打印生成的API_TOKEN
    }
    static String sign(String ak,String sk) {
        try {
            Date expiredAt = new Date(System.currentTimeMillis() + 1800*1000);
            Date notBefore = new Date(System.currentTimeMillis() - 5*1000);
            Algorithm algo = Algorithm.HMAC256(sk);
            Map<String, Object> header = new HashMap<String, Object>();
            header.put("alg", "HS256");
            return JWT.create()
                    .withIssuer(ak)
                    .withHeader(header)
                    .withExpiresAt(expiredAt)
                    .withNotBefore(notBefore)
                    .sign(algo);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
}


3 Golang Sample Code
package main

import (
    "encoding/json"
    "fmt"
    "time"
    "github.com/golang-jwt/jwt/v4"
)

func EncodeJwtToken(ak string, sk string) (string, error) {
    payload := jwt.MapClaims{
        "iss": ak,
        "exp": time.Now().Add(1800 * time.Second).Unix(),
        "nbf": time.Now().Add(-5 * time.Second).Unix(),
    }
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, payload)
    signedToken, err := token.SignedString([]byte(sk))
    if err != nil {
        fmt.Println("Error encoding JWT token:", err)
        return "", err
    }
    return signedToken, nil
}

func main() {
    ak := "" // 填写您的ak
    sk := "" // 填写您的sk
    token, err := EncodeJwtToken(ak, sk)
    if err != nil {
        fmt.Println("Error:", err)
    } else {
        fmt.Println("Encoded JWT token:", token) // 打印生成的API_TOKEN
    }
}

D. 拟人对话生成
接口描述（Description）
模型基于人设进行角色扮演，可实现多人对话生成


请求地址（Request URL）
[POST] https://api.sensenova.cn/v1/llm/character/chat-completions


请求头（Request Header）
无特殊Header，请参考接口鉴权


请求体（Request Body）
请注意，单次请求，用户输入的token总数（即所有content的token总数） + 用户输入的角色设定（即character_settings的token总数） + 用户期望模型生成的最大token数（即max_new_tokens的值），必须 <= 模型最大上下文长度（不同模型的上下文长度支持情况，参考模型清单）。

名称	类型	必须	默认值	可选值	描述
model	string	是	-	参考模型清单	模型ID
n	int	否	1	[1,4]	生成回复数量，响应参数中的index即为回复序号（在使用某些模型时不支持传入该参数，详情请参考模型清单）
max_new_tokens	int	否	300	[1,1024]	期望模型生成的最大token数（不同模型支持的上下文长度不同，因此最大值也不同，参考模型清单）
messages	object[]	是	-	-	输入给模型的对话上下文，数组中的每个对象为聊天的上下文信息
character_settings	object[]	是	-	-	多人对话中每个人的人物设定
role_setting	object	是	-	-	本轮对话的设定
extra	string	否	-	-	额外信息，用户自传
know_ids	string[]	否	-	参考查询知识库列表	检索的知识库列表
knowledge_config	object	否	-	-	知识配置
messages 部分参数如下：
名称	类型	必须	默认值	可选值	描述
name	string	是	-	角色姓名，只能选择character_settings中已设定的name	
content	string	是	-	-	对话的内容
character_settings 部分参数如下：
名称	类型	必须	默认值	可选值	描述
name	string	是	-	-	角色姓名，长度不超过50个字符
gender	string	是	-	-	角色性别，长度不超过50个字符
identity	string	否	-	-	角色身份，长度不超过200个字符
nickname	string	否	-	-	角色别名，长度不超过50个字符
feeling_toward	object[]	否	-	-	好感度设定
detail_setting	string	否	-	-	详细设定，长度不超过500个字符
other_setting	json string	否	-	-	其他设定，长度不超过2000个字符
role_setting 部分参数如下：
名称	类型	必须	默认值	可选值	描述
user_name	string	是	-	-	指定本次回复，用户扮演哪个角色，只能选择character_settings中已设定的name
primary_bot_name	string	是	-	-	指定本次回复，模型扮演哪个角色，只能选择character_settings中已设定的name
feeling_toward 部分参数如下：
名称	类型	必须	默认值	可选值	描述
name	string	是	-	-	角色姓名，只能选择character_settings中已设定的name
level	int	是	-	[1,3]	对该角色的好感度，数字越大代表好感度越高
knowledge_config 部分参数如下：
名称	类型	必须	默认值	可选值	描述
knowledge_base_result	boolean	否	false	true
false	是否返回本次请求查询的知识库检索结果
true：返回
false：不返回
knowledge_base_configs	object[]	否	-	-	知识库配置
knowledge_base_configs 部分参数如下：
名称	类型	必须	默认值	可选值	描述
know_id	string	是	-	本次请求检索的知识库ID（konw_ids中的知识库ID）	需要实现配置的知识库ID
faq_threshold	float	是	-	(0,1)	知识库中的qa_lst精准命中程度的阈值配置，越高代表对该知识库中问答对的检索结果相似度要求越严格

请求示例（Request Example）
curl --request POST "https://api.sensenova.cn/v1/llm/character/chat-completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
        "max_new_tokens": 1024, 
        "messages": [
          {
            "name": "string", 
            "content": "string" 
          }
        ],
        "character_settings":[
          {
            "name": "string", 
            "gender": "string", 
            "identity": "string",
            "nickname": "string",
            "feeling_toward":[
              {
                "name": "string", 
                "level": 1
              }
            ],
            "detail_setting": "string",
            "other_setting": "json string"
          }
        ],
        "role_setting":{
            "user_name": "string",
            "primary_bot_name": "string"
        },
        "model": "string", 
        "n": 1,
        "extra": "string",
        "know_ids": [
          "string"
        ],
        "knowledge_config": {
          "knowledge_base_result": false, 
          "knowledge_base_configs":[
            {
              "know_id": "string",
              "faq_threshold": 0
            }
          ]
        }
  }'


响应（Response）
名称	类型	描述
data	object	生成内容
data 部分参数如下：
名称	类型	描述
id	string	消息ID
reply	string	模型生成的最优回复
choices	object[]	生成的回复列表
knowledge_base_results	object[]	知识检索中间结果
usage	object	token使用量
choices 部分参数如下：
名称	类型	描述
message	string	生成的回复内容
finish_reason	string	停止生成的原因，枚举值
因结束符停止生成：stop
因达到最大生成长度停止生成：length
因触发敏感词停止生成： sensitive
因触发模型上下文长度限制： context
index	int	生成的回复序号
knowledge_base_results 部分参数如下：
名称	类型	描述
know_id	string	查询的知识库ID
results	object[]	查询到的知识库内容
usage 部分参数如下：
名称	类型	描述
prompt_tokens	int	用户输入内容的token数
completion_tokens	int	生成消息对应的token数
knowledge_tokens	int	知识库内容输入模型的token数（仅在使用了知识库且检索到知识库内容的情况下不为0）
total_tokens	int	总token数

响应示例（Response Example）
{
    "data":{
        "id":"9a18cd7f047c4b9498920d7c27a7d707", 
        "reply":"(站起身，走到他身边，俯下身，伸手拿过他手中的毛笔，将它放在一旁，然后坐在他身边，双手撑着桌子，看着他)臣有事要与陛下商议。",
        "choices":[
            {
                "index":0,
                "finish_reason":"stop", 
                "message":"这句话的翻译是：Who am I?"
            }
        ],
        "knowledge_base_results": [
          {
            "know_id": "string",
            "results": [
              {
                "result": "string",
                "score": 0
              }
            ]
          }
        ],
        "usage":{
            "prompt_tokens":12,
            "completion_tokens":170,
            "knowledge_tokens": 0,
            "total_tokens":182
        }
    }
}

E. 官方库
Python库
对于使用 Python 的开发者，我们提供了一个 Python库。

该库的设计目标是提供一种简单、灵活、强大的方式，让您可以直接从 Python 应用程序中使用我们的服务。

一、如何安装
您可以使用 pip 来安装它，并将其导入到您的项目中开始调用API。安装命令如下：

$ pip install sensenova

二、确认鉴权
python库，对HTTP接口里需要用户用JWT生成TOKEN的方法实现了内嵌，用户可以直接填写获取到的 Access Key ID 和 Access Key Sercret 。

您可以通过设置环境变量（设置完成后，sensenova会自动提取）：

export SENSENOVA_ACCESS_KEY_ID=
export SENSENOVA_SECRET_ACCESS_KEY=

或者在代码里直接给 sensenova.access_key_id 和 sensenova.secret_access_key 赋值：

# -*- coding: utf-8 -*-
import sensenova

sensenova.access_key_id = "..."
sensenova.secret_access_key = "..."

三、在代码里集成调用接口
【获取headers】

# -*- coding: utf-8 -*-
import sensenova

resp = sensenova.Model.list()
#获取http headers
print(resp.headers())

【捕获错误】

# -*- coding: utf-8 -*-
import sensenova

try:
    resp = sensenova.Model.list()
    #获取http headers
    print(resp.headers())
except sensenova.AuthenticationError as e:
    #自定义处理逻辑
    print(e.json_body)
except sensenova.InvalidRequestError as e:
    #自定义处理逻辑
    print(e.headers)
    print(e.http_body)
    print(e.code)
except sensenova.APIError as e:
    #自定义处理逻辑
    print(e.headers)
except sensenova.TryAgain as e:
    #自定义处理逻辑
    print(e.headers)
except sensenova.PermissionError as e:
    #自定义处理逻辑
    print(e.headers)
except sensenova.SensenovaError as e:
    #自定义处理逻辑
    print(e.headers)

【模型管理】

查询模型列表
# -*- coding: utf-8 -*-
import sensenova

resp = sensenova.Model.list()

查询模型详情
# -*- coding: utf-8 -*-
import sensenova

resp = sensenova.Model.retrieve(id=model_id)


【对话生成-无会话历史】

# -*- coding: utf-8 -*-
import sensenova
import sys

stream = True # 流式输出或非流式输出
model_id = "" # 填写真实的模型ID

resp = sensenova.ChatCompletion.create(
    messages=[{"role": "user", "content": "Say this is a test!"}],
    model=model_id,
    stream=stream,
    max_new_tokens=1024,
    n=1,
    repetition_penalty=1.05,
    temperature=0.8,
    top_p=0.7,
    know_ids=[],
    user="sensenova-python-test-user",
    knowledge_config={
        "control_level": "normal",
        "knowledge_base_result": True,
        "knowledge_base_configs":[]
    },
    plugins={
        "associated_knowledge": {
            "content": "需要注入给模型的知识",
            "mode": "concatenate"
        },
        "web_search": {
            "search_enable": True,
            "result_enable": True
        },
    }
)

if not stream:
    resp = [resp]
for part in resp:
    choices = part['data']["choices"]
    for c_idx, c in enumerate(choices):
        if len(choices) > 1:
            sys.stdout.write("===== Chat Completion {} =====\n".format(c_idx))
        if stream:
            delta = c.get("delta")
            if delta:
                sys.stdout.write(delta)
        else:
            sys.stdout.write(c["message"])
            if len(choices) > 1:
                sys.stdout.write("\n")
        sys.stdout.flush()


【对话生成-有会话历史】

# -*- coding: utf-8 -*-
import sensenova
import sys
# 创建会话
resp = sensenova.ChatSession.create(
    system_prompt = [
        {
            "role": "system",
            "content": "You are a translation expert."
        }
    ]
)
session_id = resp["session_id"]
# 有状态对话生成
stream = True # 流式输出或非流式输出
model_id = "" # 填写真实的模型ID
resp = sensenova.ChatConversation.create(
    action="next",
    content="地球的直径是多少米?",
    model=model_id,
    session_id=session_id,
    stream=stream,
    know_ids=[],
    knowledge_config={
        "control_level": "normal",
        "knowledge_base_result": True,
        "knowledge_base_configs":[]
    },
    plugins={
        "associated_knowledge": {
            "content": "需要注入给模型的知识",
            "mode": "concatenate"
        },
        "web_search": {
            "search_enable": True,
            "result_enable": True
        },
    }
)

if not stream:
    resp = [resp]
for part in resp:
    if stream:
        delta = part["data"]["delta"]
        if delta:
            sys.stdout.write(delta)
    else:
        sys.stdout.write(part["data"]["message"])
    sys.stdout.flush()



【文本补全】

# -*- coding: utf-8 -*-
import sensenova
import sys

stream = True # 流式输出或非流式输出
model_id = "" # 填写真实的模型ID

resp = sensenova.Completion.create(
    prompt="床前明月光下一句是什么",
    model=model_id,
    stream=stream,
    n=1,
    max_new_tokens=1024,
    repetition_penalty=1.05,
    stop=None,
    temperature=0.8,
    top_p=0.7
)

if not stream:
    resp = [resp]
for part in resp:
    choices = part['data']["choices"]
    for c_idx, c in enumerate(choices):
        if len(choices) > 1:
            sys.stdout.write("===== Chat Completion {} =====\n".format(c_idx))
        if stream:
            delta = c.get("delta")
            if delta:
                sys.stdout.write(delta)
        else:
            sys.stdout.write(c["text"])
            if len(choices) > 1:
                sys.stdout.write("\n")
        sys.stdout.flush()


【拟人对话生成】

# -*- coding: utf-8 -*-
import sensenova
import sys

model_id = "" # 填写真实的模型ID

resp = sensenova.CharacterChatCompletion.create(
    model=model_id,
    n=1,
    max_new_tokens=300,
    character_settings=[
        {
            "name": "角色1",
            "gender": "男",
            "nickname": "",
            "other_setting": "",
            "identity": "",
            "feeling_toward": [],
            "detail_setting": "",
        },
        {
            "name": "角色2",
            "gender": "女",
            "nickname": "",
            "other_setting": "",
            "identity": "",
            "feeling_toward": [],
            "detail_setting": "",
        },
    ],
    role_setting={
        "user_name": "角色1",
        "primary_bot_name": "角色2"
    },
    messages=[
        {
            "name": "角色1",
            "content": "举头望明月下一句是什么"
        }
    ]
)

choices = resp['data']["choices"]
for c_idx, c in enumerate(choices):
    if len(choices) > 1:
        sys.stdout.write("===== Character Chat Completion {} =====\n".format(c_idx))

    sys.stdout.write(c["message"])
    if len(choices) > 1:  # not in streams
        sys.stdout.write("\n")
    sys.stdout.flush()


【文本转向量】

# -*- coding: utf-8 -*-
import sensenova
import sys

model_id = "" # 填写真实的模型ID

resp = sensenova.Embedding.create(
    model=model_id,
    input=["今天天气怎么样"]
)
print(resp)


【知识库构建】

# -*- coding: utf-8 -*-
import sensenova

description="" #知识库描述
file_id="" #通过【文件管理】模块创建的文件id，只能是schemd="KNOWLEDGE_BASE_1"的文件
files=[file_id] #可以为空

## 创建知识库
resp = sensenova.KnowledgeBase.create(description=description,files=files)

knowledge_base_id=resp["knowledge_base"]["id"] #知识库id
## 更新知识库
resp = sensenova.KnowledgeBase.update(description=description,files=files,sid=knowledge_base_id)
## 查询知识库列表
resp = sensenova.KnowledgeBase.list()
## 查询知识库详情
resp = sensenova.KnowledgeBase.retrieve(id=knowledge_base_id)
## 删除知识库
resp = sensenova.KnowledgeBase.delete(sid=knowledge_base_id)



【文件管理】

# -*- coding: utf-8 -*-
import sensenova
import io
import json

# 创建文件
payload = {
    "text_lst": [
        "xxx"
    ]
}
file = io.StringIO(json.dumps(payload, ensure_ascii=False)) #构造一个file对象即可
scheme="KNOWLEDGE_BASE_1" #枚举值，请参考文件管理API文档
resp = sensenova.File.create(file=file,scheme=scheme,description="file desc")

file_id = resp["id"]
# 查询文件
resp = sensenova.File.retrieve(id=file_id)
# 下载文件
resp = sensenova.File.download(id=file_id) #resp为文件的原始内容，只有文件status="VALID"的才可以下文件内容
# 删除文件
resp = sensenova.File.delete(id=file_id)
#文件列表
resp = sensenova.File.list()




四、直接通过 Python Cli 调用接口
# 【模型管理】

## 查询模型列表
sensenova api models.list
## 查询模型详情
sensenova api models.get -i $model_id


#  【对话生成】

## 【对话生成-无会话历史】
sensenova api chat_completions.create -m $model_id -g "user" "Say this is a test! " --n 1 --stream 

## 【对话生成-有对话历史】
### 【创建会话】
sensenova api  chat_sessions.create  --prompts $role $prompt --prompts $role,$prompt

###【对话生成-有会话历史】
sensenova api  chat_conversations.create -m $model_id -s $session_id -a $action -c $content --stream

### 【文本补全】
sensenova api completions.create -m $model_id --stream -n 2 --max_new_tokens 1024 --repetition_penalty 1.05 --temperature 0.8 --top_p 0.7 --stop "" --prompt 今天天气怎么样
