# Android App Launch System

这是一个从 Android 项目直接生成 App 静态官网的 Codex 插件。用户只需要提供 Android 项目的绝对路径；系统负责分析项目、读取真实截图、生成多语言页面，并把可用于 Cloudflare Pages 的纯静态网站写到当前项目根目录。

## 项目地址与输出位置

Android 项目可以放在任意位置。你只需要把 Android 项目的绝对路径提供给 AI，系统会读取项目内容，但不会修改 Android 源码。

官网文件和全部发布资产默认直接输出到包含 `app-launch-system/` 的项目根目录。所有路径均为相对路径，不绑定具体机器目录。官网入口固定为 `index.html`：

```text
<project-root>/
├── app-launch-system/
├── index.html
├── privacy.html
├── support.html
├── 404.html
├── _headers
├── assets/
├── blog/
├── app-info.yaml
├── analysis-evidence.json
└── launch-manifest.yaml
```

## 官网图片放在哪里

官网图片统一放在 `app-launch-system/config/assets/`，不需要放进 Android 项目：

```text
<project-root>/
├── app-launch-system/
│   └── config/
│       └── assets/
│           ├── icon/
│           │   └── icon.png
│           ├── cover/
│           │   └── cover.png
│           ├── social/
│           │   └── social-cover.png
│           └── screenshots/
│               ├── home.png
│               ├── editor.png
│               └── settings.png
├── index.html
└── assets/
```

图片用途如下：

- `icon.png`：网站 Logo 和应用图标
- `cover.png`：官网首页主视觉
- `social-cover.png`：社交分享封面，建议 1200×630
- `screenshots/`：官网功能区展示的真实应用截图

在 `app-launch-system/config/app-info.yaml` 中配置：

```yaml
assets:
  root: "app-launch-system/config/assets"
  icon: "icon/icon.png"
  coverImage: "cover/cover.png"
  socialImage: "social/social-cover.png"
  screenshots:
    - "screenshots/home.png"
    - "screenshots/editor.png"
```

生成官网时，AI 会优先使用这里配置的图片，并复制到项目根目录 `assets/`。`screenshots` 可以配置任意多个文件，AI 会按列表顺序组织官网展示。没有明确封面图时，不要让 AI 随意使用无关图片。

例如项目地址可以是：

```text
D:\projects\MyAndroidApp
```

## 生成官网

在 Codex 中打开包含 `app-launch-system/` 的项目根目录，然后输入：

```text
使用 $android-app-website，分析 D:\projects\MyAndroidApp 并生成静态应用官网。
```

系统会自动执行：

```text
Android 项目分析
    ↓
生成并校验 app-info.yaml
    ↓
生成根目录 index.html、about.html、privacy.html、support.html、blog/ 和 assets/
    ↓
生成 Cloudflare Pages 可用的纯静态文件
```

生成器不会把一句功能摘要机械扩写成官网和博客。内容链路固定为：

```text
Android 源码与资源证据
    ↓
功能事实（问题、能力、输入输出、选项、步骤、限制、FAQ）
    ↓
内容就绪门槛
    ↓
首页摘要、独立功能页、功能博客
    ↓
SEO/GEO、ASO 草稿与发布就绪报告
```

只有具备完整 `details` 且有源码证据的功能才会生成独立功能页和博客。信息不足的功能可以保留在首页，但不会用通用套话生成薄文章。

生成结果不需要 Node 构建、数据库、API 或服务端渲染。`index.html` 是根入口，`404.html` 和 `_headers` 用于 Cloudflare Pages 静态托管。`static-site-manifest.json` 只列出允许部署的公开文件，避免把分析证据和插件配置上传。系统只生成文件，不会自动部署。

除公开网站外，还会生成不进入 `static-site-manifest.json` 的编辑与审计资料：

```text
content/blog/          博客 Markdown 源稿
aso/                   Google Play 文案、截图计划与审计
seo-geo/               关键词、页面、答案、实体与内链资料
launch-readiness.yaml  域名、商店、语言和内容发布门槛
```

未配置 `websiteUrl` 时，canonical、hreflang、Open Graph 绝对地址和 sitemap 会明确标记为阻塞；未配置 `googlePlayUrl` 时，ASO 会保持草稿/阻塞状态。`analysis.validatedAt` 只表示项目分析时间，不能作为博客发布日期。只有显式配置 `editorial.publishedAt` 后，博客才输出文章日期结构化数据。

## 如何把项目交给 AI

你不需要把 Android 项目代码复制到聊天框，也不需要手动整理功能列表。只要提供项目的绝对路径即可。

### 最简单的用法

```text
请分析这个 Android 项目并生成官网：
D:\projects\MyAndroidApp

官网入口直接生成到当前项目根目录 index.html，不要创建额外输出目录，不要修改 Android 项目。
```

### 推荐的标准用法

如果你还知道产品名称、目标语言或 Google Play 地址，可以一起提供：

