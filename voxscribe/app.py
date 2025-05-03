#!/usr/bin/env python
"""
VoxScribe 网页应用 - 优雅的音频转文字工具
基于OpenAI的whisper-large-v3-turbo模型
支持生成带时间轴的转录
"""

import os
import tempfile
import streamlit as st
import torch
from pathlib import Path
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from voxscribe.cli import to_text, to_srt, to_vtt


def main():
    """VoxScribe 网页应用主函数"""
    
    st.set_page_config(
        page_title="VoxScribe | 声音抄写员",
        page_icon="🎤",
        layout="wide",
    )
    
    st.title("🎤 VoxScribe | 声音抄写员")
    st.markdown("使用 OpenAI 的 whisper-large-v3-turbo 模型将音频转换为带时间轴的文字")
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # 输出格式
        output_format = st.selectbox(
            "输出格式",
            options=["text", "srt", "vtt", "json"],
            format_func=lambda x: {
                "text": "文本（带时间戳）",
                "srt": "SRT 字幕",
                "vtt": "VTT 字幕",
                "json": "JSON"
            }.get(x, x),
            help="选择转录结果的输出格式"
        )
        
        # 时间戳级别
        timestamp_level = st.selectbox(
            "时间戳级别",
            options=["sentence", "word"],
            format_func=lambda x: {
                "sentence": "句子级",
                "word": "词级"
            }.get(x, x),
            help="选择时间戳的级别"
        )
        
        # 语言选择
        language = st.selectbox(
            "音频语言",
            options=[None, "chinese", "english", "japanese", "german", "french", "spanish", "korean", "russian"],
            format_func=lambda x: "自动检测" if x is None else x.capitalize(),
            help="指定音频语言可以提高准确度"
        )
        
        # 任务类型
        task = st.selectbox(
            "任务类型",
            options=["transcribe", "translate"],
            format_func=lambda x: {
                "transcribe": "转录（保持原语言）",
                "translate": "翻译（翻译成英文）"
            }.get(x, x),
            help="选择转录或翻译任务"
        )
        
        # 高级设置折叠
        with st.expander("🔧 高级设置"):
            # 设备选择
            if torch.cuda.is_available():
                device_options = ["cuda:0", "cpu"]
                device_default = "cuda:0"
            else:
                device_options = ["cpu"]
                device_default = "cpu"
            
            device = st.selectbox(
                "计算设备",
                options=device_options,
                index=device_options.index(device_default),
                help="选择用于处理的设备"
            )
            
            # 批处理大小
            batch_size = st.slider(
                "批处理大小",
                min_value=1,
                max_value=32,
                value=16,
                help="处理长音频时的批处理大小"
            )
            
            # 分块长度
            chunk_length = st.slider(
                "分块长度（秒）",
                min_value=5,
                max_value=60,
                value=30,
                help="处理长音频时的分块长度"
            )
            
            # 本地模型路径
            model_dir = st.text_input(
                "本地模型路径（可选）",
                value="",
                help="输入本地模型目录路径，为空则从HuggingFace下载"
            )
        
        st.markdown("---")
        st.markdown("📝 **提示**: 上传音频文件后，处理可能需要一些时间，请耐心等待。")
        
        if torch.cuda.is_available():
            st.success("✅ 已检测到GPU，处理速度将更快")
        else:
            st.warning("⚠️ 未检测到GPU，将使用CPU处理（较慢）")
    
    # 主界面 - 文件上传
    uploaded_file = st.file_uploader("上传音频文件", type=["mp3", "wav", "m4a", "ogg", "flac", "mp4"])
    
    if uploaded_file is not None:
        # 显示文件信息
        st.write(f"文件名: **{uploaded_file.name}**")
        
        # 文件处理按钮
        process_button = st.button("开始处理", type="primary")
        
        if process_button:
            # 显示处理状态
            with st.status("正在处理中...", expanded=True) as status:
                st.write("正在保存上传的文件...")
                # 保存上传的文件到临时目录
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    audio_path = tmp_file.name
                
                try:
                    st.write("正在加载模型...")
                    # 设置模型参数
                    model_id = model_dir if model_dir else "openai/whisper-large-v3-turbo"
                    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
                    
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
                    st.write("正在设置转录管道...")
                    pipe = pipeline(
                        "automatic-speech-recognition",
                        model=model,
                        tokenizer=processor.tokenizer,
                        feature_extractor=processor.feature_extractor,
                        max_new_tokens=128,
                        chunk_length_s=chunk_length,
                        batch_size=batch_size,
                        torch_dtype=torch_dtype,
                        device=device,
                    )
                    
                    # 准备生成参数
                    generate_kwargs = {}
                    if language:
                        generate_kwargs["language"] = language
                    if task:
                        generate_kwargs["task"] = task
                    
                    # 设置时间戳级别
                    return_timestamps = True if timestamp_level == "sentence" else "word"
                    
                    # 开始转录
                    st.write("正在转录音频...")
                    result = pipe(
                        audio_path, 
                        return_timestamps=return_timestamps,
                        generate_kwargs=generate_kwargs,
                    )
                    
                    # 更新状态
                    status.update(label="✅ 处理完成!", state="complete")
                    
                    # 删除临时文件
                    os.unlink(audio_path)
                    
                    # 输出结果
                    st.subheader("转录结果")
                    
                    # 根据格式输出结果
                    if "chunks" in result:
                        chunks = result["chunks"]
                        if output_format == "text":
                            output_text = to_text(chunks)
                            st.text_area("文本结果（带时间戳）", output_text, height=400)
                        elif output_format == "srt":
                            srt_text = to_srt(chunks)
                            st.text_area("SRT 字幕", srt_text, height=400)
                            # 提供下载按钮
                            st.download_button(
                                label="下载 SRT 文件",
                                data=srt_text,
                                file_name=f"{Path(uploaded_file.name).stem}.srt",
                                mime="text/plain"
                            )
                        elif output_format == "vtt":
                            vtt_text = to_vtt(chunks)
                            st.text_area("VTT 字幕", vtt_text, height=400)
                            # 提供下载按钮
                            st.download_button(
                                label="下载 VTT 文件",
                                data=vtt_text,
                                file_name=f"{Path(uploaded_file.name).stem}.vtt",
                                mime="text/plain"
                            )
                        else:  # json
                            import json
                            json_text = json.dumps(result, ensure_ascii=False, indent=2)
                            st.json(result)
                            # 提供下载按钮
                            st.download_button(
                                label="下载 JSON 文件",
                                data=json_text,
                                file_name=f"{Path(uploaded_file.name).stem}.json",
                                mime="application/json"
                            )
                    else:
                        # 如果没有chunks，则输出纯文本
                        st.text_area("转录结果", result["text"], height=400)
                    
                    # 显示简要统计
                    if "chunks" in result:
                        st.subheader("统计信息")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("片段数量", len(result["chunks"]))
                        with col2:
                            total_duration = result["chunks"][-1]["timestamp"][1] if result["chunks"] else 0
                            st.metric("总时长 (秒)", f"{total_duration:.2f}")
                        with col3:
                            total_words = sum(len(chunk["text"].split()) for chunk in result["chunks"])
                            st.metric("总词数 (估计)", total_words)
                
                except Exception as e:
                    status.update(label="❌ 处理失败", state="error")
                    st.error(f"发生错误: {str(e)}")
    else:
        st.info("👆 请上传音频文件以开始处理")
    
    # 页脚
    st.markdown("---")
    st.markdown(
        "🧠 基于 [OpenAI Whisper large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo) 模型 | "
        "💡 支持 99 种语言的音频识别和转录"
    )


if __name__ == "__main__":
    main() 