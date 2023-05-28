menu_push() {
    git pull;git add .;git commit -m 'push';git push
}

menu() {
    if type "menu_$1" >/dev/null 2>&1; then
        cmd=$1
        shift
        "menu_$cmd" "$@"
    else
        echo "menu: $1 is not in the menu."
    fi
}