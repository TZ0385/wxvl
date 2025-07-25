#  Beyond REST：一种用于全面API漏洞模糊测试的工具APIF  
FuzzWiki  FuzzWiki   2025-06-16 01:48  
  
![](https://mmbiz.qpic.cn/mmbiz_gif/JchE46RGRlr92CPaC2cSiaTUCEWwOd0OucLNLlY09jGCso4gTL4BmXsBNsvOlSMv9qPopLaecg7r21KD4gBERqA/640?wx_fmt=gif "")  
  
  
**基本信息**  
  
**原文名称：**  
Beyond REST: Introducing APIF for Comprehensive API Vulnerability Fuzzing  
  
**原文作者：**  
Yu Wang，Tsinghua University；Yue Xu，PTLAB  
  
**原文链接：**  
https://dl.acm.org/doi/abs/10.1145/3678890.3678928  
  
**发表期刊：**  
RAID2024  
  
**开源代码：**  
https://github.com/apif-tool/APIF_ tool_2024（已关闭）  
  
   
  
  
  
  
**一、摘要**  
  
  
在现代软件开发中，API发挥着至关重要的作用，它们促进了平台间的互操作性并作为数据传输的通道。API模糊测试（API fuzzing）已经成为探索Web应用程序、云服务和物联网（IoT）系统中的错误和漏洞的重要方法。其有效性高度依赖于参数结构分析和模糊请求生成。然而，现有方法更多地集中在RESTful API上，缺乏对其他协议的普遍适用性。此外，测试有效负载和测试效率的不足限制了这些方法在现实场景中的大规模应用。本文介绍了APIF，一种新型的API模糊测试框架，包含了三种创新设计。首先，APIF  
采用树形结构模型来解析和变异不同API协议中的参数，从而突破了现有研究仅适用于RESTful API的局限性，拓宽了其适用范围。其次，APIF  
使用递归解码器处理API参数中的复杂编码，增加了模糊测试的有效性。第三，APIF  
结合测试优先级计算算法和参数独立性分析算法，提高了模糊测试的效率，使得该方法能够广泛应用于现实中的大规模API漏洞模糊测试。论文在7个开源项目中通过412个API对APIF进行了与现有最先进模糊测试工具的比较。结果表明，APIF在精度、召回率和效率方面具有显著优势。此外，在实际的API漏洞探索中，APIF在60个API项目中发现了188个漏洞，其中26个漏洞已被软件维护者确认。  
  
**二、研究背景**  
  
**2.1  现代服务中的API**  
  
Web服务API  
  
传统的Web应用程序通常使用GET/POST方法来获取用户输入的数据，其中：1）GET请求用于加载网页或获取资源；2）POST方法提交表单数据，如用户登录凭据或支付信息。在更先进的应用场景中，WebSocket API提供了客户端和服务器之间的实时双向通信，非常适合聊天应用或实时更新。此外，GraphQL API提供了一种更高效、更灵活的查询和操作数据的方式，允许客户端精确指定所需的数据。通过探索这些不同的API，开发者可以识别并解决更广泛的漏洞问题，如注入攻击、会话劫持或Web应用中的数据过度/不足获取问题。  
  
云服务API  
  
大多数云服务的访问通常是通过RESTful API提供的，这些API支持多种功能。在实践中，不同的请求类型会触发云服务返回不同的响应。例如，在云计算平台中，客户端可以：1）使用GET方法检索他们当前使用的服务列表；2）使用POST方法创建虚拟机实例、容器和数据库；3）使用PUT方法更新资源信息；4）使用DELETE方法删除特定的资源。这些操作允许探索云服务的不同状态。通过自动生成并发送请求序列到云服务的REST API，黑盒测试工具可以探索隐藏在不同状态中的错误，并发现诸如命令注入、数据泄露和不当访问管理等漏洞。  
  
IoT系统API  
  
在物联网（IoT）领域，MQTT是一种广泛使用的轻量级消息传递协议，适用于小型传感器和移动设备。它实现了物联网设备与服务器之间高效可靠的交易。例如，在MQTT API中，客户端可以：1）订阅主题，以接收来自设备的更新或传感器数据；2）向主题发布消息，向设备发送命令或配置更改；3）使用服务质量（QoS）级别，以确保消息根据所需的保障等级进行传递；4）使用保留消息，持久化最后一条相关消息以供未来的订阅者使用。这些MQTT API操作是物联网通信中实时、事件驱动特性的核心。通过严格测试MQTT API消息和主题订阅，安全工具可以识别漏洞，如不当的消息处理、不安全的主题订阅以及潜在的窃听风险。  
  
**2.2  API漏洞模糊测试**  
  
现有的API模糊测试方法  
旨在探索隐藏在API服务可达执行状态中的错误。首先，模糊测试工具从OAS文件中读取信息，解析出API的访问路径、身份验证机制和参数结构等关键信息，并生成包含可模糊测试参数的请求模板。随后，它从预定义的模糊测试库中选择特定的测试向量，这些向量根据API中包含的不同参数进行定制。然后，这些向量用于插入或替换现有的参数值，创建符合API参数结构的请求。最后，工具将完整的测试请求发送到目标API，获取响应数据，并将其与预定义的响应检查器进行比较。这个过程有助于确定API是否存在错误或安全漏洞。API模糊测试工具的主要模块如下。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlqVzxoZRMk5iaarnb3icYdbj4Vj9KnBAZhUzDViaaQ0pbxzGjRsbZMo6oL5tS0RafG92yrq00diaHdOmQ/640?wx_fmt=png&from=appmsg "")  
  
