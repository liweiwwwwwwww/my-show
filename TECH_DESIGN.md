# 技术设计文档（TECH_DESIGN）

> 对应 PRD v1.0。本文记录这个个人网站实际采用的技术方案。

## 一、技术栈选择

| 层 | 选型 | 理由 |
|---|---|---|
| 页面结构 | 原生 HTML5 | 单页展示，无需复杂路由 |
| 样式 | 原生 CSS3（CSS 变量 + Flex / Grid） | 不引入 Tailwind 构建流程，零依赖 |
| 交互 | 原生 JavaScript（ES6） | 无 React / Vue，无构建步骤 |
| 视觉特效 | Canvas 2D（星空粒子） | 轻量，性能好 |
| 字体 | 自托管 CDN 镜像的 Noto Serif / Sans SC | 不直连 Google Fonts |
| 部署 | Cloudflare Pages / Vercel（拖放静态文件） | 免费、自动 HTTPS、全球 CDN |

**为什么不用 React + Vite？**
本项目是纯静态单页，没有登录、数据库、复杂状态管理。用单文件 HTML 可以免去 `npm install` 和构建步骤，直接把一个 `index.html` 拖到 Cloudflare Pages 就能上线，对快速交付最友好；后期若要加后台再迁移到框架。

## 二、目录结构

```
个人网站/
├── index.html      # 唯一页面：结构 + 内联 CSS + 内联 JS，全部自包含
├── PRD.md          # 产品需求文档
├── TECH_DESIGN.md  # 本文件
└── AGENTS.md       # AI 开发约定
```

## 三、关键技术点

1. **星空背景**：一个 `position: fixed` 的 `<canvas>`，JS 生成 180 个（移动端 70 个）星点，用 `requestAnimationFrame` 做呼吸闪烁；监听鼠标移动做轻微视差；通过 `prefers-reduced-motion` 检测，用户系统开启「减少动态效果」时停止动画。
2. **响应式**：移动优先，在 `640px / 900px` 两个断点用媒体查询把多列栅格降为单列。
3. **锚点导航**：`<a href="#about">` + CSS `scroll-behavior: smooth`，无需 JS 路由。
4. **邮箱复制**：`navigator.clipboard.writeText()`，失败时降级为 toast 直接显示邮箱。
5. **技能条动画**：`IntersectionObserver` 监听进度条进入视口后再用 CSS `width` 过渡展开。
6. **避免死按钮**：社交图标等占位入口统一弹 toast 提示「请替换成自己的链接」，不做空跳转。

## 四、数据模型

无数据库。所有内容（姓名、项目、博客）直接写死在 `index.html` 里，改文案即改页面。

## 五、部署方式

1. 把 `index.html` 推到 GitHub 仓库；
2. 登录 Cloudflare Pages → 导入该仓库；
3. 框架预设选「无」，构建命令留空，输出目录填 `/`；
4. 点「保存并部署」，拿到 `*.pages.dev` 域名即上线；
5. 以后 push 代码会自动重新部署。
