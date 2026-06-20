# Aivo V5 - Live2D版本说明

## 🎀 V5 主要特性

### 使用专业Live2D模型

**为什么选择Live2D？**
- ✅ **专业级质量**：由专业艺术家制作的精美模型
- ✅ **流畅动画**：物理引擎驱动，自然流畅
- ✅ **丰富表情**：多种预设表情和动作
- ✅ **自动口型**：内置口型同步系统
- ✅ **开源免费**：使用开源Live2D Widget项目

**对比手绘SVG的优势**：
| 特性 | 手绘SVG (V4) | Live2D (V5) |
|------|-------------|-------------|
| 制作难度 | 需要手写代码 | 使用现成模型 |
| 视觉质量 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 动画流畅度 | 简单切换 | 物理引擎插值 |
| 表情丰富度 | 4种基础 | 10+种专业 |
| 互动性 | 有限 | 丰富（点击/拖拽） |
| 口型同步 | 手动实现 | 内置支持 |

## 🚀 快速开始

### 启动V5界面

```bash
bash run.sh
# 选择选项 1 - Web界面V5

# 或直接运行
python src/web_ui_v5_live2d.py
```

### 第一次使用

1. **等待模型加载**（首次需要从CDN下载，约2-3秒）
2. **观察Live2D**：右侧会出现可爱的数字人
3. **输入消息**："你好"
4. **观察口型**：播放语音时，Live2D会自动说话
5. **尝试互动**：点击Live2D，它会有反应

## 💡 Live2D功能

### 1. 自动口型同步

**工作原理**：
- Live2D模型内置口型同步系统
- JavaScript监听audio播放事件
- 播放时自动触发Live2D说话动画
- 停止时恢复默认状态

**测试方法**：
```
输入："你好，今天天气真不错，阳光明媚"
点击发送 → 观察Live2D在播放时的口型变化
```

### 2. 互动动作

**支持的互动**：
- 👆 **点击**：触发特殊动作
- 🖱️ **悬停**：透明度变化
- 📱 **移动端**：触摸反馈

### 3. 表情系统

Live2D模型自带多种表情：
- 😊 开心
- 😢 难过
- 😲 惊讶
- 😐 平静
- 😴 困倦
- 🤔 思考
- ❤️ 害羞
- 😠 生气

（根据不同模型，表情会有所不同）

## 🎨 可用的Live2D模型

V5默认使用的模型：
- **hijiki** - 可爱的女孩子，黑色长发

**想换其他模型？**

在 `src/web_ui_v5_live2d.py` 中修改模型路径：

```javascript
"jsonPath": "https://cdn.jsdelivr.net/npm/live2d-widget-model-模型名@版本/assets/模型名.model.json"
```

**推荐模型**（都是开源的）：
1. **hijiki** - 黑发女孩
   ```
   live2d-widget-model-hijiki@1.0.5/assets/hijiki.model.json
   ```

2. **tororo** - 白发女孩
   ```
   live2d-widget-model-tororo@1.0.5/assets/tororo.model.json
   ```

3. **shizuku** - 小萝莉
   ```
   live2d-widget-model-shizuku@1.0.5/assets/shizuku.model.json
   ```

4. **miku** - 初音未来
   ```
   live2d-widget-model-miku@1.0.5/assets/miku.model.json
   ```

5. **koharu** - 可爱女孩
   ```
   live2d-widget-model-koharu@1.0.5/assets/koharu.model.json
   ```

6. **haruto** - 男孩子
   ```
   live2d-widget-model-haruto@1.0.5/assets/haruto.model.json
   ```

## 🔧 技术实现

### 使用的库

- **live2d-widget** (v3.1.4)
  - 开源项目：https://github.com/stevenjoezhang/live2d-widget
  - CDN加载，无需本地安装
  - 自动处理口型和动作

### 核心代码

```javascript
// 初始化Live2D
L2Dwidget.init({
    "model": {
        "jsonPath": "模型路径",
        "scale": 1
    },
    "display": {
        "width": 280,
        "height": 500,
        "position": "right"
    },
    "react": {
        "opacityOnHover": 0.2  // 鼠标悬停效果
    }
});

// 监听音频播放
audio.addEventListener('play', function() {
    // Live2D会自动播放口型动画
});
```