**图 1  将RESTful API规范转换为请求模板，以及生成的请求和相应的响应的示例**  
  
API 参数解析  
  
API模糊测试工具需要解析API的请求消息结构，随后构建请求模板，以便进行后续的模糊测试过程。具体流程如下：首先，测试工具需要读取每个API的OAS文件，该文件包含关键的细节信息，如API请求路径、请求方法、参数名称和输入约束，如图1a所示。为了获取API规范，用户有两种主要方法：1) 手动定义API的路径和参数结构，读取供应商在网页上发布的API文档；2) 从API供应商提供的公开OAS URL或Swagger文件中自动解析。接着，基于该规范，模糊测试工具进行静态分析，构建请求模板，如图1b所示。在模板中，使用不同类型的变量来组装完整的API请求。在这里，Static类型表示不可变的字符串，用于确保请求消息的合法性，并且不受修改。Consumer类型要求输入具有上下文依赖性的指定数据。Fuzzable类型的值则用于后续的测试向量生成阶段。在该阶段，这些值将被替换或变异成不同的测试向量，以执行请求。  
  
测试向量生成  
  
在这个模块中，模糊测试工具为请求中的每个参数分配一个值，并构造一个完整的请求，该请求准备在序列模板中发送。如图1b所示，请求模板`GET /console/{id}`包含两个参数，{id}和cmd，需要设置这些参数。为了生成一个可用的请求，有两种方法可以获取参数值：1）从预定义的漏洞测试字典中选择一个替代值（例如，SecList）；或2）从先前请求的响应中读取目标对象。对于参数`id`，模糊测试工具将从另一个API的响应中读取一个目标对象值，该API在创建后提供有效的`id`对象。生成的测试请求如图1c所示，其中为参数`cmd`设置了一个命令注入漏洞载荷`cat /etc/passwd`。  
  
漏洞验证  
  
测试请求生成完成后，模糊测试工具将请求发送到目标API，并检查其响应以确定是否存在漏洞。例如，如图1d所示，API的响应包含来自/etc/passwd文件的内容（一个Linux系统文件路径），这表明命令cat /etc/passwd已成功执行，提示存在命令注入漏洞。  
  
通过利用上述主要模块，现有的API模糊测试工具能够自动生成请求，以通过其API测试不同的服务。然而，它们在参数解析和请求生成阶段仍然存在局限性，导致状态探索进展缓慢，这也是本文的主要研究重点。  
  
**三、API漏洞模糊测试的挑战**  
  
**3.1  API参数结构解析**  
  
Fuzzer 首先需要理解 API 的参数结构，才能对不同的 API 参数进行变异测试。参数解析的过程包括两个问题：  
  
通用性：现有的研究仅适用于 RESTful API，无法解决第 2.1 节中提到的其他场景，包括 Web 应用中的 SOAP 和 GraphQL API、云应用中的 gRPC，以及物联网系统中的 MQTT 等 API 类型。不同风格和协议的 API 参数结构具有相似性（图 2），这使得论文能够抽象出一种统一的表达方法，从而使 RESTful API 的模糊测试技术能够广泛应用于更多场景。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlquqbicbhhElFo6lAnv2VXntvaRPR0Urib2WVc2CZxhTA3LnGA5GicmenB9ias9dyCibuFGnfnP3Wb4O5Q/640?wx_fmt=png&from=appmsg "")  
  
**图 2  不同API协议下，包含两个参数'id=12345'和'cmd=getStatus'的查询API请求信息示例**  
  
参数编码：另一个挑战是  
识别 API 中复杂的编码结构和参数关系。这确保了测试向量能够准确地针对特定参数，而不干扰其他参数的功能。例如，常见的 API 将参数封装在 HTTP 请求体中，使用 JSON、XML 等格式，以及包含嵌套编码的数组类型对象作为参数值。如列表1所示，pfile 参数的值采用 base64 编码，而 info 参数包含 XML 结构化数据。如果没有正确的编码识别和参数解析，盲目修改消息内容进行模糊测试会导致 API 响应中的格式错误，从而妨碍漏洞的发现。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlquqbicbhhElFo6lAnv2VXntjeGskapjiafKTtSQicSVibS9Fj9Tv0oTMKcSukOWJ6q9rGUjQdicxK3icoA/640?wx_fmt=png&from=appmsg "")  
  
**列表 1  请求参数中的编码**  
  
**3.2  API参数结构解析**  
  
在同一应用程序中  
按合理顺序测试API  
非常关键。API参数往往彼此依赖，一个API的响应数据中的值字符串可能是另一个API中有效的请求参数值。如果直接注入数据而不考虑这些依赖关系，可能导致没有意义的结果，并生成大量无效的测试请求，从而影响模糊测试的效率。此外，在一些大型应用中，为了在有限的时间内完成测试，必须计算这些API的优先级，以提高测试过程的效率。  
  
**3.3  优先级测试路径选择**  
  
API安全测试通常面临大量的API及其相关的API调用依赖路径。这通常需要在单个API或特定API调用路径上进行大量有效负载注入尝试，导致安全测试结果需要较长时间才能收敛。在会话生命周期有限的情况下，这一问题尤为突出，可能在会话过期前只能完成有限数量的路径测试。通过评估测试优先级，论文可以在给定时间内优先测试那些具有更高漏洞概率的API和API调用路径。  
  
