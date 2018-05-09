gitHooks版本更新功能提示:

1.8.0:关键字符串简单加密
    a)更改部分阀值
    b)失败时的邮件添加上版本号

1.7.0:关键字符串简单加密
    a)检查失败不再抛异常阻断提交
    b)降低检查更新的频率,仅在10-17点之间检查
    c)每天检查更新失败超过2次,当天不再检查更新
    d)关键字符串进行简单加密
    
1.6.0:优化功能
    a)检查失败不再抛异常阻断提交
    b)降低检查更新的频率,仅在10-20点之间检查
    c)每天检查更新失败超过3次,当天不再检查更新
    d)更新了xcode模板

1.5.4:修复bug和优化功能
    a)提交信息的title最大改为80字
    b)修复了邮件发送失败的问题
    c)填充jira失败时,不抛出异常,同时发邮件通知去手动填充

1.5.3:修复bug和优化功能
    a)修复了邮件发送失败的问题
    b)更新成功后不再阻断提交,无感更新
    
1.5.2:修复bug和优化功能
    a)格式化代码时,只格式化新增和被修改的文件类型的文件
    b)xcode模板几乎为所有文件新增了mark标注,需要再更新一下
    c)提交reviewboard的时候,支持指定对比的parent分支(或者比较指定的提交也是一样的写法),要加中括号包起来格式例如要指定为develop,可写提交信息为: re-[develop]feat(JIRA-ID):xxxxx

1.5.1:越来越好用了:
    a)增加了强制更新的脚本的方式,项目下执行python .git/hooks/upgrade.py
    b)改进了初始化配置的方式,在拉取的脚本代码目录下执行python setup.py
    c)通过发邮件来统计了下使用的习惯
    d)初始化或强制更新命令后加-d可抹掉本仓库githooks配置;  加-a可抹掉全局githooks配置; 加-v=xxx可升级至指定版本; 加-v可输出版本; 加--help可查看帮助
    e)如果你填写jiraID时不小心写在了冒号的后边,会智能匹配帮助你应该怎么填写正确的

1.5.0:更新了初始化配置的方式;
         提交信息改为拼接ios项目版本号(暂未开启),等功能

1.4.8:修改了xcode模板里life cycle的拼写错误问题

1.4.7:修复了首次使用脚本无法更新的问题,原因是未找到本地的版本记录导致

1.4.6: 1)配置xcode模板已经开启生效,需要根据引导提示执行命令去实现。2)邮件服务器和邮箱使用邮箱发送通知邮件。3)紧急修复了当使用自动review功能时,因为mac SIP权限未禁用时导致无法向/user/rbt/里写入文件而创建软链接时的解决方案,可根据对应提示进行操作

1.4.5:配置xcode模板。

1.4.4:修复编译报错。检查更新时的请求添加请求头。

1.4.3:重写了自动更新模块,并修复了一些小问题。处理了一些异常的情况, 比如更新代码失败时, 满足特定条件则不抛出异常, 另外增加了失败的报警邮件。增加了很多更友好的打印

1.4.2:修复自动发送reviewRequest只能在命令行使用,不能在sourcetree中使用的问题

1.4.1:修复bug:首次更新未使用过reviewRequest功能而导致的崩溃问题

1.4.0:本版有两个内容更新:1)自动帮你发布reviewRequest,方法是:在提交信息前加关键字,例如review_test:test; 目前支持的关键字有"review_","rbt_", "re_", "review-","rbt-", "re-"。2)使用统一的xcode模板,会帮你自动设置统一的模板给xcode,但是还未上传模板过去,因此此功能暂未生效。

1.3.5:解决了上一版clang-format只能在命令行使用而不能在sourcetree中使用的问题

1.3.4:clang-format文件先试用一下,先只对.h文件格式化

1.3.3:修复了上一版的bug,将header前的类型如fix:去除掉了,看起来更像自己写的subject

1.3.2:如果没有填写subject,则将header自动填充为subject

1.3.1:对subject 字数超长的,给出提示超过了多少字

1.3.0:增加了自动代码格式化的功能,使用如下:
    1.此功能需确保每个人都安装了clang-format,安装方法:执行两个命令brew update & brew upgrade和brew install clang-format;其中第一个命令如果更新过就不用再更新了,安装成功的话:执行clang-format --help有输出
    2.在.git同级目录下增加自定义的.clang-format配置文件生效,不配置不生效;
    3.配置文件参考:
    http://www.cnblogs.com/PaulpauL/p/5929753.html
    http://clang.llvm.org/docs/ClangFormatStyleOptions.html
    
1.2.2:更改了下载代码的超时时长为30秒;更新成功,会有统计到我这里😁

1.2.1:所有功能增加控制开关,开启命令如下:
   1. commit message前自动拼上当前版本号,默认开启(git config githooks.premsg "YES")
   2. ios项目检查项目中图片相同的名字,默认开启(git config githooks.sameimg "YES") 
   3. commit message规范化提交,默认开启(git config githooks.checkmsg "YES")
   4. 自动将你的commit message填充到JIRA上注释上,默认开启(git config githooks.notejira "YES")
   5. 项目build版本号commit后自动加1,默认关闭(git config githooks.autoversion "YES")

1.2.0:增加了自动更新版本号的功能,此功能默认关闭,开启方法:cd到你的仓库,执行git config githooks.autoversion "YES"

1.1.9:重构了自建更新功能,将版本信息存储的位置改了,这样就更方便用命令删除版本信息,从而强制更新脚本

1.1.8:三哥,你要的功能来了,针对某个仓库定制是否需要添加当前分支到提交信息的前面,cd到你的仓库, 执行命令git config githooks.premsg "NO"即可关闭,配置其他任何内容则开启,这个命令在使用文档我也更新到了,看这儿https://github.com/spWang/gitHooks

1.1.7:当有提交信息为解决冲突时,不校验subject字数

1.1.6:修改了获取当前分支的方式,全路径为最后路径

1.1.5:修复了subject和body中存下小括号时导致issueID解析错误的问题

1.1.4:自建更新检测时长改为了24小时检查一次

1.1.3:解决了当提交代码因冲突导致检测commit-msg不通过的问题

1.1.2:增加了jira的功能,可以将commit-msg填充到jira上啦,前提是你必须填正确的jira号

1.1.1:自建更新功能fix:文件夹复制导致目录乱的修复

1.1.0:修复了因提交时未在某分支上造成的崩溃

1.0.9:在控制台输出的更新文案做了代码优化

1.0.8:在控制台输出了本次更新的内容,并且高亮显示,方便各位看官看到脚本更新了啥

1.0.7:可以在提交信息的type后可以加入issueID啦,header的格式为type(issueID):subject;当然也可以不加,header的格式依然为type:subject(注:关键字小括号()校验)
