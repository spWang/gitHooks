## gitHooks

#### 本脚本地址:https://github.com/spWang/gitHooks


### 功能
    1. 自动更新功能,一次配置,后续自动更新脚本代码,一劳永逸<br>
    2. 为xcode配置了相同的xcode模板<br>
    3. 自动格式化代码,功能使用见[changelog.md](https://github.com/spWang/gitHooks/blob/master/changelog.md)的1.3.0版本说明<br>
    4. ios项目检查项目中图片相同的名字<br>
    5. commitMsg规范化检查<br>
    6. commitMsg前自动拼上当前分支/版本号<br>
    7. ios项目build版本号commit后自动加1,默认关闭<br>
    8. 自动发布reviewRequest,需要在提交信息前加关键字("re-", "re_", "review-", "review_", "rbt-","rbt_"),如需指定比较的父分支(或者比较指定的提交也是一样的写法)例如dev,需要这样写:re-[dev]feat(JIRA-ID):xxxxx<br>
    9. 自动填充commitMsg到JIRA注释,需在提交类型(如feat)和冒号之间加上JIRA号,如feat(JIRAID-123):test。<br>

### 配置方法
1.下载master分支代码并打开setup.plist文件,填写JIRA用户名和密码,然后保存并关闭setup.plist文件 。示例如下图<br>
<img src="https://github.com/spWang/gitHooks/blob/master/demosetup.png" width="520" height="181">

2.打开控制台,切换到当前下载的脚本代码目录下,依次执行下边两个命令安装依赖库jira和biplist(执行后如果提示找不到pip命令,请参考下方的常见问题)<br>
```objc
pip install jira --user

pip install biplist --user
```

3.依赖库安装完毕后,执行下面命令初始化<br>
```objc
python setup.py
```
4.等待前3步执行完毕,就表示已经接入完成。现在可以提交一下代码试试是否会有效果<br>

-----------------------------------------------分割线----------------------------------------------------------------

### 常见问题(接入时无需执行这里,脚本出问题时可参考这里)
* 1.代码为何没有放入gitlab?代码具有自动更新自己的功能,而gitlab没法来拉取代码,因此放在这里了

* 2.执行pip install xxx --user遇到command not found之类的错误,说明没有安装pip,pip是用来安装python库的工具,可执行sudo easy_install pip命令安装(但很可能下载失败无法安装,此时可[点击我下载压缩包](https://codeload.github.com/spWang/pipZip/zip/master)手动安装,解压后安装方法见README.md)

* 3.当更新代码时,若一直拉不下来代码,请检查是否开启了蓝灯,蓝灯和github可能有冲突,请暂时关闭,待更新完代码后再开启

* 4.自动发送review时,使用sourcetree会找不到命令,需要创建软链接后使用,方法在你提交信息的时候会提示,按照提示操作就可以了

* 5.自动配置xcode模板时,因为需要临时获取root权限,因此会中断提交,并提示如果做,也按照提示操作就可以了

### 功能控制是否开启(接入时无需执行这里,脚本出问题时可参考这里)
1. 配置统一xcode模板,默认开启(git config githooks.xcodetemplate "YES")
2. 自动格式化代码功能,由提交到仓库的.clang-format文件是否存在控制(git config githooks.clangformat "YES")
3. ios项目检查图片同名,默认开启(git config githooks.sameimg "YES")
4. commitMsg规范性检查,默认开启(git config githooks.checkmsg "YES")
5. commitMsg前拼上分支/版本号,默认开启(git config githooks.premsg "YES")
6. ios项目版本号自动递增,默认关闭(git config githooks.autoversion "NO")
7. 自动帮你发布reviewRequest,默认关闭(git config githooks.review "NO"),由提交信息前添加关键字开启
8. 提交信息填充JIRA注释功能,默认开启(git config githooks.notejira "YES")

### 更多操作(接入时无需执行这里,脚本出问题时可参考这里)
* 在仓库目录下执行如下命令可强制更新升级(以上配置完毕后无需执行此命令)
```objc
python .git/hooks/upgrade.py
```

* 上个命令后加--help查看更多使用操作,例如:
a) -d可抹掉本仓库githooks配置, 加 -a可抹掉全局githooks配置
b) -v=xxx可升级至指定的版本
c) -v输出当前仓库的githooks版本号

#### [点我看更新日志](https://github.com/spWang/gitHooks/blob/master/changelog.md)


