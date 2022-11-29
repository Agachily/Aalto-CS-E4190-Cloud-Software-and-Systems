1. gPRC是Remote Procedure Calls的一种开源实现，使用gPRC， 一台机器上的程序可以调用另一台机器上的程序，就像调用本机上的程序一样。

2. In gRPC, a client application can directly call a method on a server application on a different machine as if it were a local object, making it easier for you to create distributed applications and services. 

   As in many RPC systems, gRPC is based around the idea of defining a service, specifying the methods that can be called remotely with their parameters and return types. On the server side, the server implements this interface and runs a gRPC server to handle client calls. On the client side, the client has a stub (referred to as just a client in some languages) that provides the same methods as the server.

3. gPRC使用Protocol Buffers来定义要在客户端和服务器端之间传输信息的格式。

4. 为什么使用Protocol Buffers

   The example we're going to use is a very simple "address book" application that can read and write people's contact details to and from a file. Each person in the address book has a name, an ID, an email address, and a contact phone number.

   How do you serialize and retrieve structured data like this? There are a few ways to solve this problem:

   - Use Python pickling. This is the default approach since it's built into the language, but it doesn't deal well with schema evolution, and also doesn't work very well if you need to share data with applications written in C++ or Java.
   - You can invent an ad-hoc way to encode the data items into a single string – such as encoding 4 ints as "12:3:-23:67". This is a simple and flexible approach, although it does require writing one-off encoding and parsing code, and the parsing imposes a small run-time cost. This works best for encoding very simple data.
   - Serialize the data to XML. This approach can be very attractive since XML is (sort of) human readable and there are binding libraries for lots of languages. This can be a good choice if you want to share data with other applications/projects. However, XML is notoriously space intensive, and encoding/decoding it can impose a huge performance penalty on applications. Also, navigating an XML DOM tree is considerably more complicated than navigating simple fields in a class normally would be.

   Protocol Buffer实际上就是方法2的变形。根据用户所定义的文件格式，Protocol Buffer工具会自动生成相应的代码，来将要传输的消息进行编码并传输。而无需用户自己进行定义。

