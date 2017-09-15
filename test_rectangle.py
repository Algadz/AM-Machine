import regex
txt = "E125 ;    E3  E69"

print(regex.findall("(?<!;.*)E(\d*)", txt))
