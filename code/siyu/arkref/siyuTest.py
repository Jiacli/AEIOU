import sys
import re

def main(src, dst):
    f = open(dst, 'w')
    entityDict = dict()
   
    for line in open(src, 'r'):
        newLine = ""
        newLinePointer = 0
      #  print "we see the line ", line
        for tag in re.finditer(r'(<mention)', line):
          #  print "we see the stag ",tag.group(1), tag.start()
            startIndex = tag.start()
            if startIndex > 0:
                newLine += line[newLinePointer:startIndex ]
            endTemp = line[startIndex : -1].find(">") + startIndex
           # print " the end ",endTemp
            content = line[startIndex + 1: endTemp ]
           # print "we see content ", content
            entityId = content.split(" ")[2].split("=")[1]
            entityContentEnd = line[endTemp : -1].find("<") + endTemp 
            entityContent = line[endTemp + 1: entityContentEnd ]
            if entityId not in entityDict:
                entityDict[entityId] = entityContent
            else:
                entityContent = entityDict[entityId]

            newLine += entityContent
            newLinePointer = line[entityContentEnd + 1: -1].find(">") + entityContentEnd  + 1 + 1
        newLine += line[newLinePointer: -1] 

       # print newLine
        f.write(newLine+'\n')

    f.close()

if __name__ == '__main__':
    src = sys.argv[1]
    dst = sys.argv[2]
    main(src, dst)