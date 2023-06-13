"""Check dependencies in ESO addon folder

    place in a directory next to ESOs live directory
    (or place it anywhere and change the ADDON_ROOT line)
    run with python 3.
    takes no parameters and prints it output to the command line
    """

from os import listdir
from os.path import exists, join

# pamper pylint stupidity
# pylint: disable=import-error
from classes.addon import Addon
from classes.dependency_matrix import DependencyMatrix
# pylint: enable=import-error

VERBOSITY = 5


#ADDON_ROOT = join ( "..", "live", "Addons" )
ADDON_ROOT = "C:\\Users\\sychr\\Documents\\Elder Scrolls Online\\live\\Addons"



def find_valid_addon_description_files ( root_dir ):
    """Scan addon directory to find all addon description files."""
    addon_descriptions = []
    for directory in listdir ( root_dir  ):
        description = join ( root_dir, directory, f"{directory}.txt" )
        if exists ( description ):
            addon_descriptions.append ( description )
    return addon_descriptions



def read_addon_info_files ( description_files ):
    """open and parse every addon description file, compiling a dict of dicts."""
    addon_info = {}
    for description_file in description_files:
        addon = Addon ( description_file )
        if addon is not None:
            addon_info [addon.get_name()] =  addon
    return addon_info



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
    matrix = DependencyMatrix ( addon_info )

    #print_dependency_matrix ( addon_info )
    #print_complications ( addon_info )

if __name__ == "__main__":
    main()
