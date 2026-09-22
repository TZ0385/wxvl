#  运维和信息安全同学注意： 内网AVCON系统管理平台SQL注入漏洞，可能正被一条 SQL 语句掀了底  
宝十八
                    宝十八  网络安全老宋   2026-09-21 04:00  
  
**导语：**  
 你好，我是网络安全老宋。  
安全攻防干货准时送达！  
  
网络安全  
老宋  
// 漏洞预警 · 安全运营  
  
// 漏洞预警 · 安全运营  
# 运维和信息安全同学注意：内网那台视频会议平台，可能正被一条 SQL 语句掀了底  
  
一份圈内流传的安全预警指向 AVCON6 管理平台 SQL 注入——管理面、未授权、厂商暂无补丁。  
  
目录 · Table of Contents  
  
00  
引言  
  
01  
这到底是个什么漏洞  
  
02  
为什么"内网"不等于安全  
  
03  
一条 roomid 能捅多大篓子  
  
04  
最扎心的现实：厂商还没给补丁  
  
05  
没有补丁，今天能做 6 件事  
  
06  
给开发者的根治方案  
  
07  
自查清单：两套动作  
  
## 00引言  
  
  
一份近期在圈内流传的安全预警，把矛头指向了华平股份的 AVCON6 系统管理平台：它的一个管理接口存在 SQL 注入，攻击者不用登录，只要往 roomid 参数里塞一段 SQL，就能把数据库里的敏感信息拖出来。  
  
看到"内网""管理平台"，不少人下意识觉得"黑客进不来，问题不大"。这次偏偏打在管理面，而且更麻烦的是——厂商到现在还没给出公开补丁。等补丁，等于把主动权交出去。今天我们把这个漏洞掰开讲，顺便给你一套"没有补丁时也能立刻上手"的应对打法。  
  
