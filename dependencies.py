"""Check dependencies in ESO addon folder

    place in a directory next to ESOs live directory
    (or place it anywhere and change the ADDON_ROOT line)
    run with python 3.
    takes no parameters and prints it output to the command line
    """
from os import listdir
from os.path import exists, join
from pathlib import Path

VERBOSITY = 2
ADDON_ROOT = join ( "..", "live", "Addons" )
DATA_DESIGNATOR = "## "

def log ( level, text, linebreak  = True ):
    """Print output depending on set verbosity."""
    if level <= VERBOSITY:
        if linebreak:
            print ( text )
        else:
            print ( text, end = " " )

def find_valid_addon_description_files ( root_dir ):
    """Scan addon directory to find all addon description files."""
    log ( 1, "Gathering list of valid addons" )
    addon_descriptions = []
    for directory in listdir ( root_dir  ):
        description = join ( root_dir, directory, f"{directory}.txt" )
        log ( 3, description, False )
        if exists ( description ):
            addon_descriptions.append ( description )
            log ( 3, "✔" )
        else:
            log ( 3, "✘" )
    return addon_descriptions

def parse_addon_description ( description_file ):
    """Read one addon description file and compile the addon information in a dict. """
    log ( 2, f"parsing addon info for {description_file}" )
    addon_data = {
        "name": Path ( description_file ).stem,
        "Title": Path ( description_file ).stem,
    }
    with open( description_file, encoding=None ) as file:
        lines = file.readlines()
    for line in lines:
        if line.startswith ( DATA_DESIGNATOR ):
            line = line[3:] # remove data designator
            line = line.rstrip() # remove newline
            kvp = line.split ( ": " )
            if 2 == len ( kvp ): # only consider valid lines
                addon_data [ kvp [0] ] = kvp [ 1 ]
    return addon_data

def is_library ( addon_data ):
    """try to determine whether an addon is a library or not."""
    result = False
    # check library tag
    if "is_library" in addon_data:
        result = addon_data [ "is_library" ] == "true"
    # check name
    name = str ( addon_data ["name"] ).lower()
    if name.startswith ( "lib" ):
        result = True
    if result:
        name = addon_data [ "name" ]
        log ( 3, f"{name} is a library" )
    return result

def read_addon_info_files ( description_files ):
    """open and parse every addon description file, compiling a dict of dicts."""
    log ( 1, "parsing addon info files")
    addon_info = {}
    for description_file in description_files:
        addon_data  = parse_addon_description ( description_file )
        usedby_uses_value = {
            "mandatory": {},
            "optional": {},
            "mandatoryMissing": {},
            "optionalMissing": {}
        }
        addon_data [ "usedBy" ] = usedby_uses_value
        addon_data [ "uses" ] = usedby_uses_value
        addon_data [ "markedAsLibrary"] = is_library ( addon_data )
        addon_name = addon_data [ "name" ]
        addon_info [ addon_name ] = addon_data
    return addon_info


def parse_dependency_string ( dep_string ):
    """Interpret a  list of dependencies including version information and return a dict."""
    dependency_info = {}
    dependencies = dep_string.split(" ")
    for dependency in dependencies:
        data = dependency.split(">=") if ">=" in dependency else dependency.split("<=")
        dependency_info [ dependency ] = {
            "name": data[0],
            "greater_than": data[1] if ">=" in dependency else "",
            "lower_than": data[1] if "<=" in dependency else ""
        }
    return dependency_info

