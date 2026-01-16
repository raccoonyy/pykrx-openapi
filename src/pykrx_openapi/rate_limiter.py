"""토큰 버킷 알고리즘을 사용한 요청 속도 제한 구현."""

import threading
import time
from functools import wraps


class RateLimiter:
    """
    토큰 버킷 요청 속도 제한기.

    지정된 시간 동안 최대 호출 수를 제한합니다.
    """

    def __init__(self, max_calls: int, period: float):
        """
        요청 속도 제한기를 초기화합니다.

        Args:
            max_calls: 기간 내 허용되는 최대 호출 수
            period: 시간 기간 (초)
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: list[float] = []
        self.lock = threading.Lock()

    def __call__(self, func):
        """
        함수에 요청 속도 제한을 적용하는 데코레이터.

        Args:
            func: 속도 제한을 적용할 함수

        Returns:
            속도 제한이 적용된 래핑된 함수
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                now = time.time()

                # 시간 창 밖의 호출 제거
                self.calls = [c for c in self.calls if c > now - self.period]

                # 제한에 도달했으면 대기
                if len(self.calls) >= self.max_calls:
                    sleep_time = self.period - (now - self.calls[0])
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                        # 대기 후 호출 기록 초기화
                        self.calls = []

                # 이 호출 기록
                self.calls.append(time.time())
                return func(*args, **kwargs)

        return wrapper

    def wait_if_needed(self) -> None:
        """
        요청 속도 제한 초과 시 대기합니다.

        이 메서드는 필요 시 수동으로 호출하여 확인하고 대기할 수 있습니다.
        """
        with self.lock:
            now = time.time()

            # 시간 창 밖의 호출 제거
            self.calls = [c for c in self.calls if c > now - self.period]

            # 제한에 도달했으면 대기
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    self.calls = []

            # 이 호출 기록
            self.calls.append(time.time())
