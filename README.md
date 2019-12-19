# Cryogen
A python script for showing differences between binary files.
To get started clone this repository into a Ubuntu virtual machine.
Execute the following script ``` ubuntu_dep_install.sh ```

### Features
1. Diff multiple img signatures.
2. Verify md5 checksums of extracted files.
4. Verify md5 sums of all files in an extracted file-systems.

### To-do List
  - [x] Change carv md5 verification to output list, then typecast the list into a set to do 'difference'.
     - [x] Display common extracted files that have a different checksums from each image.
     - [x] Display extracted files in img1 that do not appear in img2.
     - [x] Display extracted files in img2 that do not appear in img1.
  - [x] Make the following changes to the root-file system diffing function.
     - [x] Display files with varying checksums, but both images have those files.
  - [ ] System is a bit slugish, optimize processing functions so they can be faster.
     - [ ] Don't do indexing instead just run through the list with range(0, len(list)).

### Dependencies
Install Binwalk from scratch. There is also an installation script one can run on Ubuntu systems. ``` ubuntu_dep_install.sh ```
  - ```wget https://github.com/ReFirmLabs/binwalk/archive/master.zip```
  - ```unzip master.zip```
  - ```(cd binwalk-master && sudo python setup.py uninstall && sudo python setup.py install)```
  - ```sudo ./binwalk-master/deps.sh```

### Usage

### Issues

### Examples
