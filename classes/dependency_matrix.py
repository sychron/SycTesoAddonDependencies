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
        dependencies = {
            'mandatory': self.addon_list[addon_name].get_depends_on(),
            'optional':  self.addon_list[addon_name].get_optional_depends_on()
        }

        # check if maximum depth is reached
        print ( f"DEPTH: {depth}   Addon: {addon_name}" )
        if 0 >= depth:
            print ( "scan depth reached." )
            return dependencies

        if 0 == len ( dependencies['mandatory'] ):
            print ( "no further mandatory dependencies." )
        else:
            for dependency in dependencies['mandatory']:
                # check if current addon exists.
                # id not, just return an empty list.
                # missing dependencies are checked for later.
                addon_name = dependency.get_name()
                if addon_name in self.addon_list:
                    result = self.recursive_gathering ( addon_name, depth - 1)
                    dependencies['mandatory'].extend(result['mandatory'])
                    dependencies['optional'].extend(result['optional'])

        if 0 == len ( dependencies['optional'] ):
            print ( "no further optional dependencies." )
        else:
            for dependency in dependencies['optional']:
                # check if current addon exists.
                # id not, just return an empty list.
                # missing dependencies are checked for later.
                addon_name = dependency.get_name()
                if addon_name in self.addon_list:
                    result = self.recursive_gathering ( addon_name, depth - 1)
                    # important: we are recursing checking optional dependencies here
                    # so any mandatory dependency returned must still be listed optional
                    dependencies['optional'].extend(result['mandatory'])
                    dependencies['optional'].extend(result['optional'])

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

        print ( "Mandatory found:" )
        dependencies['mandatory'].sort()
        print ( repr ( dependencies['mandatory'] ) )
        dependencies['mandatory'] = self.reduce_dependencies ( dependencies['mandatory'] )
        print ( "Mandatory reduced to:" )
        print ( repr ( dependencies['mandatory'] ) )


        print ( "Optional found:" )
        dependencies['optional'].sort()
        print ( repr ( dependencies['optional'] ) )
        dependencies['optional'] = self.reduce_dependencies ( dependencies['optional'] )
        print ( "Optional reduced to:" )
        print ( repr ( dependencies['optional'] ) )
