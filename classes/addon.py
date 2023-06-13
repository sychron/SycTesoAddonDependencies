"""Provides a class to handle Addon information"""

from pathlib import Path
import chardet

from classes.dependency import Dependency

DATA_DESIGNATOR = "## "
COLOR_MARKER = "|"

# dafuq, this is a real world model, splitting this in "easier" classes
# just would it make more complex.
# pylint: disable=too-many-instance-attributes
class Addon:
    """Process and store addon information"""

    name = ""
    title = ""                  # Title
    description = ""            # Description
    author = ""                 # Author
    contributors = []           # Contributors
    version = ""                # Version
    addon_version = ""          # AddOnVersion
    api_versions = []           # APIVersion
    last_updated = ""           # Last Updated
    saved_variables = False     # SavedVariables
    library = None              # is_library
    depends_on = []             # DependsOn
    optional_depends_on = []    # OptionalDependsOn



    def __init__(self, text):
        """constructor: Parse text information and initialize object"""
        self.parse (text)


    def __repr__(self):
        """return a human readable string resultesentation"""
        result = ""
        template = "{:20s}: {:s}\n"
        result = result + template.format( "Title", self.title)
        result = result + template.format( "Description", self.description)
        result = result + template.format( "Version", self.version)
        result = result + template.format( "Last updated", self.last_updated)
        result = result + template.format( "AddOnVersion", self.addon_version)
        result = result + template.format( "API Versions", ", ".join ( self.api_versions ) )
        result = result + template.format( "Author", self.author)
        result = result + template.format( "Contributors", ", ".join ( self.contributors ) )
        result = result + template.format( "is library", 'yes' if ( self.is_library() ) else 'no' )
        result = result + template.format( "has saved variables", 'yes' if ( self.saved_variables ) else 'no')
        cache = []
        for dep in self.depends_on:
            cache.append(dep.get_name())
        cache.sort()
        result = result + template.format( "Mandatory Dependencies:", ", ".join ( cache ) )
        cache = []
        for dep in self.optional_depends_on:
            cache.append(dep.get_name())
        cache.sort()
        result = result + template.format( "Optional Dependencies:", ", ".join ( cache ) )
        return result



    def clear(self):
        """clear all fields"""
        self.name = ""
        self.title = ""
        self.description = ""
        self.author = ""
        self.contributors = []
        self.version = ""
        self.addon_version = ""
        self.api_versions = []
        self.last_updated = ""
        self.saved_variables = False
        self.library = None
        self.depends_on = []
        self.optional_depends_on = []



    # d8888b.  .d8b.  d8888b. .d8888. d888888b d8b   db  d888b
    # 88  `8D d8' `8b 88  `8D 88'  YP   `88'   888o  88 88' Y8b
    # 88oodD' 88ooo88 88oobY' `8bo.      88    88V8o 88 88
    # 88~~~   88~~~88 88`8b     `Y8b.    88    88 V8o88 88  ooo
    # 88      88   88 88 `88. db   8D   .88.   88  V888 88. ~8~
    # 88      YP   YP 88   YD `8888Y' Y888888P VP   V8P  Y888P


    def parse(self, filename):
        """ Parse addon description and fill data fields
            Previously stored data will be overwritten.
            Return True on success, False on failure
        """
        self.clear()

        # extract name and title from filename
        # might get overwritten by values found in file
        self.name = Path ( filename ).stem
        self.title = self.name

        # Dear pylint. You have to decide on whether to complain about
        # not specifying an encoding in the with clause, or to complain
        # about a regular open to find that encoding.
        # pylint: disable=consider-using-with
        file = open(filename, "rb")
        # pylint: enable=consider-using-with
        rawdata = file.read()
        encoding = chardet.detect(rawdata)['encoding']
        file.close()

        with open( filename, encoding=encoding ) as file:
            lines = file.readlines()

        for line in lines:
            if line.startswith ( DATA_DESIGNATOR ):
                line = line[3:] # remove data designator
                line = line.rstrip() # remove newline
                kvp = line.split ( ": " )
                if 2 == len ( kvp ): # only consider valid lines
                    self.set_data ( kvp[0], kvp[1] )



    def set_data ( self, field, value):
        """evaluate data field title and set data if field is recognized
           - only recognizes official field names by design
           - not tolerant to case errors in data field names by design
        """
        match field.strip():
            case "Title":
                self.set_title ( value )
            case "Author":
                self.set_author ( value )
            case "Contributors":
                self.set_contributors ( value )
            case "Description":
                self.set_description ( value )
            case "Version":
                self.set_version ( value )
            case "AddOnVersion":
                self.set_addon_version ( value )
            case "APIVersion":
                self.set_api_version ( value )
            case "Last Updated":
                self.set_last_updated ( value )
            case "IsLibrary":
                self.set_library ( value )
            case "DependsOn":
                self.set_depends_on_from_string ( value )
            case "OptionalDependsOn":
                self.set_optional_depends_on_from_string ( value)
            case "SavedVariables":
                # If there is any entry in saved variables,
                # set the flag to True
                self.set_saved_variables ( True )
            case _:
                print ( f"unknown data field: {field} in {self.name}" )
                return False





    def strip_color_information ( self, line ):
        """strip embedded color information from a string"""
        while COLOR_MARKER in line:
            # find position of |
            pos = line.find ( COLOR_MARKER)
            # check marker type
            end_marker = "r" == line [ pos+1 ]
            if not end_marker:
                # color marker, strip 8 chars
                line = line [:pos] + line [ pos+8: ]
            else:
                # end marker, strip 2 chars
                line = line [:pos] + line [ pos+2: ]
        return line




    def parse_dependency_string ( self, dependencies_string ):
        """Interpret a  list of dependencies including version information."""
        result = []
        dep_list = dependencies_string.split(" ")
        for dependency_string in dep_list:
            result.append (
                dependency = Dependency (dependency_string)
            )
        return result



    #  d888b  d88888b d888888b           dD      .d8888. d88888b d888888b
    # 88' Y8b 88'     `~~88~~'          d8'      88'  YP 88'     `~~88~~'
    # 88      88ooooo    88            d8'       `8bo.   88ooooo    88
    # 88  ooo 88~~~~~    88           d8'          `Y8b. 88~~~~~    88
    # 88. ~8~ 88.        88          d8'         db   8D 88.        88
    #  Y888P  Y88888P    YP         C8'          `8888Y' Y88888P    YP


    def get_name ( self ):
        """Return the addon's name"""
        return self.name
    def set_name ( self, value):
        """set this addon's name"""
        self.name = value


    def get_title ( self ):
        """Return the addon's title"""
        return self.title
    def set_title ( self, value):
        """set this addon's title stripping color information."""
        self.title = self.strip_color_information (value)



    def get_author ( self ):
        """Return the addon's author"""
        return self.author
    def set_author ( self, value):
        """set this addon's author stripping color information."""
        self.author = self.strip_color_information (value)



    def get_description ( self ):
        """Return the addon's description"""
        return self.title
    def set_description ( self, value):
        """set this addon's description"""
        self.description = value



    def get_version ( self ):
        """Return the addon's version"""
        return self.version
    def set_version ( self, value):
        """set this addon's version"""
        self.version = value



    def get_addon_version ( self ):
        """Return the addon's AddOnVersion"""
        return self.addon_version
    def set_addon_version ( self, value):
        """set this addon's AddOnVersion"""
        self.addon_version = value



    def get_last_updated ( self ):
        """Return the addon's last update date"""
        return self.last_updated
    def set_last_updated ( self, value):
        """set this addon's last update date"""
        self.last_updated = value



    def has_saved_variables ( self ):
        """Return whether the addon declared saved variables"""
        return self.saved_variables
    def set_saved_variables ( self, value):
        """set this addon's saved variables flag"""
        self.saved_variables = value



    def get_api_versions ( self ):
        """Return addon's api versions array"""
        return self.api_versions
    def set_api_version ( self, value):
        """Populate this addon's api versions array from string"""
        self.api_versions = value.split ( " " )
    def add_api_version ( self, value):
        """Add an API version to this addon's api versions array"""
        self.api_versions.append ( value )



    def get_contributors ( self ):
        """Return addon's contributors array"""
        return self.contributors
    def set_contributors ( self, value):
        """Populate this addon's api versions array from string"""
        self.contributors = []
        for contributor in value.split ( " " ):
            self.add_contributor ( contributor )
    def add_contributor ( self, value):
        """Add a contributor to this addon's api contributors array"""
        self.contributors.append ( self.strip_color_information ( value ) )



    def is_library(self):
        """ Try to determine whether this addon is a library
            Return True if library, False if not or unsure
            Only do determination on first call and store value for later calls
        """
        # only run name check if library flag is not yet set
        if self.library is None:
            self.library = False
            # check name
            name = self.title.lower()
            if name.startswith ( "lib" ):
                self.library = True
        return self.library
    def set_library ( self, value ):
        """set this addon's library flag"""
        self.library = "true" == value.lower()

    def get_depends_on ( self ):
        """Return addon's dependencies array"""
        return self.depends_on
    def set_depends_on_from_string ( self, value):
        """Populate this addon's dependencies array from string"""
        self.depends_on = []
        for dep in value.split ( " " ):
            self.add_depends_on_from_string ( dep )
    def add_depends_on_from_string ( self, value):
        """Add a dependency to this addon's dependencies  array"""
        dependency = Dependency( value )
        if dependency is not None:
            self.depends_on.append ( dependency )

    def get_optional_depends_on ( self ):
        """Return addon's optional dependencies array"""
        return self.optional_depends_on
    def set_optional_depends_on_from_string ( self, value):
        """Populate this addon's optional dependencies array from string"""
        self.optional_depends_on = []
        for dep in value.split ( " " ):
            self.add_optional_depends_on_from_string ( dep )
    def add_optional_depends_on_from_string ( self, value):
        """Add an optional dependency to this addon's optional dependencies array"""
        dependency = Dependency( value )
        if dependency is not None:
            self.optional_depends_on.append ( dependency )

    def get_combined_dependencies ( self ):
        """get mandatory and optional dependencies in one list"""
        return self.get_depends_on () + self.get_optional_depends_on()