**3.4  API参数间的相互依赖性**  
  
API参数模糊测试是检测API漏洞的关键方法，因为API参数中的任何位置都可能触发漏洞  
。通常，模糊测试工具在每次API请求中只更改一个参数，这会导致大量的测试请求，从而降低了模糊测试的效率。如果论文能够识别参数之间的相互依赖关系，就可以在一次请求中同时测试多个参数，从而提高模糊测试的效率。列表2显示了一个论坛发帖的API请求。提交时，系统会检查给定的分类值是否已存在，如果未找到则返回错误消息。在单次请求中同时测试category和title参数的模糊测试工具会发现，title的测试向量无效。因此，它们需要两个单独的请求来验证这两个参数。然而，由于title和authorName是独立的，模糊测试工具可以在一个请求中同时对这两个参数进行变异。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlquqbicbhhElFo6lAnv2VXntOrT5P41nP4K0dyGXas2qwvLZeo0FicY0NppR5A268QERYPxP4cICMXg/640?wx_fmt=png&from=appmsg "")  
  
**列表 2  API参数之间的相互依赖性**  
  
**四****、概述**  
  
论文的设计目标是创建一个实用的API漏洞模糊测试框架，具有  
更强的通用性、有效性和效率  
。该框架能够广泛适用于各种API类型，解决复杂参数编码、顺序约束和参数约束等挑战，确保测试向量的有效注入。此外，它能够根据漏洞发生的可能性优先选择测试目标，并同时在单个请求中变异多个参数，最小化计算和网络I/O资源的消耗，从而在大规模批量API模糊测试的实际场景中提供高效性。  
  
基于这些设计目标，论文提出了APIF，一个全面的黑盒API漏洞模糊测试框架。它通过三种方式增强了模糊测试过程。首先，它解码编码的API参数值，并将其解析为统一的基于树的结构。其次，它计算漏洞的发生概率，并识别API之间的依赖关系，以创建合理的测试顺序。第三，它检查API参数之间的相互关系，以便在单个请求中同时注入多个测试向量。这些改进来自现有API模糊测试工作的不足。整个过程的结构如图3所示。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlquqbicbhhElFo6lAnv2VXntico6zM9ahCELutwNLo444guaft8XbyVkshzAoTWTAXVW1VvUOb9QU2A/640?wx_fmt=png&from=appmsg "")  
  
**图 3 APIF流程概述图**  
  
  
  
**五、具体实现**  
  
**5.1  API获取**  
  
该过程首先在客户端部署一个知名的代理服务器MitmProxy，充当中间人，拦截API通信数据。拦截的消息提供了API结构和参数的相关信息，为在APIF框架内进行进一步分析和测试奠定基础。  
  
与通过OAS文件分析API参数相比，从真实的API通信流量中解析API参数结构有两个主要优点：  
  
- 通过OAS获取API参数结构的可行性取决于API类型和API声明文件的维护。在实际场景中，并非所有API都有可访问的声明文件。然而，所有协议的API交互都可以通过流量捕获获得。  
  
- 通过分析API流量，论文不仅可以观察到API的参数结构，还可以获取有效的参数值。这有助于解决不同API之间的上下文依赖性问题，从而促进合理测试顺序的确定，并增强测试覆盖率。  
  
  
  
**5.2  API参数解析**  
  
论文提出的API参数解析算法解决了以下两个问题：1) 不同类型的API具有不同的协议和参数格式。为了使模糊测试器更具通用性，论文需要一个统一的数据结构来表示API参数。2)如前所述，API参数值的解码工作影响后续测试向量生成和参数变异阶段的实施，这对于API漏洞模糊测试的有效性至关重要。  
  
论文实现了用于从多种协议的API通信中提取参数内容的解析器。首先，论文通过协议特征匹配确定API请求消息的协议类型。论文开发了一个基于特征识别的协议类型检测模块，用于识别常见的API通信协议。例如，RESTful API可以通过URL模式、版本参数和ACCEPT头等特征有效识别。GraphQL API可以通过其数据结构和特定操作字段，如“query”、“mutation”或“subscription”，来区分。SOAP API则可以通过XML数据格式以及诸如Envelope、Header、Body和Fault等独特节点来识别。  
  
随后，对于各种API协议，论文采用相应的解析库来捕获参数及其值。这个过程包括递归解码，将API参数和值组织成统一的树形结构，如算法1所示。  
  
递归解码器将在检测到结构化对象（例如JSON、XML、数组类型数据等）时，尝试解码被编码的参数。递归解码器将拦截的API请求参数中的编码API参数值（如列表1所示）转化为树形结构（如图4所示）。该参数解析算法能够有效地将所有键值对参数转换为一个综合的树形结构。这有助于更深入地分析和理解API的编码和参数结构，对于后续的漏洞模糊测试至关重要。与其他工具相比，最大的创新在于测试有效载荷的注入将在树形结构的每个节点上进行。这将模糊测试的粒度从参数级别提升到结构化对象的每个节点，从而使论文能够进行更深入的模糊测试，显著提高发现之前难以检测到的安全漏洞的可能性。此外，它在不同API通信协议之间具有一定的通用性，相比于以前的研究（其中为每个目标API生成变异模板，见图1b），具有更广泛的适用性。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlquqbicbhhElFo6lAnv2VXntrT8x9ibEU9LUBJk5RiaicqRGW5UVfMyEb53nsvibOrZ8sPTTNTXUrJgv9Q/640?wx_fmt=png&from=appmsg "")  
  
