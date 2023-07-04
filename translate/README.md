## 依赖

```
pip install requests  translators
```

## 命令行

```
python translatorGD.py "需要翻译的内容"
```

支持3个参数

- originalText  第一个参数  需要翻译的内容
- fromLanguage 第二个参数 待翻译的语言, 可以用auto自动识别 默认 `en`
- toLanguage  第三个参数 目标语言, 默认 `zh-CN`

## GoldenDict配置

编辑->词典-> 词典来源-> 程序  添加相应的命令行参数

中译英

```
python "translatorGD.py" "%GDWORD%"
```

可指定语言, 如中译英

```
python "translatorGD.py" "%GDWORD%" zh-CN en
```

个人配置如下

![image-20230704104936875](image-20230704104936875.png)



实际效果如下

![image-20230704105602906](image-20230704105602906.png)

![image-20230704105727679](image-20230704105727679.png)

## 感谢

https://github.com/UlionTse/translators 翻译库