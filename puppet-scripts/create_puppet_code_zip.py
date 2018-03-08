import sys
import getopt
import re
import os
import shutil
import zipfile
import glob

def Usage():
    print ('**************************************************************')
    print ('Usage:')
    print ('-h,--help: print help message.')
    print ('-c,--component: component name, please choose cva_core, cva_config_manifest etc')
    print ('-v,--version: a version number, its format has to follow with 2.3.0-01')
    print ('')
    print ('Sample:')
    print ('python create_puppet_code_zip.py -c cva_core -v 2.3.0-01') 
    print ('**************************************************************')

def ReplaceVersionNumber(com, ver):

    packVer = ''
    mver = re.match(r"^(\d+)\.(\d+).(\d+)\-(\d+)$", ver)
    
    if mver:
        packVer = mver.group(1) + '.' + mver.group(2) + '.' + mver.group(3)

    os.chdir('modules/' + com + '/manifests/')
    
    for ppFileName in glob.glob('*.pp'):
        with open(ppFileName, "rt") as fin:
            with open('out_' + ppFileName, "wt") as fout:
                for line in fin:
                    fout.write(line.replace('mjrVer.mnrVer.bldNum', packVer))

        os.remove(ppFileName)
        os.rename('out_'+ppFileName, ppFileName)
    os.chdir('../../../..')


def CreateZipPackage(com, ver):

    if os.getenv("DDS_COLLECTIONS_HOME") is None:
        print ("System environment variable DDS_COLLECTIONS_HOME is not defined, exit")
        return

    releasePackagePath = os.environ['DDS_COLLECTIONS_HOME'] + '/Release'

    if not os.path.exists(releasePackagePath):
        os.mkdir(releasePackagePath)

    os.chdir(releasePackagePath)

    if not os.path.exists('temp'):
        os.mkdir('temp')

    os.chdir('temp')

    if os.path.exists('modules'):
        shutil.rmtree('modules')
    shutil.copytree(os.environ['DDS_COLLECTIONS_HOME'] + '/CVA/Trunk/Tools/Puppet/code/' + com + '/modules', 'modules')

    ReplaceVersionNumber(com, ver)

    shutil.make_archive(com + '-' + ver, 'zip', 'temp')

    print ("********************************************") 
    print ("Puppet code zip:", com + '-' + ver + '.zip', "is now generated under", releasePackagePath)
    print ("Please check it out")     
    
    
def main(argv):

    if len(sys.argv) == 1:
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
            
            if not re.match(r"^(\d+)\.(\d+).(\d+)\-(\d+)$", version):
                print ("The version number is not valid, the format has to follow like 4.5.6-01") 
                sys.exit(1)

        if o in ('-c', '--component'):
            component = a
    
    if component != '' and version != '':
        CreateZipPackage(component, version)


if __name__ == '__main__':
    main(sys.argv)