**算法 1 API参数解析过程**  
  
**5.3  测试优先级计算**  
  
APIF通过利用API请求元素来计算API中漏洞的概率。该计算用于对API进行优先级排序，以便在设定的时间范围内最大化漏洞的发现，从而提高测试效率。在这个领域，模糊测试的常见优先级计算方法在应用于API时遇到了一些显著问题，例如：1) 导致API漏洞的因素与导致错误的因素不同；2)黑盒测试使得获取详细的测试覆盖率指标（例如代码或函数级别的执行覆盖率）变得困难。借鉴API相关漏洞挖掘的经验以及公开漏洞数据集的验证，论文确定了三个用于评估API漏洞可能性的指标：  
- 用户可以输入的参数越多，漏洞的概率越大。这是因为大部分API漏洞是由于对用户输入的处理不当所导致的。  
  
- API中参数类型越复杂，发现漏洞的可能性越高。复杂的参数类型意味着API中涉及多种数据类型的查询和功能。数据类型的复杂性增加了安全漏洞的可能性。  
  
- API支持的请求方法越多，发现漏洞的概率越高。例如，支持GET、POST、UPDATE和DELETE等访问路径的API通常涉及更复杂的操作功能和代码逻辑，容易导致风险实体操作和权限问题。  
  
APIF通过一个快速风险评估算法定义API测试优先级，该算法使用三个指标。指标得分越高，表示API的功能越复杂，漏洞发生的概率也越高。  
- 参数覆盖率。这是通过将单个API中的参数数量除以测试范围内所有API的总参数数量来计算的。  
  
- 参数值覆盖率。考虑到参数类型的多样性（例如，int、float、str、null、bool），该比率通过将单个API中的参数值类型数量除以测试范围内所有API中的参数值类型总数来计算。  
  
- 操作方法覆盖率。对于具有GET、POST、PUT和DELETE等操作方法的API，论文通过将单个API中的操作类型数量除以测试范围内所有API中的操作类型总数来计算该比率。  
  
为了中和计算指标之间规模和分布差异的影响，论文采用Z-score方法进行数据标准化。该方法基于原始数据集的均值μ和标准差σ对数据进行标准化，旨在将不同量级的数据统一到相同的尺度上。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlquqbicbhhElFo6lAnv2VXnt3MpIjpghUAf5VSUcXzIxcdfC5d8aYtN0UgicUfeFpXRVysvscNnByQA/640?wx_fmt=png&from=appmsg "")  
  
Z-score的转换函数如上式所示，其中x表示计算标准的每个观察值。例如，如果操作方法覆盖率在测试API中的结果为x1, x2, x3, …, xn，则在应用Z-score公式后，操作方法的标准化序列变为y1, y2, y3, …, yn，且每个值的均值为0，方差为1。  
  
对这些变量进行线性回归：漏洞概率hɵ (x)，操作方法覆盖率x1，参数覆盖率x2，以及参数值覆盖率x3。论文分析了2022年2月到2023年6月期间在开源系统中报告的206个API漏洞，作为论文的数据集。论文计算了这三个覆盖率及其相关的漏洞概率，以确定它们的权重。结果如下式所示。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlquqbicbhhElFo6lAnv2VXntHVXS5Wj71TgVlRM13WKdPSPVf5hlqGVCs5P3DoibrbXCTEPLicHpETZg/640?wx_fmt=png&from=appmsg "")  
  
**5.4  测试向量生成**  
  
测试向量生成。在计算了漏洞概率并确认了要测试的API的优先级后，APIF将使用约束求解方法生成具有适当顺序的测试向量，以适应上下文依赖关系。随后，APIF将进行参数独立性分析，并尝试在一次测试中变异多个参数，以减少总的测试数量并提高整体测试效率。确认了并行测试策略后，APIF将从预定义的模糊测试库中获取有效载荷，并基于先前生成的统一树结构进行变异。最后，APIF将根据参数的编码类型重新编码有效载荷，并发送测试请求。  
  
约束求解  
  
有必要按照适当的顺序依次测试不同的API。例如，在一个电子商务支付系统中，在创建了产品购买订单之后，才能进行支付。因此，论文不能直接对支付接口进行测试，而是必须先创建订单。在APIF中，论文设计了一种算法，根据API通信流量计算一组请求序列（算法2）。  
  
该算法最初包含一个空序列，并且如果序列中的每个请求返回有效的响应代码（定义为200范围内的任何代码），则认为该序列有效。算法从n = 1开始，迭代地计算逐步增加长度的请求序列。对于每一组有效的长度为n − 1的序列，它通过将满足依赖关系的请求添加到每个序列的末尾来创建新的长度为n的序列。函数`render`检查指定请求的所有依赖是否得到满足。如果序列中的每个动态对象（作为请求参数使用）都由序列中的先前响应生成，则该序列有效。如果所有关系得到满足，则保留长度为𝑛的新序列，否则丢弃它们。如果作为后续请求参数使用的动态对象在该请求之后被销毁，算法通过尝试重用该对象时收到无效的状态码（超出200范围）来检测到这一点，并丢弃该请求序列。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlo22t2Khhsa8KaT22e1JzhPxJJxvzq8XLicZTNUBxAb0L06DZF6Gf3fZW7k1icSj0NPicCSfZ0BUzVFQ/640?wx_fmt=png&from=appmsg "")  
  
