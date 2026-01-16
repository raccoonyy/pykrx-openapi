"""Tests for rate limiter."""

import time

from pykrx_openapi.rate_limiter import RateLimiter


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_rate_limiter_initialization(self):
        """Test rate limiter can be initialized."""
        limiter = RateLimiter(max_calls=10, period=1.0)
        assert limiter.max_calls == 10
        assert limiter.period == 1.0
        assert limiter.calls == []

    def test_rate_limiter_allows_calls_within_limit(self):
        """Test that calls within limit are allowed."""
        limiter = RateLimiter(max_calls=5, period=1.0)

        call_count = 0

        @limiter
        def test_func():
            nonlocal call_count
            call_count += 1
            return "success"

        # Should allow 5 calls without delay
        for _ in range(5):
            result = test_func()
            assert result == "success"

        assert call_count == 5

    def test_rate_limiter_delays_when_limit_exceeded(self):
        """Test that rate limiter delays when limit is exceeded."""
        limiter = RateLimiter(max_calls=3, period=0.5)

        call_times = []

        @limiter
        def test_func():
            call_times.append(time.time())
            return "success"

        # Make 6 calls - first 3 should be immediate, next 3 should wait
        start_time = time.time()
        for _ in range(6):
            test_func()

        # Total time should be at least 0.5 seconds (one period)
        total_time = time.time() - start_time
        assert total_time >= 0.5

        # Should have 6 calls recorded
        assert len(call_times) == 6

    def test_rate_limiter_resets_after_period(self):
        """Test that rate limiter resets after the time period."""
        limiter = RateLimiter(max_calls=2, period=0.3)

        call_count = 0

        @limiter
        def test_func():
            nonlocal call_count
            call_count += 1

        # Make 2 calls (at limit)
        test_func()
        test_func()

        # Wait for period to expire
        time.sleep(0.35)

        # Should be able to make more calls
        test_func()
        test_func()

        assert call_count == 4

    def test_wait_if_needed_method(self):
        """Test wait_if_needed method."""
        limiter = RateLimiter(max_calls=2, period=0.3)

        # First two calls should be immediate
        limiter.wait_if_needed()
        limiter.wait_if_needed()

        # Third call should wait
        start_time = time.time()
        limiter.wait_if_needed()
        wait_time = time.time() - start_time

        assert wait_time >= 0.3

    def test_rate_limiter_with_different_functions(self):
        """Test that rate limiter works with different functions."""
        limiter = RateLimiter(max_calls=3, period=0.5)

        results = []

        @limiter
        def func_a():
            results.append("a")

        @limiter
        def func_b():
            results.append("b")

        # Both functions should share the same rate limit
        func_a()
        func_a()
        func_a()

        # This should cause a delay since we've hit the limit
        start_time = time.time()
        func_b()
        wait_time = time.time() - start_time

        assert wait_time >= 0.5
        assert results == ["a", "a", "a", "b"]

    def test_rate_limiter_preserves_function_return_value(self):
        """Test that decorated function's return value is preserved."""
        limiter = RateLimiter(max_calls=10, period=1.0)

        @limiter
        def test_func(x, y):
            return x + y

        result = test_func(2, 3)
        assert result == 5

    def test_rate_limiter_preserves_function_signature(self):
        """Test that decorated function's signature is preserved."""
        limiter = RateLimiter(max_calls=10, period=1.0)

        @limiter
        def test_func(a, b, c=10):
            return a + b + c

        # Test with positional and keyword arguments
        assert test_func(1, 2) == 13
        assert test_func(1, 2, c=5) == 8
        assert test_func(a=1, b=2, c=3) == 6

    def test_concurrent_calls_respects_limit(self):
        """Test that concurrent calls respect the rate limit."""
        limiter = RateLimiter(max_calls=2, period=0.5)

        call_times = []

        @limiter
        def test_func():
            call_times.append(time.time())

        # Simulate rapid calls
        start_time = time.time()
        for _ in range(4):
            test_func()

        # Should take at least 0.5 seconds due to rate limiting
        total_time = time.time() - start_time
        assert total_time >= 0.5

        # All calls should have been made
        assert len(call_times) == 4
