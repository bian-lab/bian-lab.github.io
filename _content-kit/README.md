# Bian Lab 站点内容工具包

这个目录以 `_` 开头，GitHub Pages 的 Jekyll 构建不会把它发布到网站上。它用于保存内容表单、图片处理脚本和上传前检查脚本。

## 站点结构

```text
.
├── index.html                 Home：三屏轮播、简介、三张入口卡片
├── research.html              Research
├── team.html                  团队总览：PI、博后/助理、研究生、访问学生、校友
├── publication.html           论文列表
├── news.html                  新闻，按时间倒序
├── gallery.html               Gallery，筛选类别 life / science / art
├── contact.html               地址、邮箱、AMap 地图
├── members/member_*.html      每位成员一个详情页
├── images/                    团队照片、News、Gallery、头图、论文图
├── sources/                   论文 PDF
├── plugins/                   jQuery、Bootstrap 4、Slick、Lightbox、Filterizr 等
├── css/style.css              全站样式
└── js/script.js               轮播、筛选、lightbox、preloader 等初始化
```

## 内容更新流程

1. 你说要加/改什么；我按 `FORMS.md` 发对应的表。
2. 你给我图片和已填信息；我检查尺寸、文件名、公开项。
3. 我生成裁切/压缩预览，你确认构图和可读性。
4. 我修改 HTML，运行 `check_site.py`，在本地打开页面截图给你看。
5. 你确认后我 commit 并 push 到 `master`，GitHub Pages 自动发布。

## 不改变布局的边界

- 沿用现有 Bootstrap 栅格：团队卡片 `col-lg-4 col-md-6`，Gallery `col-md-3 col-sm-6`，News 图片 `col-md-4`。
- 不新增全站字体、颜色、动画或导航项。
- 不重构为 React/Vue，不引入构建步骤。
- 不批量改现有照片；如需优化历史大图，先单独确认。
- 科学图、艺术图不裁切；成员照只做构图裁切。
- 头部、导航、页脚目前是 22 个页面各自复制一份；改导航时我会全部同步检查。

## 图片规则

- 成员：3:4 竖图，1200×1600，脸部偏上，JPEG q86，目标 <500 KB。
- News / Gallery Life：4:3 横图，1600×1200，JPEG q85，目标 <500 KB。
- Gallery Science / Art：保持原始比例，长边 ≤1600；优先 PNG 或高质量 JPEG，不裁切。
- 首页/栏目头图：16:9，2400×1350，JPEG q82。
- 去除 EXIF/GPS；不磨皮、不调色、不修人脸。
- 原图默认不动；覆盖输出前自动生成 `.bak-时间戳`。例外：2026-10 历史图片批量压缩经用户确认后直接覆盖，git 历史中仍可恢复。

工具：`prepare_image.py`（Pillow）。

## 上传前检查

```bash
python _content-kit/check_site.py
```

返回码非 0 表示有本地链接/资源缺失或重复 id，不应上传。warning 包括缺少 canonical、`target="_blank"` 未加 `rel`、被引用图片超过 2 MB 等。

## 已知风险（截至 2026-10）

- **历史大图（已处理）**：2026-10 已批量生成网页尺寸并覆盖原图，所有站点文件 <25 MB；最大图片为 `images/publication/publication_header.png`（约 3.5 MB），其余照片多在 0.1–0.8 MB。
- **AMap key**：`contact.html` 中的高德 JS API key 是公开可见的，需在 AMap 控制台配置域名白名单/配额；当前使用 1.3 旧版 API。按用户要求暂不改动。
- **第三方计数器**：页脚使用 `easycounter.com`，可能被广告拦截器拦截，属于第三方请求。按用户要求暂不改动。
- **模板残留**：部分图片 alt 为空、旧 Bootstrap/jQuery 版本、22 份重复导航；这些不影响当前布局，但维护成本较高。
- **成员信息**：Shucheng Wang 已在团队页和详情页统一为 Graduate Student (2025)；Longyun Mu 已从当前团队移入 Alumni，标注 visiting student (rotation)。
- **孤立成员页**：`members/member_lyy.html`（Yunyue Li）是已离开的 rotation student，按用户说明保留页面，不加入团队页或 Alumni。
- **占位内容**：`members/member_wty.html` 使用 GIF 和“此人很神秘，什么都没留下~”，如果是有意保留则无需处理。

## 给后续维护者/AI 的固定规则

- 先读对应页面和相邻条目，再改；不要凭文件名猜结构。
- 一次只改一个内容类型；改完展示 `git diff --stat` 和页面预览。
- 不收未经本人同意的联系方式或照片。
- 上传前必须跑 `check_site.py`；不要为了通过检查而删除真实内容。
- 不直接覆盖原图，除非用户明确同意；不 force push；不改写已发布的历史提交。
