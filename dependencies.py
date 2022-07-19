import os.path
from os.path import exists
from pathlib import Path

import pprint   # for debugging
pp=pprint.PrettyPrinter();

VERBOSITY = 1
ADDON_ROOT = os.path.join ( "..", "live", "Addons" )
DATA_DESIGNATOR = "## "

def log ( level, text, linebreak  = True ):
    if ( level <= VERBOSITY ): 
        if ( linebreak ):
            print ( text )
        else: 
            print ( text, end = " " )
    
def findValidAddonDescriptionFiles ( rootDir ):
    log ( 1, "Gathering list of valid addons" )
    addonDescriptions = []
    for directory in os.listdir ( rootDir  ):
        description = os.path.join ( rootDir, directory, (directory + ".txt") )
        log ( 3, description, False )
        if exists ( description ):
            addonDescriptions.append ( description )
            log ( 3, "✔" )                
        else:
            log ( 3, "✘" )
    return addonDescriptions                

def parseAddonDescription ( descriptionFile ):
    log ( 2, "parsing addon info for " +  descriptionFile )
    addonData = {}
    addonData [ "name" ] = Path ( descriptionFile ).stem
    addonData [ "Title" ] = Path ( descriptionFile ).stem
    with open( descriptionFile ) as FILE:
        lines = FILE.readlines()            
    for line in lines:
        if line.startswith ( DATA_DESIGNATOR ):
            line = line[3:] # remove data designator
            line = line.rstrip() # remove newline
            kvp = line.split ( ": " )
            if ( 2 == len ( kvp )): # only consider valid lines
                addonData [ kvp [0] ] = kvp [ 1 ]            
    return addonData

def isLibrary ( addonData ):
    isLibrary = False
    # check library tag
    if ( "isLibrary" in addonData ):
        isLibrary = addonData [ "isLibrary" ] == "true"
    # check name
    name = str ( addonData ["name"] ).lower()  
    if name.startswith ( "lib" ):
        isLibrary = True
    if isLibrary:
        log ( 3, addonData [ "name" ] + " is a library" )            
    return isLibrary
    
def readAddonInfoFiles ( descriptionFiles ):
    log ( 1, "parsing addon info files")    
    addonInfo = {}
    for descriptionFile in descriptionFiles:
        addonData  = parseAddonDescription ( descriptionFile )
        addonData [ "usedBy" ] = { "mandatory": {}, "optional": {}, "mandatoryMissing": {}, "optionalMissing": {} }
        addonData [ "uses" ] = { "mandatory": {}, "optional": {}, "mandatoryMissing": {}, "optionalMissing": {} }        
        addonData [ "markedAsLibrary"] = isLibrary ( addonData )
        addonName = addonData [ "name" ]
        addonInfo [ addonName ] = addonData
        
    return addonInfo
        
            
def processDependencyString ( depString ):
    dependencyInfo = {}
    dependencies = depString.split(" ")
    for dependency in dependencies:
        lowerThan = ""
        greaterThan = ""
        if ">=" in dependency:
            data = dependency.split ( ">=" )
            greaterThan = data [1]
            dependency = data [0]
        if "<=" in dependency:
            data = dependency.split ( "<=" )
            lowerThan = data [1]
            dependency = data [0]
        dependencyInfo [ dependency ] = { "name": dependency, "greaterThan": greaterThan, "lowerThan": lowerThan}
    return dependencyInfo

def buildDependencyMatrix ( addons ):
    log ( 1, "building dependency matrix")
    for name in addons:                
        log ( 1, name)
        if "DependsOn" in addons [ name ]:
            mandatoryString = addonInfo [ name ] [ "DependsOn" ]
            mandatory = processDependencyString ( mandatoryString )           
            for lib in mandatory:
                print (lib)
                present = lib in addons;
                if present:
                    # add entry to addon uses
                    addons [name]["uses"]["mandatory"][lib] = mandatory [lib]
                    # add entry to libs usedBy
                    addons [lib]["usedBy"]["mandatory"][name] = { "name": name }
                else:
                    # add entry to addon uses
                    addons [name]["uses"]["mandatoryMissing"][lib] = mandatory [lib]
        if "OptionalDependsOn" in addonInfo [ name ]:
            optionalString = addonInfo [ name ] [ "OptionalDependsOn" ]
            optional  = processDependencyString ( optionalString )           
            for lib in optional:
                print (lib)
                present = lib in addons;
                if present:
                    # add entry to addon uses
                    addons [name]["uses"]["optional"][lib] = optional [lib]                
                    # add entry to libs usedBy
                    addons [lib]["usedBy"]["optional"][name] = { "name": name }
                else:                     
                    # add entry to addon uses
                    addons [name]["uses"]["optionalMissing"][lib] = optional [lib]                

def printDependencyMatrix( addons ):
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
                
def printComplications ( addons ):
    print ("Unsatisfied mandatory dependencies:")
    for name in addons:                        
        if "uses" in addons [ name ]:
            if "mandatoryMissing" in addons [name]["uses"]:
                if 0 < len ( addons [name]["uses"]["mandatoryMissing"] ):
                    print ( "* ", addons[name]["Title"], ": ", ", ".join( addons [name]["uses"]["mandatoryMissing"] ) )
    print()
    print ("Unsatisfied optional  dependencies:")
    for name in addons:                        
        if "uses" in addons [ name ]:
            if "optionalMissing" in addons [name]["uses"]:
                if 0 < len ( addons [name]["uses"]["optionalMissing"] ):
                    print ( "* ", addons[name]["Title"], ": ", ", ".join( addons [name]["uses"]["optionalMissing"] ) )
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
    print ("[please be aware that addons starting with 'lib' are detected as library, even if they might not be a library]")
    print()
    
descriptionFiles = findValidAddonDescriptionFiles ( ADDON_ROOT )
addonInfo = readAddonInfoFiles ( descriptionFiles )

buildDependencyMatrix ( addonInfo )

printDependencyMatrix ( addonInfo )
printComplications ( addonInfo )
#pp.pprint ( addonInfo )
