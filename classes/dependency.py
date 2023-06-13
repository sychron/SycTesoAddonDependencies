"""Provide a class to store and process one dependency"""

class Dependency:
    """Process and store a single dependency"""

    DEPENDENCY_MANDAOTRY    = 0
    DEPENDENCY_OPTIONAL     = 1

    name = ""
    min_version = None
    max_version = None
    dependency_type = DEPENDENCY_MANDAOTRY



    def __init__(self, dependency_string, dependency_type=DEPENDENCY_MANDAOTRY):
        """Constructor. Init fields based on dependency string"""
        self.dependency_type = dependency_type
        self.parse_dependency_string ( dependency_string )



    def __repr__(self):
        result = f"{self.name}"
        if self.min_version is not None:
            result = result + f" Version >= {self.min_version}"
        if self.max_version is not None:
            result = result + f" Version <= {self.max_version}"
        return result



    def clear(self):
        """clear instance fields"""
        self.name = ""
        self.min_version = None
        self.max_version = None
        self.dependency_type = Dependency.DEPENDENCY_MANDAOTRY



    def parse_dependency_string (self, dependency_string ):
        """Interpret a  list of dependencies including version information and return a dict."""
        # defaults
        self.clear()
        self.name = dependency_string
        # version information given
        if ">=" in dependency_string:
            data = dependency_string.split(">=")
            self.name = data[0]
            self.min_version = data[1]
        if "<=" in dependency_string:
            data = dependency_string.split("<=")
            self.name = data[0]
            self.max_version = data[1]



    #  .o88b. db   db d88888b  .o88b. db   dD d888888b d8b   db  d888b
    # d8P  Y8 88   88 88'     d8P  Y8 88 ,8P'   `88'   888o  88 88' Y8b
    # 8P      88ooo88 88ooooo 8P      88,8P      88    88V8o 88 88
    # 8b      88~~~88 88~~~~~ 8b      88`8b      88    88 V8o88 88  ooo
    # Y8b  d8 88   88 88.     Y8b  d8 88 `88.   .88.   88  V888 88. ~8~
    #  `Y88P' YP   YP Y88888P  `Y88P' YP   YD Y888888P VP   V8P  Y888P



    def merge_version_information (self, other):
        """merges the version information of two dependenies
           - name must match
           - type must match
           checks for contradictions and returns None on conflict
        """
        if self.name != other.get_name():
            raise ValueError ( "dependency names don't match" )
        if self.dependency_type != other.dependency_type:
            raise ValueError ( "dependency types don't match" )

        rmin = None
        if self.min_version is not None:
            if other.min_version is not None:
                # cannot use min, this might be strings
                if self.min_version <= other.min_version:
                    rmin = self.min_version
                else:
                    rmin = other.min_version
            else:
                # other min_version is None, use own
                rmin = self.min_version
        else:
            if other.min_version is not None:
                # own min_version is None, use other
                rmin = other.min_version

        # same for max version
        rmax = None
        if self.max_version is not None:
            if other.max_version is not None:
                # cannot use max, this might be strings
                if self.max_version >= other.max_version:
                    rmax = self.max_version
                else:
                    rmax = other.max_version
            else:
                # other min_version is None, use own
                rmax = self.max_version
        else:
            if other.min_version is not None:
                # own min_version is None, use other
                rmax = other.max_version

        #check for contraditions:
        if rmin is not None and rmax is not None:
            if rmin > rmax:
                return None

        # update own version info and return object
        self.min_version = rmin
        self.max_version = rmax
        return self



    #  d888b  d88888b d888888b           dD      .d8888. d88888b d888888b
    # 88' Y8b 88'     `~~88~~'          d8'      88'  YP 88'     `~~88~~'
    # 88      88ooooo    88            d8'       `8bo.   88ooooo    88
    # 88  ooo 88~~~~~    88           d8'          `Y8b. 88~~~~~    88
    # 88. ~8~ 88.        88          d8'         db   8D 88.        88
    #  Y888P  Y88888P    YP         C8'          `8888Y' Y88888P    YP



    def get_name(self):
        """return this dependency's name"""
        return self.name
    def set_name(self, value):
        """set this dependency's name"""
        self.name = value

    def is_mandatory ( self ):
        """returns whether a dependency is mandatory"""
        return self.dependency_type == Dependency.DEPENDENCY_MANDAOTRY



    # .d8888.  .d88b.  d8888b. d888888b d888888b d8b   db  d888b
    # 88'  YP .8P  Y8. 88  `8D `~~88~~'   `88'   888o  88 88' Y8b
    # `8bo.   88    88 88oobY'    88       88    88V8o 88 88
    #   `Y8b. 88    88 88`8b      88       88    88 V8o88 88  ooo
    # db   8D `8b  d8' 88 `88.    88      .88.   88  V888 88. ~8~
    # `8888Y'  `Y88P'  88   YD    YP    Y888888P VP   V8P  Y888P

    def __eq__(self, other):
        return ((self.name.lower()) ==
                (other.get_name().lower()))

    def __lt__(self, other):
        return ((self.name.lower() ) <
                (other.get_name().lower()))