```text
使用 $android-app-website。

Android 项目绝对路径：D:\projects\MyAndroidApp
产品名称：Image Box
目标语言：zh-CN、en-US
Google Play 地址：https://play.google.com/store/apps/details?id=com.example.app

请完成：
1. 分析 Android 项目
2. 生成并校验 app-info.yaml
3. 生成应用官网
4. 将官网入口 index.html 和相关文件直接输出到当前项目根目录
5. 不要修改 Android 项目，不要部署网站
```

### 只生成官网

```text
使用 $website-generator-skill。

Android 项目绝对路径：D:\projects\MyAndroidApp
读取项目根目录 app-info.yaml，
生成官网到项目根目录，入口为 index.html。
请使用 Android 项目中的真实截图，不要虚构功能或营销数据。
```

### 只有项目地址，没有其他资料

也可以只发送这一段：

```text
Android 项目地址：D:\projects\MyAndroidApp
请根据项目内容生成官网，入口直接输出到项目根目录 index.html。
```

AI 会自动尝试提取：

- 应用名称
- 包名
- 版本信息
- 用户可见功能
- 应用图标
- 截图
- 支持的语言
- 权限和技术信息
- README 中的产品说明

无法从项目确认的信息会列入 `unknowns`，不会自动猜测。

### 重新生成或继续上次任务

如果项目根目录已经存在 `launch-manifest.yaml`，可以这样使用：

```text
继续处理 D:\projects\MyAndroidApp 的官网任务。
读取项目根目录 launch-manifest.yaml，
只完成尚未完成的阶段，不要覆盖已经标记为 reviewed 或 published 的文件。
```

### 让 AI 修改官网

可以直接说明要改什么，并保留项目地址：

```text
修改项目根目录官网文件：
1. 首页突出图片批量处理功能
2. 保留真实截图
3. 不增加未经项目证实的功能
4. 修改后重新运行官网校验
```

### 生成后如何确认结果

让 AI 返回以下信息：

```text
请报告：
1. 官网生成目录
2. 生成了哪些页面
3. 使用了哪些项目证据
4. 哪些内容仍需要我确认
5. 校验是否通过
```

重点查看：

```text
index.html
privacy.html
support.html
app-info.yaml
launch-manifest.yaml
```

### 喂给 AI 的信息优先级

建议按以下优先级提供信息：

1. Android 项目绝对路径
2. 明确的输出目录要求
3. 产品名称和开发者名称
4. Google Play 地址
5. 支持邮箱和隐私政策地址
6. 目标语言
7. 官网风格偏好

没有提供的信息，AI 会从项目中查找；仍然无法确认的内容会保留为空或标记为待确认。

只生成官网时可以输入：

```text
使用 $website-generator-skill，读取项目根目录 app-info.yaml，
生成官网到项目根目录，入口为 index.html，并完成校验。
```

如果还没有 `app-info.yaml`，不需要手动创建，先输入：

```text
使用 $app-analyzer-skill，分析 D:\projects\MyAndroidApp，
把 app-info.yaml 和 analysis-evidence.json 直接输出到项目根目录。
```

## 项目需要包含的内容

项目最好包含：

- `build.gradle` 或 `build.gradle.kts`
- `AndroidManifest.xml`
- `strings.xml`
- Kotlin、Java 或 Compose 页面
- 应用图标和真实截图
- README、隐私政策或支持文档（如果有）

以下敏感文件不会作为公开产品资料使用：

```text
local.properties
.env
*.keystore
*.jks
google-services.json
secrets/
credentials/
```

## 输出内容

```text
<project-root>/
├── app-launch-system/
├── index.html
├── privacy.html
├── support.html
├── robots.txt
├── sitemap.xml
├── site.webmanifest
├── localization-status.yaml
├── assets/
│   ├── styles.css
│   ├── app.js
│   ├── locale-router.js
│   ├── blog.css
│   └── blog.js
├── blog/
│   ├── index.html
│   └── <locale>/<slug>/index.html
├── content/blog/
│   ├── content-plan.yaml
│   ├── localization-status.yaml
│   └── <locale>/<slug>.md
├── app-info.yaml
├── analysis-evidence.json
├── launch-manifest.yaml
├── seo-geo/
└── aso/
```

官网会尽量包含：应用名称、价值主张、真实截图、已验证功能、使用流程、Google Play 入口、隐私页、支持页、SEO metadata、Open Graph、JSON-LD、robots 和 sitemap。博客阶段同时保留 Markdown 内容源，并生成与官网共用品牌样式的博客首页、标准文章、教程和版本发布页面。

## 多语言与自动展示

源语言页面直接放在项目根目录，其他语言放在 BCP 47 目录中：

```text
<project-root>/index.html
<project-root>/privacy.html
<project-root>/zh-CN/index.html
<project-root>/zh-CN/privacy.html
<project-root>/ja-JP/index.html
```

访问根目录页面时，网站会优先使用用户之前手动选择的语言，否则根据浏览器的 `navigator.languages` 匹配完整 locale、配置别名和基础语言，无法匹配时回退到源语言。用户可以通过导航中的语言菜单随时切换，选择结果保存在当前浏览器。语言子目录不会再次自动跳转，直接链接和搜索引擎访问保持稳定。

