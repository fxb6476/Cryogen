# Cryogen
A python script for showing differences between binary files.
To get started clone this repository into a Ubuntu virtual machine.
Execute the following script ``` ubuntu_dep_install.sh ```

### Features
1. Uses binwalk to perform signature analysis of binary files.
2. Verify md5 checksums of carved files.
3. Verify md5 checksums of files within an extracted root-file system.

### Dependencies
Install Binwalk from scratch. There is also an installation script one can run on Ubuntu systems. ``` ubuntu_dep_install.sh ```
  - ```wget https://github.com/ReFirmLabs/binwalk/archive/master.zip```
  - ```unzip master.zip```
  - ```(cd binwalk-master && sudo python setup.py uninstall && sudo python setup.py install)```
  - ```sudo ./binwalk-master/deps.sh```

### Usage
   - First add all the images you would like to compare into the 'imgs' directory.
   - Next run the python script. ``` python diff.py ```
   - This will compare all images to all others. 
      - Ex: imgs = [a, b, c] ; comparision table = [ (a,b) , (a,c), (b,c) ]

### Examples
   - Compare all files in 'imgs' directory with a single image file.
      - ``` python diff.py --img <path-to-ur-img> ```
      - Ex: imgs = [a, b, c] ; my-image = d ; comparision table = [ (d,a) , (d,b) , (d,c) ]
   - When images are compared binwalk will extract file-systems and other resources from these images. To clean up these extracted directories use tthe ``` --clean-up ``` parameter.
      - Ex: ``` python diff.py --clean-up ```
