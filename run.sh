#!/bin/bash
NOTLD="$(readlink -f -- "$(dirname -- "${0}")")"

alias lift="sudo python ${NOTLD}/lift/lift.py -f -p 80"
alias kebab="(cd ${NOTLD}/kebabfight/; python kebab_fight.py -f)"

function ff()
{
    firefox "${NOTLD}/z/${1}" &
}

alias z-mic="ff micshout.swf"
alias z-road="ff roadwalk.swf"

function cs()
{
    swift "${@}" &
    clear
    cowsay "${@}"
}

