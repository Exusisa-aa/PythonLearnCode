"""摄像头采集线程。

设计要点（见 design.md 决策 5）：
- 采集在独立守护线程中进行，`cv2.VideoCapture.read()` 绝不占用 Tkinter 主线程；
- 帧写入容量为 1 的队列，满则丢弃旧帧，保证界面永远取到最新画面而不是积压的旧图；
- 摄像头打不开时不抛异常，而是把状态置为 failed，让界面降级为"仅从文件选择图片"。
"""

from __future__ import annotations

import queue
import sys
import threading
import time
from typing import Literal

import cv2
import numpy as np

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# 连续读帧失败达到该次数才判定摄像头掉线，避免偶发抖动直接判死
_MAX_CONSECUTIVE_FAILURES = 30

CaptureState = Literal["idle", "starting", "running", "failed"]


def _open_capture(index: int) -> cv2.VideoCapture | None:
    """打开摄像头。Windows 下优先用 DSHOW 后端，它比默认的 MSMF 启动快得多。"""
    backends = [cv2.CAP_DSHOW, cv2.CAP_ANY] if sys.platform == "win32" else [cv2.CAP_ANY]
    for backend in backends:
        capture = cv2.VideoCapture(index, backend)
        if capture.isOpened():
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            return capture
        capture.release()
    return None


class CameraStream:
    """后台持续采集，`read()` 取回最新一帧。"""

    def __init__(self, index: int = 0) -> None:
        self._index = index
        self._queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=1)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._state: CaptureState = "idle"
        self._error: str | None = None
        self._lock = threading.Lock()

    # -- 状态 --------------------------------------------------------------

    @property
    def state(self) -> CaptureState:
        with self._lock:
            return self._state

    @property
    def available(self) -> bool:
        return self.state == "running"

    @property
    def error(self) -> str | None:
        with self._lock:
            return self._error

    def _set_state(self, state: CaptureState, error: str | None = None) -> None:
        with self._lock:
            self._state = state
            self._error = error

    # -- 生命周期 ----------------------------------------------------------

    def start(self) -> None:
        """启动采集线程。重复调用无副作用；失败不抛异常。"""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._set_state("starting")
        self._thread = threading.Thread(target=self._run, name="camera-stream", daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        """停止采集并释放摄像头设备。"""
        self._stop_event.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=timeout)
        self._thread = None
        self._drain()
        if self.state != "failed":
            self._set_state("idle")

    def read(self) -> np.ndarray | None:
        """取回最新一帧；尚无帧可用时返回 None（调用方应保留上一帧显示）。"""
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    # -- 采集循环 ----------------------------------------------------------

    def _drain(self) -> None:
        try:
            while True:
                self._queue.get_nowait()
        except queue.Empty:
            pass

    def _publish(self, frame: np.ndarray) -> None:
        """写入最新帧；队列满则丢掉旧帧再放，保证不留积压。"""
        try:
            self._queue.put_nowait(frame)
            return
        except queue.Full:
            pass
        try:
            self._queue.get_nowait()
        except queue.Empty:
            pass
        try:
            self._queue.put_nowait(frame)
        except queue.Full:
            pass

    def _run(self) -> None:
        capture = _open_capture(self._index)
        if capture is None:
            self._set_state(
                "failed",
                f"无法打开摄像头（设备号 {self._index}）。"
                "可能是设备不存在或被其他程序占用，请改用「选择文件」。",
            )
            return

        self._set_state("running")
        consecutive_failures = 0
        try:
            while not self._stop_event.is_set():
                ok, frame = capture.read()
                if not ok or frame is None:
                    consecutive_failures += 1
                    if consecutive_failures >= _MAX_CONSECUTIVE_FAILURES:
                        self._set_state("failed", "摄像头读取中断，请检查设备连接后重试。")
                        return
                    time.sleep(0.05)
                    continue
                consecutive_failures = 0
                self._publish(frame)
        finally:
            capture.release()


def _self_test() -> None:
    """打开摄像头采集约 1 秒，验证线程、丢帧策略与降级行为。"""
    stream = CameraStream()
    stream.start()

    # 给摄像头一点启动时间
    for _ in range(50):
        if stream.state != "starting":
            break
        time.sleep(0.1)

    if stream.state == "failed":
        print(f"摄像头不可用，已按设计降级（不抛异常）：\n  {stream.error}")
        stream.stop()
        print("stop() 正常返回；界面此时应禁用抓拍、保留文件选择。")
        return

    frames = 0
    deadline = time.time() + 1.0
    while time.time() < deadline:
        frame = stream.read()
        if frame is not None:
            frames += 1
            shape = frame.shape
        time.sleep(0.03)

    stream.stop()
    print(f"摄像头采集正常：1 秒内取到 {frames} 帧，帧尺寸 {shape}")
    print(f"stop() 后状态 = {stream.state}（应为 idle）")


if __name__ == "__main__":
    _self_test()
