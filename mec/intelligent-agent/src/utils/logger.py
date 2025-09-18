class bcolors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    RED = '\033[93m'
    ENDC = '\033[0m'

    @classmethod
    def log_warning_red(cls, message):
        print(cls.RED + message + cls.ENDC)

    @classmethod
    def log_warning_blue(cls, message):
        print(cls.CYAN + message + cls.ENDC)
