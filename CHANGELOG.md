# 校修通 更新日志

## 2026-06-01

### feat: 维修知识库 (1ebd905)
- 新增 `solution` 字段到工单表，师傅完工时填写维修方案
- 新增 `/api/knowledge/search` 知识库搜索接口
- AI 客服自动检索知识库，回答时引用相似历史案例
- 师傅端快捷提问新增「查知识库」入口

### perf: 图片识别速度与精准度优化 (37b5968)

### perf: 图片识别速度与精准度优化 (37b5968)
- 前端图片压缩到 512px + JPEG 质量 0.7，上传体积减少 80%+
- 新增 `/analyze/fast` 接口，base64 直传智谱 AI，省去先存 Supabase 再取 URL 的往返
- Vision prompt 加入 8 类视觉线索指引 + 4 个 few-shot 示例，提升分类精准度

### feat: 图片一键填单 + AI 助手按钮位置上移 (c9d50b2)
- AI 图片分析新增 `description` 字段，拍照后自动填入问题描述
- 前端 AI 结果卡片展示识别的问题描述和推荐配件
- AgentChat FAB 按钮从底部 24px 上移至 80px，避免遮挡底部导航栏

### fix: 修复工单无法打开 + 多项改进 (c7770ff)
- 更新 API 地址到 `campus-fix-production.up.railway.app`（旧 Railway 地址已失效）
- 后端新增 UUID 参数校验，防止非法 ID 请求
- 后端完善错误处理，创建/更新失败时返回 500 而非空对象
- CORS 改用配置变量 `CORS_ORIGIN`
- 学生端新增班级补填提示条（存量学生 class_name 为空时显示）
- 师傅端新增"全部"和"待确认"标签页
- 新增 Electron 桌面端入口 + PWA 图标
- 新增 Windows 便携版打包脚本 `build-portable.bat`

## 2026-05-29

### feat: 主题 UI 全面升级 (9b226fc)
- 全局主题色系统：主色 #4f46e5（靛蓝）
- Naive UI 组件全局样式覆盖（Button/Input/Card/Tag/Tabs/Dialog/Select）
- 桌面端侧边栏导航 + 响应式布局优化
- 页面切换过渡动画

### fix: 重构 App.vue 为单一 router-view 避免双实例冲突 (4d938d0)

### feat: 前端交互全面优化 (1f62d0c)

### fix: 修复 workflow 重复 env 块导致解析失败 (4056787)

### fix: APK 构建使用相对路径 base=./ 修复白屏 (48478d8)

### fix: JDK 版本 17 → 21 (Capacitor v8 需要 Java 21 编译) (114e308)

### fix: gradlew 添加执行权限修复 CI Permission denied (bdc69df)

### feat: 添加 Capacitor Android 工程 + CI 自动构建 APK (92ddb34)

### feat: 新增辅导员角色 + 全站PC端响应式适配 (7639212)

### feat: AI assistant can now access user order data (3caff61)
