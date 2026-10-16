# 隐私政策维护

`privacy-policy.yaml` 是官网政策的持久化来源，生成器会将其应用到所有隐私页面。政策修订日期独立于应用分析日期和文章发布日期。正文提供完整英文、中文；其余七个语言页面显示本地语言提示及完整英文政策，使用 `lang` 标记说明正文语言，不能将其当作已完成的法律翻译。

## 本次核对依据（2026-10-16）

- `app-launch-system/config/organization.yaml`：运营主体、开发者名称、隐私联系邮箱。
- Android 源码 `C:/work/AI/SiteReport`：
  - `app/src/main/AndroidManifest.xml`：权限、禁用备份、禁止广告标识权限、允许明文连接，因此不能承诺全部传输加密。
  - `app/src/main/res/values/google_config.xml`、`app/src/release/res/values/google_config.xml`：正式版 Firebase Analytics / Crashlytics 启用，广告关闭。不能只读取 main 资源后声称正式版统计关闭。
  - `app/build.gradle`、`core/core_google/.../commercial/GoogleCommercialManager.kt`：DevHub 基础统计、机型与地区设置、购买校验及默认关闭购买账号关联。
  - `core/core_location/src/release/.../AppLocationProviderFactory.kt`：正式版仅 Google / Android 定位，高德仅在调试版使用。
  - `feature/feature_app/.../viewmodel/AccountProfileViewModel.kt`：Google 登录及 Firebase 用户标识关联。
  - `feature/feature_app/.../viewmodel/AboutUsViewModel.kt`、`account/AccountDataCleanupService.kt`：本地清理范围；不等于远端删除或取消订阅。
  - `docs/google-play-data-safety-devhub.md`：DevHub 数据种类、用途与保留原则，不能把该局部清单误当成应用全量申报。
- 应用内现有政策：https://wukuiqing49.github.io/agreement/site_report_privacy_policy.html 。旧政策的 AdMob / 高德说明与当前 release 配置存在差异，本次未照抄。
- 网站 `assets/locale-router.js`：记住语言的 localStorage；视频为外部跳转链接。
- Google Play 用户数据政策：https://support.google.com/googleplay/android-developer/answer/10144311 。仅用于检查披露范围，不代表 Google 已审查或认可本政策。

## 运行与维护边界

本次更新网站，不修改 Android、DevHub 后端或旧 GitHub Pages 政策仓库。Android 当前仍链接旧政策与旧数据删除页；后续应用发布应统一链接，并核对 Play Console 数据安全申报。

源码不能确认生产后端日志、Firebase 实际保留配置、合同保障或删除执行时限，因此政策没有编造具体保留天数、响应时限、全程加密或全面合规保证。运营者应核实实际配置与删除流程，必要时再更新政策。不要把添加政策页面当作已经实现服务器删除功能。

修改数据实践、SDK、配置、运营主体或联系地址时，同步更新政策、修订日期及 Google Play 申报。新增翻译需完整覆盖正文后才加入 `locales`；缺少明确 fallback 提示会阻止生成。
