#!/bin/sh

TEMP_DIR=tmp

echo "Starting deb package build"

echo "Making temporary directory tree"
mkdir -p $TEMP_DIR
mkdir -p $TEMP_DIR/usr/local/mypl/
mkdir -p $TEMP_DIR/DEBIAN

echo "Copy control file for DEBIAN/"
cp src/DEBIAN/control $TEMP_DIR/DEBIAN/

echo "conffiles setup for src/DEBIAN"
# cp src/DEBIAN/conffiles $TEMP_DIR/DEBIAN/
cp src/DEBIAN/postinst $TEMP_DIR/DEBIAN/
# cp src/DEBIAN/prerm $TEMP_DIR/DEBIAN/

echo "Copy binary into place"
cp src/bin/* $TEMP_DIR/usr/local/mypl/




echo "Building deb file"
dpkg-deb --root-owner-group --build $TEMP_DIR
mv $TEMP_DIR.deb mypl-v1.0.0.deb


echo "Complete."