# 博客内容维护

`editorial.yaml` 是独立教程正文的输入文件；各语言目录中的 Markdown 和根目录 `blog/` 下的 HTML 都是生成结果，不应直接修改。

输入按语言代码和功能 ID 组织。每篇可设置 `title`，并在 `sections` 中编写 `heading` 和 `paragraphs`。每个段落使用对应语言；不要把未经验证的界面名称、自动续传或交付成功等行为写成产品承诺。

功能页负责能力、输入输出和限制；博客补充现场任务、检查方法与失败排查。优先添加可验证的实际操作和示例，避免重复粘贴功能列表。新增内容应覆盖对应语言，不会自动借用其他语言的正文。

在项目根目录重新生成并检查：

```powershell
python -B app-launch-system/scripts/generate_website.py --force
python -B -m unittest discover -s app-launch-system/tests
python -B app-launch-system/scripts/validate_output.py .
```

生成器会检查正文结构、转义 HTML，并把新增章节同步到页面目录和生成的 Markdown。更新教程标题不会改变 URL。部署后才会影响线上页面；搜索引擎是否收录及处理时间由搜索引擎决定。