## 📊 版本对比

### V2 → V3 → V4 → V5

| 特性 | V2 | V3 | V4 | V5 |
|------|----|----|----|----|
| 数字人类型 | 静态图片 | 简单SVG | 精美SVG | 🌟 Live2D |
| 视觉质量 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 口型同步 | ❌ | 固定循环 | 手动实现 | ✅ 内置 |
| 动画流畅度 | ❌ | 简单 | 中等 | ✅ 物理引擎 |
| 表情数量 | 4种 | 4种 | 4种 | 10+种 |
| 互动性 | ❌ | 有限 | 有限 | ✅ 丰富 |
| 制作难度 | 简单 | 中等 | 困难 | ✅ 使用现成 |

### 推荐使用场景

- 🌟 **答辩演示**：V5（最专业）
- 🎨 **日常使用**：V5或V4
- 🔧 **快速开发**：V2
- 📚 **学习研究**：V4（了解实现原理）

## 🎓 答辩演示建议

### 演示话术

```
"我们的数字人系统使用了专业的Live2D技术。

【展示外观】
这是一个Live2D模型，由专业艺术家制作，
相比手绘SVG有更高的视觉质量和动画流畅度。

【演示口型同步】
现在我输入一句话...[输入并发送]
请注意，当播放语音时，Live2D会自动同步口型，
这是Live2D内置的功能，不需要手动实现。

【演示互动】
Live2D还支持互动，我点击一下...[点击]
它会有反应。

【技术说明】
我们使用了开源的live2d-widget项目，
通过CDN加载，集成简单，效果专业。"
```

### 技术亮点

1. **选型合理**：使用成熟的开源方案
2. **集成简单**：只需引入JS库，无需复杂配置
3. **效果专业**：媲美商业产品
4. **成本可控**：完全免费的开源模型

## ⚙️ 配置选项

### 调整Live2D位置

```javascript
"display": {
    "position": "right",    // 位置：right/left
    "width": 280,          // 宽度
    "height": 500,         // 高度
    "hOffset": 0,          // 水平偏移
    "vOffset": -20         // 垂直偏移
}
```

### 调整模型大小

```javascript
"model": {
    "scale": 1    // 缩放：0.5-2.0
}
```

### 移动端适配

```javascript
"mobile": {
    "show": true,      // 是否在移动端显示
    "scale": 0.8       // 移动端缩放
}
```

## 🐛 常见问题

### Q1: Live2D不显示？

**原因**：CDN加载失败或网络问题

**解决**：
1. 检查网络连接
2. 刷新页面重试
3. 查看浏览器控制台错误信息

### Q2: 口型不同步？

**原因**：audio元素未被正确监听

**解决**：
1. 确保使用autoplay自动播放
2. 检查浏览器是否允许自动播放
3. 查看控制台日志

### Q3: 想换其他模型？

参考上面"可用的Live2D模型"部分，修改jsonPath

### Q4: 模型太大/太小？

修改scale参数：
```javascript
"scale": 1.2  // 放大20%
```

## 📚 相关资源

- **Live2D官网**：https://www.live2d.com/
- **live2d-widget项目**：https://github.com/stevenjoezhang/live2d-widget
- **更多模型**：https://github.com/xiazeyu/live2d-widget-models
- **模型制作教程**：Live2D Cubism官方文档

## 🎉 总结

V5版本采用专业的Live2D技术，相比手绘SVG：

**优势**：
- ✅ 视觉质量更高
- ✅ 动画更流畅
- ✅ 表情更丰富
- ✅ 开发更简单（使用现成模型）
- ✅ 口型同步更自然

**适合场景**：
- 🎓 答辩演示（最佳选择）
- 📱 实际应用
- 🎨 追求视觉效果的项目

---

**版本**：V5.0
**日期**：2026-06-20
**状态**：✅ 推荐使用
**特色**：🎀 专业Live2D + 👄 内置口型同步
