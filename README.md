# Countdowner

## 有一个无法解决的未知问题

> 当`assets/wallpapers/`里面没有壁纸或者关闭背景图时时，导致窗口无法显示
>
> 暂时使用一个奇葩方法解决了，解决方法是 `WallpaperSwitcher.switchNext`里面不执行设置背景

一个倒计时的傻逼玩意

这个东西使用的时候要先往`assets/wallpapers`里面建文件夹，一个文件夹代表一张壁纸，然后要建配置文件`config.json`

```json
// 开始使用前请删除所有注释
{
  //默认配置
  "name": "default",
  // 名字，必要
  "image": "image.jpg",
  // 图片，相对于壁纸文件夹的路径
  "timebox": {
    // 时间显示框，跟随系统时间
    "pos": [10, 10]
    // 时间显示框的位置，屏幕总尺寸1920*1080，时间框大小500*200
  },
  "countdownbox": {
    // 倒计时
    "pos": [586, 10],
    // 位置, 748*64, 这个位置在屏幕顶部中央
    "color": {
      // 颜色 文本格式为 距离<target>还有<days>天
      "text": "black",
      // 距离 还有 天 的颜色
      "days": "red",
      // <days>的颜色
      "target": "green"
      // <target>的颜色
    }
  },
  "textbox": {
    // 文本框
    "pos": [
      // 位置 x, y, width, height 多个，随机选定
      [0, 0, 200, 200]
    ],
    "stylesheet": "",
    // Qt5样式表
    "align": "left",
    // 对齐方式
    "use_global_texts": false,
    // 使用全局文本库，需要使用manage导入
    "texts": []
    // 文本，多个，随机选定，可放励志名言
  }
}
```

启动之后会生成一个 `config.yaml` 在根目录

里面可以设置