**算法 2 API请求约束求解**  
  
参数独立性分析  
  
当前的API模糊测试方法通常一次只变异一个参数，以确保全面的测试，这导致了大量的测试。为了解决这一低效问题，论文开发了一种参数独立性算法。该算法分析了参数之间的相关性，识别了API的独立参数。在黑盒模糊测试中，这使得可以在每个请求中同时变异多个不相关的参数，从而显著减少测试数量并提高漏洞发现效率。  
  
对于一个具有n个可选参数的API（如下公式所示），假设每个参数有P1、P2、...、Pn个有效负载和Q个无效负载，则需要进行总共S次测试。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlo22t2Khhsa8KaT22e1JzhP5UZqb7EaibBFrV4B12AHX0dk7LxS6VZ5HsJ1DEZUAjRibpsEwmcrFa1Q/640?wx_fmt=png&from=appmsg "")  
  
通常，漏洞（或缺陷）是由单个输入或一对输入触发的，三种或更多因素组合引发的漏洞较为罕见。因此，将测试用例减少到触发漏洞所需的最小有效输入变化是至关重要的。如果每个测试用例不仅改变API中的一个参数，则在下公式中将生成R个测试用例，从而大大减少了测试用例的数量。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlo22t2Khhsa8KaT22e1JzhPagb3COxicVbmOwEyseZPkmYDupSkHCrF1AKa8KBhBWCzPWSuAfseUWA/640?wx_fmt=png&from=appmsg "")  
  
基于此，如果改变参数n1、n2、...、nk会导致响应结构与原始结构相同，而单独改变ni会导致不同的响应，则后续测试可以同时嵌入n1、n2、...、nk的负载，从而进一步提高测试效率。该算法在伪代码中描述，如算法3所示。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlo22t2Khhsa8KaT22e1JzhPJYv95PZGy0Hnrw2cOVVbP60ThqpAcKnInQxgo4aY5lehLqVYqHnEIg/640?wx_fmt=png&from=appmsg "")  
  
**算法 3 API参数独立性分析**  
  
例如，一个具有三个不同参数A、B和C的API，分别具有3、4和5个有效负载，通常需要60次（3 × 4 × 5）测试以进行全面测试。此外，还需要使用无效负载进行测试，比如将字符串用作int类型的参数。考虑到API通常以JSON格式传输数据，且具有基本类型，如int、float、str、null和bool，这会增加15次（3 × 5）用于无效格式的测试。然而，如果单独更改参数A和B的结果与原始响应结构相同，而更改C则产生不同的响应，那么在随后的测试中，A和B的负载可以同时嵌入，从而将总测试次数减少到26次（3+3+5+5×3）。这显著降低了所需的测试数量。  
  
在上述过程中，参数A和参数B的独立性通过双向验证进行分析和确保。在第一轮中，算法首先对参数A进行变异以获得响应resp，然后在已变异的参数A基础上继续变异参数B，得到响应resp1。在第二轮中，算法首先对参数B进行变异以获得响应resp，然后在已变异的参数B基础上继续变异参数A，得到响应resp1。只有当两轮中的resp和resp1的结构完全匹配时，论文才将参数A和参数B标记为独立参数，并在后续步骤中进行同时测试。  
  
参数树变异  
  
在初步步骤之后，API测试序列中的参数被标记为可模糊的原始值。根据用户配置的漏洞字典，测试向量被插入到这些原始值中，替换它们的原始值。对于在分析阶段被识别为“独立”的API参数，多个测试向量会在单个测试请求中同时嵌入。  
  
APIF 引入了四种基本的变异策略，以增强API漏洞模糊测试，如图5所示。首先，它允许对特定参数节点的名称或值进行变异。例如，可以将有效负载专门注入到 `uid` 参数中（图5a）。其次，框架支持遍历并变异所有符合特定过滤条件的节点。例如，应用命令注入漏洞测试向量到所有字符串数据类型的节点（图5b）。第三，APIF 允许向请求参数中添加新节点，例如插入名为 `admin` 且值为 `true` 的节点，有助于绕过权限检查（图5c）。最后，APIF 还支持删除节点；例如，删除与身份验证相关的参数可能会暴露由于验证策略不充分而导致的身份验证漏洞（图5d）。这些变异方法能够识别各种类型的API漏洞，并且能够适应不同的API格式，如RESTful、GraphQL、SOAP和gRPC，展示了很高的通用性。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlo22t2Khhsa8KaT22e1JzhPCcX5iadqibp8Xk4iaBAofzX2uiccJvROA8ullYHibLpqcXE9Ad7aSMQMsoA/640?wx_fmt=png&from=appmsg "")  
  
**图 5 APIF使用的参数树变异方法**  
  
**5.5  漏洞验证**  
  
漏洞验证。每个测试向量对应一个特定的验证方法，用于确定当前API中是否存在安全漏洞，并识别漏洞类型。论文将这些方法总结为三种类型：  
  
1) 响应消息中的内容匹配。例如，在使用模糊测试向量检查跨站脚本（XSS）漏洞时，论文验证API响应内容是否包含特定字符串，如JavaScript有效载荷或注入的DOM元素。类似的方法也适用于数据暴露、文件上传、命令执行等多种漏洞类型。  
  
2) 基于响应状态码的验证。在API序列的约束求解阶段，通常有效请求会返回200状态码。此模型对于检测具有不同状态码的漏洞非常有效。例如，如果对拒绝服务（DoS）攻击向量的响应返回503或504状态码，则确认API中存在此类漏洞。  
  
