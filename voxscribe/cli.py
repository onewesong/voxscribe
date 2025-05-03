#!/usr/bin/env python
"""
VoxScribe CLI - 命令行音频转文字工具
基于OpenAI的whisper-large-v3-turbo模型
支持生成带时间轴的转录
"""

import argparse
import sys
import json
import torch
from pathlib import Path
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="使用Whisper模型将音频转为带时间轴的文字"
    )
    parser.add_argument(
        "audio_file", 
        type=str, 
        help="音频文件路径"
    )
    parser.add_argument(
        "--output", "-o", 
        type=str, 
        help="输出文件路径，默认为标准输出"
    )
    parser.add_argument(
        "--format", "-f", 
        choices=["text", "srt", "vtt", "json"], 
        default="text",
        help="输出格式: text(纯文本), srt, vtt 或 json"
    )
    parser.add_argument(
        "--timestamp-level", "-t", 
        choices=["sentence", "word"], 
        default="sentence",
        help="时间戳级别: sentence(句子级) 或 word(词级)"
    )
    parser.add_argument(
        "--model-dir", 
        type=str,
        help="本地模型目录路径，如果不指定则从HuggingFace下载"
    )
    parser.add_argument(
        "--language", 
        type=str,
        help="音频语言，例如'chinese'、'english'等"
    )
    parser.add_argument(
        "--task", 
        choices=["transcribe", "translate"], 
        default="transcribe",
        help="任务类型：transcribe(转录) 或 translate(翻译成英文)"
    )
    parser.add_argument(
        "--device", 
        type=str, 
        default="cuda:0" if torch.cuda.is_available() else "cpu",
        help="使用的设备: cpu 或 cuda:0"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="处理长音频时的批处理大小"
    )
    parser.add_argument(
        "--chunk-length",
        type=float,
        default=30,
        help="处理长音频时的分块长度(秒)"
    )
    return parser.parse_args()


def format_timestamp(seconds):
    """将秒数格式化为 HH:MM:SS.mmm 格式"""
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')


def to_srt(chunks):
    """转换为SRT格式"""
    lines = []
    for i, chunk in enumerate(chunks):
        start = format_timestamp(chunk["timestamp"][0])
        end = format_timestamp(chunk["timestamp"][1])
        lines.append(str(i + 1))
        lines.append(f"{start} --> {end}")
        lines.append(chunk["text"].strip())
        lines.append("")
    return "\n".join(lines)


def to_vtt(chunks):
    """转换为VTT格式"""
    lines = ["WEBVTT", ""]
    for i, chunk in enumerate(chunks):
        start = format_timestamp(chunk["timestamp"][0]).replace(',', '.')
        end = format_timestamp(chunk["timestamp"][1]).replace(',', '.')
        lines.append(f"{start} --> {end}")
        lines.append(chunk["text"].strip())
        lines.append("")
    return "\n".join(lines)


def to_text(chunks):
    """转换为纯文本格式，每行一个句子，带时间戳"""
    lines = []
    for chunk in chunks:
        start_time = chunk["timestamp"][0]
        end_time = chunk["timestamp"][1]
        lines.append(f"[{start_time:.2f}s - {end_time:.2f}s] {chunk['text'].strip()}")
    return "\n".join(lines)


def transcribe_audio(args):
    """使用whisper-large-v3-turbo模型转录音频"""
    print(f"正在加载Whisper模型...", file=sys.stderr)
    
    device = args.device
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model_id = args.model_dir or "openai/whisper-large-v3-turbo"
    
    # 加载模型
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True
    )
    model.to(device)
    
    # 加载处理器
    processor = AutoProcessor.from_pretrained(model_id)
    
    # 创建pipeline
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=128,
        chunk_length_s=args.chunk_length,
        batch_size=args.batch_size,
        torch_dtype=torch_dtype,
        device=device,
    )
    
    # 生成转录参数
    generate_kwargs = {}
    if args.language:
        generate_kwargs["language"] = args.language
    if args.task:
        generate_kwargs["task"] = args.task
    
    # 设置时间戳级别
    return_timestamps = True if args.timestamp_level == "sentence" else "word"
    
    print(f"开始转录音频文件: {args.audio_file}...", file=sys.stderr)
    result = pipe(
        args.audio_file, 
        return_timestamps=return_timestamps,
        generate_kwargs=generate_kwargs,
    )
    
    return result


def main():
    """主函数"""
    args = parse_args()
    
    # 检查音频文件是否存在
    if not Path(args.audio_file).exists():
        print(f"错误: 音频文件 '{args.audio_file}' 不存在", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 转录音频
        result = transcribe_audio(args)
        
        # 根据格式输出结果
        if "chunks" in result:
            chunks = result["chunks"]
            if args.format == "text":
                output = to_text(chunks)
            elif args.format == "srt":
                output = to_srt(chunks)
            elif args.format == "vtt":
                output = to_vtt(chunks)
            else:  # json
                output = json.dumps(result, ensure_ascii=False, indent=2)
        else:
            # 如果没有chunks，则输出纯文本
            output = result["text"]
        
        # 输出结果
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"转录结果已保存至: {args.output}", file=sys.stderr)
        else:
            print(output)
            
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 