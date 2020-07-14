colorscheme inkpot
set shell=/bin/zsh

set lines=48
set columns=120

" set guioptions=em
set showtabline=2

" Set the font
if has("gui_gtk2")
	set gfn=Anonymous\ Pro\ 11
elseif has("gui_macvim")
	set gfn=Anonymous\ Pro:h12
endif

" ==============
" Line Numbering
" ==============
set number

set guioptions-=t
set guioptions+=aT

" Had a bad experience with the "Print" toolbar button (Print is, and always shall be, under File->Print)
if has("toolbar")
	aunmenu ToolBar.Print
endif

" Make shift-insert work as it does in gnome-terminal
map <S-Insert> <MiddleMouse>
map! <S-Insert> <MiddleMouse>

