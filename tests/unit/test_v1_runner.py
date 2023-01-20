from src.command_runner import CommandRunnerV1
from src.models import RequestV1, Command

def test_foo():
    req = RequestV1(
        env={'foo': 'bar'},
        commands=[
            Command(
                title='foo',
                slug='foo',
                command='echo $foo',
                check=False
            )
        ]
    )
    runner = CommandRunnerV1(req)


    assert 'bar' in runner.run()[0].output

def test_check():
    req = RequestV1(
        env={'foo': 'bar'},
        commands=[
            Command(
                title='foo',
                slug='foo',
                command='echo fail; exit 1',
                check=True
            ),
            Command(
                title='non-critical',
                slug='foo',
                command='echo bar',
                check=False,
            ),
            Command(
                title='critical',
                slug='foo',
                command='echo foo',
                check=False,
                run_on_fail=True
            )
        ]
    )
    runner = CommandRunnerV1(req)

    o = runner.run()

    assert len(o) == 2
    assert 'foo' in o[1].output