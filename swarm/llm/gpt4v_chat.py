import os
import time
import cv2
import base64
import requests
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

from swarm.llm.price import cost_count
from swarm.llm.visual_llm import VisualLLM
from swarm.llm.visual_llm_registry import VisualLLMRegistry
from swarm.utils.log import logger

OLLAMA_COMPLETIONS_URL = "http://localhost:11434/v1/chat/completions"


@VisualLLMRegistry.register('GPT4VChat')
class GPT4VChat(VisualLLM):
    def __init__(
        self,
        model_name: str,
        max_workers: int = 10,
        max_tokens: int = 300,
    ):
        self.model_name = model_name
        self.max_workers = max_workers
        self.max_tokens = max_tokens
        if model_name.startswith("gpt"):
            self.llm_proxy = "https://api.openai.com/v1/chat/completions"
        else:
            self.llm_proxy = OLLAMA_COMPLETIONS_URL
        
        load_dotenv()
        self.OPENAI_API_KEY = os.getenv("MULTIMODE_OPENAI_API_KEY")


    def base64_img(self, file_path: Path) -> str:
        with open(file_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_image

    def base64_video(self, file_path: Path, frame_interval: int = 10) -> list:
        video = cv2.VideoCapture(str(file_path))
        base64_frames = []
        frame_count = 0
        while video.isOpened():
            success, frame = video.read()
            if not success:
                break
            if frame_count % frame_interval == 0:
                _, buffer = cv2.imencode(".jpg", frame)
                base64_frames.append(base64.b64encode(buffer).decode("utf-8"))
            frame_count += 1
        video.release()
        return base64_frames

    def gen(self, task: Optional[str] = None, img: Optional[str] = None) -> str:
        try:
            base64_image = self.base64_img(Path(img))
            api_call = self.prepare_api_call(task, base64_image)
            start_time = time.time()
            response = requests.post(self.llm_proxy, headers=self.get_headers(), json=api_call)
            out = response.json()
            print("image response", out)
            content = out["choices"][0]["message"]["content"]
            logger.info(content)
            end_time = time.time()
            cost_count(out, self.model_name, start_time, end_time)
            return content
        except Exception as error:
            logger.error(f"Error with the request: {error}")
            raise

    def gen_video(self, task: Optional[str] = None, video: Optional[str] = None, frame_interval: int = 30) -> str:
        video_summary = ""
        idx = 0
        task = task or "This is one frame from a video, please summarize this frame."
        base64_frames = self.base64_video(Path(video))
        selected_frames = base64_frames[::frame_interval]

        if len(selected_frames) > 30:
            new_interval = len(base64_frames) // 30
            selected_frames = base64_frames[::new_interval]

        print(f"Totally {len(selected_frames)} would be analyze...")

        idx = 0
        for base64_frame in selected_frames:
            idx += 1
            print(f"Process the {video}, current No. {idx * frame_interval} frame...")

            api_call = self.prepare_api_call(task, base64_frame)
            try:
                start_time = time.time()
                response = requests.post(self.llm_proxy, headers=self.get_headers(), json=api_call)
                end_time = time.time()
                content = response.json()["choices"][0]["message"]["content"]
                current_frame_content = f"Frame {idx}'s content: {content}\n"
                video_summary += current_frame_content
                cost_count(response, self.model_name, start_time, end_time)

                print(current_frame_content)

            except Exception as error:
                logger.error(f"Error with the request: {error}")
                raise

        print(f"video summary: {video_summary}")
        return video_summary

    def prepare_api_call(self, task: str, base64_frame: str) -> dict:
        return {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": task},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_frame}"}},
                    ],
                }
            ],
            "max_tokens": self.max_tokens,
        }

    def get_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.OPENAI_API_KEY}",
        }
