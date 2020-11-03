# eoffcn-ts-decode
 中公网ts加密研究学习，多线程下载已经购买的视频并合并为mp4

#### 测试环境

Windows 10 19041、Python 3.8、NodeJS 14.15.0

#### 使用方法

1. 填入`headers['cookie']`的值或在启动时输入`cookie`
2. 下载最新[ffmpeg.exe](https://github.com/FFmpeg/FFmpeg)放置运行目录

#### 实现功能

- ts二次加密算法还原
- 自动构建目录、多线程下载
- 自动将下载的视频ts合并解密为mp4，合并完成后将会清除目录下的其他文件

#### 声明

遵循Apache Licence，仅供交流学习禁止商业用途