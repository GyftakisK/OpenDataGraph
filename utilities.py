import subprocess


class DiseaseGraphException(Exception):
    pass


class CommandExecutionFailed(DiseaseGraphException):
    pass


def run_jar(jar_name,  args=()):
    """
    Utility function to run a JAR
    :param jar_name: name of the JAR to be run
    :param args: Tuple containing arguments for JAR
    :return: Command output
    """
    command = ['java', '-jar', jar_name]
    command.extend(args)
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        raise CommandExecutionFailed(e.output)

    return result.stdout