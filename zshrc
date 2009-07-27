autoload -U compinit promptinit
compinit
promptinit
prompt clint 			# Clint theme
cat /etc/remind  	# Reminders

# Aliases

alias path='echo -e ${PATH//:/\\n}'

#o_O pretty
alias ls='ls --color'
alias tree='tree -C'

## Need to comment more on these
alias realias="vim $HOME/.zshrc; source $HOME/.zshrc"

alias gvim='gvim -p'
alias vim='vim -p'

alias nsvim='gvim -S ~/.vim/sources/*.vim'
alias ns='nsvim'

alias xo="xdg-open"

alias ack='ack-grep'

# Shamelessly stolen from mattikus
alias cal='cal | sed "s/.*/ & /;s/ \($(date +%e)\) / $(echo -e "\033[01;31m")\1$(echo -e "\033[00m") /"'

# Some of mine
alias digg='dig +short'
alias ll='ls -lFhrt --color=auto'
alias lla='ls -lAhrt --color=auto'
alias l="ll"
alias ..="cd .."
alias ...="cd ../.."
alias svim='sudo gvim'
alias grep='grep --color=auto'
alias cgrep='grep --color=always'
alias igrep='grep -i'
alias lsd="tree -d -L 1"



alias startmdns='/home/twright/mDNSResponder-107.6/mDNSPosix/build/prod/mDNSProxyResponderPosix 127.0.0.1 squeal "story:remote" _daap._tcp. 3689'

# Do I ever use these anymore?
alias sep='EDITOR=pico'
alias sev='EDITOR=vim'

# Handy
alias stopwatch="time > /dev/null"


# Handles SVN externals
alias resvndiff="for i in *; do svn diff \"\$i\"; done"

alias info="info --vi-keys"



alias gvd="gvimdiff"

# Stolen from someone's bashrc
alias findy="find . -xdev -name"
alias sc="grep -v '^[ ]*#\|^[	]*$' " # Remove spaces and comments from files

alias VCfind="find . -type f -iname \"$1\" | grep -v \"\.svn\""

# Prevent accidentally pingspamming servers
alias ping="ping -c 25"

# Go back
alias gb="cd $OLDPWD" # I should use this one more

# SVN 
alias svnlast='svn log --limit 1'
# Before ack
alias nosvn="svn st | grep \"^[?]\""


#Exports
export EDITOR='vim'
export LESS=-R





# I don't use this either
export CDPATH='$HOME/.paths'



set -o vi

hosts=(story)


# Tab completion for ssh
compctl -k hosts ssh

# Functions
function van
{
	/usr/bin/man $* | col -b | /usr/bin/gview -c 'set ft=man nomod nolist' -
}

# Wrapper for "svn diff"
function svndiff()
{
svn diff $@ | gvim - "+%foldo!" "+set bt=nofile"
}

function tell()
{
	tail -20 $@ | head
}
 
# From http://woss.name/2007/02/01/display-svn-changelog-on-svn-up
function svnrev()
{
svn info $@ | awk '/^Revision:/ {print $2}';
}
 
# From http://woss.name/2007/01/01/display-svn-changelog-on-svn-up
function svnup()
{
local old_revision=`svnrev $@`
local first_update=$((${old_revision} + 1))
svn up -q $@
if [ $(svnrev $@) -gt ${old_revision} ]; then
svn log -v -rHEAD:${first_update} $@
else
echo "No changes."
fi
}

function svnci() {
	local SVN="`which svn`"
	${SVN} commit -m "'$*'"
}

function svnst() {
	local SVN="`which svn`"
	# My thanks for this snippet go to Kore Nordmann
	# (http://kore-nordmann.de)
	${SVN} st --ignore-externals "$@" | grep -v '^X' | sed -e 's/^\?.*$/[1;34m\0[m/' -e 's/^!.*$/[1;31m\0[m/' -e 's/^A.*$/[1;32m\0[m/' -e 's/^M.*$/[1;33m\0[m/' -e 's/^D.*$/[0;31m\0[m/'
}

function phpsh() {
	echo "$1"
	php -r "echo $1;"
}

function strtotime() {
	phpsh "date( 'Y-m-d H:i:s', strtotime('$*') )"
}

# Useful for parsing PHP logs for unique messages
function sniplog() {
	grep -e "^\[" | sed -e "s/\[[^]]*\]//" | sort | uniq
}


# Very nifty function I stole from somewhere
function mycd {

MYCD="$HOME/.mycd.txt"
touch ${MYCD}

typeset -i x
typeset -i ITEM_NO
typeset -i i
x=0

if [[ -n "${1}" ]]; then
   if [[ -d "${1}" ]]; then
      print "${1}" >> ${MYCD}
      sort -u ${MYCD} > ${MYCD}.tmp
      mv ${MYCD}.tmp ${MYCD}
      FOLDER=${1}
   else
      i=${1}
      FOLDER=$(sed -n "${i}p" ${MYCD})
   fi
fi

if [[ -z "${1}" ]]; then
   print ""
   cat ${MYCD} | while read f; do
      x=$(expr ${x} + 1)
      print "${x}. ${f}"
   done
   print "\nSelect #"
   read ITEM_NO
   FOLDER=$(sed -n "${ITEM_NO}p" ${MYCD})
fi

if [[ -d "${FOLDER}" ]]; then
   cd ${FOLDER}
fi

}

function treediff() {
	diff -X ~/svn_exclusion.txt -r "$@"
}

# Key Maps
bindkey  history-incremental-search-backward

