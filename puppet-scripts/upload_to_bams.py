import sys
import getopt
import re
import os
import shutil
import glob
import hashlib

onlyPuppetCodeZip = False

def Usage():
    print ('**************************************************************')
    print ('Usage:')
    print ('-h,--help: print help message.')
    print ('-c,--component: component name, please choose cva_core, cva_config_manifest etc')
    print ('-v,--version: a version number, its format has to follow with 2.3.0-01')
    print ('-p,--puppet: upload only puppet code zip but not release package')
    print ('')
    print ('Sample:')
    print ('python upload_to_bams.py -c cva_core -v 2.3.0-01')
    print ('python upload_to_bams.py -c cva_core -p -v 2.5.1-10')    
    print ('**************************************************************')

def doUpload(filePath, fileName, bamsDir):
    

    uploadCmd = "curl -u zhuang.li:Retry@2018"
    
    fileToUpload = filePath + '/' + fileName
    targetFileInBams = bamsDir + '/' + fileName

    

    if os.path.isfile(fileToUpload):
        md5number = hashlib.md5(open(fileToUpload,'rb').read()).hexdigest()
        dquote = '"'
        
        checksumstr = " -H " + dquote + "X-Checksum-Md5: " + md5number + dquote

        # it is tricky that join following strings together with checksumstr would report an invalid identifier error, so join remaining strings one by one 
        fullCmd = uploadCmd + checksumstr
        fullCmd += " -T "
        fullCmd += fileToUpload
        fullCmd += " "
        fullCmd += targetFileInBams
        
        os.system(fullCmd)
    else:
        print("The file to be uploaded does not exist", fileToUpload)

def uploadToBams(component, version):
    dictPackageNames = {'cva_core':'CVA_Core_Releasev', 'cva_config_manifest':'CVA_Manifest_Releasev'}

    dictBamsDir = {'cva_core':'https://bams-apac-sami.int.thomsonreuters.com/artifactory/default.generic.global/cva/core',
                    'cva_config_manifest':'https://bams-apac-sami.int.thomsonreuters.com/artifactory/default.generic.global/cva/config-manifest'}

    if component not in dictPackageNames:
        print("Component" , component, "is not support to upload to BAMS, exit")
        return False

    mver = re.match(r"^(\d+)\.(\d+).(\d+)\-(\d+)$", version)
    
    packVer = ''
    
    if mver:
        packVer = mver.group(1) + '.' + mver.group(2) + '.' + mver.group(3)    
        
    releasePackage = dictPackageNames[component] + packVer + ".zip"
    puppetCodePackage = component + '-' + version + ".zip"

    if os.getenv("DDS_COLLECTIONS_HOME") is None:
        print ("System environment variable DDS_COLLECTIONS_HOME is not defined, exit")

    releasePackagePath = os.environ['DDS_COLLECTIONS_HOME'] + '/Release'

    doUpload(releasePackagePath, puppetCodePackage, dictBamsDir[component])
    
    if not onlyPuppetCodeZip:
        doUpload(releasePackagePath, releasePackage, dictBamsDir[component])


def main(argv):

    if len(sys.argv) == 1:
        Usage()
        sys.exit(2) 

    try:
        opts, args = getopt.getopt(argv[1:], 'hpv:c:', ['help','puppet', 'version=', 'component='])
    except:
        Usage()
        sys.exit(2)

    version = ''
    component = ''

    # Parse input arguments
    for o, a in opts:
        if o in ('-h', '--help'):
            Usage()
            sys.exit(1)
        if o in ('-v', '--version'):
            version = a
            
            if not re.match(r"^(\d+)\.(\d+).(\d+)\-(\d+)$", version):
                print ("The version number is not valid, the format has to follow like 4.5.6-01") 
                sys.exit(1)

        if o in ('-c', '--component'):
            component = a
            
        if o in ('-p', '--puppet'):
            onlyPuppetCodeZip = True
    
    if component != '' and version != '':
        uploadToBams(component, version)


if __name__ == '__main__':
    main(sys.argv)