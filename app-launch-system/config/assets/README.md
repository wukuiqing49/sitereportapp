# 官网素材目录

把官网使用的图片放在这里。Android 项目可以位于任意绝对路径，skill 只从这个目录读取你指定的官网素材。

```text
config/assets/
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

在 `config/app-info.yaml` 中配置：

```yaml
assets:
  root: "app-launch-system/config/assets"
  icon: "icon/icon.png"
  coverImage: "cover/cover.png"
  socialImage: "social/social-cover.png"
  screenshots:
    - "screenshots/home.png"
    - "screenshots/editor.png"
    - "screenshots/settings.png"
```

`screenshots` 是列表，可以放任意多张截图。列表顺序就是官网展示顺序。
