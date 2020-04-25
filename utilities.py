import subprocess
import ntpath

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
        result = subprocess.run(command)
    except subprocess.CalledProcessError as e:
        raise CommandExecutionFailed(e.output)

    return result.stdout


def get_filename_from_file_path(path):
    """
    Utility function to get filename from path
    :param path: Path to file
    :return: filename
    """
    return ntpath.basename(path)