![](https://mmbiz.qpic.cn/sz_mmbiz_png/yJLbez93fl9RUTCWtCxcvFlGicSznEa962YQrsrsPgibFK25DZKj6paiaZsy9GO0VrQbrbkufvb3hFe2lPpQoYLhoUTFtHoKJJh8ONrgUxeictE/640?wx_fmt=png&from=appmsg "")  
  
## 01这到底是个什么漏洞  
  
  
先说清楚 AVCON 是什么。它是华平信息技术股份有限公司推出的一套视音频通信与图像综合管理平台，覆盖视频会议、视频监控、指挥调度、流媒体传输和综合运维，广泛部署在政企、教育、医疗等单位的内网，也经常开在互联网出口做远程接入。  
  
漏洞出在平台的一个接口上：/OrgLinkVote_queryGroup.action;login.jsp  
，具体是  
 roomid  
   
这个参数。问题很典型——后端在拼 SQL 的时候既没用参数化查询，也没做有效过滤，等于把 SQL 语法的解释权直接交给了用户提交的参数。攻击者可以不经认证直接访问这个接口，往 roomid 里注入恶意语句，最终读取数据库里的敏感内容。  
  
给不太写代码的同学补一句人话解释。数据库平时靠 SQL 这种"查询语言"去取数据，正常请求里 roomid 是个普通值，比如  
 roomid=1024  
，后端就去找 1024 号房间。可一旦后端偷懒，直接把用户输入和 SQL 拼成一长串再交给数据库执行，攻击者就可以把 roomid 写成  
 1024 OR 1=1  
   
甚至更长的恶意片段——数据库分不清哪部分是"数据"、哪部分是"命令"，于是老老实实把整张表甚至整个库都交了出来。这一步，就是 SQL 注入。  
  
一句话概括：管理面 + 未授权 + 可注入 = 一扇没锁的数据库后门。  
  
![视讯管理平台 SQL 注入攻击链配图](https://mmbiz.qpic.cn/mmbiz_png/yJLbez93fl9sWZBSW6cwufQLaX9fFG9DO4sWHQa6tkFu2OicTzjiatsuDP5hMMMEH3NT4aGksh94QiaVHqc46mKPuEvH3iavS0GXBopARcSxU3A/640?wx_fmt=png&from=appmsg "")  
  
## 02为什么"内网"不等于安全  
  
  
很多单位把 AVCON 这类平台开在互联网出口，理由是"方便远程运维和调度"。可一旦管理面暴露，攻击者从公网就能摸到接口，所谓的"内网"只剩一层薄薄的信任。  
  
更值得警惕的是，视讯、会议类平台的 SQL 注入不是孤例，是一条反复出现的攻击链：  
  
• 2026 年 7 月披露的神州视翰视频会议系统（CVE-2026-51821），同样是登录接口的 user_name 参数未过滤，未授权即可触发，特定配置下还能从 SQL 注入一路演进到任意代码执行；  
  
• 2013 年的绿盟视频会议系统注入，攻击者直接拿到管理账户密码，登录后台查看会议密码，进而控制远程会议；  
  
• Cisco Unified MeetingPlace（CVE-2010-0139）更夸张，未授权用户能发 SQL 命令操纵数据库，甚至创建管理员账号、提权；  
  
• 还有 TOPMeeting（CVE-2019-13409）等多款产品，都栽在"外部输入没做 SQL 校验"上。  
  
把镜头拉回 AVCON 自己，这也不是头一回。早在 2016 年，它就有过 name 参数 SQL 注入的记录（CNVD-2016-08325），当时厂商同样没有给出修补方案；公开的安全社区里还能翻到针对 AVCON 综合管理平台的任意文件读取记录。十年过去，同类问题换了个参数名又出现了。这说明它不是偶发笔误，而是产品底层对"外部输入"的处理习惯有欠账。  
  
🔑 视讯平台托着的是会议内容、人员信息和调度权限，它一旦被拖库，泄露的往往是一家单位最不想外传的那部分，而且这类平台集成度高、权限又集中，单点失守的代价比普通业务系统大得多。  
  
## 03一条 roomid 能捅多大篓子  
  
  
有人觉得"不就是读点数据"。我们顺着攻击链往下看。  
  
第一步，拖库。  
数据库里通常躺着管理员密码、用户名单、会议记录和配置信息。对政企、医院、学校来说，这些东西本身就是高敏感资产。  
  
第二步，升级。  
如果应用把 SQL 错误信息直接回显给前端，攻击者用 EXTRACTVALUE、CONCAT 这类报错函数就能一段段把库名、表名、字段名挤出来；有的接口甚至会回显数据库类型与版本，等于把地图递到对方面前。在部分配置下，还能借 INTO OUTFILE、UDF 等通道往服务器写文件、加载动态库，把"读数据"变成"控服务器"——神州视翰那个 CVE 就是这么从注入走向远程代码执行的。还有一种不回显的"时间盲注"，攻击者用 sleep() 这类延时函数判断注入是否生效，慢但同样致命。  
  
第三步，横向移动。  
数据库里往往还存着别的系统的凭据，攻击者拿到手就能当跳板，往内网更深处走。  
  
别以为 SQL 注入是"老黄历"。TalkTalk 在 2015 年因为一个没打补丁的旧数据库被一名少年用 SQL 注入拖走 15.7 万条客户记录，最终付出 7700 万英镑代价；2012 年 LinkedIn 上亿凭证泄露，SQL 注入也是其中一条攻击路径；2021 年 Twitch 源码与收入数据外泄，SQL 注入同样出现在访问链里。OWASP Top 10:2025 把 Injection 排在 A05，但按 CVE 数量算它仍是所有类别里最多的一档（9 万多条），而 Cobalt 的渗透实测数据显示 SQL 注入以 10.6% 的占比稳居真实漏洞榜首。纸面排名降了，实战威胁一点没减。  
  
## 04最扎心的现实：厂商还没给补丁  
  
  
回到这份预警本身，有一句话必须划重点：截至目前，华平方面没有发布针对该漏洞的公开安全公告或明确修复版本。  
  
这不是 AVCON 一家的问题。不少国内软硬件产品的漏洞响应节奏偏慢，从预警到补丁往往隔着数周甚至数月。如果你选择"等厂商发补丁再说"，等于把公司的数据库安全寄托在别人的排期上。  
  
正确姿势是：把"临时缓解 + 资产自查"当成现在就能开工的动作，而不是补丁到了才动手。下面这几招，不依赖厂商，今天就能动手。  
  
## 05没有补丁，今天能做 6 件事  
  
  
这几条把预警里的排查建议拆成了可操作项，运维侧立刻能用：  
<table><tbody><tr><td data-colwidth="52" style="vertical-align: top;padding: 16px 14px 16px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(137, 109, 67);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">R1</span></span></td><td style="vertical-align: top;padding: 16px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><b style="display: block;font-family: &#34;Songti SC&#34;, serif;font-size: 17px;color: rgb(26, 23, 20);margin-bottom: 4px;"><span leaf="">资产梳理，收敛暴露面</span></b><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">先盘清楚内网有哪些 AVCON6 管理平台、装的是什么版本、补丁打到哪了，重点盯互联网可访问、或与低信任网络互通的那几台，把管理访问限制在可信网络和必要运维终端里。</span></span></td></tr><tr><td data-colwidth="52" style="vertical-align: top;padding: 16px 14px 16px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(137, 109, 67);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">R2</span></span></td><td style="vertical-align: top;padding: 16px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><b style="display: block;font-family: &#34;Songti SC&#34;, serif;font-size: 17px;color: rgb(26, 23, 20);margin-bottom: 4px;"><span leaf="">给接口加鉴权，关掉匿名访问</span></b><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">那个出事的 OrgLinkVote_queryGroup 接口，先补上身份认证，取消不必要的匿名可达；后台管理面别直接对公网裸奔。</span></span></td></tr><tr><td data-colwidth="52" style="vertical-align: top;padding: 16px 14px 16px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(137, 109, 67);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">R3</span></span></td><td style="vertical-align: top;padding: 16px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><b style="display: block;font-family: &#34;Songti SC&#34;, serif;font-size: 17px;color: rgb(26, 23, 20);margin-bottom: 4px;"><span leaf="">数据库账号收最小权限</span></b><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">应用连库只用专用低权账号，拒绝 DROP、ALTER、CREATE、FILE、EXECUTE 这类高危权限，更别用 root 或 sa 跑业务查询。</span></span></td></tr><tr><td data-colwidth="52" style="vertical-align: top;padding: 16px 14px 16px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(137, 109, 67);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">R4</span></span></td><td style="vertical-align: top;padding: 16px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><b style="display: block;font-family: &#34;Songti SC&#34;, serif;font-size: 17px;color: rgb(26, 23, 20);margin-bottom: 4px;"><span leaf="">WAF 上规则拦一道</span></b><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">针对单引号、UNION、EXTRACTVALUE、INTO OUTFILE、SQL 注释符等注入特征做临时拦截。注意 WAF 是补充层，挡得住脚本小子，挡不住精心编码的绕过，不能当终结方案。</span></span></td></tr><tr><td data-colwidth="52" style="vertical-align: top;padding: 16px 14px 16px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(137, 109, 67);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">R5</span></span></td><td style="vertical-align: top;padding: 16px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><b style="display: block;font-family: &#34;Songti SC&#34;, serif;font-size: 17px;color: rgb(26, 23, 20);margin-bottom: 4px;"><span leaf="">日志审计盯异常</span></b><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">把 Web 访问日志、应用日志、数据库审计记录拉通看，重点抓那个接口和 roomid 参数里的异常 SQL 片段，以及数据库报错、短时间重复查询、异常批量读取、返回数据量突增这些情况。</span></span></td></tr><tr><td data-colwidth="52" style="vertical-align: top;padding: 16px 14px 16px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(137, 109, 67);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">R6</span></span></td><td style="vertical-align: top;padding: 16px 0px;"><b style="display: block;font-family: &#34;Songti SC&#34;, serif;font-size: 17px;color: rgb(26, 23, 20);margin-bottom: 4px;"><span leaf="">roomid 做白名单校验</span></b><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">按业务只接受期望的类型、长度、字符集，拒绝 SQL 注释、引号、逻辑运算、联合查询和报错函数；对请求先做解码，再用规则检测，避免编码绕过。</span></span></td></tr></tbody></table>  
💡 快速确认是否中招有个笨办法但管用：用资产探测工具搜一下  
 web.title="AVCON"  
   
或  
 body="AVCON-系统管理平台"  
   
的外网命中，再核对这些资产是否属于自己单位；凡是能从公网直接打开管理登录页的，都先按上面的清单处置一遍，不要等。  
  
## 06给开发者的根治方案：别再拼字符串  
  
  
预警讲的是"应急"，这里补一层"治本"。SQL 注入唯一的根本解，是让用户输入永远只当"数据"、不参与"语法"。  
  
参数化查询（预编译 / PreparedStatement）是底线。把 SQL 写成带占位符的模板，用户数据作为独立参数传进去，数据库就不会把它当成命令的一部分去解析。主流 ORM 框架（Hibernate、SQLAlchemy、MyBatis 等）默认就走参数化，但坑在"Raw Query"——一旦你图省事写  
 execute("SELECT * FROM x WHERE name=" + input)  
，ORM 的保护全白费。  
  
输入白名单是纵深防御，不是替代。期望整数就只允许数字，期望枚举列就只认硬编码的那几个值。最小权限数据库账号能压住爆炸半径：即便注入成功，攻击者最多读到几张业务表，动不了系统配置。统一错误处理要关掉回显，生产环境只给"系统繁忙"这种通用提示，把 SQL 报错和堆栈留在受控日志里——这正是为了防住 error-based 注入那种"靠报错挤 schema"的打法。还有容易被忽略的二级注入：从自己数据库里读出来的数据，再次进 SQL 时照样要参数化，别假设"库里的就是干净的"。  
  
   
   
   
⏺ 危险写法 vs 安全写法  
```
```  
  
  
## 07自查清单：两套动作，一条都不能少  
  
  
运维侧（应急，今天就能打勾）  
<table><tbody><tr><td data-colwidth="57" style="vertical-align: top;padding: 14px 14px 14px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(26, 110, 92);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">A1</span></span></td><td style="vertical-align: top;padding: 14px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">已盘点内网 AVCON6 管理平台的数量、版本与补丁状态</span></span></td></tr><tr><td data-colwidth="57" style="vertical-align: top;padding: 14px 14px 14px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(26, 110, 92);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">A2</span></span></td><td style="vertical-align: top;padding: 14px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">已确认出事接口及管理面未直接暴露公网</span></span></td></tr><tr><td data-colwidth="57" style="vertical-align: top;padding: 14px 14px 14px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(26, 110, 92);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">A3</span></span></td><td style="vertical-align: top;padding: 14px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">已为相关接口补齐身份认证，关闭匿名访问</span></span></td></tr><tr><td data-colwidth="57" style="vertical-align: top;padding: 14px 14px 14px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(26, 110, 92);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">A4</span></span></td><td style="vertical-align: top;padding: 14px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">数据库账号已降为专用低权，禁用高危权限</span></span></td></tr><tr><td data-colwidth="57" style="vertical-align: top;padding: 14px 14px 14px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(26, 110, 92);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">A5</span></span></td><td style="vertical-align: top;padding: 14px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">已在 WAF 配置 SQL 注入特征拦截规则</span></span></td></tr><tr><td data-colwidth="57" style="vertical-align: top;padding: 14px 14px 14px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(26, 110, 92);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">A6</span></span></td><td style="vertical-align: top;padding: 14px 0px;"><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">已建立 Web / 应用 / 数据库三方日志的异常告警</span></span></td></tr></tbody></table>  
开发侧（治本，纳入下次发版）  
<table><tbody><tr><td data-colwidth="57" style="vertical-align: top;padding: 14px 14px 14px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(137, 109, 67);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">B1</span></span></td><td style="vertical-align: top;padding: 14px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">全量 SQL 已改为参数化 / 预编译，无字符串拼接</span></span></td></tr><tr><td data-colwidth="57" style="vertical-align: top;padding: 14px 14px 14px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(137, 109, 67);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">B2</span></span></td><td style="vertical-align: top;padding: 14px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">ORM 的 Raw Query 已逐一排查并改造</span></span></td></tr><tr><td data-colwidth="57" style="vertical-align: top;padding: 14px 14px 14px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(137, 109, 67);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">B3</span></span></td><td style="vertical-align: top;padding: 14px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">关键输入已加类型 / 长度 / 字符集白名单</span></span></td></tr><tr><td data-colwidth="57" style="vertical-align: top;padding: 14px 14px 14px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(137, 109, 67);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">B4</span></span></td><td style="vertical-align: top;padding: 14px 0px;border-bottom-width: 1px;border-bottom-style: dashed;border-bottom-color: rgb(219, 210, 196);"><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">生产环境已关闭数据库错误回显</span></span></td></tr><tr><td data-colwidth="57" style="vertical-align: top;padding: 14px 14px 14px 0px;"><span style="display: inline-block;width: 40px;height: 40px;background-color: rgb(137, 109, 67);color: rgb(255, 255, 255);font-family: monospace;font-size: 13px;font-weight: 600;text-align: center;line-height: 40px;"><span leaf="">B5</span></span></td><td style="vertical-align: top;padding: 14px 0px;"><span style="font-size: 14.5px;color: rgb(94, 93, 93);line-height: 1.7;"><span leaf="">已把 SQL 注入测试纳入 SAST / DAST / 上线前渗透</span></span></td></tr></tbody></table>  
// 老宋说  
  
第一，漏洞从来不挑"内网"还是"公网"，它只挑"哪个参数没被当回事"。AVCON 这回的 roomid，和十年前那个 name，病灶是同一个。  
  
第二，没有补丁不是躺平的理由。资产梳理、接口鉴权、权限收缩、WAF 拦截、日志审计，这五件事今天就能干，而且干完立刻见效。  
  
第三，应急只能止血，参数化查询才是断根。别等下一次预警点到自己头上，才想起把 SQL 拼串改成预编译。  
  
你单位内网里有没有这类被开在互联网出口的管理平台？欢迎在评论区聊聊你们的收敛经验。也提醒一句：本文只做防护科普，文中涉及的漏洞细节请勿用于未授权测试。  
网络安全老宋 · 转载请注明出处  
  
防御，不是在演练期间发现攻击，而是在演练开始前就把攻击面收敛到最小。  
  
end  
  
  
  
不想错过文章内容？读完请点一下**“在看**  
**”**  
，加个**“****关注”**  
，您的支持  
是我创作的动力  
  
期待您的一键三连支持（点赞、在看、分享~）  
  
