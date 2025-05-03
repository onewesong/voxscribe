# VoxScribe 安装指南

## 前提条件

在安装 VoxScribe 音频转文字工具前，请确保您的系统满足以下要求：

1. **Python 环境**：Python 3.8 或更高版本
2. **PyTorch**：建议安装支持CUDA的版本以提高性能
3. **磁盘空间**：模型文件约需1.7GB空间
4. **GPU（推荐）**：虽然可以在CPU上运行，但GPU将大大提高处理速度

## 安装步骤

### 方法一：从本地安装

```bash
# 克隆代码库（如果您已下载代码，可跳过此步骤）
git clone https://github.com/yourusername/voxscribe.git
cd voxscribe

# 安装软件包
pip install -e .
```

### 方法二：直接从GitHub安装

```bash
pip install git+https://github.com/yourusername/voxscribe.git
```

## 验证安装

安装完成后，您可以通过运行以下命令验证安装是否成功：

```bash
# 查看命令行帮助
voxscribe-cli --help

# 启动Web界面
voxscribe
```

## 使用GPU加速

为了获得最佳性能，建议使用支持CUDA的GPU：

1. 确保您已安装支持CUDA的PyTorch版本：
   ```bash
   # 检查PyTorch是否支持CUDA
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. 如果输出为`False`，请重新安装支持CUDA的PyTorch版本：
   ```bash
   # 例如，安装支持CUDA 11.8的PyTorch
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```

## 离线使用

如果您需要在没有互联网连接的环境中使用此工具：

1. 首先，在有网络的环境中下载模型：
   ```python
   from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

   model_id = "openai/whisper-large-v3-turbo"
   model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, use_safetensors=True)
   processor = AutoProcessor.from_pretrained(model_id)

   # 保存到本地目录
   model.save_pretrained("./whisper-large-v3-turbo")
   processor.save_pretrained("./whisper-large-v3-turbo")
   ```

2. 然后将保存的模型目录复制到离线环境，并在命令行或Web界面中指定本地模型路径。

## 常见问题解决

### 内存不足错误

如果遇到内存不足错误，可以尝试以下方法：

1. 减小批处理大小（通过`--batch-size`参数或Web界面中的"批处理大小"设置）
2. 在CPU上运行（通过`--device cpu`参数或Web界面中的"计算设备"设置）
3. 对于特别长的音频，可以先将其分割成较小的片段再处理

### 模型下载速度慢

初次使用时，需要从HuggingFace下载模型文件（约1.7GB）。如果下载速度慢，可以：

1. 使用代理服务器
2. 手动下载模型并指定本地路径
3. 使用HuggingFace的镜像站点

## 更多帮助

如有任何问题或建议，请通过GitHub仓库提交问题报告。 