def build_dependency_matrix ( addons ):
    """Note which addon is using/used by which other addon."""
    log ( 1, "building dependency matrix")
    for name in addons:
        log ( 3, name)
        if "DependsOn" in addons [ name ]:
            mandatory = parse_dependency_string ( addons [ name ] [ "DependsOn" ] )
            for lib, spec in mandatory.items(): # pylint: disable=unused-variable
                if lib in addons:
                    # add entry to addon uses
                    addons [name]["uses"]["mandatory"][lib] = mandatory [lib]
                    # add entry to libs usedBy
                    addons [lib]["usedBy"]["mandatory"][name] = { "name": name }
                else:
                    # add entry to addon uses
                    addons [name]["uses"]["mandatoryMissing"][lib] = mandatory [lib]
        if "OptionalDependsOn" in addons [ name ]:
            optional  = parse_dependency_string ( addons [ name ] [ "OptionalDependsOn" ] )
            for lib, spec in optional.items():
                if lib in addons:
                    # add entry to addon uses
                    addons [name]["uses"]["optional"][lib] = optional [lib]
                    # add entry to libs usedBy
                    addons [lib]["usedBy"]["optional"][name] = { "name": name }
                else:
                    # add entry to addon uses
                    addons [name]["uses"]["optionalMissing"][lib] = optional [lib]

def print_dependency_matrix( addons ):
    """Dump dependency matrix to screen."""
    for name in addons:
        print ( addons[name]["Title"] )
        if "uses" in addons [ name ]:
            if "mandatory" in addons [name]["uses"]:
                if 0 < len ( addons [name]["uses"]["mandatory"] ):
                    print ("    Satisfied mandatory dependencies: ", end="")
                    for dep in addons [name]["uses"]["mandatory"]:
                        print ( dep, end=", " )
                    print()
            if "optional" in addons [name]["uses"]:
                if 0 < len ( addons [name]["uses"]["optional"] ):
                    print ("    Satisfied optional  dependencies: ", end="")
                    for dep in addons [name]["uses"]["optional"]:
                        print ( dep, end=", " )
                    print()
        if "usedBy" in addons [ name ]:
            if "mandatory" in addons [name]["usedBy"]:
                if 0 < len ( addons [name]["usedBy"]["mandatory"] ):
                    print ("    mandatory dependency for        : ", end="")
                    for dep in addons [name]["usedBy"]["mandatory"]:
                        print ( dep, end=", " )
                    print()
            if "optional" in addons [name]["usedBy"]:
                if 0 < len ( addons [name]["usedBy"]["optional"] ):
                    print ("    optional  dependency for        : ", end="")
                    for dep in addons [name]["usedBy"]["optional"]:
                        print ( dep, end=", " )
                    print()
    print()

def print_complications ( addons ):
    """Print compiled complications to screen."""
    print ("Unsatisfied mandatory dependencies:")
    for name in addons:
        if "uses" in addons [ name ]:
            if "mandatoryMissing" in addons [name]["uses"]:
                if 0 < len ( addons [name]["uses"]["mandatoryMissing"] ):
                    print (
                        "* ",
                        addons[name]["Title"],
                        ": ",
                        ", ".join( addons [name]["uses"]["mandatoryMissing"] )
                    )
    print()
    print ("Unsatisfied optional  dependencies:")
    for name in addons:
        if "uses" in addons [ name ]:
            if "optionalMissing" in addons [name]["uses"]:
                if 0 < len ( addons [name]["uses"]["optionalMissing"] ):
                    print (
                        "* ",
                        addons[name]["Title"],
                        ": ",
                        ", ".join( addons [name]["uses"]["optionalMissing"] )
                    )
    print()
    print ("assumed libraries not used by any other addon:")
    for name in addons:
        if addons[name]["markedAsLibrary"]:
            used = False
            if "usedBy" in addons [ name ]:
                if "mandatory" in addons [name]["usedBy"]:
                    if 0 < len ( addons [name]["usedBy"]["mandatory"] ):
                        used = True
                if "optional" in addons [name]["usedBy"]:
                    if 0 < len ( addons [name]["usedBy"]["optional"] ):
                        used = True
            if not used:
                print ( "* ", addons[name]["Title"] )
    print (
        "[please be aware that addons starting with 'lib' are detected as library, ",
        "even if they might not be a library]"
    )
    print()

def main():
    """Check dependencies in ESO addon folder."""
    file_list = find_valid_addon_description_files ( ADDON_ROOT )
    addon_info = read_addon_info_files ( file_list )
    build_dependency_matrix ( addon_info )
    print_dependency_matrix ( addon_info )
    print_complications ( addon_info )

if __name__ == "__main__":
    main()
