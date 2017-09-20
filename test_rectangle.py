import regex
text = "G92 G3 X0 E0"
print(regex.findall("(?<!;.*)G(0|1|3|92|90|91)\s", text)) # todo : include 2 char