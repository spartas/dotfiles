#!/usr/bin/perl -w

use strict;

open (FILE, $ENV{'HOME'} . "/.zshrc") or die "Can not open file";
undef $/;    #Unset variable to read whole file as one variable.
my $text = <FILE>; $text =~ s/## BEGIN_BLOCK IP ##.*?## END_BLOCK IP ##//gism;
print $text;
close FILE;
$/ = "n";    #Reset variable to original definition exit();

