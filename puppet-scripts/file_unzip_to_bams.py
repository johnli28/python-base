import sys
import getopt
import re
import os
import shutil
import glob
import hashlib

def Usage():
    print ('**************************************************************')
    print ('Usage:')
    print ('-h,--help: print help message.')
    print ('-c,--component: component name, please choose cva_core, cva_config_manifest etc')
    print ('-v,--version: a version number, its format has to follow with 2.3.0')
    print ('')
    print ('Sample:')
    print ('python upload_to_bams.py -c cva_core -v 2.3.0') 
    print ('**************************************************************')

def doUpload():
    

    uploadCmd = "curl -u zhuang.li:Retry@2018"
    
    fileToUpload = 'unzip.exe'
    targetFileInBams = 'https://bams-emea-sami.int.thomsonreuters.com/artifactory/default.generic.global/cva/toolkit/' + 'unzip.exe'

    

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


def main(argv):

    if len(sys.argv) == 1:
        doUpload()
        Usage()
        sys.exit(2) 

    try:
        opts, args = getopt.getopt(argv[1:], 'hv:c:', ['help', 'version=', 'component='])
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
            
            if not re.match(r"^(\d+)\.(\d+).(\d+)$", version):
                print ("The version number is not valid, the format has to follow like 4.5.6") 
                sys.exit(1)

        if o in ('-c', '--component'):
            component = a
    
    if component != '' and version != '':
        uploadToBams(component, version)


if __name__ == '__main__':
    main(sys.argv)