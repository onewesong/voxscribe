# VoxScribe | 声音抄写员

![VoxScribe音频转文字工具](screenshots/app_screenshot.png)

一个优雅、直观的音频转文字工具，使用OpenAI的[whisper-large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo)模型将音频快速转换为带时间轴的文字。提供美观的网页界面和强大的命令行支持。

> 💡 VoxScribe基于OpenAI的Whisper Large V3 Turbo模型，该模型在处理速度和准确性上达到了良好的平衡。支持超过99种语言的音频识别，并且可以生成精确的时间轴信息。

## 特点

- **美观直观的网页界面**，无需编程知识即可使用
- 支持多种输出格式：纯文本、SRT、VTT和JSON
- 支持句子级和词级时间戳
- 支持多语言音频识别（99种语言）
- 支持翻译模式（将任何语言翻译成英文）
- 支持CPU和GPU加速
- 高效处理长音频文件
- 一键下载转录结果

## 安装

### 前提条件

- Python 3.8 或更高版本
- PyTorch
- 足够的磁盘空间用于存储模型（约1.7GB）

### 使用pip安装

```bash
# 从GitHub安装
pip install git+https://github.com/yourusername/voxscribe.git

# 或从本地安装
pip install -e /path/to/voxscribe
```

## 使用方法

### 网页图形界面

启动网页界面（推荐使用方式）：

```bash
# 启动VoxScribe网页界面
voxscribe
```

然后在浏览器中访问 `http://localhost:8501` 即可使用图形界面。

网页界面特点:
- 直观的文件上传和处理
- 可视化配置参数（语言、格式、时间戳等）
- 实时处理状态显示
- 一键下载转录结果（SRT、VTT、JSON格式）
- 处理统计数据可视化

![网页界面](screenshots/web_interface.png)

网页界面包含以下主要部分：

1. **侧边栏配置面板** - 设置各种转录参数
   - 输出格式选择（文本、SRT、VTT、JSON）
   - 时间戳级别（句子级或词级）
   - 音频语言选择（支持自动检测）
   - 任务类型（转录或翻译）
   - 高级设置（设备、批处理大小等）

2. **主界面** - 文件上传和结果显示
   - 文件上传区
   - 转录结果显示
   - 结果下载按钮
   - 统计信息展示

3. **处理状态** - 实时展示处理进度
   - 模型加载状态
   - 转录进度
   - 完成状态和结果

### 命令行界面

VoxScribe也提供强大的命令行工具，适合自动化脚本或高级用户使用：

```bash
# 转录音频文件（默认生成带时间戳的文本）
voxscribe-cli your_audio_file.mp3

# 转录并保存为SRT格式
voxscribe-cli your_audio_file.mp3 --format srt --output transcript.srt

# 转录中文音频
voxscribe-cli your_audio_file.mp3 --language chinese

# 使用词级时间戳
voxscribe-cli your_audio_file.mp3 --timestamp-level word
```

### 完整参数列表

```
用法: voxscribe-cli [-h] [--output OUTPUT] [--format {text,srt,vtt,json}]
                [--timestamp-level {sentence,word}] [--model-dir MODEL_DIR]
                [--language LANGUAGE] [--task {transcribe,translate}]
                [--device DEVICE] [--batch-size BATCH_SIZE] 
                [--chunk-length CHUNK_LENGTH]
                audio_file

使用Whisper模型将音频转为带时间轴的文字

位置参数:
  audio_file             音频文件路径

可选参数:
  -h, --help             显示此帮助信息并退出
  --output OUTPUT, -o OUTPUT
                         输出文件路径，默认为标准输出
  --format {text,srt,vtt,json}, -f {text,srt,vtt,json}
                         输出格式: text(纯文本), srt, vtt 或 json
  --timestamp-level {sentence,word}, -t {sentence,word}
                         时间戳级别: sentence(句子级) 或 word(词级)
  --model-dir MODEL_DIR  本地模型目录路径，如果不指定则从HuggingFace下载
  --language LANGUAGE    音频语言，例如'chinese'、'english'等
  --task {transcribe,translate}
                         任务类型：transcribe(转录) 或 translate(翻译成英文)
  --device DEVICE        使用的设备: cpu 或 cuda:0
  --batch-size BATCH_SIZE
                         处理长音频时的批处理大小
  --chunk-length CHUNK_LENGTH
                         处理长音频时的分块长度(秒)
```

## 示例

### 使用网页界面转录视频

1. 启动VoxScribe: `voxscribe`
2. 在浏览器中上传视频文件
3. 选择输出格式为SRT
4. 点击"开始处理"
5. 处理完成后下载SRT字幕文件

### 使用命令行生成SRT字幕文件

```bash
voxscribe-cli lecture.mp4 -f srt -o lecture.srt
```

### 将中文音频翻译成英文

```bash
voxscribe-cli chinese_speech.mp3 --task translate -o english_transcript.txt
```

### 使用本地模型（离线使用）

```bash
# 首先，下载模型到本地
# 然后使用model-dir参数
voxscribe-cli podcast.mp3 --model-dir /path/to/whisper-large-v3-turbo
```

## 注意事项

### 性能考虑

- **GPU加速**: 强烈推荐使用支持CUDA的GPU，可以显著提高处理速度
- **内存使用**: 运行模型需要约4GB内存，处理长音频时可能更多
- **批处理大小**: 增大批处理大小可提高处理速度，但会增加内存使用

### 准确性提示

- **指定语言**: 若明确知道音频语言，指定`--language`参数可提高准确性
- **音频质量**: 背景噪音少、说话清晰的音频通常有更高的识别准确率
- **长音频**: 对于超过10分钟的长音频，推荐使用默认的30秒分块长度

### 常见问题

- **首次运行**: 首次运行时会下载模型文件（约1.7GB），请确保网络连接良好
- **句子边界**: 词级时间戳比句子级更精确，但处理速度较慢
- **特殊标点**: 模型可能会在识别特殊标点符号时出现不一致

## 许可证

MIT

## 致谢

VoxScribe基于OpenAI的[Whisper](https://github.com/openai/whisper)模型和HuggingFace的[Transformers](https://github.com/huggingface/transformers)库。 