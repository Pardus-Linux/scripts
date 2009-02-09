#!/bin/bash

texlive-common_is_file_present_in_texmf() {
local mark="${T}/$1.found"
find texmf -name $1 -exec touch "${mark}" \;
find texmf-dist -name $1 -exec touch "${mark}" \;
[ -f "${mark}" ]
}


for i  in `egrep '^(Mixed)?Map' "texmf/web2c/updmap.cfg" | sed 's@.* @@'`; do
    texlive-common_is_file_present_in_texmf "$i" || echo "$i"
done > "${T}/updmap_update"
{
    sed 's@/@\\/@g; s@^@/^MixedMap[     ]*@; s@$@$/s/^/#! /@' <"${T}/updmap_update"
    sed 's@/@\\/@g; s@^@/^Map[  ]*@; s@$@$/s/^/#! /@' <"${T}/updmap_update"
} > "${T}/updmap_update2"
sed -f "${T}/updmap_update2" "texmf/web2c/updmap.cfg" > "${T}/updmap_update3"\
&& cat "${T}/updmap_update3" > "texmf/web2c/updmap.cfg"