每个语言页面必须包含自身 canonical、互相对应的 `hreflang`、`x-default`、正确的 `lang` 和 `dir`。非源语言内容默认标记为 `machine-draft`，发布前需要人工审核。

目标语言在生成后的 `app-info.yaml` 中配置，例如：

```yaml
languages:
  source: "zh-CN"
  targets:
    - "en-US"
    - "ja-JP"
  availableInApp:
    - "zh-CN"
    - "en-US"
    - "ja-JP"
  routing:
    autoDetect: true
    rememberSelection: true
    sourceAtRoot: true
    aliases:
      zh-HK: "zh-TW"
```

`targets` 必须明确配置或来自已验证的 App 语言资源，生成器不会自行虚构目标语言。

## 共享公司信息

公司主体统一配置在 `app-launch-system/config/organization.yaml`。该文件独立于具体 App，默认被所有官网、公司页、隐私页、支持页、博客和结构化数据复用。公司简介应描述公司的通用业务，不要绑定某一个 App。

```yaml
legalName: "公司法定名称"
displayName: "对外开发者名称"
website: "https://company.example/"
email: "contact@company.example"
localized:
  zh-CN:
    description: "不关联具体项目的公司简介。"
```

如需为某次生成使用另一家公司配置，可传入 `--organization <organization.yaml>`。

博客会根据 `app-info.yaml` 中经过验证的功能自动生成。每个功能可通过 `blog.template` 选择 `standard-article` 或 `tutorial`；公开页面写入 `blog/`，可编辑 Markdown 写入 `content/blog/`。`content/blog/` 不会进入 `static-site-manifest.json`。

## 命令行校验

从包含 `app-launch-system/` 的项目根目录执行：

```powershell
python app-launch-system/scripts/launch.py scan D:\projects\MyAndroidApp --output analysis-evidence.json
python app-launch-system/scripts/launch.py validate-app-info app-info.yaml
python app-launch-system/scripts/launch.py generate-website
python app-launch-system/scripts/launch.py validate-output .
```

官网生成器默认读取项目根目录的 `app-info.yaml` 和 `app-launch-system/config/organization.yaml`，并直接把 `index.html`、`about.html`、语言目录、`blog/` 和 `assets/` 写到同一个项目根目录。不会创建 `launch-output/` 或 `website/`。每个 `languages.targets` 目标语言都必须先准备 `content/locales/<locale>.yaml`，结构参考 `app-launch-system/templates/website-template/locale-content.yaml`；缺少翻译时命令会停止，不会用源语言冒充翻译。

首次生成直接运行上面的命令。刷新已经生成的网站时需要明确使用：

```powershell
python app-launch-system/scripts/launch.py generate-website --force
```

Python 依赖通过以下命令安装：

```powershell
python -m pip install -r app-launch-system/requirements.txt
```

校验器会检查必填信息、功能 evidence、证据文件、URL、locale、未替换 token 和占位文本。

## Google Search Console 验证

Cloudflare Pages 的 `pages.dev` 地址应在 Search Console 中添加为“网址前缀”资源，例如 `https://sitereport-app.pages.dev/`；“域名”资源只能用 DNS TXT 验证。

如果选择 HTML 标签验证，把 Google 提供的 token 写入 `app-info.yaml`：

```yaml
searchConsole:
  verificationToken: "google-site-verification=你的token"
```

官网生成器会把它写入根首页的 `<head>`。如果选择 HTML 文件验证，必须填写 Google 下载文件中的真实文件名和完整内容：

```yaml
searchConsole:
  verificationFileName: "google1234567890abcdef.html"
  verificationContent: "google-site-verification: google1234567890abcdef.html"
```

验证文件会写入站点根目录并加入 `static-site-manifest.json`；不完整或伪造的配置会直接阻止生成。

## 需要人工确认的信息

如果 Android 项目中没有明确证据，系统不会猜测：

- 开发者或公司名称
- Google Play 地址
- 官网域名
- 隐私政策
- 支持邮箱
- 价格、订阅和试用
- 数据安全声明
- 用户量、评分、奖项和客户案例

没有 Google Play URL 时，官网会显示不可点击的可用性状态，不会生成空链接。非源语言页面默认标记为 `machine-draft`，发布前需要人工审核。

## 生成前检查

- 提供 Android 项目绝对路径
- 确认正确的 module 和 release variant
- 项目至少有一个用户可见功能
- 至少有一张当前版本截图
- 应用名称和包名可被确认
- 不把密钥或签名文件当作产品资料

## 发布前检查

- 没有 `{{TOKEN}}`、`TODO` 或 `example.com`
- 图片和内部链接有效
- Google Play 地址正确
- privacy/support 内容已审核
- JSON-LD 与页面可见内容一致
- 移动端没有横向滚动
- 非源语言内容已经人工审核
- 没有虚构评分、评论、价格或数据安全声明

系统只生成本地文件，不会自动部署网站、上传 Google Play 或修改外部服务。