3) 基于响应时间的验证。一个典型例子是识别SQL时间盲注漏洞。在这种情况下，如果攻击向量包含SQL的sleep函数，论文将监控向量嵌入前后响应时间的变化。  
  
基于以上三种验证方法，论文列出了13种常见的API漏洞类型，包括：数据暴露、命令注入、对象级别权限控制漏洞、文件读取漏洞、权限控制漏洞、服务器端请求伪造（SSRF）、SQL注入、安全配置错误、拒绝服务（DoS）、错误处理不当、跨站脚本（XSS）、未实现内容安全策略（CSP）以及未验证的重定向。  
  
****  
**六、实验设计及结果**  
  
****  
**6.1  实验设计**  
  
数据集  
为了验证论文的研究，论文选择了4个在API模糊测试方法中广泛使用的API漏洞沙箱和3个真实世界的API项目作为模糊测试目标。该数据集不仅涵盖了API漏洞的全面性，还提供了在真实环境中的实用性。API漏洞沙箱包括：  
  
1) crAPI：一个旨在帮助测试人员了解关键API安全风险的项目，设计上容易被攻击，为API模糊测试工具提供了一个实际的测试平台。  
  
2) vAPI：另一个API漏洞平台，模拟了OWASP API安全Top10。  
  
3) APISandbox：提供更广泛的API攻击场景，包括4A认证系统下的问题、基于GraphQL的论坛、经典API漏洞、WSDL泄漏和未经授权的服务器访问。  
  
4) VAmPI：一个由Flask创建的漏洞API集合，包含来自OWASP API安全Top10的漏洞，旨在评估工具在检测API安全问题方面的效率。  
  
对于这些API漏洞沙箱，论文从项目文档中获取了漏洞API和正常API，分别作为正负样本的标签。为了衡量APIF在真实世界API应用中的表现，论文测试了三个开源项目：Spree 、GitLab-CE和SilverStripe，这些项目在真实商业环境中广泛使用。论文从这三个项目过去三年的官方安全更新中获取了漏洞，作为数据集中的正样本。最终的数据集涵盖了7个项目，共有412个API和112个安全漏洞。这些漏洞的类型也已按表1所示进行分类。  
  
模糊测试工具  
  
为了验证论文的研究，论文将APIF与三种最先进的API模糊测试工具进行了比较：  
  
1) RESTler：第一个有状态的RESTful API模糊测试工具，旨在通过REST API自动测试服务中的错误。后来，研究人员改进了该工具用于检测安全漏洞，它被认为是API漏洞模糊测试领域的代表性研究成果。  
  
2) Fuzzapi：GitHub上最受欢迎的API漏洞模糊测试工具，允许安全专家通过进行各种攻击载荷的模糊测试来发现API中的漏洞，并广泛应用于实际的漏洞测试场景。  
  
3) OpenAPI-Fuzzer：另一个在业界广泛使用的开源API漏洞模糊测试工具，已经发现了多个公共系统（如Kubernetes、Vault和Gitea）中的API漏洞。  
  
4) APIF-A：基于该APIF框架的完整技术实现，使用Golang开发。它包括API参数树结构解析、漏洞概率计算以及基于参数相互依赖分析的并发测试。  
  
5) APIF-B：论文提出的理论框架的部分实现。与APIF-A不同，它不进行漏洞概率计算和独立性分析。每个请求仅进行单次突变。  
  
测试向量库  
API模糊测试工具的有效性不仅取决于框架，还取决于精心制作的测试向量库。为了避免专家经验带来的偏差，论文使用了广泛认可的安全漏洞测试库SecLists，该库包含不同类型的漏洞测试载荷，作为论文的测试向量库。通过在各个工具中标准化使用该向量库，论文可以更准确地比较不同工具在框架和算法设计方面的优缺点。上述所有工具都配置为仅使用SecLists中的向量进行自动化测试，无需人工干预。  
  
实验指标  
  
论文的实验是在一台运行Ubuntu 20.04操作系统的计算机上进行的，该计算机配备了Intel I7处理器和16GB的内存。论文使用RESTler、Fuzzapi、OpenAPI-Fuzzer、APIF-A和APIF-B进行了测试。论文记录了以下指标：总测试时间、达到50%和90% API覆盖率的时间、网络指标以及漏洞输出指标：  
(1) 报告的漏洞（TP+FP）：指每个模糊测试工具自动计算和报告的漏洞结果。一条漏洞信息包含三个关键元素：1）漏洞类型，2）漏洞所在的API端点，3）触发漏洞参数位置。  
  
(2) 验证的漏洞（TP）：指通过人工验证模糊测试工具所产生的漏洞（上述三个元素）是否与数据集中的记录完全一致，若一致，则标记该漏洞为“已验证”。  
  
由于RESTler、Fuzzapi和OpenAPI-Fuzzer需要从OpenAPI规范（OAS）文件中解析API参数结构，论文统一为412个目标API生成了OAS文件。此外，论文使用Postman（一种能够向API发送请求并接收响应的API调试工具）来触发每个API的访问行为，这使得APIF-A和APIF-B的MITM模块能够捕获API通信流量，从而推导出API参数的结构。此外，目标程序和测试工具都配置了有效的身份验证会话。这些设置确保所有模糊测试工具都适用于所有目标API，消除了由于无法获取API参数结构（例如缺少OAS文件或缺乏API访问流量）以及缺失身份验证机制而对测试有效性产生的影响。  
  
