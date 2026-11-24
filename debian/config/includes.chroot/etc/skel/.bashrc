# OpenBruma shell environment
[ -f /etc/bash.bashrc ] && . /etc/bash.bashrc

HISTCONTROL=ignoreboth
HISTSIZE=10000
HISTFILESIZE=20000
shopt -s histappend checkwinsize

# WIC neo-noir prompt
PS1='\[\e[38;2;0;255;157m\]\u\[\e[0m\]@\[\e[38;2;0;184;255m\]\h\[\e[0m\] \[\e[38;2;176;184;197m\]\w\[\e[0m\]\n\[\e[38;2;0;255;157m\]❯\[\e[0m\] '

alias ls='ls --color=auto'
alias ll='ls -lah --color=auto'
alias la='ls -A --color=auto'
alias grep='grep --color=auto'
alias bruma='fastfetch --config ~/.config/fastfetch/config.jsonc'
alias wic='fastfetch --config ~/.config/fastfetch/config.jsonc'
alias openbruma='fastfetch --config ~/.config/fastfetch/config.jsonc'

# Helpful OSINT shortcuts
alias ports='ss -tulpn'
alias myip='curl -s https://ifconfig.me; echo'
