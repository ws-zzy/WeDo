# 前后端教务接口

## URL：/usr/sign_up

* 说明：用户注册信息

`header`：     `content-type`:`application/json`

* 方法：POST

* 参数：

| 字段     | 含义                 | 类型   | 限制                        |
| -------- | -------------------- | ------ | --------------------------- |
| mail     | 用户邮箱             | string | 符合邮箱格式                |
| usr      | 用户名               | string | 8-16个字符 只包含字母和数字 |
| pwd      | 密码                 | string | 8-16个字符 只包含字母和数字 |
| iden-ord | 用户类型为普通用户   | bool   | 无                          |
| iden-dev | 用户类型为开发者     | bool   | 无                          |
| iden-lab | 用户类型为实验室官方 | bool   | 无                          |

响应：

| 字段   | 含义                                                         | 类型 |
| ------ | ------------------------------------------------------------ | ---- |
| status | 返回成功与否 200：注册成功 400：注册失败（用户已经注册）404：链接失败，找不到对象 | int  |

***

## URL：/usr/sign_in

* 说明：用户登录信息

* 方法：POST

`header`：    `content-type`:`application/json`

* 参数：

| 字段 | 含义   | 类型   | 限制                        |
| ---- | ------ | ------ | --------------------------- |
| usr  | 用户名 | string | 8-16个字符 只包含字母和数字 |
| pwd  | 密码   | string | 8-16个字符 只包含字母和数字 |

* 响应：

| 字段   | 含义                                                         | 类型 |
| ------ | ------------------------------------------------------------ | ---- |
| status | 返回成功与否 200：注册成功 400：登录失败 404：链接失败，找不到对象 | int  |

***

## URL：/usr/info/mail

* 说明：修改用户邮箱

* 方法：POST

`header`：    `content-type`:`application/json`

* 参数：

| 字段 | 含义   | 类型   | 限制           |
| ---- | ------ | ------ | -------------- |
| mail | 新邮箱 | string | 必须为邮箱格式 |

* 响应：

| 字段   | 含义          | 类型 |
| ------ | ------------- | ---- |
| status | 200：修改成功 | int  |

***

## URL：/usr/info/name

* 说明：修改用户昵称

* 方法：POST

`header`：    `content-type`:`application/json`

* 参数：

| 字段 | 含义     | 类型   | 限制                        |
| ---- | -------- | ------ | --------------------------- |
| name | 用户昵称 | string | 8-16个字符 只包含字母和数字 |

* 响应：

| 字段   | 含义          | 类型 |
| ------ | ------------- | ---- |
| status | 200：修改成功 | int  |

***

## URL：/usr/info/password

* 说明：修改用户密码

* 方法：POST

`header`：    `content-type`:`application/json`

* 参数：

| 字段     | 含义     | 类型   | 限制                        |
| -------- | -------- | ------ | --------------------------- |
| password | 用户密码 | string | 8-16个字符 只包含字母和数字 |

* 响应：

| 字段   | 含义          | 类型 |
| ------ | ------------- | ---- |
| status | 200：修改成功 | int  |

***

## URL：/usr/info/collection

* 说明：获取用户收藏

* 方法：GET

`header`：    `content-type`:`application/json`

* 参数：

| 字段 | 含义                          | 类型 | 限制           |
| ---- | ----------------------------- | ---- | -------------- |
| page | 显示第几页的内容 一页20个项目 | int  | 不得超过总页数 |

* 响应：

| 字段          | 含义                                             | 类型   |
| ------------- | ------------------------------------------------ | ------ |
| status        | 返回成功与否  200：OK  404：链接失败，找不到对象 | int    |
| link          | 下一个列表的位置                                 | string |
| project       | 以下内容为project数组的单个元素                  | array  |
| photo_url     | 项目照片的url                                    | string |
| project_name  | 项目名                                           | string |
| project_intro | 项目简介                                         | string |

***

## URL：/usr/info/follow

* 说明：获取用户关注的项目

* 方法：GET

`header`：    `content-type`:`application/json`

* 参数：

| 字段 | 含义                          | 类型 | 限制           |
| ---- | ----------------------------- | ---- | -------------- |
| page | 显示第几页的内容 一页20个项目 | int  | 不得超过总页数 |

* 响应：

| 字段          | 含义                                             | 类型   |
| ------------- | ------------------------------------------------ | ------ |
| status        | 返回成功与否  200：OK  404：链接失败，找不到对象 | int    |
| link          | 下一个列表的位置                                 | string |
| project       | 以下内容为project数组的单个元素                  | array  |
| photo_url     | 项目照片的url                                    | string |
| project_name  | 项目名                                           | string |
| project_intro | 项目简介                                         | string |

***

## URL：/usr/info/public

* 说明：获取用户发布的项目

* 方法：GET

`header`：    `content-type`:`application/json`

* 参数：

| 字段 | 含义                          | 类型 | 限制           |
| ---- | ----------------------------- | ---- | -------------- |
| page | 显示第几页的内容 一页20个项目 | int  | 不得超过总页数 |

* 响应：

| 字段          | 含义                                             | 类型   |
| ------------- | ------------------------------------------------ | ------ |
| status        | 返回成功与否  200：OK  404：链接失败，找不到对象 | int    |
| link          | 下一个列表的位置                                 | string |
| project       | 以下内容为project数组的单个元素                  | array  |
| photo_url     | 项目照片的url                                    | string |
| project_name  | 项目名                                           | string |
| project_intro | 项目简介                                         | string |

***

## URL：/usr/info/participate

* 说明：获取用户参与的项目

* 方法：GET

`header`：    `content-type`:`application/json`

* 参数：

| 字段 | 含义                          | 类型 | 限制           |
| ---- | ----------------------------- | ---- | -------------- |
| page | 显示第几页的内容 一页20个项目 | int  | 不得超过总页数 |

* 响应：

| 字段          | 含义                                             | 类型   |
| ------------- | ------------------------------------------------ | ------ |
| status        | 返回成功与否  200：OK  404：链接失败，找不到对象 | int    |
| link          | 下一个列表的位置                                 | string |
| project       | 以下内容为project数组的单个元素                  | array  |
| photo_url     | 项目照片的url                                    | string |
| project_name  | 项目名                                           | string |
| project_intro | 项目简介                                         | string |


***
