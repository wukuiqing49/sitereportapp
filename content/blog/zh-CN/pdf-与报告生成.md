---
contentId: report-generation
locale: zh-CN
status: machine-draft
title: 巡检 PDF 发给客户前，应检查哪些内容
description: 从巡检数据生成结构化现场报告。 了解它解决的问题、具体选项、真实操作步骤和已知限制。
slug: pdf-与报告生成
intent: feature education
audience: app users
canonical: ''
evidence:
- SiteReport.md
- core/core_pdf/src/main/java/com/wkq/nativepdf/NativeReportPdfRenderer.kt
- feature/feature_app/src/main/java/com/wkq/feature/app/upload/NativeSiteReportPdfGateway.kt
primaryKeyword: 巡检 PDF 发给客户前，应检查哪些内容
relatedPages:
- /
- /support.html
template: tutorial
---

# 巡检 PDF 发给客户前，应检查哪些内容

把现场观察整理成格式一致的报告，通常需要大量手动排版。

## 这项功能解决什么问题

- 生成 PDF 现场报告
- 包含检查结果、照片、位置、备注和签字
- 预览并重新打开已生成的报告

## 如何融入处理流程

- 完成巡检记录
- 选择报告和 PDF 呈现选项
- 生成报告并检查导出文件

## 导出前需要检查什么

- 报告模板、PDF 样式、导出格式和签字选项

## 注意事项

- 部分报告样式和模板取决于应用版本或访问计划。

## 先检查原始记录，再检查导出文件

生成前核对项目身份、检查结果、照片、备注和签字资料。根据接收方需要选择模板、PDF 样式和签字选项；部分样式受版本或访问方案限制，应以当前安装版本实际提供的选项为准。不要把尚未录入的内容寄希望于模板自动补齐。

打开生成的 PDF，检查项目名称、照片清晰度、问题描述以及签字显示。发现遗漏时，先回到源记录和模板选项检查，再生成替换文件。重新打开替换文件，并确认分享时选中的是这一份。文件生成成功和对方收到文件是两个不同的验收步骤。

