"""provides a dependency matrix class"""

# pamper pylint stupidity
# pylint: disable=import-error
# from classes.addon import Addon
# from classes.dependency import Dependency
# pylint: enable=import-error

class DependencyMatrix:
    """builds and stores the dependency matrix
       provides several reporting methods
    """

    SCAN_DEPTH = 10

    matrix = []
    addon_list = None


    def __init__(self, addon_list):
        """initialize matrix with list of addons"""
        self.addon_list = addon_list
        self.build_matrix ( self.SCAN_DEPTH )



    def __repr__(self):
        return "DependencyMatrix"


    def recursive_gathering ( self, addon_name, depth ):
        """recursive addon scanner.
           checks dependencies of dependencies
           reduces depth by one on every call, breaks if depth==0
        """

        # Gather all dependencies from current addon
        # regardless of mandatory or optional.
        # dependencies carry a mandatory flag to determine type later.

        # at this point in the recursion, the addon_name is valid.
        dependencies = self.addon_list[addon_name].get_combined_dependencies()

        # check if maximum depth is reached
        print ( f"DEPTH: {depth}   Addon: {addon_name}" )
        if 0 >= depth:
            print ( "scan depth reached." )
            return dependencies

        if 0 == len ( dependencies ):
            print ( "no further dependencies." )
            return dependencies

        # if not: extend list for every dependency listed
        for dependency in dependencies:
            # check if current addon exists.
            # id not, just return an empty list.
            # missing dependencies are checked for later.
            addon_name = dependency.get_name()
            if addon_name in self.addon_list:
                dependencies.extend(
                    self.recursive_gathering ( addon_name, depth - 1)
                )
        return dependencies


    def reduce_dependencies ( self, gathered_list ):
        """reduces gathered list of dependencies
           using the dependency_weight method to sort out dublicates
        """
        dependencies = []

        for dep in gathered_list:
            # check whether already present
            if dep in dependencies:
                index = dependencies.index( dep )
                # check version information for
                # higher demand or conflicts
                merged = dependencies [ index ].merge_version_information ( dep )
                if merged is None:
                    print ("PROBLEM!")
                    raise ValueError ("SNAFU!")
                gathered_list [ index ] = merged
            else:
                # else: add
                dependencies.append ( dep )
        return dependencies



    def build_matrix ( self, scan_depth ):
        """builds the dependency matrix based on the list of addons"""
        print ( "Building Matrix." )
        # for addon_name in self.addon_list.keys():
        #     print ( addon_name )
        #     dependencies = self.recursive_gathering ( addon_name, scan_depth )
        dependencies = self.recursive_gathering ( "AAQ", scan_depth )
        dependencies.sort()
        print ( "All found:" )
        print ( repr ( dependencies ) )

        dependencies = self.reduce_dependencies ( dependencies )
        print ( "Reduced to:" )
        print ( repr ( dependencies ) )
