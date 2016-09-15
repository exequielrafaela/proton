VERSION = "repvernumber"

# Definition of directories and files
CONFIG_DIR = "./conf/"
RESULTS_DIR = "./results/"
AUDIOFILES_DIR = "./audiofiles/"
LOGS_DIR = "./logs/"
RECORDED_CALLS_DIR = "./recorded_calls/"

CONFIG_FILE_PATH = CONFIG_DIR + "artemisa.conf"
BEHAVIOUR_FILE_PATH = CONFIG_DIR + "behaviour.conf"
ACTIONS_FILE_PATH = CONFIG_DIR + "actions.conf"
EXTENSIONS_FILE_PATH = CONFIG_DIR + "extensions.conf"
SERVERS_FILE_PATH = CONFIG_DIR + "servers.conf"

NUMBER_OF_OPTIONS_MATCHES = 3 # Maximum number of different extension that an OPTIONS message can "target" after being considered a scanning attack