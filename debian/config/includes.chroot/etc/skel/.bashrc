# OpenBruma shell environment
[ -f /etc/bash.bashrc ] && . /etc/bash.bashrc

HISTCONTROL=ignoreboth
HISTSIZE=10000
HISTFILESIZE=20000
shopt -s histappend checkwinsize

# WIC neo-noir prompt
PS1='\[\e[38;2;46;230;160m\]\u\[\e[0m\]@\[\e[38;2;0;184;255m\]\h\[\e[0m\] \[\e[38;2;176;184;197m\]\w\[\e[0m\]\n\[\e[38;2;46;230;160m\]»\[\e[0m\] '

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

# Branded banner with live system metrics on every new terminal.
if [ -n "$PS1" ] && [ -z "$OPENBRUMA_BANNER_SHOWN" ] && [ "${TERM:-dumb}" != "dumb" ]; then
  export OPENBRUMA_BANNER_SHOWN=1
  echo
  if [ -r /usr/share/openbruma/ascii-logo.txt ]; then
    cat /usr/share/openbruma/ascii-logo.txt
    echo
  fi
  if command -v fastfetch >/dev/null 2>&1; then
    fastfetch --config "$HOME/.config/fastfetch/config.jsonc" 2>/dev/null || fastfetch
  else
    printf '  OPENBRUMA  WinterGate Intelligence Collective\n'
    printf '  Host   : %s\n' "$(hostname)"
    printf '  Kernel : %s\n' "$(uname -r)"
    printf '  Uptime : %s\n' "$(uptime -p 2>/dev/null || uptime)"
    printf '  Memory : %s\n' "$(free -h 2>/dev/null | awk '/Mem:/ {print $3" / "$2}')"
  fi
  printf '\n  \033[2mDocs: https://github.com/WinterGate-IC/OpenBruma\033[0m\n\n'
fi