**6.2  结论**  
  
论文对数据集中的所有目标API进行了漏洞测试。图6a展示了每个工具报告的漏洞数量。通过与数据集中的结果进行比较，图6b显示了实际的API漏洞数量。每个工具识别的详细漏洞列在表1中。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlo22t2Khhsa8KaT22e1JzhPtmSdlhaN6ZLAA7y9WJDkticjHQGw4633h8Aafor0v4qYp7FGiaUYib6Xw/640?wx_fmt=png&from=appmsg "")  
  
**图 6 每个模糊测试工具发现的漏洞数量**  
  
每个工具的详细指标，包括总测试时间、达到50%和90% API覆盖率的时间、网络I/O次数、网络流量和漏洞数量，如表2所示。论文从多个角度比较了不同工具的实验结果：有效性、效率和通用性。论文还进行了消融测试，并评估了在实际场景中漏洞检测的有效性。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlo22t2Khhsa8KaT22e1JzhPlWw22xq3sdIyGLTiaKCKfx9vcvYaLr73UxtnDSLIUcP4MsWp1eLZg9Q/640?wx_fmt=png&from=appmsg "")  
  
**表 1 对于每一个模糊测试工具的真阳性结果**  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlo22t2Khhsa8KaT22e1JzhPwaSchztePJRYw7cjia0HkQwfR3OTiaUrQOayU2k1wJ2ibywSgxkscjXFg/640?wx_fmt=png&from=appmsg "")  
  
**表 2 指标和对比结果**  
  
实验一：有效性比较  
  
表2显示，APIF-A和APIF-B在漏洞检测的召回率和精确度方面优于其他工具。除了真实API通信通常包含更多信息外，许多参数只有经过递归解码和编码后才能有效测试。在使用一致的测试载荷库的情况下，这表明  
论文的API参数解码和树结构突变显著提升了漏洞测试的覆盖率，从而发现了更多潜在的问题。  
  
实验二：效率比较  
  
虽然APIF-A和APIF-B产生了相似的漏洞检测结果，但APIF-A节省了58.9%的测试时间，并显著减少了网络I/O请求和网络流量的消耗。这表明论文在  
测试向量生成阶段采用的API参数独立性分析算法有效地减少了测试次数并提升了整体测试效率  
。参数的并发测试导致APIF-A比APIF-B少识别了2个漏洞，表明该算法的准确性仍需进一步优化。  
  
此外，根据图6b中APIF-A的漏洞发现曲线，论文可以观察到，APIF-A在测试时间的前半部分报告了76.4%的漏洞检测结果。APIF-A数据曲线的下降斜率表明，测试优先级计算算法有效地优先考虑了高风险API。在实际的大规模应用测试中，普遍存在在有限的时间内发现尽可能多的安全漏洞的目标。这一要求为在大规模实际应用中部署APIF的可行性提供了有力的支持。  
  
实验三：可推广性比较  
  
论文观察到，SilverStripe项目包含四个GraphQL API漏洞：CVE-2023-44401、CVE-2023-40180、CVE-2023-28104和CVE-2021-28661。如前所述，现有的API漏洞研究已针对RESTful API进行了优化，但未考虑其他类型的API。因此，工具RESTler、Fuzzapi和OpenAPI-Fuzzer未能识别这四个漏洞。同时，APIF-A和APIF-B成功识别了其中的两个漏洞，CVE-2023-28104和CVE-2023-40180。触发这些漏洞需要在插入测试向量之前进一步解码GraphQL消息。论文的APIF框架的递归解码器和树结构变异完成了这一任务，表明  
APIF的理论方法在不同API协议中都有效，具有更强的可推广性  
。  
  
实验四：消融实验  
  
为了研究API参数独立性分析和优先级计算策略如何提升APIF的效率，论文对这两个主要组件进行了消融研究。论文实现了APIF的不同变体：1) APIF-A，启用了参数独立性分析和优先级计算，2) APIF-B，移除了参数独立性分析和优先级计算，3) APIFWith-Priority，移除了API参数独立性分析的实现，4) APIF-With-Independence，移除了优先级计算的实现。结果如图7所示。如同之前的研究，测试有效载荷集使用了Seclists，四个测试使用了相同的API通信数据。  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlo22t2Khhsa8KaT22e1JzhP1VLjHsia8zvWJA8WPUj6LWb06d2Fsw7V9tPbv58adYCutPpm7AN63VQ/640?wx_fmt=png&from=appmsg "")  
  
  
**图 7 每个模糊测试工具发现的漏洞数量**  
  
在图7a中，与未优化的APIF-B相比，APIF-WithPriority在相对较短的时间内能够发现更多的漏洞，并且不会影响漏洞检测的有效性，同时总体模糊测试持续时间几乎保持不变。这是因为参数优先级分析主要优化了测试顺序。在图7b中，APIF-WithIndependence的曲线显著缩短了整体模糊测试的持续时间，大大提高了效率。这个改进是由于在单个请求中并行插入多个有效负载，使得在给定时间内可以完成更多的测试用例。然而，由于在某些情况下对API参数独立性的判断不准确，检测到的漏洞数量略有下降。这表明  
参数独立性分析方法仍有进一步优化的空间。  
  
**七、局限及不足**  
  
**7.1  API通信流量分析**  
  
