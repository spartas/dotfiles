#!/usr/bin/perl -w

# Used to mount VirtualBox Disk Image (.vdi) files
use strict;
my $infile=shift;
open(my $f, "<", $infile) or die $!;
my $buf;
read($f, $buf, 348);
close $f;

my $vditype=substr($buf, 76, 1);
if($vditype ne "\002") {
        die "type is not fixed size";
}
