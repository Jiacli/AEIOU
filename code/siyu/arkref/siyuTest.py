import sys
import re

# input is a list of strings
def coreference_resolution(input_pharagraph):
    rst = ""
    entityDict = dict()
    targetPronoun = ['IT','THIS','THAT','SHE','HE','HIS','HER','ITS','THESE','THOSE']
    for line in input_pharagraph:
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
            elif entityContent.upper() in targetPronoun:
                entityContent = entityDict[entityId]
            newLine += entityContent
            newLinePointer = line[entityContentEnd + 1: -1].find(">") + entityContentEnd  + 1 + 1
        newLine += line[newLinePointer: -1] 
        rst += newLine +'\n'

    return rst

def main(src, dst):
    f = open(dst, 'w')
    entityDict = dict()

    targetPronoun = ['IT','THIS','THAT','SHE','HE','HIS','HER','ITS','THESE','THOSE']
   
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
            elif entityContent.upper() in targetPronoun:
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