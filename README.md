# Cryogen
   - A python script for showing differences between binary files.
   - To get started clone this repository into a Ubuntu virtual machine.
   - Execute the following script ``` ubuntu_dep_install.sh ```

### Features
| Parameter | Description|
| --- | --- |
| --img IMG | Specify image you would like to analyze against. |
| --more-carvs | Show particular carvs. |
| --more-files | Show particular files. |
| --clean-up | Clean up extracted directories. |
| --rfs-filters FSFILTER [FSFILTER ...] | Only output files whos paths match these strings. |

1. Uses binwalk to perform signature analysis of binary files.
2. Validate md5 checksums of carved files.
3. Validate md5 checksums of files within an extracted root-file system.

### Dependencies
Install Binwalk from scratch, or on Ubuntu VM's use installation script. ``` ubuntu_dep_install.sh ```
  - ```wget https://github.com/ReFirmLabs/binwalk/archive/master.zip```
  - ```unzip master.zip```
  - ```(cd binwalk-master && sudo python setup.py uninstall && sudo python setup.py install)```
  - ```sudo ./binwalk-master/deps.sh```

### Usage
   - Run installation script. 
   - Make a file called ``` imgs ``` in the root of this repo.
   - Add images you would like to compare, into the 'imgs' directory.
   - Next run the python script. ``` python diff.py ```
   - This will compare all images to each other. 
      - Ex: imgs = [a, b, c] ; comparision table = [ (a,b) , (a,c), (b,c) ]

### Examples
   - Compare all files in 'imgs' directory with 'my-image.chk'.
      - ``` python diff.py --img my-image.chk ```
      - Ex: imgs = [a, b, c] ; my-image = d ; comparision table = [ (d,a) , (d,b) , (d,c) ]
   - Compare all files in 'imgs' directory with each other, clean up after yourself.
      - Ex: ``` python diff.py --clean-up ```
   - Compare 'my-image.chk' with all files in 'imgs' directory and only show me things that have been changed in '/etc/' or 'root/bin/', and clean up after yourself.
      - Ex: ``` python diff.py --img my-image.chk --clean-up --rfs-filters /etc/ root/bin/ ```
   - Compare all files in 'imgs' directory with each other and only show me things that have changed in '/www/', clean up after yourself.
      - Ex: ``` python diff.py --clean-up --rfs-filters /www/ ```
   - Compare all files in 'imgs' and give me everything! Clean up after yourself.
      - Ex: ``` python diff.py --clean-up --more-files --more-carvs ```
