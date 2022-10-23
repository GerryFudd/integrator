import time

from algebra.linear.utils import TimingContext, Profiler


def test_with_timing_metrics():
    def other_action():
        time.sleep(0.063)
        with Profiler('baz'):
            time.sleep(0.031)
        # 94ms

    with TimingContext.get() as overall:
        # 63ms
        time.sleep(0.063)
        with Profiler('foo'):
            time.sleep(0.125)
        # 188ms
        with Profiler('bar'):
            other_action()
        # 344ms
        time.sleep(0.062)

    results = overall.get_results()

    assert results.name == 'Overall'
    assert results.duration_ms >= 344
    assert len(results.children) == 2
    foo = results.children[0]
    assert foo.name == 'foo'
    assert foo.duration_ms >= 125
    assert foo.children == []
    bar = results.children[1]
    assert bar.name == 'bar'
    assert bar.duration_ms >= 94
    assert results.duration_ms >= foo.duration_ms + bar.duration_ms
    baz = bar.children[0]
    assert baz.name == 'baz'
    assert 31 <= baz.duration_ms <= bar.duration_ms


def test_re_use_metric_name():
    with TimingContext.get() as overall:
        with Profiler('foo'):
            time.sleep(0.125)
        with Profiler('bar'):
            time.sleep(0.005)
            with Profiler('foo'):
                time.sleep(0.063)
        with Profiler('foo'):
            time.sleep(0.063)

    result = overall.get_results()
    assert len(result.children) == 2
    foo = result.children[0]
    assert foo.name == 'foo'
    assert foo.duration_ms >= 188
    bar = result.children[1]
    assert len(bar.children) == 1
    bar_foo = bar.children[0]
    assert bar_foo.name == 'foo'
    assert bar.duration_ms >= 68
    assert foo.duration_ms + bar.duration_ms <= result.duration_ms < foo.duration_ms + bar.duration_ms + bar_foo.duration_ms


def test_profile_without_context():
    with Profiler('foo') as foo:
        time.sleep(0.25)
    results = foo.get_results()
    assert results.name == 'foo'
    assert results.duration_ms >= 250
