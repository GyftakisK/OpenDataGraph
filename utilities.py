import subprocess
import ntpath


class DiseaseGraphException(Exception):
    pass


class CommandExecutionFailed(DiseaseGraphException):
    pass


class DiseaseAlreadyInGraph(DiseaseGraphException):
    pass


class NoDiseasesInGraph(DiseaseGraphException):
    def __init__(self):
        super(NoDiseasesInGraph, self).__init__("Graph is empty")


class NotSupportedOboFile(DiseaseGraphException):
    def __init__(self, obo_type: str):
        super(NotSupportedOboFile, self).__init__("Not supported OBO type: {}".format(obo_type))


class ResourceNotInGraph(DiseaseGraphException):
    def __init__(self, resource_name: str):
        super(ResourceNotInGraph, self).__init__("Couldn't find resource \"{}\" in current graph".format(resource_name))


def run_jar(jar_name: str,  args: tuple = ()):
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


def get_filename_from_file_path(path: str):
    """
    Utility function to get filename from path
    :param path: Path to file
    :return: filename
    """
    return ntpath.basename(path)
