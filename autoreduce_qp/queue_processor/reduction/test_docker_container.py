import docker
import os

# Return a client configured from environment variables
# The environment variables used are the same as those used by the Docker command-line client
# https://docs.docker.com/engine/reference/commandline/cli/#environment-variables
client = docker.from_env()
args = ["pytest", "tests/"]
container = client.containers.create(
    'autoreduce/mantid',
    command="/bin/sh",
    volumes={
        f'{os.path.expanduser("~")}/.autoreduce/': {
            'bind': f'{os.path.expanduser("~")}/.autoreduce/',
            'mode': 'rw'
        },
        f'{os.path.expanduser("~")}/.autoreduce/dev/data-archive': {
            'bind': '/isis/',
            'mode': 'rw'
        },
        f'{os.path.expanduser("~")}/.autoreduce/dev/reduced-data': {
            'bind': '/instrument/',
            'mode': 'rw'
        }
    },
    tty=True,
    environment=["AUTOREDUCTION_PRODUCTION=1"],
    stdin_open=True,
    detach=True,
    auto_remove=True,
)

# Start the container
container.start()
exe = container.exec_run(cmd=args)
container.stop()