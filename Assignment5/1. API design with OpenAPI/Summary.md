1. 什么是OnpenAPI
OpenAPI是一种用来描述RESTful风格API的文档规范。其定义了这些API应当如何被描述。使用OpenAPI我们可以对所要开发的API进行很规范的描述。

2. OpenAPI的描述范围
An OpenAPI file allows you to describe your entire API, including:
	- Available endpoints (/users) and operations on each endpoint (GET /users, POST /users)
	- Operation parameters Input and output for each operation
	- Authentication methods
	- Contact information, license, terms of use and other information.
在本次练习中，我们主要关注：
	- 如何描述URL以及对URL的操作
	- 如何描述请求参数
	- 如何描述请求体
	- 如何描述响应信息（包括响应数据，响应状态码等）

3. 如何定义data scheme以及在多个响应信息中对其进行复用。以及如何使用所定义的这些data scheme
