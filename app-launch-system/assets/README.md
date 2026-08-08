# Website Assets

正式素材目录已经迁移到 `../config/assets/`。请把图片放到 `config/assets/`，本目录不再作为 skill 的默认素材来源。

把希望用于官网的图片放在这个目录，不需要放进 Android 项目，也不需要复制到聊天框。

当前使用的结构：

```text
app-launch-system/config/assets/
├── icon/
│   └── icon.png
├── cover/
│   └── cover.png
├── social/
│   └── social-cover.png
└── screenshots/
    ├── home.png
    ├── editor.png
    └── settings.png
```

用途：

- `icon.png`：网站 Logo、导航栏图标和 Web Manifest 图标
- `cover.png`：官网首页 Hero 主视觉
- `social-cover.png`：Open Graph 和社交分享封面，建议 1200×630
- `screenshots/`：官网功能区使用的真实应用截图

在 `app-info.yaml` 中填写相对路径，例如：

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

如果没有 `cover.png` 或 `social-cover.png`，生成器只能从已验证截图中选择，并会在结果中报告这个决定。
