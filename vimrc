"=========================================================================="
"
" Description: 	My personal vimrc. I am in the process of cleaning it up.
"
" Author: 			T.Wright <spartas AT gmail DOT com>
"
" Last Change:  2009.07.23
"
" Version: 			0.015
"
" Usage: 				I am unable to provide content from my sources directory.
" 	See line 46.
"=========================================================================="

" ============
" Nice buffers
" ============
map <F7> :b# <CR>

" ====== === =============== === ===== ====
" VimTip for editing/loading teh vimrc file
" ====== === =============== === ===== ====
nmap ,s :source $MYVIMRC
nmap ,v :e $MYVIMRC


" =====================
" Dis/Enable Paste Mode
" =====================
"map <S-F11> :call Paste_on_off()<CR>
set pastetoggle=<S-F11>

let paste_mode = 0 " 0 = normal, 1 = paste

set visualbell
set cul
set modeline

set nocompatible

" ===
" PDV
" ===
so ~/.vim/plugin/supertab.vim

" Include various helper files [Commented]
" (This includes things I am unable to provide for intelluctual
" property, copyright, and/or personal reasons)
"ru! ~/.vim/sources/*.vim


" ===========================
" The paste switcher function
" ===========================
"func! Paste_on_off()
"  if g:paste_mode == 0
"    set paste
"    let g:paste_mode = 1
"  else
"    set nopaste
"    let g:paste_mode = 0
"  endif
"  return
"endfunc


" =======================================
" Dark background to match your dark soul
" =======================================
set bg=dark


" ===================================
" Smart options for those who program
" ====================================
set smarttab
set noexpandtab
set tabstop=2
set shiftwidth=2
set autoindent
set smartindent
set cindent
"filetype plugin indent on
set fmr={,}
set linespace=1 " Display additional space between lines for easier readability
set fo=tcrqn
set ignorecase
set smartcase


" =============================================
" Syntax highlighting and incremental searching
" =============================================
syn on
set incsearch


" ======================================
" Do syntax highlight syncing from start
" ======================================
autocmd BufEnter * :syntax sync fromstart

" ===========================
" Always show the status line
" ===========================
set ruler

" ============================
" Format with Q in visual mode
" ============================
nnoremap Q gq

" Remap ctrl-space to omnicompletion
" Thx mattikus
inoremap <C-space> <C-x><C-o>

map <F10> :new<CR>:read !svn diff<CR>:set syntax=diff buftype=nofile<CR>gg

set notr


" ============
" PHP Checking
" ============
:set autowrite " Enabled, so files are automatically saved before syntax checking is performed

:set makeprg=php\ -l\ %
:set errorformat=%m\ in\ %f\ on\ line\ %l

" taglist plugin settings
"let Tlist_Inc_Winwidth = 0
let tlist_php_settings = 'php;c:class;f:function'
noremap <silent> <F8> :TlistToggle<CR>

set mousehide

" ==========
" 256 Colors
" ==========
set t_Co=256


" =======================
" Hide un-necessary files
" =======================
let g:explHideFiles='^\.svn,\.$'

" No help, plz
nmap <F1> <Esc>
	

map <F10> :new<CR>:read !svn diff<CR>:set syntax=diff buftype=nofile<CR>gg

set notr


if version > 700
	set autochdir "Magic

endif

"let g:SuperTabDefaultCompletionType = "<C-X><C-O>"

" HTML generation
let html_use_css = 1
let use_xhtml = 1

" Highlighted groups
:hi Commented_CSS ctermbg=darkgreen guibg=darkgreen


" Highlighting matches
:match Commented_CSS /\/\*\s*\(\w\|-\)*\s*:\s\(\w\|\s\)*;\?\*\//
:match Commented_CSS /\/\*\s*\(\w\|-\)*\s*:\s\(\w\|\s\)*;\?\s*\*\//

" Pretty print SQL
map ,sql <ESC>:s/\(from\<Bar>where\<Bar>select\<Bar>left join\)/<C-V><CR>\U\1/g
vmap ,sql <ESC>:'<,'>s/\(from\<Bar>where\<Bar>select\<Bar>left join\)/\U\1/g

" Nifty abbreviations
iab AlP ABCDEFGHIJKLMNOPQRSTUVWXYZ
iab MoN January February March April May June July August September October November December
iab MoO Jan Feb Mar Apr May Jun Jul Aug Sep Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec
iab NuM 12345678901234567890123456789012345678901234567890123456789012345678901234567890 
iab RuL -----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8----+----9----+----0----+----1----+----2