APIF采用被动流量分析来解析API的参数结构。然而，在上述实验过程中，其他工具解析了OpenAPI规范（OAS）文件。为了确保实验结果的有效性，论文为数据集中每个API生成了统一的OAS文件，确保对照组工具不会因为缺少API文档而未能发现漏洞。  
  
在API参数解析中，流量分析和OAS解析是互补的方法，各有优缺点。流量分析擅长捕捉广泛的API上下文，并适用于缺少OAS文件的API，适用各种API类型。其缺点是需要一个中间人服务来拦截API流量。OAS解析则因其简便性而脱颖而出，不需要流量拦截，并且非常适合RESTful API。然而，当OAS文档不可用时，其效果有限，必须手动生成OAS文档。  
  
**7.2  API认证**  
  
对于在线服务API，某些功能需要用户认证。例如，一个典型场景可能允许普通用户使用GET方法访问信息，但只有管理员才能使用PUT方法修改信息。为了提高测试覆盖率，API模糊测试器需要理解不同API的认证机制。  
  
在论文的实验中，论文为测试工具和被测应用配置了有效的认证会话，使得模糊测试工具能够访问需要授权的内容。在API漏洞模糊测试中，未能获得API认证信息会显著影响API测试覆盖率。因此，论文为APIF开发了一个认证模块，能够根据预定义的配置在测试请求中携带各种认证信息。用户可以通过配置文件向APIF提交其API访问凭证。一旦APIF识别到认证请求，它将自动携带这些凭证进行后续测试。然而，在实际场景中，并非所有目标应用都支持长期有效的认证会话。在这种情况下，测试工具只能使用它们获得的短期会话执行限时的安全测试。  
  
**7.3  参数优先级计算的普适性**  
  
在进行参数优先级计算之前，论文使用历史CVE漏洞作为数据集，并基于TCL模糊测试验证了相关指标。借鉴论文在API漏洞挖掘领域的经验以及黑盒API安全测试场景的实际特点，论文最终选择了安全测试场景中最具代表性的三个特征维度来计算优先级。通过实验，论文成功地证明了这一改进可以提高基于参数注入、参数修改和参数删除的API漏洞模糊测试效率，从而推动更多后续研究的开展。  
  
然而，API漏洞还包括许多其他类别，例如逻辑漏洞。由于这类漏洞通常需要更为复杂且高度案例化的测试方法，因此本文并未涉及这类漏洞的效率优化方法。在未来的工作中，论文将进一步优化针对不同类型漏洞的优先级引导方法。  
  
**八、总结**  
  
本文介绍了一个API漏洞模糊测试框架。论文创新性地采用了树状结构进行API参数的结构分析，有效解决了复杂编码问题，并实现了更深入的API漏洞发现，同时提升了框架的泛化能力，以应对实际批量测试场景中各种类型的API。随后，论文通过计算单个API中漏洞的可能性来进行优先级排序，并分析每个API中的参数独立性，从而优化了API漏洞测试效率。这使得论文能够  
在单个请求中嵌入多个测试向量，从而显著减少了测试数量，提高了测试效率。  
  
论文的实验结果验证了框架的有效性，显示出其在效率和发现更多漏洞的能力方面，相较于现有的API测试技术具有明显优势。论文将该框架应用于实际漏洞模糊测试，发现了188个BUG和26个漏洞，其中包括6个CVE和12个CNVD，涵盖60个开源API项目。总体而言，论文的方法可以作为改进API漏洞模糊测试技术的一个实际方向。  
  
未来的工作将重点通过引入与漏洞相关的其他因素来完善漏洞可能性评估，并探索这些因素之间的相互关系，以优化论文的评估方法。此外，论文将进一步改进参数独立性分析，以实现更精确和有效的结果。这些改进将进一步提升黑盒API模糊测试的效率。  
  
**—END—**  
  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlrFxo5eqwR0gsfAItibNmfykKRSz1SvNIKndIPoSB9dQk8u1iaH2IcWlV4vR3Ov4uXgMibO6uPGRA2dQ/640?wx_fmt=png "")  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlqicsiaxDHZjSsKx6Eoahhic8tm1AUvF5TI33T7kuQmpqnP5HoOUicFhuIhrcXcyaZJzHJrYaLibPCZSRQ/640?wx_fmt=png "")  
  
[SELECTFUZZ:采用选择性路径探索的高效定向模糊测试](https://mp.weixin.qq.com/s?__biz=MzU1NTEzODc3MQ==&mid=2247487127&idx=1&sn=7bded765fbc0019e4e001fefee6b7a04&scene=21#wechat_redirect)  
  
  
[Towards Generic DBMS Fuzzing：面向通用数据库的模糊测试](https://mp.weixin.qq.com/s?__biz=MzU1NTEzODc3MQ==&mid=2247487110&idx=1&sn=c01835f0d73bacfec6660f8fad0a5975&scene=21#wechat_redirect)  
  
  
[mGPTFuzz：大型语言模型辅助Matter物联网设备模糊测试](https://mp.weixin.qq.com/s?__biz=MzU1NTEzODc3MQ==&mid=2247487094&idx=1&sn=8043fce594033c46aab557a313eee70c&scene=21#wechat_redirect)  
  
  
![](https://mmbiz.qpic.cn/mmbiz_png/JchE46RGRlrFxo5eqwR0gsfAItibNmfyk5wLcpKFBfhV2gLHUvrA15ticyqNAUM2Nvak36LBpQmxVQdliabzKmaSg/640?wx_fmt=png "")  
  
  
  
