#! /usr/bin/env perl
# Obsoleted in favor of ,sql in vi

$cnt_arg = $#ARGV + 1;

if( $cnt_arg < 1) {
	print "Usage: fixSQL sql_input_file";
}

$in_file = $ARGV[0];

my @lines = <FH>;

{
	local( $\, *FH );
	open( FH, $in_file ) or die "Unable to open SQL file for reading.";
	$in_text = <FH>;
}

close(FH);

$in_text =~s/`,`/`,\n`/gs;

print $in_text;
